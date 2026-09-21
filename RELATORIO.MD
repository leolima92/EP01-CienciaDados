
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

### Análise 5: Relação entre diferença de velocidade e vitória

| Faixa de Diferença de Velocidade | Combates | Taxa de Vitórias |
| --- | --- | --- |
| muito mais lento (<= -50) | 12.407 | 9,40% |
| mais lento (-49 a -1) | 36.265 | 4,98% |
| mesma velocidade (0) | 2.656 | 50,00% |
| mais rápido (1 a 49) | 36.265 | 95,02% |
| muito mais rápido (>= 50) | 12.407 | 90,60% |

**Interpretação:**
Nessa análise podemos observar a comprovação que a velocidade não é apenas uma vantagem, mas sim o fator determinante para o resultado dos combates.

Quando os Pokémons têm a mesma velocidade, a taxa de vitórias é de exatamente 50%, indicando um cenário de "coinflip" (empate estatístico). No entanto, basta ser um pouco mais rápido (diferença de 1 a 49 pontos) para a taxa de vitórias saltar para absurdos **95,02%**. Nas faixas extremas ("muito mais lento" e "muito mais rápido"), há uma leve regressão para o centro (9,40% e 90,60%, respectivamente). Isso provavelmente ocorre porque Pokémon extremamente rápidos costumam ser "glass canons" (muito ataque e pouca defesa, podendo perder para ataques de prioridade) e Pokémon extremamente lentos costumam ser "tanques" colossais capazes de resistir ao primeiro golpe e revidar. Ainda assim, a conclusão é quem ataca primeiro quase sempre vence.

---

### Análise 6: Relação entre vantagem de tipo e vitória

| Multiplicador (Vantagem de Tipo) | Combates | Taxa de Vitórias |
| --- | --- | --- |
| 0.0 (Imunidade) | 1.824 | 31,69% |
| 0.5 (Desvantagem / Resistência) | 18.976 | 47,54% |
| 1.0 (Dano Neutro) | 64.651 | 50,05% |
| 2.0 (Vantagem / Super Efetivo) | 14.333 | 55,34% |

**Interpretação:**
Nesta análise cruzamos os resultados do simulador com a tabela de efetividade oficial da PokéAPI (considerando o tipo primário). O resultado mostra quanto maior o multiplicador de dano, maior a taxa de vitórias (crescendo de 31,69% para 55,34%).

Porém, o impacto da vantagem de tipo é muito fraco quando comparado ao impacto da velocidade (visto na Análise 5). O caso mais gritante é o multiplicador 0.0 (imunidade): na mecânica real do jogo, um ataque desse tipo não causa dano algum, mas aqui o Pokémon teoricamente "imune" ainda perde 31,69% das vezes. Da mesma forma, ter o dobro de dano a seu favor (2.0) só garante vitória em cerca de 55% dos casos, um número muito pouco acima da média neutra. Isso indica que a lógica por trás de `combats.csv` valorizou excessivamente os *status* brutos (principalmente a velocidade e o poder ofensivo), deixando as interações de tipos da franquia em segundo plano.

---

### Análise 7: Matriz de confronto entre tipos (18x18) e Divergências

