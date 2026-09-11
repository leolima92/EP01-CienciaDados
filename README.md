# EP01 — ETL e Arquitetura Medalhão

**Disciplina:** Ciência de Dados
**Autores:** Leonardo Rodrigues de Lima e Yasmin Ayumi Foltran Mano

---

## 📌 Sobre o projeto

Este projeto implementa um pipeline de dados que extrai informações da **PokéAPI** e de um conjunto de dados de **batalhas simuladas de Pokémon**.

Os dados são organizados seguindo a **Arquitetura Medalhão**:

**Bronze → Silver → Gold**

Ao final do pipeline, o projeto disponibiliza dados tratados e agregados para responder a **oito análises exclusivamente em SQL**.

---

## 🏗️ Arquitetura

| Camada        | Tecnologia | Conteúdo                                               | Scripts                          |
| ------------- | ---------- | ------------------------------------------------------ | -------------------------------- |
| 🥉 **Bronze** | MongoDB    | Dados brutos, preservados conforme a fonte             | `extrair.py`                     |
| 🥈 **Silver** | PostgreSQL | Dados tratados em modelo dimensional / esquema estrela | `carregar.py` + `sql/silver.sql` |
| 🥇 **Gold**   | PostgreSQL | Dados agregados no grão das perguntas analíticas       | `publicar.py` + `sql/gold.sql`   |

O fluxo do projeto segue a seguinte estrutura:

```text
PokéAPI + CSVs
      │
      ▼
🥉 BRONZE
MongoDB
Dados brutos
      │
      ▼
🥈 SILVER
PostgreSQL
Modelo dimensional
      │
      ▼
🥇 GOLD
PostgreSQL
Agregações
      │
      ▼
📊 Consultas SQL
8 análises
```

Cada etapa lê somente da camada anterior e escreve na camada seguinte.

A principal propriedade desse padrão é a **imutabilidade da camada Bronze**. Como os dados originais são preservados, eventuais erros de transformação podem ser corrigidos reprocessando apenas as camadas seguintes, sem realizar novamente consultas às fontes originais.

---

# 📚 Fontes de dados

## PokéAPI

API REST pública disponível em:

`https://pokeapi.co/api/v2/`

Não exige autenticação.

### Endpoints utilizados

```text
/pokemon/{id}
/pokemon-species/{id}
/type/{id}
```

O escopo utilizado no projeto contempla:

* Gerações **I a VI**;
* **721 espécies**;
* formas **Mega**;
* formas **Primal**, quando aplicável.

---

## Dataset de batalhas

Dataset público disponibilizado sob licença **MIT**.

Arquivos utilizados:

| Arquivo       | Conteúdo             |       Quantidade |
| ------------- | -------------------- | ---------------: |
| `pokemon.csv` | Cadastro dos Pokémon |    800 registros |
| `combats.csv` | Batalhas simuladas   | 50.000 registros |

---

# 📁 Estrutura do repositório

```text
.
├── README.md
├── RELATORIO.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── extrair.py
├── carregar.py
├── publicar.py
│
├── sql/
│   ├── silver.sql
│   ├── gold.sql
│   └── consultas.sql
│
├── conciliacao.csv
│
└── dados_brutos/
```

### Status dos arquivos

```text
extrair.py          fontes → Bronze                     ✅ PRONTO
carregar.py         Bronze → Silver                     ⏳ PENDENTE
publicar.py         Silver → Gold                       ⏳ PENDENTE

sql/silver.sql      DDL do modelo dimensional           ⏳ PENDENTE
sql/gold.sql        Schema e agregações da Gold         ⏳ PENDENTE
sql/consultas.sql   8 análises em SQL                   ⏳ PENDENTE

conciliacao.csv     Relatório de conciliação (R4)       ⏳ PENDENTE
```

> **Observação**
>
> No estado atual do projeto, o extrator está localizado em `bronze/extractor.py`.
>
> Caso esse layout seja mantido, os comandos apresentados neste README deverão ser ajustados. O enunciado sugere `extrair.py` na raiz do projeto, portanto é recomendável alinhar a estrutura antes da entrega final.

---

# ⚙️ Pré-requisitos

## Python

Recomenda-se:

```text
Python 3.12+
```

Instale as dependências com:

```bash
pip install -r requirements.txt
```

---

## MongoDB

Utilizado para armazenamento da camada **Bronze**.

Pode ser utilizado:

* MongoDB local; ou
* MongoDB Atlas.

---

## PostgreSQL

Utilizado nas camadas:

* **Silver**
* **Gold**

---

# 🔐 Variáveis de ambiente

As credenciais de acesso aos bancos **não ficam armazenadas diretamente no código**.

Crie o arquivo `.env` a partir do modelo:

```bash
cp .env.example .env
```

No arquivo `.env`, configure a variável:

```env
MONGO_URI=
```

### MongoDB local

```env
MONGO_URI=mongodb://localhost:27017
```

