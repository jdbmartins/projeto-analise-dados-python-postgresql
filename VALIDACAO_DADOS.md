# Validação preliminar dos arquivos fornecidos

A validação foi feita sobre o ZIP fornecido junto à atividade, antes da carga no PostgreSQL.

| Arquivo | Registros | Colunas |
|---|---:|---:|
| 2025_Viagem.csv | 341.860 | 22 |
| 2025_Pagamento.csv | 606.916 | 10 |
| 2025_Passagem.csv | 167.260 | 19 |
| 2025_Trecho.csv | 763.349 | 14 |

Também foram verificados:

- todas as linhas possuem a quantidade esperada de colunas;
- `id_viagem` é único na tabela de viagens;
- não foram encontrados registros filhos sem `id_viagem` correspondente na tabela de viagens;
- não foram encontrados valores negativos nos campos submetidos às constraints `CHECK`;
- as datas de início/fim das viagens estão em formato `DD/MM/AAAA` e não apresentam início posterior ao fim;
- `(id_viagem, sequencia_trecho)` não apresentou duplicidades no CSV de trechos.

A confirmação definitiva da integridade após a carga deve ser feita executando `4_validacao_pgadmin.sql` no pgAdmin.
