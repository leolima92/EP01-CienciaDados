EP01 — ETL e Arquitetura Medalhão (Ciência de Dados)

Leonado Rodrigues de Lima, Yasmin Ayumi Foltran Mano

Pipeline de dados que extrai informações da PokéAPI e de um conjunto de dados de batalhas simuladas de Pokémon, organiza tudo em arquitetura medalhão (bronze → silver → gold) e responde a oito análises exclusivamente em SQL.

Visão geral da arquitetura
Camada	Tecnologia	Conteúdo	Script
🥉 Bronze	MongoDB	Dado bruto, idêntico à fonte	extrair.py
🥈 Silver	PostgreSQL	Modelo dimensional (esquema estrela)	carregar.py + sql/silver.sql
🥇 Gold	PostgreSQL	Agregados no grão das perguntas	publicar.py + sql/gold.sql

Cada script lê apenas da camada anterior e escreve na seguinte. A propriedade central do padrão é a imutabilidade da bronze: como o dado bruto é preservado, um erro de transformação se corrige reprocessando as camadas seguintes, sem nova consulta às fontes originais.

Fontes de dados
PokéAPI (https://pokeapi.co/api/v2/) — API REST pública, sem autenticação. Endpoints usados: /pokemon/{id}, /pokemon-species/{id}, /type/{id}. Escopo: gerações I–VI (721 espécies) mais as formas Mega.
CSV de batalhas (licença MIT, público):
pokemon.csv — 800 linhas de cadastro.
combats.csv — 50.000 batalhas simuladas.
Estrutura do repositório
.
├── README.md                 # este arquivo
├── RELATORIO.md              # resultados e interpretação das análises
├── requirements.txt
├── .env.example              # modelo de configuração (sem segredos)
├── .gitignore
├── extrair.py                # fontes  -> bronze (MongoDB)      [PRONTO]
├── carregar.py               # bronze  -> silver (PostgreSQL)   [pendente]
├── publicar.py               # silver  -> gold   (PostgreSQL)   [pendente]
├── sql/
│   ├── silver.sql            # DDL do modelo dimensional        [pendente]
│   ├── gold.sql              # schema e tabelas agregadas        [pendente]
│   └── consultas.sql         # as 8 análises                    [pendente]
├── conciliacao.csv           # relatório de conciliação (R4)    [pendente]
└── dados_brutos/             # cache local (NÃO versionado)

Nota: no estado atual do projeto o extrator vive em bronze/extractor.py. Se mantiver esse layout, ajuste os caminhos dos comandos abaixo. O enunciado sugere extrair.py na raiz — vale alinhar com o grupo antes da entrega.

Pré-requisitos e configuração
Python 3.12+ (recomendado) e as dependências:
bash
   pip install -r requirements.txt
MongoDB — local ou MongoDB Atlas (nuvem).
PostgreSQL — para as camadas silver e gold (etapas seguintes).
Variáveis de ambiente

As credenciais não ficam no código. Copie o modelo e preencha:

bash
cp .env.example .env

No .env, defina a MONGO_URI:

Local: mongodb://localhost:27017
Atlas: mongodb+srv://USUARIO:SENHA@SEU_CLUSTER.mongodb.net/?retryWrites=true&w=majority

O .env está no .gitignore e nunca deve ser commitado — ele contém a senha do banco. Bots que varrem o GitHub encontram credenciais expostas em minutos.

Como executar
Camada bronze
bash
python extrair.py        # 1ª execução: baixa tudo e popula o MongoDB
python extrair.py        # 2ª execução: ZERO requisições, mesmas contagens

Contagens esperadas ao final:

Coleção	Documentos
tipos	21
especies	721
pokemon	~770 (721 padrão + Mega/Primal)
pokemon_csv	800
combates	50.000
Camadas silver e gold


🥉 Camada bronze — decisões
Por que um banco de documentos (MongoDB) na bronze?

A regra da bronze é espelhar a fonte sem transformar. As respostas da PokéAPI têm características que tornam o banco de documentos a escolha natural:

JSON profundamente aninhado. Cada /pokemon traz listas como types[], stats[], abilities[]; cada /type traz damage_relations com seis sublistas. Representar isso fielmente em tabelas relacionais exigiria várias tabelas e joins já na ingestão — ou seja, transformação, que a bronze proíbe. No MongoDB, um documento = uma resposta da API, sem achatamento.
Estruturas heterogêneas entre endpoints. /pokemon, /pokemon-species e /type têm formatos completamente diferentes. Um schema relacional fixo teria de ser modelado e migrado a cada divergência; o documento acomoda formatos variados sem DDL prévio (schema-on-read).
Preservação verbatim. Guardar a resposta inteira, com todos os campos — inclusive os que hoje parecem dispensáveis — é o que permite reprocessar a silver no futuro sem nova consulta à fonte.
Coleções e chaves naturais

Cada documento usa _id derivado da chave natural da origem, o que reduz a carga a um update_one com upsert (base da idempotência):

Coleção	_id	Origem
pokemon	pokemon/{id}	/pokemon/{id}
especies	especie/{id}	/pokemon-species/{id}
tipos	tipo/{id}	/type/{id}
pokemon_csv	pokemon_csv/{#}	linha do pokemon.csv (campo #)
combates	combate/{nº da linha}	linha do combats.csv

combats.csv não possui chave natural única (as colunas First/Second/Winner podem se repetir), então o número da linha é usado como chave.

Linhagem

Todo documento registra metadados de origem, com prefixo _ para não colidir com os campos da fonte:

json
{ "_id": "pokemon/25",
  "_fonte": "pokeapi",
  "_url": "https://pokeapi.co/api/v2/pokemon/25",
  "_ingerido_em": "2026-09-05T14:32:10Z",
  "id": 25, "name": "pikachu", "...": "..." }
Formas Mega

A iteração de 1 a 721 não alcança as formas Mega (id > 10000). Por isso a extração parte de /pokemon-species/{id} e segue o campo varieties[], coletando a forma padrão e as formas cujo nome contém -mega (e -primal, por segurança contra os nomes presentes no CSV de batalhas). Demais formas alternativas ficam fora do escopo.

Valores do CSV preservados como texto

As linhas dos CSV são gravadas com todos os valores como texto, sem conversão — incluindo o nome vazio da linha 63 e o Legendary "True"/"False". A conversão de tipos é responsabilidade da camada silver.

Cache e idempotência (bronze)
Cache em disco antes do MongoDB. Cada resposta é gravada em dados_brutos/…; a API só é consultada quando o arquivo ainda não existe. Isso garante que a 2ª execução faça zero requisições. O diretório é ignorado pelo Git (reconstituível).
Upsert idempotente. A carga usa update_one/bulk_write com upsert e _id derivado da chave natural; _ingerido_em vai em $setOnInsert (gravado só na 1ª inserção), de modo que reexecuções deixam o documento idêntico e não duplicam nada.
