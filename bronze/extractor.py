import os
import csv
import json
import time
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne
 
load_dotenv()   

API_BASE      = "https://pokeapi.co/api/v2"
MONGO_URI     = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME       = "pokedex_bronze"
CACHE_DIR     = "dados_brutos"
REQUEST_DELAY = 0.1        
MAX_SPECIES   = 721
TYPE_IDS      = list(range(1, 19)) + [19, 10001, 10002]  
 
CSV_POKEMON = "https://raw.githubusercontent.com/cdiener/pokemon_app/master/pokemon.csv"
CSV_COMBATS = "https://raw.githubusercontent.com/cdiener/pokemon_app/master/combats.csv"
 
 

def agora_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
 
 
def buscar_texto(rel_path, url):
    """Retorna o corpo da resposta como texto. Lê do cache em disco quando
    existe; só consulta a API (e só dorme REQUEST_DELAY) quando o arquivo
    correspondente ainda não foi baixado."""
    caminho = os.path.join(CACHE_DIR, rel_path)
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            return f.read()
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(resp.text)
    time.sleep(REQUEST_DELAY)
    return resp.text
 
 
def buscar_json(rel_path, url):
    return json.loads(buscar_texto(rel_path, url))
 
 

# Gravação na bronze (upsert idempotente + linhagem)
def op_upsert(_id, payload, fonte, campo_origem, valor_origem):
    """Monta um UpdateOne idempotente.
 
    A linhagem usa prefixo `_` para não colidir com os campos da fonte.
    `_ingerido_em` vai em $setOnInsert: só é gravado na PRIMEIRA inserção, de
    modo que reexecuções deixem o documento idêntico (idempotência plena)."""
    linhagem = {"_fonte": fonte, campo_origem: valor_origem}
    return UpdateOne(
        {"_id": _id},
        {"$set": {**payload, **linhagem},
         "$setOnInsert": {"_ingerido_em": agora_iso()}},
        upsert=True,
    )
 
 
def gravar(colecao, operacoes, tam_lote=5000):
    for i in range(0, len(operacoes), tam_lote):
        colecao.bulk_write(operacoes[i:i + tam_lote], ordered=False)
 
 

# Extração — PokéAPI
def extrair_tipos(db):
    ops = []
    for tid in TYPE_IDS:
        url = f"{API_BASE}/type/{tid}"
        data = buscar_json(f"tipos/{tid}.json", url)
        ops.append(op_upsert(f"tipo/{tid}", data, "pokeapi", "_url", url))
    gravar(db["tipos"], ops)
    print(f"tipos:       {len(ops)} documentos")
 
 
def extrair_especies_e_formas(db):
    """Itera as 721 espécies. A forma padrão e as formas Mega/Primal vivem em
    `varieties[]`; a iteração 1..721 NÃO alcança as Mega (id > 10000), por isso
    partimos da espécie e seguimos as varieties."""
    ops_esp, ops_pk = [], []
    ids_pokemon = set()
    for sid in range(1, MAX_SPECIES + 1):
        url_sp = f"{API_BASE}/pokemon-species/{sid}"
        especie = buscar_json(f"especies/{sid}.json", url_sp)
        ops_esp.append(op_upsert(f"especie/{sid}", especie, "pokeapi", "_url", url_sp))
 
        for v in especie.get("varieties", []):
            nome = v["pokemon"]["name"]
            # Forma padrão + Mega (e Primal, por garantia contra o CSV de batalhas).
            # Demais formas alternativas ficam fora do escopo.
            if not (v.get("is_default") or "-mega" in nome or "-primal" in nome):
                continue
            pid = int(v["pokemon"]["url"].rstrip("/").split("/")[-1])
            if pid in ids_pokemon:
                continue
            ids_pokemon.add(pid)
            url_pk = f"{API_BASE}/pokemon/{pid}"
            forma = buscar_json(f"pokemon/{pid}.json", url_pk)
            ops_pk.append(op_upsert(f"pokemon/{pid}", forma, "pokeapi", "_url", url_pk))
 
        if sid % 100 == 0:
            print(f"  ... {sid}/{MAX_SPECIES} espécies")
 
    gravar(db["especies"], ops_esp)
    gravar(db["pokemon"], ops_pk)
    print(f"especies:    {len(ops_esp)} documentos")
    print(f"pokemon:     {len(ops_pk)} documentos")
 

# Extração — CSV de batalhas
def extrair_pokemon_csv(db):
    texto = buscar_texto("csv/pokemon.csv", CSV_POKEMON)
    ops = []
    for linha in csv.DictReader(texto.splitlines()):
        # Todos os valores permanecem como TEXTO (inclui o nome vazio da linha 63
        # e Legendary "True"/"False"); a conversão é responsabilidade do silver.
        _id = f"pokemon_csv/{linha['#']}"          # o campo `#` é a chave natural
        ops.append(op_upsert(_id, dict(linha), "csv", "_arquivo", "pokemon.csv"))
    gravar(db["pokemon_csv"], ops)
    print(f"pokemon_csv: {len(ops)} documentos")
 
 
def extrair_combates_csv(db):
    texto = buscar_texto("csv/combats.csv", CSV_COMBATS)
    ops = []
    # combats.csv não tem chave natural única -> o número da linha é a chave.
    for i, linha in enumerate(csv.DictReader(texto.splitlines()), start=1):
        _id = f"combate/{i}"
        ops.append(op_upsert(_id, dict(linha), "csv", "_arquivo", "combats.csv"))
    gravar(db["combates"], ops)
    print(f"combates:    {len(ops)} documentos")
 
 
def main():
    cliente = MongoClient(MONGO_URI)
    db = cliente[DB_NAME]
 
    print("== PokéAPI ==")
    extrair_tipos(db)
    extrair_especies_e_formas(db)
 
    print("== CSV ==")
    extrair_pokemon_csv(db)
    extrair_combates_csv(db)
 
    print("\n== Contagem final ==")
    for c in ("pokemon", "especies", "tipos", "pokemon_csv", "combates"):
        print(f"  {c}: {db[c].count_documents({})}")
 
    cliente.close()
 
 
if __name__ == "__main__":
    main()
 