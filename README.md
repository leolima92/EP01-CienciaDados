**Integrantes:** Leonardo Rodrigues de Lima, Yasmin Ayumi Foltran Mano e Eduardo Leal Aruth

# EP01 — ETL e Arquitetura Medalhão

**Disciplina:** Ciência de Dados

---

## 📌 Sobre o projeto

Este projeto implementa um pipeline de dados que extrai informações da **PokéAPI** e de um conjunto de dados de **batalhas simuladas de Pokémon**.

Os dados são organizados seguindo a **Arquitetura Medalhão**:

**Bronze → Silver → Gold**

Ao final do pipeline, o projeto disponibiliza dados tratados e agregados para responder a **oito análises exclusivamente em SQL**.

---

## 🏗️ Arquitetura

| Camada        | Tecnologia | Conteúdo                                               | Scripts                                 |
| ------------- | ---------- | ------------------------------------------------------ | --------------------------------------- |
| 🥉 **Bronze** | MongoDB    | Dados brutos, preservados conforme a fonte             | `bronze/extractor.py`                   |
| 🥈 **Silver** | PostgreSQL | Dados tratados em modelo dimensional / esquema estrela | `silver/carregar.py` + `sql/silver.sql` |
| 🥇 **Gold**   | PostgreSQL | Dados agregados no grão das perguntas analíticas       | `gold/publicar.py` + `sql/gold.sql`     |

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
* **todas as formas alternativas** de cada espécie (Mega, Primal, e formas como Deoxys, Rotom, Giratina, Therian, Kyurem, etc.), listadas em `varieties[]`.

---

## Dataset de batalhas

Dataset público disponibilizado sob licença **MIT**.

Arquivos utilizados:

| Arquivo       | Conteúdo             | Quantidade       |
| ------------- | -------------------- | ---------------- |
| `pokemon.csv` | Cadastro dos Pokémon | 800 registros    |
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
├── bronze/
│   └── extractor.py
├── silver/
│   └── carregar.py
├── gold/
│   └── publicar.py
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
bronze/extractor.py   fontes → Bronze                    ✅ PRONTO
silver/carregar.py    Bronze → Silver                    ✅ PRONTO
gold/publicar.py      Silver → Gold                      ✅ PRONTO

sql/silver.sql        DDL do modelo dimensional          ✅ PRONTO
sql/gold.sql          Schema e agregações da Gold        ✅ PRONTO
sql/consultas.sql     8 análises em SQL                  ✅ PRONTO

conciliacao.csv       Relatório de conciliação (R4)      ✅ PRONTO
```

> **Observação sobre a organização**
>
> Os scripts estão organizados em pastas por camada (`bronze/`, `silver/`, `gold/`). Os comandos apresentados neste README já refletem esses caminhos. Os arquivos SQL ficam centralizados em `sql/`, e os scripts localizam automaticamente o `.sql` correspondente independentemente da pasta a partir da qual são executados.

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

## Bibliotecas utilizadas

Conforme a restrição do enunciado (R11), o pipeline **não utiliza `pandas`, `numpy`, `polars` nem `pyarrow`**. Toda a leitura das fontes usa os módulos `csv` e `json` da biblioteca padrão do Python.

As dependências externas são:

| Biblioteca      | Uso                                                                           |
| --------------- | ----------------------------------------------------------------------------- |
| `requests`      | cliente HTTP para a PokéAPI                                                   |
| `pymongo`       | driver do MongoDB (camada Bronze)                                             |
| `psycopg`       | driver do PostgreSQL (camadas Silver e Gold)                                  |
| `python-dotenv` | carrega as credenciais do `.env`, mantendo segredos fora do código versionado |

O `python-dotenv` é a única biblioteca fora da lista prevista no R11; sua função é exclusivamente de configuração (leitura do `.env`), não de manipulação de dados, e é justificada aqui conforme exigido.

---

## MongoDB

Utilizado para armazenamento da camada **Bronze**. O banco lógico utilizado pela camada é `pokedex_bronze`.

Pode ser utilizado:

* MongoDB local; ou
* MongoDB Atlas.

### Inicialização

Antes da execução de `bronze/extractor.py`, uma instância do MongoDB deve estar acessível pela URI configurada em `MONGO_URI`.

* **MongoDB local:** inicie o serviço do MongoDB instalado na máquina e utilize, por exemplo, `mongodb://localhost:27017`. Não é necessário executar `CREATE DATABASE`: o banco `pokedex_bronze` e suas coleções são criados na primeira escrita.
* **MongoDB Atlas:** crie o cluster, libere o acesso da máquina utilizada, crie o usuário do banco e informe a URI de conexão no `.env`.