| Tipo Atacante | Tipo Defensor | Combates | Taxa de Vitórias | Multiplicador |
| --- | --- | --- | --- | --- |
| bug | bug | 772 | 50,00% | 1.0 |
| bug | dark | 309 | 36,25% | 2.0 |
| bug | dragon | 342 | 28,36% | 1.0 |
| bug | electric | 473 | 26,64% | 1.0 |
| bug | fairy | 190 | 61,05% | 0.5 |
| bug | fighting | 259 | 44,02% | 0.5 |
| bug | fire | 599 | 33,06% | 0.5 |
| bug | flying | 38 | 21,05% | 0.5 |
| bug | ghost | 356 | 45,51% | 0.5 |
| bug | grass | 764 | 51,83% | 2.0 |
| bug | ground | 335 | 47,76% | 1.0 |
| bug | ice | 295 | 48,81% | 1.0 |
| bug | normal | 1066 | 38,65% | 1.0 |
| bug | poison | 324 | 46,60% | 0.5 |
| bug | psychic | 646 | 42,41% | 2.0 |
| bug | rock | 487 | 45,79% | 1.0 |
| bug | steel | 289 | 47,06% | 0.5 |
| bug | water | 1204 | 46,10% | 1.0 |
| dark | bug | 309 | 63,75% | 1.0 |
| dark | dark | 148 | 50,00% | 0.5 |
| dark | dragon | 149 | 51,68% | 1.0 |
| dark | electric | 210 | 44,76% | 1.0 |
| dark | fairy | 83 | 79,52% | 0.5 |
| dark | fighting | 97 | 53,61% | 0.5 |
| dark | fire | 249 | 51,00% | 1.0 |
| dark | flying | 23 | 26,09% | 1.0 |
| dark | ghost | 142 | 66,90% | 2.0 |
| dark | grass | 332 | 72,29% | 1.0 |
| dark | ground | 148 | 60,81% | 1.0 |
| dark | ice | 119 | 68,07% | 1.0 |
| dark | normal | 495 | 54,75% | 1.0 |
| dark | poison | 125 | 66,40% | 1.0 |
| dark | psychic | 291 | 94,50% | 2.0 |
| dark | rock | 246 | 73,58% | 1.0 |
| dark | steel | 153 | 67,32% | 1.0 |
| dark | water | 520 | 64,42% | 1.0 |
| dragon | bug | 342 | 71,64% | 1.0 |
| dragon | dark | 149 | 48,32% | 1.0 |
| dragon | dragon | 150 | 50,00% | 2.0 |
| dragon | electric | 178 | 54,49% | 1.0 |
| dragon | fairy | 84 | 10,71% | 0.0 (Imunidade) |
| dragon | fighting | 121 | 66,94% | 1.0 |
| dragon | fire | 252 | 56,75% | 1.0 |
| dragon | flying | 22 | 18,18% | 1.0 |
| dragon | ghost | 153 | 68,63% | 1.0 |
| dragon | grass | 313 | 69,01% | 1.0 |
| dragon | ground | 137 | 69,34% | 1.0 |
| dragon | ice | 116 | 68,97% | 1.0 |
| dragon | normal | 479 | 57,41% | 1.0 |
| dragon | poison | 173 | 68,79% | 1.0 |
| dragon | psychic | 276 | 53,62% | 1.0 |
| dragon | rock | 260 | 74,62% | 1.0 |
| dragon | steel | 141 | 79,43% | 0.5 |
| dragon | water | 584 | 71,58% | 1.0 |
| electric | bug | 473 | 73,36% | 1.0 |
| electric | dark | 210 | 55,24% | 1.0 |
| electric | dragon | 178 | 45,51% | 0.5 |
| electric | electric | 268 | 50,00% | 0.5 |
| electric | fairy | 132 | 81,82% | 1.0 |
| electric | fighting | 175 | 69,71% | 1.0 |
| electric | fire | 327 | 59,94% | 1.0 |
| electric | flying | 16 | 31,25% | 2.0 |
| electric | ghost | 214 | 76,17% | 1.0 |
| electric | grass | 459 | 66,67% | 0.5 |
| electric | ground | 218 | 9,63% | 0.0 (Imunidade) |
| electric | ice | 163 | 71,17% | 1.0 |
| electric | normal | 676 | 61,83% | 1.0 |
| electric | poison | 201 | 72,14% | 1.0 |
| electric | psychic | 422 | 56,64% | 1.0 |
| electric | rock | 286 | 71,33% | 1.0 |
| electric | steel | 211 | 71,09% | 1.0 |
| electric | water | 713 | 69,85% | 2.0 |
| fairy | bug | 190 | 38,95% | 1.0 |
| fairy | dark | 83 | 20,48% | 2.0 |
| fairy | dragon | 84 | 89,29% | 2.0 |
| fairy | electric | 132 | 18,18% | 1.0 |
| fairy | fairy | 50 | 50,00% | 1.0 |
| fairy | fighting | 59 | 35,59% | 2.0 |
| fairy | fire | 142 | 21,83% | 0.5 |
| fairy | flying | 11 | 27,27% | 1.0 |
| fairy | ghost | 62 | 45,16% | 1.0 |
| fairy | grass | 203 | 29,06% | 1.0 |
| fairy | ground | 82 | 29,27% | 1.0 |
| fairy | ice | 60 | 40,00% | 1.0 |
| fairy | normal | 247 | 24,29% | 1.0 |
| fairy | poison | 77 | 29,87% | 0.5 |
| fairy | psychic | 138 | 26,81% | 1.0 |
| fairy | rock | 140 | 40,71% | 1.0 |
| fairy | steel | 67 | 37,31% | 0.5 |
| fairy | water | 321 | 31,15% | 1.0 |
| fighting | bug | 259 | 55,98% | 0.5 |
| fighting | dark | 97 | 46,39% | 2.0 |
| fighting | dragon | 121 | 33,06% | 1.0 |
| fighting | electric | 175 | 30,29% | 1.0 |
| fighting | fairy | 59 | 64,41% | 0.5 |
| fighting | fighting | 126 | 50,00% | 1.0 |
| fighting | fire | 208 | 33,65% | 1.0 |
| fighting | flying | 10 | 0,00% | 0.5 |
| fighting | ghost | 124 | 13,71% | 0.0 (Imunidade) |
| fighting | grass | 260 | 55,77% | 1.0 |
| fighting | ground | 122 | 48,36% | 1.0 |
| fighting | ice | 90 | 57,78% | 2.0 |
| fighting | normal | 431 | 42,46% | 2.0 |
| fighting | poison | 127 | 54,33% | 0.5 |
| fighting | psychic | 231 | 35,93% | 0.5 |
| fighting | rock | 186 | 66,67% | 2.0 |
| fighting | steel | 109 | 58,72% | 2.0 |
| fighting | water | 461 | 45,12% | 1.0 |
| fire | bug | 599 | 66,94% | 2.0 |
| fire | dark | 249 | 49,00% | 1.0 |
| fire | dragon | 252 | 43,25% | 0.5 |
| fire | electric | 327 | 40,06% | 1.0 |
| fire | fairy | 142 | 78,17% | 1.0 |
| fire | fighting | 208 | 66,35% | 1.0 |
| fire | fire | 430 | 50,00% | 0.5 |
| fire | flying | 29 | 27,59% | 1.0 |
| fire | ghost | 244 | 64,34% | 1.0 |
| fire | grass | 547 | 70,38% | 2.0 |
| fire | ground | 266 | 51,88% | 1.0 |
| fire | ice | 196 | 68,37% | 2.0 |
| fire | normal | 861 | 54,12% | 1.0 |
| fire | poison | 225 | 67,11% | 1.0 |
| fire | psychic | 448 | 47,99% | 1.0 |
| fire | rock | 358 | 60,34% | 0.5 |
| fire | steel | 232 | 68,53% | 2.0 |
| fire | water | 931 | 58,43% | 0.5 |
| flying | bug | 38 | 78,95% | 2.0 |
| flying | dark | 23 | 73,91% | 1.0 |
| flying | dragon | 22 | 81,82% | 1.0 |
| flying | electric | 16 | 68,75% | 0.5 |
| flying | fairy | 11 | 72,73% | 1.0 |
| flying | fighting | 10 | 100,00% | 2.0 |
| flying | fire | 29 | 72,41% | 1.0 |
| flying | flying | 2 | 50,00% | 1.0 |
| flying | ghost | 23 | 82,61% | 1.0 |
| flying | grass | 36 | 75,00% | 2.0 |
| flying | ground | 19 | 89,47% | 1.0 |
| flying | ice | 20 | 80,00% | 1.0 |
| flying | normal | 61 | 72,13% | 1.0 |
| flying | poison | 20 | 80,00% | 1.0 |
| flying | psychic | 35 | 60,00% | 1.0 |
| flying | rock | 24 | 66,67% | 0.5 |
| flying | steel | 21 | 85,71% | 0.5 |
| flying | water | 68 | 76,47% | 1.0 |
| ghost | bug | 356 | 54,49% | 1.0 |
| ghost | dark | 142 | 33,10% | 0.5 |
| ghost | dragon | 153 | 31,37% | 1.0 |
| ghost | electric | 214 | 23,83% | 1.0 |
| ghost | fairy | 62 | 54,84% | 1.0 |
| ghost | fighting | 124 | 86,29% | 1.0 |
| ghost | fire | 244 | 35,66% | 1.0 |
| ghost | flying | 23 | 17,39% | 1.0 |
| ghost | ghost | 166 | 50,00% | 2.0 |
| ghost | grass | 351 | 49,29% | 1.0 |
| ghost | ground | 159 | 46,54% | 1.0 |
| ghost | ice | 123 | 50,41% | 1.0 |
| ghost | normal | 484 | 50,62% | 0.0 (Imunidade) |
| ghost | poison | 145 | 57,24% | 1.0 |
| ghost | psychic | 289 | 44,98% | 2.0 |
| ghost | rock | 208 | 61,54% | 1.0 |
| ghost | steel | 158 | 55,06% | 1.0 |
| ghost | water | 500 | 46,80% | 1.0 |
| grass | bug | 764 | 48,17% | 0.5 |
| grass | dark | 332 | 27,71% | 1.0 |
| grass | dragon | 313 | 30,99% | 0.5 |
| grass | electric | 459 | 33,33% | 1.0 |
| grass | fairy | 203 | 70,94% | 1.0 |
| grass | fighting | 260 | 44,23% | 1.0 |
| grass | fire | 547 | 29,62% | 0.5 |
| grass | flying | 36 | 25,00% | 0.5 |
| grass | ghost | 351 | 50,71% | 1.0 |
| grass | grass | 708 | 50,00% | 0.5 |
| grass | ground | 318 | 49,06% | 2.0 |
| grass | ice | 244 | 41,80% | 1.0 |
| grass | normal | 984 | 39,94% | 1.0 |
| grass | poison | 301 | 43,52% | 0.5 |
| grass | psychic | 632 | 37,34% | 1.0 |
| grass | rock | 482 | 56,85% | 2.0 |
| grass | steel | 274 | 50,36% | 0.5 |
| grass | water | 1208 | 49,83% | 2.0 |
| ground | bug | 335 | 52,24% | 0.5 |
| ground | dark | 148 | 39,19% | 1.0 |
| ground | dragon | 137 | 30,66% | 1.0 |
| ground | electric | 218 | 90,37% | 2.0 |
| ground | fairy | 82 | 70,73% | 1.0 |
| ground | fighting | 122 | 51,64% | 1.0 |
| ground | fire | 266 | 48,12% | 2.0 |
| ground | flying | 19 | 10,53% | 0.0 (Imunidade) |
| ground | ghost | 159 | 53,46% | 1.0 |
| ground | grass | 318 | 50,94% | 0.5 |
| ground | ground | 144 | 50,00% | 1.0 |
| ground | ice | 122 | 48,36% | 1.0 |
| ground | normal | 472 | 48,94% | 1.0 |
| ground | poison | 149 | 61,74% | 2.0 |
| ground | psychic | 274 | 50,36% | 1.0 |
| ground | rock | 229 | 64,19% | 2.0 |
| ground | steel | 122 | 62,30% | 2.0 |
| ground | water | 571 | 53,06% | 1.0 |
| ice | bug | 295 | 51,19% | 1.0 |
| ice | dark | 119 | 31,93% | 1.0 |
| ice | dragon | 116 | 31,03% | 2.0 |
| ice | electric | 163 | 28,83% | 1.0 |
| ice | fairy | 60 | 60,00% | 1.0 |
| ice | fighting | 90 | 42,22% | 1.0 |
| ice | fire | 196 | 31,63% | 0.5 |
| ice | flying | 20 | 20,00% | 2.0 |
| ice | ghost | 123 | 49,59% | 1.0 |
| ice | grass | 244 | 58,20% | 2.0 |
| ice | ground | 122 | 51,64% | 2.0 |
| ice | ice | 94 | 50,00% | 0.5 |
| ice | normal | 365 | 39,45% | 1.0 |
| ice | poison | 99 | 49,49% | 1.0 |
| ice | psychic | 224 | 37,50% | 1.0 |
| ice | rock | 182 | 48,90% | 1.0 |
| ice | steel | 119 | 47,06% | 0.5 |
| ice | water | 445 | 47,19% | 0.5 |
| normal | bug | 1066 | 61,35% | 1.0 |
| normal | dark | 495 | 45,25% | 1.0 |
| normal | dragon | 479 | 42,59% | 1.0 |
| normal | electric | 676 | 38,17% | 1.0 |
| normal | fairy | 247 | 75,71% | 1.0 |
| normal | fighting | 431 | 57,54% | 1.0 |
| normal | fire | 861 | 45,88% | 1.0 |
| normal | flying | 61 | 27,87% | 1.0 |
| normal | ghost | 484 | 49,38% | 0.0 (Imunidade) |
| normal | grass | 984 | 60,06% | 1.0 |
| normal | ground | 472 | 51,06% | 1.0 |
| normal | ice | 365 | 60,55% | 1.0 |
| normal | normal | 1416 | 50,00% | 1.0 |
| normal | poison | 432 | 63,89% | 1.0 |
| normal | psychic | 811 | 45,25% | 1.0 |
| normal | rock | 682 | 60,56% | 0.5 |
| normal | steel | 422 | 57,82% | 0.5 |
| normal | water | 1702 | 60,58% | 1.0 |
| poison | bug | 324 | 53,40% | 1.0 |
| poison | dark | 125 | 33,60% | 1.0 |
| poison | dragon | 173 | 31,21% | 1.0 |
| poison | electric | 201 | 27,86% | 1.0 |
| poison | fairy | 77 | 70,13% | 2.0 |
| poison | fighting | 127 | 45,67% | 1.0 |
| poison | fire | 225 | 32,89% | 1.0 |
| poison | flying | 20 | 20,00% | 1.0 |
| poison | ghost | 145 | 42,76% | 0.5 |
| poison | grass | 301 | 56,48% | 2.0 |
| poison | ground | 149 | 38,26% | 0.5 |
| poison | ice | 99 | 50,51% | 1.0 |
| poison | normal | 432 | 36,11% | 1.0 |
| poison | poison | 148 | 50,00% | 0.5 |
| poison | psychic | 270 | 38,89% | 1.0 |
| poison | rock | 194 | 60,82% | 0.5 |
| poison | steel | 120 | 24,17% | 0.0 (Imunidade) |
| poison | water | 518 | 45,37% | 1.0 |
| psychic | bug | 646 | 57,59% | 1.0 |
| psychic | dark | 291 | 5,50% | 0.0 (Imunidade) |
| psychic | dragon | 276 | 46,38% | 1.0 |
| psychic | electric | 422 | 43,36% | 1.0 |
| psychic | fairy | 138 | 73,19% | 1.0 |
| psychic | fighting | 231 | 64,07% | 2.0 |
| psychic | fire | 448 | 52,01% | 1.0 |
| psychic | flying | 35 | 40,00% | 1.0 |
| psychic | ghost | 289 | 55,02% | 1.0 |
| psychic | grass | 632 | 62,66% | 1.0 |
| psychic | ground | 274 | 49,64% | 1.0 |
| psychic | ice | 224 | 62,50% | 1.0 |
| psychic | normal | 811 | 54,75% | 1.0 |
| psychic | poison | 270 | 61,11% | 2.0 |
| psychic | psychic | 518 | 50,00% | 0.5 |
| psychic | rock | 445 | 62,92% | 1.0 |
| psychic | steel | 279 | 55,20% | 0.5 |
| psychic | water | 1086 | 61,60% | 1.0 |
| rock | bug | 487 | 54,21% | 2.0 |
| rock | dark | 246 | 26,42% | 1.0 |
| rock | dragon | 260 | 25,38% | 1.0 |
| rock | electric | 286 | 28,67% | 1.0 |
| rock | fairy | 140 | 59,29% | 1.0 |
| rock | fighting | 186 | 33,33% | 0.5 |
| rock | fire | 358 | 39,66% | 2.0 |
| rock | flying | 24 | 33,33% | 2.0 |
| rock | ghost | 208 | 38,46% | 1.0 |
| rock | grass | 482 | 43,15% | 1.0 |
| rock | ground | 229 | 35,81% | 0.5 |
| rock | ice | 182 | 51,10% | 2.0 |
| rock | normal | 682 | 39,44% | 1.0 |
| rock | poison | 194 | 39,18% | 1.0 |
| rock | psychic | 445 | 37,08% | 1.0 |
| rock | rock | 314 | 50,00% | 1.0 |
| rock | steel | 179 | 48,04% | 0.5 |
| rock | water | 759 | 40,97% | 1.0 |
| steel | bug | 289 | 52,94% | 1.0 |
| steel | dark | 153 | 32,68% | 1.0 |
| steel | dragon | 141 | 20,57% | 1.0 |
| steel | electric | 211 | 28,91% | 0.5 |
| steel | fairy | 67 | 62,69% | 2.0 |
| steel | fighting | 109 | 41,28% | 1.0 |
| steel | fire | 232 | 31,47% | 0.5 |
| steel | flying | 21 | 14,29% | 1.0 |
| steel | ghost | 158 | 44,94% | 1.0 |
| steel | grass | 274 | 49,64% | 1.0 |
| steel | ground | 122 | 37,70% | 1.0 |
| steel | ice | 119 | 52,94% | 2.0 |
| steel | normal | 422 | 42,18% | 1.0 |
| steel | poison | 120 | 75,83% | 1.0 |
| steel | psychic | 279 | 44,80% | 1.0 |
| steel | rock | 179 | 51,96% | 2.0 |
| steel | steel | 146 | 50,00% | 0.5 |
| steel | water | 497 | 38,23% | 0.5 |
| water | bug | 1204 | 53,90% | 1.0 |
| water | dark | 520 | 35,58% | 1.0 |
| water | dragon | 584 | 28,42% | 0.5 |
| water | electric | 713 | 30,15% | 1.0 |
| water | fairy | 321 | 68,85% | 1.0 |
| water | fighting | 461 | 54,88% | 1.0 |
| water | fire | 931 | 41,57% | 2.0 |
| water | flying | 68 | 23,53% | 1.0 |
| water | ghost | 500 | 53,20% | 1.0 |
| water | grass | 1208 | 50,17% | 0.5 |
| water | ground | 571 | 46,94% | 2.0 |
| water | ice | 445 | 52,81% | 1.0 |
| water | normal | 1702 | 39,42% | 1.0 |
| water | poison | 518 | 54,63% | 1.0 |
| water | psychic | 1086 | 38,40% | 1.0 |
| water | rock | 759 | 59,03% | 2.0 |
| water | steel | 497 | 61,77% | 1.0 |
| water | water | 1942 | 50,00% | 0.5 |

