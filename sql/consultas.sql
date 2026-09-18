----   Análises 1 e 2: sobre o schema SILVER (cadastro)
--   Análises 3 a 8: leitura DIRETA do schema GOLD (sem agregar nem juntar)


-- Análise 1 - Quantidade de Pokémons por tipo primário e geração
-- Verificação de consistência: divergências indicam  falha na conciliação

SELECT 
    tipo_primario,
    COUNT(*) FILTER (WHERE geracao = 1) AS gen1,
    COUNT(*) FILTER (WHERE geracao = 2) AS gen2,
    COUNT(*) FILTER (WHERE geracao = 3) AS gen3,
    COUNT(*) FILTER (WHERE geracao = 4) AS gen4,
    COUNT(*) FILTER (WHERE geracao = 5) AS gen5,
    COUNT(*) FILTER (WHERE geracao = 6) AS gen6,
    COUNT(*)                            AS total
FROM silver.dim_pokemon
WHERE sk_pokemon <> -1
GROUP BY tipo_primario
ORDER BY tipo_primario;


-- Análise 2 — Média de cada atributo de status por tipo primário.
-- Identificar o tipo mais veloz, o mais resistente, e se algum domina em tudo.
SELECT
    tipo_primario,
    COUNT(*)               AS qtd,
    ROUND(AVG(hp), 1)         AS hp,
    ROUND(AVG(ataque), 1)     AS ataque,
    ROUND(AVG(defesa), 1)     AS defesa,
    ROUND(AVG(sp_ataque), 1)  AS sp_ataque,
    ROUND(AVG(sp_defesa), 1)  AS sp_defesa,
    ROUND(AVG(velocidade), 1) AS velocidade
FROM silver.dim_pokemon
WHERE sk_pokemon <> -1
GROUP BY tipo_primario
ORDER BY velocidade DESC;
 

 -- ANÁLISES SOBRE AS BATALHAS

 -- Análise 3 — Taxa de vitórias por Pokémon: 10 maiores e 10 menores.
-- Corte mínimo de 30 combates para eliminar ruído estatístico (justificado no README).
-- Top 10:
SELECT nome, tipo_primario, num_combates, vitorias, taxa_vitorias
FROM gold.ranking_pokemon
WHERE num_combates >= 30
ORDER BY taxa_vitorias DESC, num_combates DESC
LIMIT 10;

-- Bottom 10:
SELECT nome, tipo_primario, num_combates, vitorias, taxa_vitorias
FROM gold.ranking_pokemon
WHERE num_combates >= 30
ORDER BY taxa_vitorias ASC, num_combates DESC
LIMIT 10;

-- Análise 4 — Taxa de vitórias por tipo primário (existe tipo dominante?).
SELECT tipo, num_combates, vitorias, taxa_vitorias
FROM gold.taxa_vitorias_por_tipo
ORDER BY taxa_vitorias DESC;


-- Análise 5 — Relação entre diferença de velocidade e vitória.
SELECT faixa, num_combates, taxa_vitorias
FROM gold.taxa_vitorias_por_faixa_velocidade
ORDER BY ordem;
 

-- Análise 6 — Relação entre vantagem de tipo e vitória.
-- Espera-se taxa crescente do multiplicador 0 -> 0.5 -> 1 -> 2.
SELECT multiplicador, num_combates, taxa_vitorias
FROM gold.taxa_vitorias_por_multiplicador
ORDER BY multiplicador;

-- Análise 7 — Matriz de confronto entre tipos (18x18).
SELECT tipo_atacante, tipo_defensor, num_combates, taxa_vitorias, multiplicador
FROM gold.matriz_confronto
ORDER BY tipo_atacante, tipo_defensor;

-- Análise 7 (destaque) — posições onde vitória e efetividade DIVERGEM:
-- vence apesar de desvantagem de tipo, ou perde apesar de vantagem.
SELECT tipo_atacante, tipo_defensor, num_combates, taxa_vitorias, multiplicador
FROM gold.matriz_confronto
WHERE (taxa_vitorias > 0.5 AND multiplicador < 1)
   OR (taxa_vitorias < 0.5 AND multiplicador > 1)
ORDER BY taxa_vitorias DESC;
 


 -- Análise 8 (proposta do grupo) — Taxa de vitórias por categoria de raridade.
SELECT categoria_raridade, num_combates, taxa_vitorias
FROM gold.taxa_vitorias_por_raridade
ORDER BY taxa_vitorias DESC;