import os
import re
import psycopg
from dotenv import load_dotenv

load_dotenv()
 
POSTGRES_URI = os.getenv("POSTGRES_URI", "postgresql://localhost:5432/pokedex")

GOLD_TABELAS = [
    "ranking_pokemon",
    "taxa_vitorias_por_tipo",
    "taxa_vitorias_por_faixa_velocidade",
    "taxa_vitorias_por_multiplicador",
    "matriz_confronto",
    "taxa_vitorias_por_raridade",
]

def achar_sql(nome):
    diretorio_script = os.path.dirname(os.path.abspath(__file__))
    raiz = os.path.abspath(os.path.join(diretorio_script, ".."))

    env = os.getenv(nome.replace(".sql", "").upper() + "_SQL_PATH")
    if env and os.path.exists(env):
        return env

    candidatos =[
        os.path.join(os.getcwd(), "sql", nome),
        os.path.join(os.getcwd(), nome),
        os.path.join(diretorio_script, nome),
        os.path.join(diretorio_script, "sql", nome),
        os.path.join(raiz, "sql", nome),
        os.path.join(raiz, nome),
    ]

    for i in candidatos:
        if os.path.exists(i):
            return i

    for base, dirs, arquivos in os.walk(raiz):
        dirs[:] = [d for d in dirs if d not in (".venv", ".venv-antigo",
                                                "dados_brutos", ".git", "__pycache__")]
        if nome in arquivos:
            return os.path.join(base, nome)

    raise FileNotFoundError(
        f"Não encontrei {nome} no projeto. Salve-o em uma pasta do projeto "
        f"(ex.: sql/{nome})."
    )

def dividir_comandos(sql):
    """Separa comandos SQL respeitando blocos $$...$$ e literais '...'."""
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


def executa_arquivo_sql(conn, caminho):
    with open(caminho, encoding="utf-8") as f:
        sql = f.read()
    with conn.cursor() as cur:
        for comando in dividir_comandos(sql):
            cur.execute(comando)

def main():
    with psycopg.connect(POSTGRES_URI) as conn:
        caminho = achar_sql("gold.sql")
        print(f"Publicando o gold a partir de: {caminho}")
        executa_arquivo_sql(conn, caminho)
 
        print("\n Contagem gold")
        with conn.cursor() as cur:
            for t in GOLD_TABELAS:
                cur.execute(f"SELECT COUNT(*) FROM gold.{t}")
                linhas = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO gold.log_publicacao (tabela, linhas) VALUES (%s, %s)",
                    (t, linhas),
                )
                print(f"  {t}: {linhas}")
        conn.commit()
 
    print("\nGold publicado. Rode sql/consultas.sql para as 8 análises.")
 
 
if __name__ == "__main__":
    main()
 