**Destaque: Posições onde vitória e efetividade divergem**
*(Cenários onde o atacante tem desvantagem [Mult < 1] mas vence na maioria das vezes, ou onde tem vantagem [Mult > 1] mas perde na maioria das vezes)*

| Tipo Atacante | Tipo Defensor | Combates | Taxa de Vitórias | Multiplicador |
| --- | --- | --- | --- | --- |
| flying | steel | 21 | 85,71% | 0.5 |
| dark | fairy | 83 | 79,52% | 0.5 |
| dragon | steel | 141 | 79,43% | 0.5 |
| flying | electric | 16 | 68,75% | 0.5 |
| electric | grass | 459 | 66,67% | 0.5 |
| flying | rock | 24 | 66,67% | 0.5 |
| fighting | fairy | 59 | 64,41% | 0.5 |
| bug | fairy | 190 | 61,05% | 0.5 |
| poison | rock | 194 | 60,82% | 0.5 |
| normal | rock | 682 | 60,56% | 0.5 |
| fire | rock | 358 | 60,34% | 0.5 |
| fire | water | 931 | 58,43% | 0.5 |
| normal | steel | 422 | 57,82% | 0.5 |
| fighting | bug | 259 | 55,98% | 0.5 |
| psychic | steel | 279 | 55,20% | 0.5 |
| fighting | poison | 127 | 54,33% | 0.5 |
| dark | fighting | 97 | 53,61% | 0.5 |
| ground | bug | 335 | 52,24% | 0.5 |
| ground | grass | 318 | 50,94% | 0.5 |
| ghost | normal | 484 | 50,62% | 0.0 (Imunidade) |
| grass | steel | 274 | 50,36% | 0.5 |
| water | grass | 1208 | 50,17% | 0.5 |
| grass | water | 1208 | 49,83% | 2.0 |
| grass | ground | 318 | 49,06% | 2.0 |
| ground | fire | 266 | 48,12% | 2.0 |
| water | ground | 571 | 46,94% | 2.0 |
| fighting | dark | 97 | 46,39% | 2.0 |
| ghost | psychic | 289 | 44,98% | 2.0 |
| fighting | normal | 431 | 42,46% | 2.0 |
| bug | psychic | 646 | 42,41% | 2.0 |
| water | fire | 931 | 41,57% | 2.0 |
| rock | fire | 358 | 39,66% | 2.0 |
| bug | dark | 309 | 36,25% | 2.0 |
| fairy | fighting | 59 | 35,59% | 2.0 |
| rock | flying | 24 | 33,33% | 2.0 |
| electric | flying | 16 | 31,25% | 2.0 |
| ice | dragon | 116 | 31,03% | 2.0 |
| fairy | dark | 83 | 20,48% | 2.0 |
| ice | flying | 20 | 20,00% | 2.0 |

