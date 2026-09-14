"""
EP01 — Camada SILVER (bronze -> PostgreSQL)

Lê os documentos crus do MongoDB (bronze), transforma e popula o modelo
dimensional no PostgreSQL. Lê SOMENTE da bronze — nunca da API ou dos CSVs.

Etapas:
  1. recria o schema silver (roda sql/silver.sql)
  2. popula dim_geracao, dim_tipo e efetividade_tipo
  3. concilia pokemon_csv <-> PokéAPI por nome, popula dim_pokemon e log_conciliacao
  4. popula fato_confronto no grão de participação (2 linhas por combate)

Conciliação (3 níveis, por nome):
  a. pokemon por nome canônico (trata Mega/Primal, apóstrofos, ♀/♂, acentos)
  b. forma padrão da espécie (nomes-base tipo "Deoxys")
  c. fallback: espécie cujo nome aparece no nome do CSV (formas alternativas:
     "Heat Rotom", "Deoxys Attack Forme", ...) — atributos vêm da espécie;
     tipos e status vêm do próprio CSV (form-accurate e consistente com a simulação).

Uso:
    python carregar.py          (rode a partir da raiz do projeto)

Idempotência: sql/silver.sql recria as tabelas do zero a cada execução.
"""

import os
import re
import csv
import unicodedata
import psycopg
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI    = os.getenv("MONGO_URI", "mongodb://localhost:27017")
POSTGRES_URI = os.getenv("POSTGRES_URI", "postgresql://localhost:5432/pokedex")
DB_BRONZE    = "pokedex_bronze"

GERACOES = [
    (1, "Geração I",   "Kanto"),
    (2, "Geração II",  "Johto"),
    (3, "Geração III", "Hoenn"),
    (4, "Geração IV",  "Sinnoh"),
    (5, "Geração V",   "Unova"),
    (6, "Geração VI",  "Kalos"),
]

ROMANO_PARA_NUM = {
    "generation-i": 1, "generation-ii": 2, "generation-iii": 3,
    "generation-iv": 4, "generation-v": 5, "generation-vi": 6,
}

CONCILIACAO_CSV = "conciliacao.csv"   # relatório exigido por R4


# ----------------------------------------------------------------------------
# Utilitários de arquivo/SQL
# ----------------------------------------------------------------------------
def achar_silver_sql():
    aqui = os.path.dirname(os.path.abspath(__file__))
    raiz = os.path.abspath(os.path.join(aqui, ".."))
    env = os.getenv("SILVER_SQL_PATH")
    if env and os.path.exists(env):
        return env
    candidatos = [
        os.path.join(os.getcwd(), "sql", "silver.sql"),
        os.path.join(os.getcwd(), "silver.sql"),
        os.path.join(aqui, "silver.sql"),
        os.path.join(aqui, "sql", "silver.sql"),
        os.path.join(raiz, "sql", "silver.sql"),
        os.path.join(raiz, "silver.sql"),
    ]
    for c in candidatos:
        if os.path.exists(c):
            return c
    for base, dirs, arquivos in os.walk(raiz):
        dirs[:] = [d for d in dirs if d not in (".venv", ".venv-antigo",
                                                "dados_brutos", ".git", "__pycache__")]
        if "silver.sql" in arquivos:
            return os.path.join(base, "silver.sql")
    raise FileNotFoundError(
        "Não encontrei o arquivo silver.sql no projeto. Salve-o em uma pasta do "
        "projeto (ex.: silver/silver.sql), ou aponte o caminho em SILVER_SQL_PATH."
    )


def dividir_comandos(sql):
    sql = "\n".join(re.sub(r"--.*$", "", linha) for linha in sql.splitlines())
    comandos, buffer = [], []
    em_dollar = em_aspas = False
    i, n = 0, len(sql)
    while i < n:
        par = sql[i:i + 2]
        c = sql[i]
        if not em_aspas and par == "$$":
            em_dollar = not em_dollar
            buffer.append(par); i += 2; continue
        if not em_dollar and c == "'":
            em_aspas = not em_aspas
            buffer.append(c); i += 1; continue
        if c == ";" and not em_dollar and not em_aspas:
            cmd = "".join(buffer).strip()
            if cmd:
                comandos.append(cmd)
            buffer = []; i += 1; continue
        buffer.append(c); i += 1
    resto = "".join(buffer).strip()
    if resto:
        comandos.append(resto)
    return comandos


