# EP01 — ETL e Arquitetura Medalhão

**Disciplina:** Ciência de Dados
**Autores:** Leonardo Rodrigues de Lima, Yasmin Ayumi Foltran Mano e Eduardo Leal Aruth

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
carregar.py         Bronze → Silver                     ✅ PRONTO
publicar.py         Silver → Gold                       ✅ PRONTO

sql/silver.sql      DDL do modelo dimensional           ✅ PRONTO
sql/gold.sql        Schema e agregações da Gold         ✅ PRONTO
sql/consultas.sql   8 análises em SQL                   ✅ PRONTO

conciliacao.csv     Relatório de conciliação (R4)       ✅ PRONTO
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

Pode ser utilizado:

* PostgreSQL local; ou
* PostgreSQL na nuvem (ex.: Neon).

---

# 🔐 Variáveis de ambiente

As credenciais de acesso aos bancos **não ficam armazenadas diretamente no código**.

Crie o arquivo `.env` a partir do modelo:

```bash
cp .env.example .env
```

No arquivo `.env`, configure as variáveis:

```env
MONGO_URI=
POSTGRES_URI=
```

### MongoDB

```env
# Local
MONGO_URI=mongodb://localhost:27017

# Atlas
MONGO_URI=mongodb+srv://USUARIO:SENHA@SEU_CLUSTER.mongodb.net/?retryWrites=true&w=majority
```

### PostgreSQL

```env
# Local
POSTGRES_URI=postgresql://USUARIO:SENHA@localhost:5432/pokedex

# Neon (nuvem)
POSTGRES_URI=postgresql://USUARIO:SENHA@ENDPOINT.neon.tech/DB?sslmode=require
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

Execute:

```bash
python carregar.py
```

O script recria o schema `silver`, executa `sql/silver.sql`, concilia os dados
da Bronze e popula o modelo dimensional no PostgreSQL.

**Status:** ✅ Concluída.

---

## 3. Camada Gold

Execute:

```bash
python publicar.py
```

O script executa `sql/gold.sql`, que materializa as tabelas agregadas
(uma por análise) **dentro do PostgreSQL**, e registra a publicação.

**Status:** ✅ Concluída.

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

# 🥈 Camada Silver

A camada Silver transforma os documentos brutos da Bronze em um **modelo dimensional** (esquema estrela) no PostgreSQL.

Arquivos responsáveis:

```text
carregar.py
sql/silver.sql
```

A regra de ouro desta camada:

> A Silver lê **somente da Bronze** (MongoDB) — nunca da PokéAPI ou dos CSVs.
> Se algo necessário não estiver na Bronze, a extração está incompleta.

---

## 🎯 Grão da tabela fato (RS1)

> **Uma linha por PARTICIPAÇÃO de um Pokémon em um combate.**

Cada combate gera **duas linhas** (uma por combatente), totalizando **100.000 linhas** na fato.

Essa escolha (decisão 1) reduz o cálculo da taxa de vitórias à **média de uma única coluna booleana** (`venceu`), eliminando o risco de dupla contagem que existiria se procurássemos cada Pokémon em duas colunas distintas. O custo é dobrar o volume da tabela fato.

---

## ⭐ Esquema estrela

```text
                 dim_geracao
                      │
 dim_pokemon ── fato_confronto ── dim_tipo
  (2 papéis)         │           (2 papéis)
                efetividade_tipo
```

| Tabela                     | Conteúdo                                                         | Ordem de grandeza |
| -------------------------- | --------------------------------------------------------------- | ----------------: |
| `silver.fato_confronto`    | resultado dos combates no grão de participação                  |           100.000 |
| `silver.dim_pokemon`       | identificação, classificação, raridade e status de cada Pokémon |   800 (+especial) |
| `silver.dim_tipo`          | os tipos, com denominação legível                               |    18 (+especial) |
| `silver.dim_geracao`       | as gerações, com nome e região                                  |                 6 |
| `silver.efetividade_tipo`  | multiplicador de dano de cada tipo atacante × defensor          |               324 |
| `silver.log_conciliacao`   | auditoria da conciliação CSV × API (não é fato nem dimensão)    |               800 |

As **chaves substitutas** (`sk_*`) são inteiros gerados pelo próprio PostgreSQL. As chaves naturais (número da Pokédex e `#` do CSV) ficam como **atributos**, nunca como PK/FK — são o registro auditável da conciliação (RS3).

`dim_tipo` e `dim_pokemon` são **dimensões papel** (*role-playing*): a fato as referencia duas vezes (participante e oponente). O `id_combate` na fato é uma **dimensão degenerada**, que liga as duas participações de um mesmo combate.

---

## 🧩 As 6 decisões de modelagem (seção 4.2)

**1. Grão da fato — participação.**
Uma linha por combatente por combate (100.000 linhas). A taxa de vitórias vira `AVG(venceu)`. Custo: dobra o volume.

**2. Diferença de velocidade — métrica na fato.**
A coluna `diferenca_velocidade` é gravada na fato (velocidade do participante − do oponente). Deixa a análise 5 aditiva; recalcular exigiria um auto-join com o oponente a cada consulta. Custo: espaço de armazenamento.

**3. Efetividade de tipos — tabela separada (`efetividade_tipo`).**
A matriz 18×18 (324 linhas) é materializada, então as análises 6 e 7 viram um `JOIN` (RS7). Quando o defensor tem dois tipos, os multiplicadores se multiplicam — esse caso é tratado na consulta/gold.