A conexão deve estar disponível **antes** da execução da camada Bronze.

---

## PostgreSQL

Utilizado nas camadas:

* **Silver**
* **Gold**

Pode ser utilizado:

* PostgreSQL local; ou
* PostgreSQL na nuvem (ex.: Neon).

### Inicialização

Antes de executar `silver/carregar.py`, o PostgreSQL deve estar acessível pela URI configurada em `POSTGRES_URI`.

* **PostgreSQL local:** inicie o serviço do PostgreSQL e crie o banco `pokedex`, caso ele ainda não exista. Isso pode ser feito com `createdb pokedex` ou, dentro do `psql`, com `CREATE DATABASE pokedex;`.
* **PostgreSQL na nuvem:** crie a instância/banco no provedor escolhido e copie a string de conexão para `POSTGRES_URI`.

Os schemas `silver` e `gold` **não precisam ser criados manualmente**: eles são criados/recriados pelos arquivos SQL executados pelo pipeline.

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

# ▶️ Como executar

A ordem obrigatória do pipeline é **Bronze → Silver → Gold**. Cada etapa lê somente da camada imediatamente anterior.

## 0. Preparar o ambiente

1. instale as dependências com `pip install -r requirements.txt`;
2. crie o arquivo `.env` a partir de `.env.example`;
3. confirme que o MongoDB está acessível por `MONGO_URI`;
4. confirme que o PostgreSQL está acessível por `POSTGRES_URI`;
5. somente então execute os três scripts, na ordem indicada abaixo.

---

## 1. Camada Bronze

Execute:

```bash
python bronze/extractor.py
```

### Primeira execução

Na primeira execução, o script:

1. consulta as fontes externas;
2. salva as respostas no cache local;
3. carrega os dados no MongoDB.

### Segunda execução

Na segunda execução:

```bash
python bronze/extractor.py
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
| `pokemon`     |                 ~940 |
| `pokemon_csv` |                  800 |
| `combates`    |               50.000 |

A coleção `pokemon` possui aproximadamente 940 documentos porque contém as **721 espécies padrão + todas as formas alternativas** listadas em `varieties[]`.

Isso inclui as formas de batalha (Mega, Primal, Deoxys, Rotom, Giratina, etc.) e também formas cosméticas da PokéAPI (padrões do Vivillon, cortes do Furfrou, cores do Flabébé) que não aparecem no `combats.csv`.

A Bronze preserva a fonte por completo; a conciliação, na Silver, seleciona apenas as formas presentes no CSV.

### Por que a Bronze possui 21 tipos e a Silver utiliza 18?

O endpoint `/type/` da PokéAPI retorna **21 registros**. Os tipos `stellar`, `unknown` e `shadow` não pertencem ao conjunto de 18 tipos utilizado nas batalhas do dataset.

Por isso, a decisão do projeto é:

* preservar os **21 registros** na Bronze, mantendo a fonte intacta;
* utilizar apenas os **18 tipos aplicáveis ao dataset de batalhas** na Silver e nas análises.

O filtro ocorre somente durante a transformação Bronze → Silver. Dessa forma, a Bronze continua fiel à origem e a camada analítica evita categorias sem ocorrência no conjunto de batalhas.

---

## 2. Camada Silver

Execute:

```bash
python silver/carregar.py
```

O script recria o schema `silver`, executa `sql/silver.sql`, concilia os dados da Bronze e popula o modelo dimensional no PostgreSQL.

**Status:** ✅ Concluída.

---

## 3. Camada Gold

Execute:

```bash
python gold/publicar.py
```

O script executa `sql/gold.sql`, que materializa as tabelas agregadas (uma por análise) **dentro do PostgreSQL**, e registra a publicação.

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
First_pokemon
Second_pokemon
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

# 🧬 Formas alternativas

Uma simples iteração pelos IDs `1 → 721` não alcança as formas alternativas (Mega, Primal, Deoxys, Rotom, etc.), pois muitas usam IDs superiores a `10000` na PokéAPI.

Por isso, o fluxo de extração parte de `/pokemon-species/{id}` e percorre o campo `varieties[]`, coletando **todas as formas** de cada espécie — a forma padrão e todas as alternativas.

Isso é exigido pelo escopo do trabalho: extrair apenas as formas Mega inviabilizaria a conciliação de dezenas de registros do `combats.csv` que correspondem a formas alternativas (Deoxys, Rotom, Giratina, Therian, etc.).

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
silver/carregar.py
sql/silver.sql
```

