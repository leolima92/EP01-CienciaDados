
# Relatório de Análises — EP01: ETL e Arquitetura Medalhão

Este relatório apresenta os resultados das oito consultas analíticas formuladas sobre os dados de cadastro e o histórico de batalhas simuladas de Pokémon. As análises baseiam-se no modelo dimensional construído na camada Silver e nas agregações materializadas na camada Gold. O objetivo é explorar as características do cadastro e os fatores que influenciam a taxa de vitórias nos combates.

---

## Análises sobre o cadastro (Silver)

### Análise 1: Quantidade de Pokémon por tipo primário e por geração

| Tipo Primário | Gen 1 | Gen 2 | Gen 3 | Gen 4 | Gen 5 | Gen 6 | Total |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bug | 14 | 12 | 12 | 10 | 18 | 3 | 69 |
| dark | 0 | 6 | 6 | 3 | 13 | 3 | 31 |
| dragon | 3 | 0 | 12 | 4 | 9 | 4 | 32 |
| electric | 9 | 7 | 5 | 12 | 8 | 3 | 44 |
| fairy | 2 | 5 | 0 | 1 | 0 | 9 | 17 |
| fighting | 6 | 2 | 5 | 3 | 7 | 3 | 26 |
| fire | 14 | 8 | 8 | 5 | 9 | 8 | 52 |
| flying | 0 | 0 | 0 | 0 | 2 | 2 | 4 |
| ghost | 4 | 1 | 5 | 7 | 5 | 10 | 32 |
| grass | 13 | 9 | 13 | 15 | 15 | 5 | 70 |
| ground | 8 | 3 | 7 | 4 | 10 | 0 | 32 |
| ice | 2 | 4 | 7 | 3 | 6 | 2 | 24 |
| normal | 24 | 15 | 18 | 18 | 19 | 4 | 98 |
| poison | 14 | 1 | 3 | 6 | 2 | 2 | 28 |
| psychic | 11 | 7 | 12 | 8 | 14 | 5 | 57 |
| rock | 10 | 5 | 8 | 6 | 6 | 9 | 44 |
| steel | 0 | 3 | 12 | 3 | 4 | 5 | 27 |
| water | 31 | 18 | 27 | 13 | 18 | 5 | 112 |

**Interpretação:**
A matriz de tipo por geração serve como uma verificação de consistência do processo de conciliação. A distribuição reflete perfeitamente a base de dados esperada, sem perdas anormais.

Observando a distribuição, destaca-se que o tipo primário **Água** é de longe o mais abundante na franquia (112 registros), mantendo uma presença forte em praticamente todas as gerações, especialmente na Geração 1 (31) e Geração 3 (27). No extremo oposto, o tipo **Voador** é extremamente raro como tipo primário (apenas 4 ocorrências em todo o dataset), sendo normalmente utilizado como um tipo secundário. A introdução do tipo **Fada** na Geração 6 também fica evidente, com um pico de 9 novos registros nessa geração.

### Análise 2: Média de cada atributo de status por tipo primário