**4. Oponente — dimensão papel.**
O oponente é a mesma `dim_pokemon` referenciada uma segunda vez pela fato (`sk_pokemon` e `sk_pokemon_oponente`).

**5. Status — em `dim_pokemon`.**
HP, ataque, defesa e velocidade descrevem o Pokémon, então ficam na dimensão (para a análise 2). A diferença de velocidade é **duplicada** como métrica na fato (para a análise 5). Custo da duplicação avaliado como aceitável.

**6. Raridade — derivada na carga.**
`categoria_raridade` (Lendário / Mítico / Bebê / Comum) é derivada dos indicadores booleanos durante a carga, em vez de resolvida por expressão em cada consulta.

**Decisão adicional — tipos vindos do CSV.**
Os tipos de cada Pokémon são lidos do `pokemon.csv`, não da PokéAPI. O CSV traz a linha de cada **forma específica** (ex.: Wash Rotom é Água, não o tipo do Rotom padrão) e foi o CSV que alimentou a simulação de batalhas, o que mantém as análises de efetividade coerentes com os combates reais.

---

## 🧷 Membros especiais (RS4)

Nenhuma chave estrangeira da fato é nula. A ausência é representada por uma linha dedicada (`sk = -1`) em cada dimensão:

| Dimensão      | Membro especial   | Uso                                       |
| ------------- | ----------------- | ----------------------------------------- |
| `dim_pokemon` | `(desconhecido)`  | registro sem nome (#63) e não conciliados |
| `dim_tipo`    | `(nenhum)`        | tipo desconhecido / secundário ausente    |
| `dim_geracao` | `(desconhecida)`  | geração desconhecida                      |

As batalhas dos registros não conciliados **permanecem** no modelo, apontando para o membro especial (R5: entram 50.000 combates, permanecem 50.000).

---

## 🔗 Conciliação por nome (R4)

O `#` do `pokemon.csv` **não é** o número da Pokédex — é um índice sequencial de 1 a 800 no qual as formas Mega ocupam linhas próprias, deslocando a numeração. Não há relação aritmética entre os dois: a conciliação só é possível **por nome**.

A estratégia normaliza os nomes em três níveis:

**1. Canonização.**
Ambos os lados são reduzidos a minúsculas, sem acentos e sem caracteres especiais. Isso resolve automaticamente:

```text
Farfetch'd   → farfetchd
Mr. Mime     → mrmime
Ho-oh        → hooh
Flabébé      → flabebe
Nidoran♀     → nidoranf
```

**2. Reordenação de Mega e Primal.**
A PokéAPI inverte a ordem desses nomes, então eles são reordenados antes de canonizar:

```text
Mega Charizard X → charizard-mega-x
Primal Groudon   → groudon-primal
```

**3. Fallback por espécie.**
As formas alternativas (`Heat Rotom`, `Deoxys Attack Forme`, `Giratina Origin Forme`...) não existem na Bronze como pokémon (só as formas padrão + Mega/Primal foram extraídas). Para elas, busca-se a **espécie** cujo nome aparece no nome do CSV. Os atributos de classificação vêm da espécie; os tipos e status vêm do próprio CSV.

### Resultado da conciliação

```text
799 registros conciliados
  1 não conciliado  → registro #63 (sem nome)
```

O único não conciliado é o registro sem nome (Problema 2 do enunciado). Ele é um **dado ausente**: existe, tem tipo (Fighting), status e batalhas, mas o nome não foi registrado na fonte. É tratado com membro especial, não descartado.

> **Observação sobre o #63**
>
> O `#63` do CSV **não é o Abra** (Pokédex #63). Como o `#` do CSV está deslocado pelas formas Mega, e pelos status/tipo (Fighting, 65/105/60/60/70/95, geração 1) o registro corresponde ao **Primeape** (Pokédex #57). Ainda assim, o modelo o mantém como desconhecido de propósito: o objetivo é tratar o dado ausente, não adivinhá-lo.

O relatório completo da conciliação é gerado em `conciliacao.csv` e também na tabela `silver.log_conciliacao`.

---

## ♻️ Idempotência da Silver

O `sql/silver.sql` recria o schema do zero a cada execução (`DROP TABLE IF EXISTS ... CASCADE` seguido de `CREATE TABLE`). O `carregar.py` executa esse DDL e em seguida repovoa as tabelas.

Como cada execução parte de tabelas vazias, rodar o pipeline novamente produz **exatamente o mesmo estado**, sem duplicar linhas.

---

## ✅ Contagens esperadas da Silver

| Tabela             | Linhas esperadas       |
| ------------------ | ---------------------: |
| `dim_geracao`      |       7 (6 + especial) |
| `dim_tipo`         |     19 (18 + especial) |
| `efetividade_tipo` |                    324 |
| `dim_pokemon`      |   800 (799 + especial) |
| `fato_confronto`   |                100.000 |
| `log_conciliacao`  |                    800 |

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
| Idempotência Bronze | ✅ Implementada       |
| PostgreSQL / Silver | ✅ Concluída          |
| Modelo dimensional  | ✅ Concluído          |
| Conciliação (R4)    | ✅ Concluída          |
| PostgreSQL / Gold   | ✅ Concluída          |
| Consultas SQL       | ✅ Concluída          |
| Relatório final     | ⏳ Em desenvolvimento |

---