**Interpretação:**
Esta análise isola os casos onde a simulação "quebra" a mecânica clássica da franquia.

No topo da tabela, vemos Pokémon vencendo a maioria dos confrontos mesmo quando seus ataques causam apenas metade do dano (Multiplicador = 0.5). O caso mais extremo é **Voador** contra **Aço** (85,71% de vitória para Voador). Sabendo pela Análise 2 que Voador é o tipo mais rápido do jogo e Aço é o penúltimo mais lento, fica evidente que um Pokémon ágil compensa a resistência do oponente desferindo o primeiro ataque, possivelmente o derrotando antes que ele possa reagir.

Ainda mais grave é o caso do atacante **Fantasma** contra o defensor **Normal**. Na mecânica real do Pokemon, ataques Fantasma não afetam Pokémon Normais (Multiplicador = 0.0), e ainda assim o tipo Fantasma venceu **50,62%** das 484 batalhas desse cruzamento. Isso prova de forma definitiva que o programa que gerou os dados do arquivo `combats.csv` **não implementou corretamente a matriz de imunidades do jogo**, tratando esse confronto como um embate neutro.

Por fim, a base da tabela mostra tipos com vantagem (Multiplicador = 2.0) perdendo a maioria dos confrontos. Tipos classicamente frágeis e defensivamente fracos (Gelo e Fada) frequentemente perdem para os tipos sobre os quais deveriam ter vantagem (Dragão e Sombrio), simplesmente porque não sobrevivem ao primeiro turno de ataque para usar seu multiplicador a seu favor.