A regra de ouro desta camada:

> A Silver lê **somente da Bronze** (MongoDB) — nunca da PokéAPI ou dos CSVs.
>
> Se algo necessário não estiver na Bronze, a extração está incompleta.

---

## 🎯 Grão da tabela fato (RS1)

> **Uma linha por PARTICIPAÇÃO de um Pokémon em um combate.**

Cada combate gera **duas linhas** (uma por combatente), totalizando **100.000 linhas** na fato.

Essa escolha (decisão 1) reduz o cálculo da taxa de vitórias à **média de uma única coluna booleana** (`venceu`), eliminando o risco de dupla contagem que existiria se procurássemos cada Pokémon em duas colunas distintas.

O custo é dobrar o volume da tabela fato.

---

## ⭐ Esquema estrela

```text
                 dim_geracao
                      │
 dim_pokemon ── fato_confronto ── dim_tipo
  (2 papéis)         │           (2 papéis)
                efetividade_tipo
```

| Tabela                    | Conteúdo                                                        | Ordem de grandeza |
| ------------------------- | --------------------------------------------------------------- | ----------------: |
| `silver.fato_confronto`   | resultado dos combates no grão de participação                  |           100.000 |
| `silver.dim_pokemon`      | identificação, classificação, raridade e status de cada Pokémon |   800 (+especial) |
| `silver.dim_tipo`         | os tipos, com denominação legível                               |    18 (+especial) |
| `silver.dim_geracao`      | as gerações, com nome e região                                  |                 6 |
| `silver.efetividade_tipo` | multiplicador de dano de cada tipo atacante × defensor          |               324 |
| `silver.log_conciliacao`  | auditoria da conciliação CSV × API (não é fato nem dimensão)    |               800 |

As **chaves substitutas** (`sk_*`) são inteiros gerados pelo próprio PostgreSQL.

As chaves naturais (número da Pokédex e `#` do CSV) ficam como **atributos**, nunca como PK/FK — são o registro auditável da conciliação (RS3).

`dim_tipo` e `dim_pokemon` são **dimensões papel** (*role-playing*): a fato as referencia duas vezes (participante e oponente).

O `id_combate` na fato é uma **dimensão degenerada**, que liga as duas participações de um mesmo combate.

---

## 🧩 As 6 decisões de modelagem (seção 4.2)

**1. Grão da fato — participação.**

Uma linha por combatente por combate (100.000 linhas). A taxa de vitórias vira `AVG(venceu)`.

**Custo:** dobra o volume da tabela fato.

---

**2. Diferença de velocidade — métrica na fato.**

A coluna `diferenca_velocidade` é gravada na fato (velocidade do participante − do oponente).

Isso deixa a análise 5 aditiva; recalcular a diferença exigiria um auto-join com o oponente a cada consulta.

**Custo:** espaço adicional de armazenamento.

---

**3. Efetividade de tipos — tabela separada (`efetividade_tipo`).**

A matriz 18×18 (324 linhas) é materializada, então as análises 6 e 7 podem obter a efetividade por `JOIN` (RS7).

**Critério adotado:** o multiplicador considera apenas o **tipo primário** do defensor, resultando nos valores 0, 0,5, 1 e 2 — e não o critério de dois tipos, que produziria 0, 0,25, 0,5, 1, 2 e 4.