| Tipo Primário | Qtd | HP | Ataque | Defesa | Sp. Ataque | Sp. Defesa | Velocidade |
| --- | --- | --- | --- | --- | --- | --- | --- |
| flying | 4 | 70.8 | 78.8 | 66.3 | 94.3 | 72.5 | 102.5 |
| electric | 44 | 59.8 | 69.1 | 66.3 | 90.0 | 73.7 | 84.5 |
| dragon | 32 | 83.3 | 112.1 | 86.4 | 96.8 | 88.8 | 83.0 |
| psychic | 57 | 70.6 | 71.5 | 67.7 | 98.4 | 86.3 | 81.5 |
| dark | 31 | 66.8 | 88.4 | 70.2 | 74.6 | 69.5 | 76.2 |
| fire | 52 | 69.9 | 84.8 | 67.8 | 89.0 | 72.2 | 74.4 |
| normal | 98 | 77.3 | 73.5 | 59.8 | 55.8 | 63.7 | 71.6 |
| water | 112 | 72.1 | 74.2 | 72.9 | 74.8 | 70.5 | 66.0 |
| fighting | 26 | 70.0 | 96.5 | 66.2 | 52.8 | 64.5 | 65.0 |
| ghost | 32 | 64.4 | 73.8 | 81.2 | 79.3 | 76.5 | 64.3 |
| ground | 32 | 73.8 | 95.8 | 84.8 | 56.5 | 62.8 | 63.9 |
| poison | 28 | 67.3 | 74.7 | 68.8 | 60.4 | 64.4 | 63.6 |
| ice | 24 | 72.0 | 72.8 | 71.4 | 77.5 | 76.3 | 63.5 |
| grass | 70 | 67.3 | 73.2 | 70.8 | 77.5 | 70.4 | 61.9 |
| bug | 69 | 56.9 | 71.0 | 70.7 | 53.9 | 64.8 | 61.7 |
| rock | 44 | 65.4 | 92.9 | 100.8 | 63.3 | 75.5 | 55.9 |
| steel | 27 | 65.2 | 92.7 | 126.4 | 67.5 | 80.6 | 55.3 |
| fairy | 17 | 74.1 | 61.5 | 65.7 | 78.5 | 84.7 | 48.6 |

**Interpretação:**
Esta análise traça o perfil tático de cada tipo primário com base em seus atributos médios base. Respondendo aos pontos levantados no escopo do projeto:

* **Maior velocidade média:** O tipo **Voador** é o mais veloz (média de 102,5), seguido de longe por **Elétrico** (84,5) e **Dragão** (83,0). Com isso, podemos observar que Pokémons puramente voadores dependem muito da iniciativa de atacar primeiro.
* **Maior resistência média:** Avaliando a Defesa, o tipo **Aço** é absoluto (média de 126,4), seguido por **Pedra** (100,8). No que diz respeito à vitalidade (HP), o tipo **Dragão** lidera (83,3), acompanhado pelo tipo **Normal** (77,3).
* **Existe um tipo superior em todos os atributos?** Não. Os dados evidenciam o balanceamento da franquia, baseado em vantagens e desvantagens. Embora o tipo **Dragão** possua os maiores atributos ofensivos gerais (112,1 de Ataque) e o maior HP, ele não é o mais rápido (fica atrás de Voador e Elétrico) nem o mais defensivo (fica atrás de Aço e Pedra). Da mesma forma, a incrível resistência do tipo **Aço** é cobrada em sua agilidade (é o penúltimo mais lento, com 55,3 de velocidade). Portanto, não há um tipo que domine todas as frentes (HP, ataque, defesa e velocidade) simultaneamente.

---

## Análises sobre as batalhas (Gold)

### Análise 3: Taxa de vitórias por Pokémon (10 Maiores e 10 Menores)

**Top 10 (Maiores taxas de vitória)**

| Nome | Tipo Primário | Combates | Vitórias | Taxa de Vitórias |
| --- | --- | --- | --- | --- |
| Mega Aerodactyl | rock | 129 | 127 | 98,45% |
| Weavile | dark | 119 | 116 | 97,48% |
| Tornadus Therian Forme | flying | 125 | 121 | 96,80% |
| Mega Beedrill | bug | 119 | 115 | 96,64% |
| Aerodactyl | rock | 141 | 136 | 96,45% |
| Mega Lopunny | normal | 129 | 124 | 96,12% |
| Greninja | water | 127 | 122 | 96,06% |
| Meloetta Pirouette Forme | normal | 123 | 118 | 95,93% |
| Mega Mewtwo Y | psychic | 125 | 119 | 95,20% |
| Mega Sharpedo | water | 120 | 114 | 95,00% |

**Bottom 10 (Menores taxas de vitória)**