def executar_sql_arquivo(conn, caminho):
    with open(caminho, encoding="utf-8") as f:
        sql = f.read()
    with conn.cursor() as cur:
        for comando in dividir_comandos(sql):
            cur.execute(comando)


# ----------------------------------------------------------------------------
# Conciliação de nomes
# ----------------------------------------------------------------------------
def canonizar(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", s.lower())


def csv_para_api(nome):
    n = (nome or "").strip()
    n = n.replace("\u2640", " f").replace("\u2642", " m")   # ♀ ♂
    m = re.match(r"(?i)^mega\s+(.+?)(?:\s+([xy]))?$", n)
    if m:
        base, suf = m.group(1), m.group(2)
        n = f"{base} mega" + (f" {suf}" if suf else "")
    p = re.match(r"(?i)^primal\s+(.+)$", n)
    if p:
        n = f"{p.group(1)} primal"
    return n


def to_int(v):
    v = (v or "").strip()
    return int(v) if re.fullmatch(r"-?\d+", v) else None


# ----------------------------------------------------------------------------
# Dimensões limpas
# ----------------------------------------------------------------------------
def carregar_dim_geracao(conn):
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO silver.dim_geracao (num_geracao, nome, regiao) VALUES (%s, %s, %s)",
            GERACOES,
        )
    print(f"dim_geracao:      {len(GERACOES)} gerações (+ membro especial)")


def carregar_dim_tipo_e_efetividade(conn, bronze):
    tipos = list(bronze["tipos"].find({"id": {"$lte": 18}}))
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO silver.dim_tipo (id_tipo, nome) VALUES (%s, %s)",
            [(t["id"], t["name"]) for t in tipos],
        )
        cur.execute("SELECT nome, sk_tipo FROM silver.dim_tipo WHERE id_tipo IS NOT NULL")
        sk_por_nome = dict(cur.fetchall())
    print(f"dim_tipo:         {len(tipos)} tipos (+ membro especial)")

    linhas = []
    for t in tipos:
        atacante = sk_por_nome[t["name"]]
        mult = {nome: 1.0 for nome in sk_por_nome}
        dr = t["damage_relations"]
        for d in dr["double_damage_to"]:
            if d["name"] in mult: mult[d["name"]] = 2.0
        for d in dr["half_damage_to"]:
            if d["name"] in mult: mult[d["name"]] = 0.5
        for d in dr["no_damage_to"]:
            if d["name"] in mult: mult[d["name"]] = 0.0
        for nome_def, m in mult.items():
            linhas.append((atacante, sk_por_nome[nome_def], m))
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO silver.efetividade_tipo "
            "(sk_tipo_atacante, sk_tipo_defensor, multiplicador) VALUES (%s, %s, %s)",
            linhas,
        )
    print(f"efetividade_tipo: {len(linhas)} combinações (esperado 324)")