### MongoDB Atlas

```env
MONGO_URI=mongodb+srv://USUARIO:SENHA@SEU_CLUSTER.mongodb.net/?retryWrites=true&w=majority
```

> ⚠️ **Importante**
>
> O arquivo `.env` está incluído no `.gitignore` e **nunca deve ser versionado**.
>
> Ele pode conter usuários, senhas e outras informações sensíveis de acesso aos bancos de dados.

---

# ▶️ Como executar

## 1. Camada Bronze

Execute:

```bash
python extrair.py
```

### Primeira execução

Na primeira execução, o script:

1. consulta as fontes externas;
2. salva as respostas no cache local;
3. carrega os dados no MongoDB.

```bash
python extrair.py
```

### Segunda execução

Na segunda execução:

```bash
python extrair.py
```

o pipeline reutiliza o cache local.

O resultado esperado é:

```text
0 novas requisições às fontes
0 documentos duplicados
mesmas contagens no MongoDB
```

Isso demonstra a **idempotência da camada Bronze**.

---

## Contagens esperadas

| Coleção       | Documentos esperados |
| ------------- | -------------------: |
| `tipos`       |                   21 |
| `especies`    |                  721 |
| `pokemon`     |                 ~770 |
| `pokemon_csv` |                  800 |
| `combates`    |               50.000 |

A coleção `pokemon` possui aproximadamente 770 documentos porque contém:

```text
721 Pokémon padrão
+
formas Mega
+
formas Primal
```

---

## 2. Camada Silver

A camada Silver realizará a transformação dos documentos da Bronze para um **modelo dimensional no PostgreSQL**.

Arquivos responsáveis:

```text
carregar.py
sql/silver.sql
```

**Status:** ⏳ Em desenvolvimento.

---

## 3. Camada Gold

A camada Gold armazenará os dados agregados utilizados diretamente pelas consultas analíticas.

Arquivos responsáveis:

```text
publicar.py
sql/gold.sql
```

**Status:** ⏳ Em desenvolvimento.

---

# 🥉 Camada Bronze

## Por que MongoDB?

A regra da camada Bronze é simples:

> **Preservar os dados da fonte com o mínimo possível de transformação.**

As respostas fornecidas pela PokéAPI possuem características que tornam um banco orientado a documentos adequado para essa etapa.

---

## 1. JSON profundamente aninhado

Cada resposta de `/pokemon` possui estruturas como:

```text
types[]
stats[]
abilities[]
```

Já `/type` possui estruturas como:

```text
damage_relations
```

com diversas listas internas.

Representar essas informações diretamente em um banco relacional exigiria a criação de várias tabelas e relacionamentos já durante a ingestão.

Isso significaria realizar transformações ainda na Bronze.

No MongoDB:

```text
1 resposta da API = 1 documento
```

permitindo armazenar o JSON praticamente no mesmo formato retornado pela fonte.

---

## 2. Estruturas heterogêneas

Os endpoints:

```text
/pokemon
/pokemon-species
/type
```

possuem formatos de resposta bastante diferentes.

Em um banco relacional seria necessário definir previamente um schema específico para cada estrutura.

O MongoDB permite armazenar esses formatos variados sem exigir um DDL rígido na ingestão, seguindo uma abordagem de **schema-on-read**.

---

## 3. Preservação dos dados originais

A resposta completa da API é armazenada na Bronze, inclusive campos que inicialmente podem não ser utilizados.

Isso permite que novas transformações sejam criadas posteriormente sem a necessidade de consultar novamente a PokéAPI.

---

# 🔑 Coleções e chaves naturais

Cada documento utiliza um `_id` derivado da chave natural da origem.

| Coleção       | `_id`                    | Origem                     |
| ------------- | ------------------------ | -------------------------- |
| `pokemon`     | `pokemon/{id}`           | `/pokemon/{id}`            |
| `especies`    | `especie/{id}`           | `/pokemon-species/{id}`    |
| `tipos`       | `tipo/{id}`              | `/type/{id}`               |
| `pokemon_csv` | `pokemon_csv/{#}`        | Campo `#` de `pokemon.csv` |
| `combates`    | `combate/{numero_linha}` | Linha de `combats.csv`     |

Essa estratégia permite utilizar operações de:

```text
update_one
bulk_write
upsert
```

e constitui a base da **idempotência da ingestão**.

---

## Identificação das batalhas

O arquivo `combats.csv` não possui uma chave natural única.

As colunas:

```text
First
Second
Winner
```

podem apresentar combinações repetidas.

Por isso, o número da linha do CSV é utilizado para criar o identificador:

```text
combate/{numero_linha}
```

---

# 🔎 Linhagem dos dados

Todo documento armazenado na Bronze possui metadados que identificam sua origem.

Esses campos utilizam o prefixo `_` para evitar colisões com atributos existentes na fonte.

Exemplo:

```json
{
  "_id": "pokemon/25",
  "_fonte": "pokeapi",
  "_url": "https://pokeapi.co/api/v2/pokemon/25",
  "_ingerido_em": "2026-09-05T14:32:10Z",
  "id": 25,
  "name": "pikachu"
}
```

Os principais campos de linhagem são:

| Campo          | Descrição                        |
| -------------- | -------------------------------- |
| `_id`          | Identificador único do documento |
| `_fonte`       | Origem do dado                   |
| `_url`         | Endpoint utilizado               |
| `_ingerido_em` | Data e hora da primeira ingestão |

---

# 🧬 Formas Mega

Uma simples iteração pelos IDs:

```text
1 → 721
```

não é suficiente para encontrar todas as formas Mega.

Algumas delas utilizam IDs superiores a `10000` na PokéAPI.

Por isso, o fluxo de extração parte de:

```text
/pokemon-species/{id}
```

e utiliza o campo:

```text
varieties[]
```

para identificar as diferentes formas disponíveis para uma espécie.

São coletadas:

* a forma padrão;
* formas contendo `-mega`;
* formas contendo `-primal`.

As demais formas alternativas ficam fora do escopo do projeto.

Essa estratégia também aumenta a compatibilidade com os nomes encontrados no dataset de batalhas.

---

# 📄 Preservação dos CSVs

Na camada Bronze, os valores provenientes dos CSVs são armazenados **sem conversão de tipos**.

Por exemplo:

```text
Legendary = "True"
Legendary = "False"
```

é armazenado exatamente como texto.

Também são preservados valores vazios, como o nome ausente presente em uma das linhas do `pokemon.csv`.

A responsabilidade de converter:

```text
texto → inteiro
texto → booleano
texto → decimal
```

é da camada **Silver**.

Dessa forma, a Bronze continua representando fielmente a fonte original.

---

# 💾 Cache local

Antes de inserir os dados no MongoDB, as respostas da PokéAPI são armazenadas em:

```text
dados_brutos/
```

O fluxo é:

```text
Existe arquivo no cache?
        │
        ├── Sim → utiliza o arquivo local
        │
        └── Não → consulta a API e salva o resultado
```

Isso evita chamadas desnecessárias à PokéAPI.

O diretório `dados_brutos/` não é versionado no Git, pois pode ser completamente reconstruído executando novamente a extração.

---

# ♻️ Idempotência

A camada Bronze foi construída para que múltiplas execuções produzam o mesmo estado final.

## Cache idempotente

Após a primeira execução, as respostas já estão disponíveis em:

```text
dados_brutos/
```

Assim, uma nova execução não precisa consultar novamente a PokéAPI.

---

## Upsert no MongoDB

A carga utiliza operações como:

```text
update_one
bulk_write
```

com:

```text
upsert = true
```

Como cada documento possui um `_id` determinístico, executar o pipeline novamente não cria registros duplicados.

---

## Data de ingestão

O campo:

```text
_ingerido_em
```

é definido utilizando:

```text
$setOnInsert
```

Ou seja, ele é preenchido apenas quando o documento é inserido pela primeira vez.

Em execuções posteriores:

```text
mesmo _id
+
mesmo conteúdo
+
mesma data de ingestão
=
mesmo documento
```

---

# ✅ Garantias da camada Bronze

A implementação busca garantir quatro propriedades principais:

| Propriedade           | Implementação                               |
| --------------------- | ------------------------------------------- |
| **Preservação**       | Dados mantidos próximos ao formato original |
| **Linhagem**          | `_fonte`, `_url` e `_ingerido_em`           |
| **Idempotência**      | `_id` determinístico + `upsert`             |
| **Reprodutibilidade** | Cache local das respostas externas          |

---

# 📊 Análises

Após a construção das camadas Silver e Gold, o projeto responderá às **oito perguntas analíticas definidas no trabalho exclusivamente por SQL**.

As consultas ficarão disponíveis em:

```text
sql/consultas.sql
```

Os resultados e interpretações serão documentados em:

```text
RELATORIO.md
```

---

# 📌 Status do projeto

| Etapa               | Status               |
| ------------------- | -------------------- |
| Extração da PokéAPI | ✅ Concluída          |
| Extração dos CSVs   | ✅ Concluída          |
| Cache local         | ✅ Concluído          |
| MongoDB / Bronze    | ✅ Concluído          |
| Idempotência        | ✅ Implementada       |
| PostgreSQL / Silver | ⏳ Em desenvolvimento |
| Modelo dimensional  | ⏳ Em desenvolvimento |
| PostgreSQL / Gold   | ⏳ Em desenvolvimento |
| Consultas SQL       | ⏳ Em desenvolvimento |
| Relatório final     | ⏳ Em desenvolvimento |

---

## 👥 Autores

**Leonardo Rodrigues de Lima**
**Yasmin Ayumi Foltran Mano**

EP01 — Ciência de Dados
