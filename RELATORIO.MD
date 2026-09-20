
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

