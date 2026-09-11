import os
import re
import psycopg
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI     = os.getenv("MONGO_URI", "mongodb://localhost:27017")
POSTGRES_URI  = os.getenv("POSTGRES_URI", "postgresql://localhost:5432/pokedex")
DB_BRONZE     = "pokedex_bronze"

GERACOES =[
    (1, "Greação I", "Kanto"),
    (2, "Greação II", "Johto"),
    (3, "Greação III", "Hoenn"),
    (4, "Greação IV", "Sinnoh"),
    (5, "Greação V", "Unova"),
    (6, "Greação VI", "Kalos"),
]

def achar_silver_sql():
    arquivo = os.path.dirname(os.path.abspath(__file__))
    candidatos = [
        os.path.join("sql", "silver.sql"),
        os.path.join(arquivo, "sql", "silver.sql"),
        os.path.join(arquivo, "..", "sql", "silver.sql"),
    ]
    for c in candidatos:
        if os.path.exists(c):
            return c
    raise FileNotFoundError(
        "Não foi possível encontrar sql/silver.sql. Rode o script a partir da raiz do projeto."
    )

def executar_sql_arquivo(conn, caminho):
    with open(caminho, encoding="utf-8") as f:
        bruto = f.read()
    sem_comentarios = "\n".join(re.sub(r"--.*$", "", linha) for linha in bruto.splitlines())
    with conn.cursor() as cur:
        for comando in sem_comentarios.split(";"):
            if comando.strip():
                cur.execute(comando)

#ETAPA 1 DIMENSÕES LIMPAS
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
        # Mapa nome_do_tipo -> sk_tipo (só os reais, ignorando o membro especial)
        cur.execute("SELECT nome, sk_tipo FROM silver.dim_tipo WHERE id_tipo IS NOT NULL")
        sk_por_nome = dict(cur.fetchall())
    print(f"dim_tipo:         {len(tipos)} tipos (+ membro especial)")
 
    linhas = []
    for t in tipos:
        atacante = sk_por_nome[t["name"]]
        mult = {nome: 1.0 for nome in sk_por_nome} 
        dr = t["damage_relations"]
        for d in dr["double_damage_to"]:
            if d["name"] in mult:
                mult[d["name"]] = 2.0
        for d in dr["half_damage_to"]:
            if d["name"] in mult:
                mult[d["name"]] = 0.5
        for d in dr["no_damage_to"]:
            if d["name"] in mult:
                mult[d["name"]] = 0.0
        for nome_def, m in mult.items():
            linhas.append((atacante, sk_por_nome[nome_def], m))
 
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO silver.efetividade_tipo "
            "(sk_tipo_atacante, sk_tipo_defensor, multiplicador) VALUES (%s, %s, %s)",
            linhas,
        )
    print(f"efetividade_tipo: {len(linhas)} combinações (esperado 324)")

def contagens(conn):
    print("\n Contagem silver")
    with conn.cursor() as cur:
        for tabela in ("dim_geracao", "dim_tipo", "efetividade_tipo",
                       "dim_pokemon", "fato_confronto"):
            cur.execute(f"SELECT COUNT(*) FROM silver.{tabela}")
            print(f"  {tabela}: {cur.fetchone()[0]}")


def main():
    cliente = MongoClient(MONGO_URI)
    bronze = cliente[DB_BRONZE]
 
    with psycopg.connect(POSTGRES_URI) as conn:
        print("Recriando o schema silver (sql/silver.sql)...")
        executar_sql_arquivo(conn, achar_silver_sql())
 
        print("\n== Etapa 1: dimensões limpas ==")
        carregar_dim_geracao(conn)
        carregar_dim_tipo_e_efetividade(conn, bronze)
 
        conn.commit()
        contagens(conn)
 
    cliente.close()
 

 
if __name__ == "__main__":
    main()