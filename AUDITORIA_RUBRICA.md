# Auditoria de aderência à rubrica

| Critério | Implementação | Situação |
|---|---|---|
| 1. Versionamento | `main` + branches `feature/database`, `feature/raw`, `feature/silver`, `feature/gold` e `docs/readme`, com commits por funcionalidade | OK |
| 2. Organização | SQL, Python, notebook, README, `.env.example`, `.gitignore` e validação pgAdmin separados; CSVs locais ficam em `data/` | Estrutura local organizada; CSVs não versionados conforme seção 5.2 do PDF, embora o critério 2 cite arquivos `.csv` no repositório |
| 3. Extração/Raw | Download via Google Drive com `gdown`, leitura em blocos, `TRUNCATE`, `try/except` e carga dos 4 CSVs | Download oficial testado por `baixar_zip()`; SHA-256 idêntico ao ZIP local; carga idempotente validada |
| 4. Tipagem/limpeza | Raw → Silver com `DATE`, `DECIMAL`, `INT`, tratamento de vírgula decimal e datas | Script executado com sucesso; contagens Raw/Silver iguais |
| 5. Gold | `gold_orgao` e `gold_orgao_pagador` com `JOIN` + `GROUP BY`; agregações adicionais `gold_tipo_pagamento`, `gold_transporte` e `gold_uf_destino`, cada uma com VIEW | 5 tabelas e 5 views existentes; conteúdo correspondente sem diferenças |
| 6. Perguntas de negócio | As 7 perguntas da atividade estão implementadas com consultas SQL; as perguntas 4, 5, 6 e 7 usam VIEWs Gold agregadas | Notebook executado; consultas retornaram tabelas com resultados |
| 7. Dataviz | Cada pergunta possui gráfico com título, eixos nomeados e legenda | Gráficos conferidos; eixos monetários em BRL e contagens sem moeda |
| 8. Modelagem Silver | PK, FK e 2 constraints adicionais em cada tabela Silver | 4 PKs, 3 FKs, 5 CHECKs e 1 UNIQUE; verificações de integridade zeradas |

## Constraints Silver

- `silver_viagem`: `NOT NULL` em `nome_orgao_superior` + `CHECK valor_diarias >= 0`.
- `silver_pagamento`: `NOT NULL` em `tipo_pagamento` + `CHECK valor >= 0`.
- `silver_passagem`: `CHECK valor_passagem >= 0` + `CHECK taxa_servico >= 0`.
- `silver_trecho`: `CHECK numero_diarias >= 0` + `UNIQUE (id_viagem, sequencia_trecho)`.

Além dessas oito constraints exigidas, as quatro tabelas Silver possuem PK e as tabelas filhas possuem FK para `silver_viagem`.


## Revisão técnica desta versão

- Corrigida a vírgula excedente no `CREATE TABLE silver_viagem`.
- Colunas Raw declaradas como `VARCHAR` sem limite artificial de tamanho para preservar os campos originais.
- O ID oficial do ZIP está em `DRIVE_FILE_ID` no `.env.example`; o `.env` local contém o mesmo ID e continua ignorado pelo Git. O download remoto foi testado.
- A carga Raw é confirmada em uma única transação: se um CSV falhar, as quatro tabelas voltam ao estado anterior.
- A consulta de destinos não exclui destinos com apenas uma viagem sem justificativa.
- A pergunta 7 consulta o órgão pagador efetivo (`nome_orgao_pagador`) por meio de uma agregação Gold própria, distinta do órgão superior da viagem.
- O script `4_validacao_pgadmin.sql` também verifica as novas estruturas Gold.
- As perguntas 4, 5 e 6 consultam `vw_gold_tipo_pagamento`, `vw_gold_transporte` e `vw_gold_uf_destino`, respectivamente, e mantêm seus gráficos correspondentes.

## Resultado da validação executada

| Tabela | Raw | Silver |
|---|---:|---:|
| `viagem` | 341.860 | 341.860 |
| `pagamento` | 606.916 | 606.916 |
| `passagem` | 167.260 | 167.260 |
| `trecho` | 763.349 | 763.349 |

- `baixar_zip()` baixou o ZIP oficial a partir do ID fornecido; o SHA-256 coincidiu com o arquivo local.
- `1_extrair.py` foi executado duas vezes; as contagens permaneceram estáveis e coincidiram com os registros dos quatro CSVs.
- `2_transformar.py` concluiu com sucesso. Órfãos, valores negativos e duplicidades `(id_viagem, sequencia_trecho)` retornaram zero.
- As sete consultas do notebook retornaram resultados e seus gráficos foram renderizados. A viagem mais longa tem 383 dias e custo zero; esse dado atípico deve ser conferido na fonte.
- As cinco tabelas Gold e suas cinco VIEWs foram comparadas, sem diferenças. O total de pagamentos por órgão também coincidiu com uma agregação independente sobre `silver_pagamento`.
- `4_validacao_pgadmin.sql` foi executado integralmente contra o banco PostgreSQL configurado, sem erro. A execução foi feita via conexão do projeto, não pela interface gráfica do pgAdmin.

**Nota sobre a organização dos dados:** o PDF pede que ZIP/CSVs e `data/` sejam ignorados no `.gitignore`, mas o critério 2 também cita arquivos `.csv` no repositório. Os dados permanecem organizados localmente em `data/` e não foram versionados, conforme a instrução específica para ignorá-los. A validação do SQL foi feita via conexão PostgreSQL do projeto, não pela interface gráfica do pgAdmin.