# ----------------------------------------------------------------------------
# Conciliação + dim_pokemon
# ----------------------------------------------------------------------------
def carregar_conciliacao_e_pokemon(conn, bronze):
    especies = list(bronze["especies"].find())
    pokemons = list(bronze["pokemon"].find())
    especie_por_nome = {canonizar(e["name"]): e for e in especies}
    pokemon_por_nome = {canonizar(p["name"]): p for p in pokemons}
    default_por_especie = {}
    for p in pokemons:
        if p.get("is_default"):
            default_por_especie[canonizar(p["species"]["name"])] = p

    def conciliar(nome_csv):
        """Retorna (especie, pokemon) ou (None, None)."""
        if not nome_csv:
            return None, None
        chave = canonizar(csv_para_api(nome_csv))
        pk = pokemon_por_nome.get(chave) or default_por_especie.get(chave)
        if pk:
            esp = especie_por_nome.get(canonizar(pk["species"]["name"]))
            return esp, pk
        # fallback: espécie cujo nome canônico aparece no nome do CSV (maior casamento)
        canon_full = canonizar(nome_csv)
        melhor = None
        for canon_esp, esp in especie_por_nome.items():
            if canon_esp and canon_esp in canon_full:
                if melhor is None or len(canon_esp) > len(melhor[0]):
                    melhor = (canon_esp, esp)
        if melhor:
            esp = melhor[1]
            pk = default_por_especie.get(canonizar(esp["name"]))
            return esp, pk
        return None, None

    with conn.cursor() as cur:
        cur.execute("SELECT nome, sk_tipo FROM silver.dim_tipo")
        sk_tipo_por_nome = dict(cur.fetchall())
        cur.execute("SELECT num_geracao, sk_geracao FROM silver.dim_geracao "
                    "WHERE num_geracao IS NOT NULL")
        sk_geracao_por_num = dict(cur.fetchall())

    linhas = list(bronze["pokemon_csv"].find())
    dim_rows, log_rows = [], []
    tipo_por_csv, geracao_por_csv, velocidade_por_csv = {}, {}, {}
    conciliados = 0

    for l in linhas:
        num_csv = to_int(l["#"])
        nome_csv = (l.get("Name") or "").strip()
        velocidade_por_csv[num_csv] = to_int(l.get("Speed")) or 0

        # tipos vêm SEMPRE do CSV (form-accurate; base da simulação)
        t1 = (l.get("Type 1") or "").strip().lower()
        t2 = (l.get("Type 2") or "").strip().lower()
        tipo_primario = t1 or None
        tipo_secundario = t2 or "nenhum"

        esp, pk = conciliar(nome_csv)

        if esp is None:
            motivo = "sem nome" if not nome_csv else "nome não encontrado na PokéAPI"
            log_rows.append((num_csv, nome_csv or None, False, None, motivo))
            tipo_por_csv[num_csv] = -1        # rota para os membros especiais
            geracao_por_csv[num_csv] = -1
            continue

        conciliados += 1
        pk = pk or {}
        num_pokedex = esp.get("id")
        geracao = ROMANO_PARA_NUM.get((esp.get("generation") or {}).get("name"))

        is_leg = bool(esp.get("is_legendary"))
        is_myt = bool(esp.get("is_mythical"))
        is_bb  = bool(esp.get("is_baby"))
        if is_myt:   raridade = "Mítico"
        elif is_leg: raridade = "Lendário"
        elif is_bb:  raridade = "Bebê"
        else:        raridade = "Comum"

        is_mega = ("-mega" in pk.get("name", "")) or ("-primal" in pk.get("name", ""))

        hab = esp.get("habitat")
        if hab:
            habitat = hab["name"]
        elif geracao and geracao >= 4:
            habitat = "não se aplica"
        else:
            habitat = "desconhecido"
        cor = (esp.get("color") or {}).get("name")

        dim_rows.append((
            num_pokedex, num_csv, nome_csv,
            tipo_primario, tipo_secundario, geracao, raridade,
            is_leg, is_myt, is_bb, is_mega,
            habitat, cor,
            pk.get("height"), pk.get("weight"), pk.get("base_experience"),
            esp.get("capture_rate"), esp.get("base_happiness"),
            to_int(l.get("HP")), to_int(l.get("Attack")), to_int(l.get("Defense")),
            to_int(l.get("Sp. Atk")), to_int(l.get("Sp. Def")), to_int(l.get("Speed")),
        ))
        tipo_por_csv[num_csv] = sk_tipo_por_nome.get(tipo_primario, -1)
        geracao_por_csv[num_csv] = sk_geracao_por_num.get(geracao, -1)
        log_rows.append((num_csv, nome_csv, True, num_pokedex, None))

    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO silver.dim_pokemon "
            "(num_pokedex, num_csv, nome, tipo_primario, tipo_secundario, geracao, "
            " categoria_raridade, is_legendary, is_mythical, is_baby, is_mega, "
            " habitat, cor, altura, peso, base_experience, capture_rate, base_happiness, "
            " hp, ataque, defesa, sp_ataque, sp_defesa, velocidade) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            dim_rows,
        )
        cur.executemany(
            "INSERT INTO silver.log_conciliacao "
            "(num_csv, nome_csv, conciliado, num_pokedex, motivo) VALUES (%s,%s,%s,%s,%s)",
            log_rows,
        )
        cur.execute("SELECT num_csv, sk_pokemon FROM silver.dim_pokemon "
                    "WHERE num_csv IS NOT NULL")
        sk_pokemon_por_csv = dict(cur.fetchall())

    nao = len(linhas) - conciliados
    print(f"dim_pokemon:      {len(dim_rows)} conciliados (+ membro especial); "
          f"{nao} não conciliados")

    with open(CONCILIACAO_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["num_csv", "nome_csv", "conciliado", "num_pokedex", "motivo"])
        for r in sorted(log_rows, key=lambda x: (x[0] or 0)):
            w.writerow(r)
    print(f"                  relatório salvo em {CONCILIACAO_CSV}")

    return {
        "sk_pokemon": sk_pokemon_por_csv,
        "sk_tipo": tipo_por_csv,
        "sk_geracao": geracao_por_csv,
        "velocidade": velocidade_por_csv,
    }