| Nome | Tipo Primário | Combates | Vitórias | Taxa de Vitórias |
| --- | --- | --- | --- | --- |
| Shuckle | bug | 135 | 0 | 0,00% |
| Silcoon | bug | 138 | 3 | 2,17% |
| Togepi | fairy | 122 | 3 | 2,46% |
| Solosis | psychic | 129 | 4 | 3,10% |
| Slugma | fire | 123 | 4 | 3,25% |
| Munna | psychic | 128 | 5 | 3,91% |
| Igglybuff | normal | 115 | 5 | 4,35% |
| Wynaut | psychic | 130 | 6 | 4,62% |
| Wooper | water | 125 | 6 | 4,80% |
| Cascoon | bug | 133 | 7 | 5,26% |

**Interpretação:**
O corte de 30 combates eliminou distorções estatísticas, garantindo que o ranking reflita o desempenho real. O Top 10 revela um padrão: o domínio quase absoluto de formas alternativas (Megas e outras Formas especiais) e de Pokémons com o atributo Velocidade alto. Mega Aerodactyl, Weavile e Greninja estão entre os atacantes mais rápidos do jogo. Podemos concluir que atacar primeiro (velocidade maior) é um grande fator pra determinar a vitória

Nos 10 menores, temos o inverso. Encontramos predominantemente Pokémons em estágios iniciais de evolução (Togepi, Igglybuff) ou casulos (Silcoon, Cascoon). O maior destaque, no entanto, é Shuckle: apesar de possuir as maiores defesas do jogo, sua velocidade é uma das mais baixas e seu poder ofensivo é baixíssimo. O fato de Shuckle ter perdido todos os 135 combates que disputou (taxa de 0%) confirma que uma estratégia puramente defensiva falha miseravelmente no algoritmo que gera as batalhas.

---

### Análise 4: Taxa de vitórias por tipo primário

| Tipo Primário | Combates | Vitórias | Taxa de Vitórias |
| --- | --- | --- | --- |
| flying | 478 | 362 | 75,73% |
| dark | 3845 | 2447 | 63,64% |
| dragon | 3932 | 2490 | 63,33% |
| electric | 5346 | 3370 | 63,04% |
| fire | 6552 | 3802 | 58,03% |
| psychic | 7320 | 3998 | 54,62% |
| normal | 12098 | 6518 | 53,88% |
| ground | 3889 | 2088 | 53,69% |
| ghost | 3908 | 1877 | 48,03% |
| water | 14041 | 6569 | 46,78% |
| fighting | 3198 | 1458 | 45,59% |
| ice | 3079 | 1357 | 44,07% |
| grass | 8426 | 3707 | 43,99% |
| bug | 8760 | 3772 | 43,06% |
| poison | 3654 | 1571 | 42,99% |
| steel | 3546 | 1523 | 42,95% |
| rock | 5669 | 2299 | 40,55% |
| fairy | 2151 | 707 | 32,87% |

**Interpretação:**
Existe uma clara diferença de desempenho entre os tipos na simulação de batalhas. O tipo **Voador** apresenta um domínio estatístico (75,73% de vitórias). Isso se explica pelo fato mostrado na Análise 1: existem apenas 4 Pokémon com Voador como tipo primário (frequentemente formas de lendários poderosos como Tornadus), o que puxa a média do tipo agressivamente para cima e consolida a alta velocidade que o tipo demonstrou na Análise 2.

Logo em seguida, observamos os tipos **Sombrio**, **Dragão** e **Elétrico** superando a marca de 60%. Esses tipos compartilham perfis ofensivos e ágeis. Em contraste, os tipos puramente defensivos ou lentos, como **Aço** e **Pedra**, ocupam as últimas posições (40 a 42%), apesar de terem os maiores status de defesa do jogo. O tipo **Fada** ocupa a última posição (32,87%), o que é coerente com a Análise 2, onde este tipo registrou a pior média de velocidade (48,6). Esses resultados confirmam a conclusão da análise anterior: a simulação de combate penaliza Pokémon lentos e recompensa a agilidade e poder de ataque.

---
