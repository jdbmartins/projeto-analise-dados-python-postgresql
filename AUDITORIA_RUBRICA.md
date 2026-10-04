# Auditoria de aderência à rubrica

| Critério | Implementação | Situação |
|---|---|---|
| 1. Versionamento | `main` + branches `feature/database`, `feature/raw`, `feature/silver`, `feature/gold` e `docs/readme`, com commits por funcionalidade | OK |
| 2. Organização | SQL, Python, notebook, README, `.env.example`, `.gitignore` e validação pgAdmin separados | OK |
| 3. Extração/Raw | Download via Google Drive com `gdown`, leitura em blocos, `TRUNCATE`, `try/except` e carga dos 4 CSVs | OK |
| 4. Tipagem/limpeza | Raw → Silver com `DATE`, `DECIMAL`, `INT`, tratamento de vírgula decimal e datas | OK |
| 5. Gold | `gold_orgao` criada com `JOIN` + `GROUP BY` e `vw_gold_orgao` | OK |
| 6. Perguntas de negócio | As 7 perguntas da atividade são respondidas por SQL com resultados e análise | OK |
| 7. Dataviz | Cada pergunta possui visualização com título e eixos identificados | OK |
| 8. Modelagem Silver | PK, FK e 2 constraints adicionais em cada tabela Silver | OK |

## Constraints Silver

- `silver_viagem`: `NOT NULL` em `nome_orgao_superior` + `CHECK valor_diarias >= 0`.
- `silver_pagamento`: `NOT NULL` em `tipo_pagamento` + `CHECK valor >= 0`.
- `silver_passagem`: `CHECK valor_passagem >= 0` + `CHECK taxa_servico >= 0`.
- `silver_trecho`: `CHECK numero_diarias >= 0` + `UNIQUE (id_viagem, sequencia_trecho)`.

Além dessas oito constraints exigidas, as quatro tabelas Silver possuem PK e as tabelas filhas possuem FK para `silver_viagem`.