# ----------------------------------------------------------------------------
# fato_confronto (grão de participação, via COPY)
# ----------------------------------------------------------------------------
def carregar_fato(conn, bronze, mapas):
    sk_pok = lambda c: mapas["sk_pokemon"].get(c, -1)
    sk_tp  = lambda c: mapas["sk_tipo"].get(c, -1)
    sk_ger = lambda c: mapas["sk_geracao"].get(c, -1)
    vel    = lambda c: mapas["velocidade"].get(c, 0)

    combates = bronze["combates"].find(
        {}, {"First_pokemon": 1, "Second_pokemon": 1, "Winner": 1}
    )
    total = 0
    colunas = ("id_combate, sk_pokemon, sk_pokemon_oponente, sk_tipo_participante, "
               "sk_tipo_oponente, sk_geracao, venceu, atacou_primeiro, diferenca_velocidade")
    with conn.cursor() as cur:
        with cur.copy(f"COPY silver.fato_confronto ({colunas}) FROM STDIN") as cp:
            for doc in combates:
                id_c = int(doc["_id"].split("/")[1])
                a = to_int(doc["First_pokemon"])
                b = to_int(doc["Second_pokemon"])
                w = to_int(doc["Winner"])
                cp.write_row((id_c, sk_pok(a), sk_pok(b), sk_tp(a), sk_tp(b),
                              sk_ger(a), 1 if w == a else 0, 1, vel(a) - vel(b)))
                cp.write_row((id_c, sk_pok(b), sk_pok(a), sk_tp(b), sk_tp(a),
                              sk_ger(b), 1 if w == b else 0, 0, vel(b) - vel(a)))
                total += 2
    print(f"fato_confronto:   {total} participações (esperado 100000)")


def contagens(conn):
    print("\n== Contagem silver ==")
    with conn.cursor() as cur:
        for tabela in ("dim_geracao", "dim_tipo", "efetividade_tipo",
                       "dim_pokemon", "fato_confronto", "log_conciliacao"):
            cur.execute(f"SELECT COUNT(*) FROM silver.{tabela}")
            print(f"  {tabela}: {cur.fetchone()[0]}")


def main():
    cliente = MongoClient(MONGO_URI)
    bronze = cliente[DB_BRONZE]
    with psycopg.connect(POSTGRES_URI) as conn:
        caminho_sql = achar_silver_sql()
        print(f"Recriando o schema silver a partir de: {caminho_sql}")
        executar_sql_arquivo(conn, caminho_sql)

        print("\n== Etapa 1: dimensões limpas ==")
        carregar_dim_geracao(conn)
        carregar_dim_tipo_e_efetividade(conn, bronze)

        print("\n== Etapa 2: conciliação e dim_pokemon ==")
        mapas = carregar_conciliacao_e_pokemon(conn, bronze)

        print("\n== Etapa 3: fato_confronto ==")
        carregar_fato(conn, bronze, mapas)

        conn.commit()
        contagens(conn)
    cliente.close()


if __name__ == "__main__":
    main()