---

Aqui está a formatação e a interpretação para a sua Análise 8. Essa foi uma sacada excelente do seu grupo para fechar o trabalho, pois ela usa aquele atributo derivado que vocês criaram na carga do *Silver*!

Pode copiar e colar no seu `RELATORIO.md`:

---

### Análise 8 (Proposta do Grupo): Taxa de vitórias por categoria de raridade

**Pergunta de Negócio:** Pokémon de categorias mais raras (Lendários e Míticos) realmente apresentam um desempenho superior nas batalhas em relação aos Pokémon comuns?

| Categoria de Raridade | Combates | Taxa de Vitórias |
| --- | --- | --- |
| Mítico | 3.075 | 80,36% |
| Lendário | 6.373 | 77,06% |
| Comum | 88.256 | 47,50% |
| Bebê | 2.188 | 27,88% |

**Interpretação:**
A análise confirma a hipótese levantada pelo nosso grupo: a raridade de um Pokémon implica em uma vantagem nos combates.

Pokémon **Míticos** e **Lendários** vencem aproximadamente 8 em cada 10 batalhas que disputam (80,36% e 77,06%, respectivamente). Esse domínio acontece porque a raridade está atrelada a atributos base (status) significativamente maiores do que a média. Como a Análise 5 provou que o algoritmo do simulador recompensa brutalmente atributos brutos (especialmente a velocidade), os Lendários e Míticos levam uma vantagem natural.

Do outro lado, os Pokémon da categoria **Comum** perdem um pouco mais do que ganham (47,50%), o que é esperado, já que essa categoria engloba desde formas evoluídas fortes até formas base muito fracas, puxando a média para baixo. Por fim, os Pokémon classificados como **Bebê** (*Baby*) possuem o pior desempenho da simulação (27,88%), o que é coerente com o design do jogo, visto que são estágios pré-evolutivos com os menores status possíveis.

---