A escolha simplifica a análise e mantém a matriz de confronto como um 18×18 limpo.

**Custo:** perde-se parte da fidelidade da mecânica real para Pokémon com tipo secundário, pois a interação entre os dois tipos do defensor não entra no multiplicador.

---

**4. Oponente — dimensão papel.**

O oponente é representado pela mesma `dim_pokemon`, referenciada uma segunda vez pela fato (`sk_pokemon` e `sk_pokemon_oponente`).

Essa opção evita duplicar uma dimensão inteira apenas para representar o segundo papel exercido pela mesma entidade.

**Custo:** a tabela fato passa a possuir duas referências para `dim_pokemon`, exigindo aliases claros nas consultas para distinguir participante e oponente.

---

**5. Status — em `dim_pokemon`.**

HP, ataque, defesa e velocidade descrevem o Pokémon, então ficam na dimensão, atendendo à análise 2.

A diferença de velocidade é **duplicada** como métrica na fato, atendendo à análise 5 e evitando recalcular a comparação entre os dois lados a cada consulta.

**Custo:** há pequena redundância de informação, considerada aceitável em troca de consultas analíticas mais simples.

---

**6. Raridade — derivada na carga.**

`categoria_raridade` (Lendário / Mítico / Bebê / Comum) é derivada dos indicadores booleanos durante a carga, em vez de ser reconstruída por uma expressão condicional em cada consulta.

Isso centraliza a regra de classificação na Silver e mantém as consultas consistentes.

**Custo:** uma mudança na regra de classificação exige nova carga da camada Silver, em vez de apenas alterar uma consulta.

---

**Decisão adicional — tipos vindos do CSV.**

Os tipos de cada Pokémon são lidos do `pokemon.csv`, não da PokéAPI.

O CSV traz a linha de cada **forma específica** (ex.: Wash Rotom é Água, não o tipo do Rotom padrão) e foi o CSV que alimentou a simulação de batalhas, o que mantém as análises de efetividade coerentes com os combates reais.

---

## 🧷 Membros especiais (RS4)

Nenhuma chave estrangeira da fato é nula.

A ausência é representada por uma linha dedicada (`sk = -1`) em cada dimensão:

| Dimensão      | Membro especial  | Uso                                       |
| ------------- | ---------------- | ----------------------------------------- |
| `dim_pokemon` | `(desconhecido)` | registro sem nome (#63) e não conciliados |
| `dim_tipo`    | `(nenhum)`       | tipo desconhecido / secundário ausente    |
| `dim_geracao` | `(desconhecida)` | geração desconhecida                      |

As batalhas dos registros não conciliados **permanecem** no modelo, apontando para o membro especial.

Assim, entram 50.000 combates e permanecem 50.000 combates.

### Ausência de nome × habitat não aplicável

O projeto diferencia duas ausências que aparecem como `null` na origem, mas possuem significados diferentes:

* o registro `#63` do `pokemon.csv` possui **nome ausente**: a informação deveria existir, mas não foi registrada. Por isso, ele é tratado por um membro especial de `dim_pokemon`;
* o campo `habitat` nulo em parte das espécies da PokéAPI representa **conceito não aplicável**, e não falha de coleta ou de conciliação. Esse valor é preservado como ausência semântica do atributo e **não transforma o Pokémon em desconhecido**.

Assim, uma ausência de atributo descritivo não é confundida com ausência da entidade ou falha na chave de dimensão.

---

## 🔗 Conciliação por nome (R4)

O `#` do `pokemon.csv` **não é** o número da Pokédex — é um índice sequencial de 1 a 800 no qual as formas alternativas ocupam linhas próprias, deslocando a numeração.

Não há relação aritmética entre os dois: a conciliação só é possível **por nome**.

A estratégia normaliza os nomes em três níveis:

### 1. Canonização

Ambos os lados são reduzidos a minúsculas, sem acentos e sem caracteres especiais.

Isso resolve automaticamente:

```text
Farfetch'd   → farfetchd
Mr. Mime     → mrmime
Ho-oh        → hooh
Flabébé      → flabebe
Nidoran♀     → nidoranf
```

### 2. Reordenação de Mega e Primal

A PokéAPI inverte a ordem desses nomes, então eles são reordenados antes de canonizar:

```text
Mega Charizard X → charizard-mega-x
Primal Groudon   → groudon-primal
```

### 3. Fallback por espécie

Nos nomes de formas alternativas o CSV acrescenta palavras que a PokéAPI não usa (`Deoxys Attack Forme` vs `deoxys-attack`, `Heat Rotom` vs `rotom-heat`), então a correspondência direta falha.

Para esses casos, busca-se a **espécie** cujo nome aparece no nome do CSV.

Os **atributos de espécie** — geração, habitat, cor e raridade — são **herdados da espécie** correspondente, já que não existem nas formas alternativas, que só constam em `/pokemon` e não em `/pokemon-species`.

Os tipos e status vêm do próprio CSV, específicos de cada forma.

### Resultado da conciliação

```text
799 registros conciliados
1 não conciliado → registro #63 (sem nome)
```

O único não conciliado é o registro sem nome (Problema 2 do enunciado).

Ele é um **dado ausente**: existe, tem tipo (Fighting), status e batalhas, mas o nome não foi registrado na fonte.

É tratado com membro especial, não descartado.

> **Observação sobre o #63**
>
> O `#63` do CSV **não é o Abra** (Pokédex #63). Como o `#` do CSV está deslocado pelas formas Mega, e pelos status/tipo (Fighting, 65/105/60/60/70/95, geração 1) o registro corresponde ao **Primeape** (Pokédex #57).
>
> Ainda assim, o modelo o mantém como desconhecido de propósito: o objetivo é tratar o dado ausente, não adivinhá-lo.

O relatório completo da conciliação é gerado em `conciliacao.csv` e também na tabela `silver.log_conciliacao`.

---

## ♻️ Idempotência da Silver

O `sql/silver.sql` recria o schema do zero a cada execução (`DROP TABLE IF EXISTS ... CASCADE` seguido de `CREATE TABLE`).

O `silver/carregar.py` executa esse DDL e em seguida repovoa as tabelas.

Como cada execução parte de tabelas vazias, rodar o pipeline novamente produz **exatamente o mesmo estado**, sem duplicar linhas.

---

## ✅ Contagens esperadas da Silver

| Tabela             |     Linhas esperadas |
| ------------------ | -------------------: |
| `dim_geracao`      |     7 (6 + especial) |
| `dim_tipo`         |   19 (18 + especial) |
| `efetividade_tipo` |                  324 |
| `dim_pokemon`      | 800 (799 + especial) |
| `fato_confronto`   |              100.000 |
| `log_conciliacao`  |                  800 |

---

# 🥇 Camada Gold

A camada Gold é a **camada de consumo**: contém dados já agregados no grão de cada pergunta analítica.

As consultas finais apenas leem estas tabelas, sem agregar nem juntar nada.

Arquivos responsáveis:

```text
gold/publicar.py
sql/gold.sql
```

---

## Agregação dentro do banco

A principal regra desta camada:

> A agregação acontece **dentro do PostgreSQL** (`CREATE TABLE ... AS SELECT`), nunca na memória do Python.

O `gold/publicar.py` apenas orquestra: executa o `sql/gold.sql`, conta as linhas resultantes e registra a execução.

Ele não transporta dados do Silver para o Python para agregá-los — isso seria ineficiente e não escalável.

O `gold.sql` faz todo o trabalho de agregação no próprio banco.

---

## Tabelas do Gold

Cada tabela corresponde a uma análise, materializada no grão da pergunta:

| Tabela                                    | Grão                         | Análise |
| ----------------------------------------- | ---------------------------- | ------: |
| `gold.ranking_pokemon`                    | um Pokémon                   |       3 |
| `gold.taxa_vitorias_por_tipo`             | um tipo primário             |       4 |
| `gold.taxa_vitorias_por_faixa_velocidade` | uma faixa de velocidade      |       5 |
| `gold.taxa_vitorias_por_multiplicador`    | um multiplicador (0/0.5/1/2) |       6 |
| `gold.matriz_confronto`                   | tipo atacante × defensor     |       7 |
| `gold.taxa_vitorias_por_raridade`         | uma categoria de raridade    |       8 |

A tabela `gold.log_publicacao` registra o histórico de execuções, com tabela e contagem de linhas.

---

## ♻️ Idempotência da Gold

Cada tabela é recriada com `DROP TABLE IF EXISTS` seguido de `CREATE TABLE AS SELECT`.

Assim, reexecutar o `gold/publicar.py` reconstrói o Gold do zero a partir do Silver, sem duplicar linhas.

---

## 🧠 Análise proposta pelo grupo (8ª análise)

**Pergunta:** Pokémon de categorias mais raras (lendários e míticos) realmente vencem mais que os comuns?

**Relevância:** a análise testa uma hipótese intuitiva sobre o domínio: a de que Pokémon classificados como raros também apresentam desempenho superior nas batalhas simuladas.

Comparar as categorias permite verificar se a raridade está de fato associada à taxa de vitórias ou se o rótulo de raridade não se traduz diretamente em vantagem no conjunto analisado.

**Capacidade exigida do modelo:** usa o atributo derivado `categoria_raridade` (decisão 6 da modelagem), que **nenhuma** das sete análises obrigatórias utiliza.

Isso demonstra que o modelo dimensional responde a perguntas não previstas em sua construção.

---

## ✅ Contagens esperadas da Gold

| Tabela                               | Linhas esperadas |
| ------------------------------------ | ---------------: |
| `ranking_pokemon`                    |             ~783 |
| `taxa_vitorias_por_tipo`             |               18 |
| `taxa_vitorias_por_faixa_velocidade` |                5 |
| `taxa_vitorias_por_multiplicador`    |                4 |
| `matriz_confronto`                   |              324 |
| `taxa_vitorias_por_raridade`         |                4 |

> `ranking_pokemon` tem aproximadamente 783 registros, e não 799, porque alguns Pokémon conciliados não aparecem em nenhum combate do `combats.csv` — existem no cadastro, mas não têm batalhas.

---

# 📊 Análises

As oito análises do trabalho são respondidas exclusivamente por SQL.

As análises 1 e 2 consultam a camada Silver; as análises 3 a 7 e a análise proposta pelo grupo leem diretamente tabelas já agregadas da camada Gold.

As consultas estão implementadas em:

```text
sql/consultas.sql
```

## Decisões das consultas finais

**Análise 3 — corte mínimo de combates.** Adotou-se um mínimo de **30 combates** para que um Pokémon entre no ranking. A quantidade de combates por Pokémon é bastante desigual (média de ~125, mas com muitos abaixo de 10), e uma taxa de vitórias calculada sobre poucos combates é ruído estatístico — um Pokémon com 3 combates e 100% de vitória não indica desempenho real. O corte de 30 equilibra representatividade e amostra suficiente.

A coluna `num_combates` permanece materializada em `gold.ranking_pokemon`, e o corte é aplicado **apenas na consulta final**, o que permite alterá-lo sem reconstruir a Gold. A quantidade de combates é exibida ao lado da taxa de vitórias, conforme exige o enunciado.

**Análise 5 — faixas de diferença de velocidade.** Adotaram-se **5 faixas**, com cortes em ±50:

```text
muito mais lento   (diferença ≤ -50)
mais lento         (-49 a -1)
mesma velocidade   (0)
mais rápido        (1 a 49)
muito mais rápido  (≥ 50)
```

A faixa central isolada (diferença = 0) serve de referência neutra, e o corte em ±50 separa uma vantagem de velocidade marginal de uma vantagem expressiva. A simetria das faixas permite comparar diretamente os dois lados do confronto.

---

## Orientação da matriz da análise 7

A matriz de confronto é orientada pelo **resultado da batalha**, e não por `First_pokemon`.

A célula `(A, B)` representa a proporção de confrontos entre os tipos primários A e B vencida pelo Pokémon do tipo A.

O mesmo confronto contribui de forma complementar para `(A, B)` e `(B, A)`.

Os resultados e suas interpretações são registrados em `RELATORIO.md`.

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

EP01 — Ciência de Dados
