# Projeto Avaliativo — Análise de Dados com Python | Módulo 1

Pipeline ETL para transformar os dados de **Viagens a Serviço** do Portal da Transparência em informações analíticas, utilizando **Python + PostgreSQL** e a Arquitetura Medallion (**Raw → Silver → Gold**).

## 1. Problema

Os dados públicos de viagens a serviço são disponibilizados em arquivos brutos. O projeto automatiza a extração, preserva o conteúdo original, realiza a limpeza/tipagem e produz indicadores para apoiar a análise dos gastos públicos.

## 2. Arquitetura

```text
Google Drive / ZIP oficial
          │
          ▼
     1_extrair.py
          │
          ▼
   ┌─────────────────┐
   │      RAW        │  cópia fiel; VARCHAR; sem constraints
   │  4 tabelas      │
   └────────┬────────┘
            │
            ▼
    2_transformar.py
            │
            ▼
   ┌─────────────────┐
   │     SILVER      │  DATE / DECIMAL / INT + PK + FK + constraints
   │  4 tabelas      │
   └────────┬────────┘
            │
            ▼
     3_analise.ipynb
            │
            ▼
   ┌─────────────────┐
   │      GOLD       │  gold_orgao + vw_gold_orgao
   │  métricas SQL   │
   └─────────────────┘
```

## 3. Perguntas de negócio

O projeto responde às sete perguntas propostas na atividade:

1. Os 5 órgãos com maior custo total?
2. Os 3 destinos com maior custo médio por viagem?
3. A viagem de maior duração e seu custo total?
4. Qual o tipo de pagamento com maior valor médio?
5. Qual o meio de transporte mais usado nos trechos?
6. Qual UF de destino aparece em mais trechos?
7. Qual órgão pagou mais no total?

As respostas são calculadas no PostgreSQL e exibidas no notebook com tabelas e gráficos.

## 4. Tecnologias

- Python 3
- PostgreSQL
- pgAdmin 4
- VSCode
- pandas
- matplotlib
- psycopg2
- gdown
- Jupyter Notebook
- Git/GitHub

## 5. Estrutura do projeto

```text
projeto/
├── 00_criar_database.sql
├── 0_criar_banco.sql
├── 1_extrair.py
├── 2_transformar.py
├── 3_analise.ipynb
├── 4_validacao_pgadmin.sql
├── config.py
├── banco.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── data/
    └── viagens_2025_6meses.zip   # obtido por download; não versionar
```

## 6. Preparação no pgAdmin 4

### 6.1 Criar o banco

No pgAdmin, conecte-se ao banco padrão `postgres` e execute o arquivo `00_criar_database.sql` uma única vez. Depois, conecte o Query Tool ao database `transparencia` e execute `0_criar_banco.sql`. A criação do database é separada porque o PostgreSQL não permite executar `CREATE DATABASE` dentro de uma transação nem trocar a conexão de database no meio de um script SQL comum.

### 6.2 Criar as tabelas

Abra `0_criar_banco.sql` e execute a criação das oito tabelas no banco `transparencia`.

São criadas:

**Raw**
- `raw_viagem`
- `raw_pagamento`
- `raw_passagem`
- `raw_trecho`

**Silver**
- `silver_viagem`
- `silver_pagamento`
- `silver_passagem`
- `silver_trecho`

A Raw mantém todas as colunas dos CSVs como `VARCHAR`. A Silver aplica os tipos especificados no dicionário da atividade.

## 7. Preparação no VSCode

Crie um ambiente virtual e instale as dependências:

```bash
python -m venv .venv
```

No Windows:

```bash
.venv\Scripts\activate
```

Instale:

```bash
pip install -r requirements.txt
```

Copie `.env.example` para `.env` e preencha a senha do PostgreSQL. O exemplo já contém o ID do ZIP oficial no Google Drive. Os dados locais são ignorados pelo Git e não acompanham o repositório; após clonar, o script baixa o ZIP automaticamente. Se o ZIP já estiver disponível localmente, coloque-o em `data/viagens_2025_6meses.zip`; nesse caso o script usa o arquivo local.

## 8. Execução do pipeline

### Fase 1 — Raw

No terminal integrado do VSCode:

```bash
python 1_extrair.py
```

O script:

- utiliza o ZIP em `data/` quando ele está disponível; caso contrário, baixa o ZIP oficial do Google Drive usando `DRIVE_FILE_ID` do `.env` (preenchido pelo `.env.example`);
- extrai os quatro CSVs;
- lê os arquivos em blocos de 50.000 registros;
- executa `TRUNCATE` antes da carga, tornando o processo idempotente;
- mantém os valores originais como texto na Raw;
- utiliza `try/except` para tratamento de erros.

### Fase 2 — Silver

```bash
python 2_transformar.py
```

A transformação:

- converte datas `DD/MM/AAAA` para `DATE`;
- converte valores com vírgula decimal para `DECIMAL`;
- calcula `valor_total` como diárias + passagens − devoluções + outros gastos;
- calcula `duracao_dias` pela diferença entre data final e inicial;
- respeita as chaves estrangeiras e as constraints da Silver.

### Fase 3 — Gold e análises

No VSCode, abra `3_analise.ipynb`, selecione o interpretador Python do `.venv` e execute as células em ordem.

O notebook:

- responde às sete perguntas de negócio;
- cria gráficos com títulos e eixos identificados;
- cria a tabela `gold_orgao` e a VIEW `vw_gold_orgao`, agregadas por órgão superior;
- cria a tabela `gold_orgao_pagador` e a VIEW `vw_gold_orgao_pagador`, agregadas pelo órgão pagador efetivo;
- cria as agregações `gold_tipo_pagamento`, `gold_transporte` e `gold_uf_destino`, cada uma acompanhada de VIEW;
- responde às perguntas 4, 5 e 6 por meio das VIEWs Gold agregadas e evita confundir órgão superior com órgão pagador.

## 9. Validação pelo pgAdmin

Depois de executar as fases 1 e 2 e o notebook, execute `4_validacao_pgadmin.sql` no pgAdmin.

A validação verifica:

- quantidade de registros em Raw e Silver;
- integridade referencial das FK;
- ausência de valores negativos proibidos;
- unicidade de `(id_viagem, sequencia_trecho)`;
- tipos das colunas Silver;
- constraints cadastradas;
- existência das tabelas e VIEWs Gold, inclusive as agregações das perguntas 4, 5 e 6.

## 10. Boas práticas

- Credenciais ficam exclusivamente em `.env`.
- `.env`, ZIPs e CSVs estão no `.gitignore`.
- O código é separado por etapa do pipeline.
- A carga Raw é idempotente.
- A transformação ocorre no PostgreSQL, preservando a Raw.
- Os pagamentos associados às viagens são agregados por viagem antes da consolidação de custo por órgão superior, evitando multiplicação de valores em JOINs; o total pago por órgão pagador é calculado separadamente a partir dos registros de pagamento.

## 11. Possíveis melhorias

- Automatizar execução periódica do pipeline.
- Adicionar testes automatizados de qualidade de dados.
- Registrar logs estruturados de execução.
- Criar monitoramento de volume e alterações na fonte.
- Evoluir a camada Gold para indicadores temporais e painéis interativos.

## 12. Conclusão

A solução implementa um pipeline completo de dados com separação entre ingestão, tratamento e análise. A arquitetura preserva a rastreabilidade da fonte na Raw, aplica tipagem e integridade relacional na Silver e disponibiliza indicadores agregados na Gold para responder às perguntas de negócio propostas.
