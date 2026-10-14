# Auditoria de aderência à rubrica

| Critério | Implementação | Situação |
|---|---|---|
| 1. Versionamento | `main` + branches `feature/database`, `feature/raw`, `feature/silver`, `feature/gold` e `docs/readme`, com commits por funcionalidade | OK |
| 2. Organização | SQL, Python, notebook, README, `.env.example`, `.gitignore` e validação pgAdmin separados | OK |
| 3. Extração/Raw | Download via Google Drive com `gdown`, leitura em blocos, `TRUNCATE`, `try/except` e carga dos 4 CSVs | OK |
| 4. Tipagem/limpeza | Raw → Silver com `DATE`, `DECIMAL`, `INT`, tratamento de vírgula decimal e datas | OK |
| 5. Gold | `gold_orgao` e `gold_orgao_pagador` com `JOIN` + `GROUP BY`; agregações adicionais `gold_tipo_pagamento`, `gold_transporte` e `gold_uf_destino`, cada uma com VIEW | Implementado; executar para comprovar |
| 6. Perguntas de negócio | As 7 perguntas da atividade estão implementadas com consultas SQL; as perguntas 4, 5, 6 e 7 usam VIEWs Gold agregadas | Implementado; conferir resultados após execução |
| 7. Dataviz | Cada pergunta possui gráfico com título, eixos nomeados e legenda | Implementado; conferir renderização no notebook |
| 8. Modelagem Silver | PK, FK e 2 constraints adicionais em cada tabela Silver | OK |

## Constraints Silver

- `silver_viagem`: `NOT NULL` em `nome_orgao_superior` + `CHECK valor_diarias >= 0`.
- `silver_pagamento`: `NOT NULL` em `tipo_pagamento` + `CHECK valor >= 0`.
- `silver_passagem`: `CHECK valor_passagem >= 0` + `CHECK taxa_servico >= 0`.
- `silver_trecho`: `CHECK numero_diarias >= 0` + `UNIQUE (id_viagem, sequencia_trecho)`.

Além dessas oito constraints exigidas, as quatro tabelas Silver possuem PK e as tabelas filhas possuem FK para `silver_viagem`.


## Revisão técnica desta versão

- Corrigida a vírgula excedente no `CREATE TABLE silver_viagem`.
- Colunas Raw declaradas como `VARCHAR` sem limite artificial de tamanho para preservar os campos originais.
- O ID do Google Drive é configurado por variável `DRIVE_FILE_ID` no `.env`; não há ID inventado no código. O pacote fornecido inclui o ZIP local para execução sem download.
- A carga Raw é confirmada em uma única transação: se um CSV falhar, as quatro tabelas voltam ao estado anterior.
- A consulta de destinos não exclui destinos com apenas uma viagem sem justificativa.
- A pergunta 7 consulta o órgão pagador efetivo (`nome_orgao_pagador`) por meio de uma agregação Gold própria, distinta do órgão superior da viagem.
- O script `4_validacao_pgadmin.sql` também verifica as novas estruturas Gold.
- As perguntas 4, 5 e 6 consultam `vw_gold_tipo_pagamento`, `vw_gold_transporte` e `vw_gold_uf_destino`, respectivamente, e mantêm seus gráficos correspondentes.

**Limite da auditoria:** a validação de código e estrutura não substitui a execução no ambiente PostgreSQL do usuário. Execute o roteiro do README e registre a saída de `4_validacao_pgadmin.sql` antes da submissão.
