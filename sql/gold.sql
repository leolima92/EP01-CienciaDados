-- EP01 — Camada GOLD (silver -> gold, agregação DENTRO do PostgreSQL)

-- Cada tabela é materializada no grão de uma análise (CREATE TABLE AS SELECT).
-- A agregação roda no banco, nunca na memória do Python (seção 5.1).
-- Idempotente: DROP + CTAS recria cada tabela do zero a cada execução.
-- As consultas finais (consultas.sql) leem estas tabelas SEM agregar nem juntar.

CREATE SCHEMA IF NOT EXISTS gold;

-- Log de publicação (histórico de execuções; preenchido pelo publicar.py)
CREATE TABLE IF NOT EXISTS gold.log_publicacao (
    tabela        TEXT,
    linhas        BIGINT,
    executado_em  TIMESTAMPTZ DEFAULT now()
);


-- Análise 3 — taxa de vitórias por Pokémon 
DROP TABLE IF EXISTS gold.ranking_pokemon;
CREATE TABLE gold.ranking_pokemon AS
SELECT
    p.nome,
    p.tipo_primario,
    COUNT(*)                             AS num_combates,
    SUM(f.venceu)                        AS vitorias,
    ROUND(AVG(f.venceu::numeric), 4)     AS taxa_vitorias
FROM silver.fato_confronto f
JOIN silver.dim_pokemon p ON p.sk_pokemon = f.sk_pokemon
WHERE f.sk_pokemon <> -1
GROUP BY p.nome, p.tipo_primario;


-- Análise 4 — taxa de vitórias por tipo primário 
DROP TABLE IF EXISTS gold.taxa_vitorias_por_tipo;
CREATE TABLE gold.taxa_vitorias_por_tipo AS
SELECT
    t.nome                              AS tipo,
    COUNT(*)                            AS num_combates,
    SUM(f.venceu)                       AS vitorias,
    ROUND(AVG(f.venceu::numeric), 4)    AS taxa_vitorias
FROM silver.fato_confronto f
JOIN silver.dim_tipo t ON t.sk_tipo = f.sk_tipo_participante
WHERE f.sk_tipo_participante <> -1
GROUP BY t.nome;


-- Análise 5 — efeito da diferença de velocidade 
DROP TABLE IF EXISTS gold.taxa_vitorias_por_faixa_velocidade;
CREATE TABLE gold.taxa_vitorias_por_faixa_velocidade AS
SELECT
    CASE
        WHEN diferenca_velocidade <= -50 THEN 1
        WHEN diferenca_velocidade <    0 THEN 2
        WHEN diferenca_velocidade =    0 THEN 3
        WHEN diferenca_velocidade <   50 THEN 4
        ELSE 5
    END AS ordem,
    CASE
        WHEN diferenca_velocidade <= -50 THEN 'muito mais lento (<= -50)'
        WHEN diferenca_velocidade <    0 THEN 'mais lento (-49 a -1)'
        WHEN diferenca_velocidade =    0 THEN 'mesma velocidade'
        WHEN diferenca_velocidade <   50 THEN 'mais rapido (1 a 49)'
        ELSE 'muito mais rapido (>= 50)'
    END AS faixa,
    COUNT(*)                          AS num_combates,
    ROUND(AVG(venceu::numeric), 4)    AS taxa_vitorias
FROM silver.fato_confronto
GROUP BY 1, 2;


-- Análise 6 — efeito da vantagem de tipo (multiplicador) 
DROP TABLE IF EXISTS gold.taxa_vitorias_por_multiplicador;
CREATE TABLE gold.taxa_vitorias_por_multiplicador AS
SELECT
    e.multiplicador,
    COUNT(*)                          AS num_combates,
    ROUND(AVG(f.venceu::numeric), 4)  AS taxa_vitorias
FROM silver.fato_confronto f
JOIN silver.efetividade_tipo e
      ON e.sk_tipo_atacante = f.sk_tipo_participante
     AND e.sk_tipo_defensor = f.sk_tipo_oponente
GROUP BY e.multiplicador;


-- Análise 7 — matriz de confronto 18x18 (tipo atacante x defensor) 
DROP TABLE IF EXISTS gold.matriz_confronto;
CREATE TABLE gold.matriz_confronto AS
SELECT
    ta.nome                           AS tipo_atacante,
    td.nome                           AS tipo_defensor,
    COUNT(*)                          AS num_combates,
    ROUND(AVG(f.venceu::numeric), 4)  AS taxa_vitorias,
    e.multiplicador
FROM silver.fato_confronto f
JOIN silver.dim_tipo ta ON ta.sk_tipo = f.sk_tipo_participante
JOIN silver.dim_tipo td ON td.sk_tipo = f.sk_tipo_oponente
JOIN silver.efetividade_tipo e
      ON e.sk_tipo_atacante = f.sk_tipo_participante
     AND e.sk_tipo_defensor = f.sk_tipo_oponente
WHERE f.sk_tipo_participante <> -1 AND f.sk_tipo_oponente <> -1
GROUP BY ta.nome, td.nome, e.multiplicador;


-- Análise 8 (proposta do grupo) — taxa de vitórias por raridade 
-- Usa o atributo derivado categoria_raridade (decisão 6), não exigido pelas
-- 7 análises anteriores. Pergunta: lendários/míticos vencem mais nas batalhas?
DROP TABLE IF EXISTS gold.taxa_vitorias_por_raridade;
CREATE TABLE gold.taxa_vitorias_por_raridade AS
SELECT
    p.categoria_raridade,
    COUNT(*)                          AS num_combates,
    ROUND(AVG(f.venceu::numeric), 4)  AS taxa_vitorias
FROM silver.fato_confronto f
JOIN silver.dim_pokemon p ON p.sk_pokemon = f.sk_pokemon
WHERE f.sk_pokemon <> -1
GROUP BY p.categoria_raridade;