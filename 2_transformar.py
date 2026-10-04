"""Fase 2: transformação Raw -> Silver no PostgreSQL."""

from banco import conectar

SQL_TRANSFORMACAO = """
TRUNCATE TABLE silver_trecho, silver_passagem, silver_pagamento, silver_viagem
RESTART IDENTITY;

INSERT INTO silver_viagem (
    id_viagem, num_proposta, situacao, viagem_urgente, cod_orgao_superior,
    nome_orgao_superior, nome_viajante, cargo, data_inicio, data_fim,
    destinos, motivo, valor_diarias, valor_passagens, valor_devolucao,
    valor_outros_gastos, valor_total, duracao_dias
)
SELECT
    TRIM(id_viagem),
    NULLIF(TRIM(num_proposta), ''),
    NULLIF(TRIM(situacao), ''),
    NULLIF(TRIM(viagem_urgente), ''),
    NULLIF(TRIM(cod_orgao_superior), ''),
    TRIM(nome_orgao_superior),
    NULLIF(TRIM(nome_viajante), ''),
    NULLIF(TRIM(cargo), ''),
    to_date(NULLIF(TRIM(data_inicio), ''), 'DD/MM/YYYY'),
    to_date(NULLIF(TRIM(data_fim), ''), 'DD/MM/YYYY'),
    NULLIF(TRIM(destinos), ''),
    NULLIF(TRIM(motivo), ''),
    COALESCE(NULLIF(REPLACE(TRIM(valor_diarias), ',', '.'), '')::DECIMAL(10,2), 0),
    COALESCE(NULLIF(REPLACE(TRIM(valor_passagens), ',', '.'), '')::DECIMAL(10,2), 0),
    COALESCE(NULLIF(REPLACE(TRIM(valor_devolucao), ',', '.'), '')::DECIMAL(10,2), 0),
    COALESCE(NULLIF(REPLACE(TRIM(valor_outros_gastos), ',', '.'), '')::DECIMAL(10,2), 0),
    (
        COALESCE(NULLIF(REPLACE(TRIM(valor_diarias), ',', '.'), '')::DECIMAL(10,2), 0)
        + COALESCE(NULLIF(REPLACE(TRIM(valor_passagens), ',', '.'), '')::DECIMAL(10,2), 0)
        - COALESCE(NULLIF(REPLACE(TRIM(valor_devolucao), ',', '.'), '')::DECIMAL(10,2), 0)
        + COALESCE(NULLIF(REPLACE(TRIM(valor_outros_gastos), ',', '.'), '')::DECIMAL(10,2), 0)
    )::DECIMAL(12,2),
    (to_date(NULLIF(TRIM(data_fim), ''), 'DD/MM/YYYY')
     - to_date(NULLIF(TRIM(data_inicio), ''), 'DD/MM/YYYY'))::INT
FROM raw_viagem;

INSERT INTO silver_pagamento (
    id_viagem, num_proposta, nome_orgao_pagador, nome_ug_pagadora,
    tipo_pagamento, valor
)
SELECT
    TRIM(id_viagem),
    NULLIF(TRIM(num_proposta), ''),
    NULLIF(TRIM(nome_orgao_pagador), ''),
    NULLIF(TRIM(nome_unidade_gestora_pagadora), ''),
    TRIM(tipo_pagamento),
    COALESCE(NULLIF(REPLACE(TRIM(valor), ',', '.'), '')::DECIMAL(10,2), 0)
FROM raw_pagamento;

INSERT INTO silver_passagem (
    id_viagem, meio_transporte, pais_origem_ida, uf_origem_ida,
    cidade_origem_ida, pais_destino_ida, uf_destino_ida, cidade_destino_ida,
    valor_passagem, taxa_servico, data_emissao
)
SELECT
    TRIM(id_viagem),
    NULLIF(TRIM(meio_transporte), ''),
    NULLIF(TRIM(pais_origem_ida), ''),
    NULLIF(TRIM(uf_origem_ida), ''),
    NULLIF(TRIM(cidade_origem_ida), ''),
    NULLIF(TRIM(pais_destino_ida), ''),
    NULLIF(TRIM(uf_destino_ida), ''),
    NULLIF(TRIM(cidade_destino_ida), ''),
    COALESCE(NULLIF(REPLACE(TRIM(valor_passagem), ',', '.'), '')::DECIMAL(10,2), 0),
    COALESCE(NULLIF(REPLACE(TRIM(taxa_servico), ',', '.'), '')::DECIMAL(10,2), 0),
    to_date(NULLIF(TRIM(data_emissao), ''), 'DD/MM/YYYY')
FROM raw_passagem;

INSERT INTO silver_trecho (
    id_viagem, sequencia_trecho, origem_data, origem_uf, origem_cidade,
    destino_data, destino_uf, destino_cidade, meio_transporte, numero_diarias
)
SELECT
    TRIM(id_viagem),
    NULLIF(TRIM(sequencia_trecho), '')::INT,
    to_date(NULLIF(TRIM(origem_data), ''), 'DD/MM/YYYY'),
    NULLIF(TRIM(origem_uf), ''),
    NULLIF(TRIM(origem_cidade), ''),
    to_date(NULLIF(TRIM(destino_data), ''), 'DD/MM/YYYY'),
    NULLIF(TRIM(destino_uf), ''),
    NULLIF(TRIM(destino_cidade), ''),
    NULLIF(TRIM(meio_transporte), ''),
    COALESCE(NULLIF(REPLACE(TRIM(numero_diarias), ',', '.'), '')::DECIMAL(10,2), 0)
FROM raw_trecho;
"""


def main():
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            cursor.execute(SQL_TRANSFORMACAO)
        conexao.commit()
        print("Transformação Raw -> Silver concluída com sucesso.")
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


if __name__ == "__main__":
    main()
