-- ================================================================
-- VALIDAÇÃO FINAL NO pgAdmin 4
-- Execute conectado ao banco transparencia.
-- ================================================================

-- 1. Quantidade de registros em cada camada
SELECT 'raw_viagem' AS tabela, COUNT(*) AS registros FROM raw_viagem
UNION ALL SELECT 'raw_pagamento', COUNT(*) FROM raw_pagamento
UNION ALL SELECT 'raw_passagem', COUNT(*) FROM raw_passagem
UNION ALL SELECT 'raw_trecho', COUNT(*) FROM raw_trecho
UNION ALL SELECT 'silver_viagem', COUNT(*) FROM silver_viagem
UNION ALL SELECT 'silver_pagamento', COUNT(*) FROM silver_pagamento
UNION ALL SELECT 'silver_passagem', COUNT(*) FROM silver_passagem
UNION ALL SELECT 'silver_trecho', COUNT(*) FROM silver_trecho
ORDER BY tabela;

-- 2. Integridade referencial: todas devem retornar 0.
SELECT COUNT(*) AS pagamentos_sem_viagem
FROM silver_pagamento p LEFT JOIN silver_viagem v ON v.id_viagem = p.id_viagem
WHERE v.id_viagem IS NULL;

SELECT COUNT(*) AS passagens_sem_viagem
FROM silver_passagem p LEFT JOIN silver_viagem v ON v.id_viagem = p.id_viagem
WHERE v.id_viagem IS NULL;

SELECT COUNT(*) AS trechos_sem_viagem
FROM silver_trecho t LEFT JOIN silver_viagem v ON v.id_viagem = t.id_viagem
WHERE v.id_viagem IS NULL;

-- 3. Valores negativos: todas devem retornar 0.
SELECT COUNT(*) AS diarias_negativas FROM silver_viagem WHERE valor_diarias < 0;
SELECT COUNT(*) AS pagamentos_negativos FROM silver_pagamento WHERE valor < 0;
SELECT COUNT(*) AS passagens_negativas FROM silver_passagem WHERE valor_passagem < 0;
SELECT COUNT(*) AS taxas_negativas FROM silver_passagem WHERE taxa_servico < 0;
SELECT COUNT(*) AS trecho_diarias_negativas FROM silver_trecho WHERE numero_diarias < 0;

-- 4. Duplicidade proibida pela UNIQUE: deve retornar 0.
SELECT COUNT(*) - COUNT(DISTINCT (id_viagem, sequencia_trecho)) AS duplicidades_trecho
FROM silver_trecho;

-- 5. Tipos das colunas Silver exigidas pela rubrica.
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_name IN ('silver_viagem','silver_pagamento','silver_passagem','silver_trecho')
ORDER BY table_name, ordinal_position;

-- 6. Constraints declaradas nas tabelas Silver.
SELECT conrelid::regclass AS tabela, conname AS constraint, contype AS tipo
FROM pg_constraint
WHERE conrelid::regclass::text IN ('silver_viagem','silver_pagamento','silver_passagem','silver_trecho')
ORDER BY 1, 2;

-- 7. Camada Gold: tabela e VIEW devem existir depois da execução do notebook.
SELECT table_name
FROM information_schema.tables
WHERE table_name IN ('gold_orgao', 'gold_orgao_pagador', 'gold_tipo_pagamento', 'gold_transporte', 'gold_uf_destino');

SELECT table_name, table_type
FROM information_schema.views
WHERE table_name IN ('vw_gold_orgao', 'vw_gold_orgao_pagador', 'vw_gold_tipo_pagamento', 'vw_gold_transporte', 'vw_gold_uf_destino');

-- 8. Conferência das respostas de negócio gravadas na Gold.
SELECT * FROM gold_orgao ORDER BY custo_total DESC LIMIT 5;


-- 9. Órgão pagador efetivo (a maior soma deve coincidir com a pergunta 7).
SELECT * FROM vw_gold_orgao_pagador ORDER BY total_pago DESC LIMIT 5;

SELECT * FROM vw_gold_tipo_pagamento ORDER BY valor_medio DESC LIMIT 5;
SELECT * FROM vw_gold_transporte ORDER BY quantidade_trechos DESC LIMIT 5;
SELECT * FROM vw_gold_uf_destino ORDER BY quantidade_trechos DESC LIMIT 5;
