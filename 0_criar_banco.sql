-- ================================================================
-- PROJETO MÓDULO 1 - ANÁLISE DE DADOS COM PYTHON
-- PostgreSQL | Arquitetura Medallion: Raw -> Silver -> Gold
-- ================================================================
-- EXECUÇÃO NO pgAdmin 4
-- 1) Conecte-se ao banco padrão (postgres) e execute SOMENTE:
--      CREATE DATABASE transparencia;
-- 2) Conecte-se ao banco "transparencia" e execute o restante deste arquivo.
--
-- O bloco abaixo não deve ser executado na conexão "postgres".
-- ================================================================

-- Opcional para uma nova execução do projeto: recria as tabelas.
DROP TABLE IF EXISTS silver_trecho CASCADE;
DROP TABLE IF EXISTS silver_passagem CASCADE;
DROP TABLE IF EXISTS silver_pagamento CASCADE;
DROP TABLE IF EXISTS silver_viagem CASCADE;
DROP TABLE IF EXISTS raw_trecho CASCADE;
DROP TABLE IF EXISTS raw_passagem CASCADE;
DROP TABLE IF EXISTS raw_pagamento CASCADE;
DROP TABLE IF EXISTS raw_viagem CASCADE;

-- ================================================================
-- CAMADA RAW: cópia fiel do CSV. Todas as colunas são VARCHAR.
-- Não são aplicadas PK, FK, NOT NULL ou CHECK nesta camada.
-- ================================================================

CREATE TABLE raw_viagem (
    id_viagem VARCHAR(255),
    num_proposta VARCHAR(255),
    situacao VARCHAR(255),
    viagem_urgente VARCHAR(255),
    justificativa_urgencia_viagem VARCHAR(255),
    cod_orgao_superior VARCHAR(255),
    nome_orgao_superior VARCHAR(255),
    cod_orgao_solicitante VARCHAR(255),
    nome_orgao_solicitante VARCHAR(255),
    cpf_viajante VARCHAR(255),
    nome_viajante VARCHAR(255),
    cargo VARCHAR(255),
    funcao VARCHAR(255),
    descricao_funcao VARCHAR(255),
    data_inicio VARCHAR(255),
    data_fim VARCHAR(255),
    destinos VARCHAR(4000),
    motivo VARCHAR(4000),
    valor_diarias VARCHAR(255),
    valor_passagens VARCHAR(255),
    valor_devolucao VARCHAR(255),
    valor_outros_gastos VARCHAR(255)
);

CREATE TABLE raw_pagamento (
    id_viagem VARCHAR(255),
    num_proposta VARCHAR(255),
    cod_orgao_superior VARCHAR(255),
    nome_orgao_superior VARCHAR(255),
    cod_orgao_pagador VARCHAR(255),
    nome_orgao_pagador VARCHAR(255),
    cod_unidade_gestora_pagadora VARCHAR(255),
    nome_unidade_gestora_pagadora VARCHAR(255),
    tipo_pagamento VARCHAR(255),
    valor VARCHAR(255)
);

CREATE TABLE raw_passagem (
    id_viagem VARCHAR(255),
    num_proposta VARCHAR(255),
    meio_transporte VARCHAR(255),
    pais_origem_ida VARCHAR(255),
    uf_origem_ida VARCHAR(255),
    cidade_origem_ida VARCHAR(255),
    pais_destino_ida VARCHAR(255),
    uf_destino_ida VARCHAR(255),
    cidade_destino_ida VARCHAR(255),
    pais_origem_volta VARCHAR(255),
    uf_origem_volta VARCHAR(255),
    cidade_origem_volta VARCHAR(255),
    pais_destino_volta VARCHAR(255),
    uf_destino_volta VARCHAR(255),
    cidade_destino_volta VARCHAR(255),
    valor_passagem VARCHAR(255),
    taxa_servico VARCHAR(255),
    data_emissao VARCHAR(255),
    hora_emissao VARCHAR(255)
);

CREATE TABLE raw_trecho (
    id_viagem VARCHAR(255),
    num_proposta VARCHAR(255),
    sequencia_trecho VARCHAR(255),
    origem_data VARCHAR(255),
    origem_pais VARCHAR(255),
    origem_uf VARCHAR(255),
    origem_cidade VARCHAR(255),
    destino_data VARCHAR(255),
    destino_pais VARCHAR(255),
    destino_uf VARCHAR(255),
    destino_cidade VARCHAR(255),
    meio_transporte VARCHAR(255),
    numero_diarias VARCHAR(255),
    missao VARCHAR(255)
);

-- ================================================================
-- CAMADA SILVER: dados tipados + PK/FK + duas constraints extras
-- por tabela, conforme a rubrica.
-- ================================================================

CREATE TABLE silver_viagem (
    id_viagem VARCHAR(20) PRIMARY KEY,
    num_proposta VARCHAR(20),
    situacao VARCHAR(50),
    viagem_urgente VARCHAR(5),
    cod_orgao_superior VARCHAR(20),
    nome_orgao_superior VARCHAR(255) NOT NULL,
    nome_viajante VARCHAR(255),
    cargo VARCHAR(255),
    data_inicio DATE,
    data_fim DATE,
    destinos VARCHAR(4000),
    motivo VARCHAR(4000),
    valor_diarias DECIMAL(10,2) CONSTRAINT ck_silver_viagem_valor_diarias CHECK (valor_diarias >= 0),
    valor_passagens DECIMAL(10,2),
    valor_devolucao DECIMAL(10,2),
    valor_outros_gastos DECIMAL(10,2),
    valor_total DECIMAL(12,2),
    duracao_dias INT,
);

CREATE TABLE silver_pagamento (
    id_pagamento SERIAL PRIMARY KEY,
    id_viagem VARCHAR(20) NOT NULL,
    num_proposta VARCHAR(20),
    nome_orgao_pagador VARCHAR(255),
    nome_ug_pagadora VARCHAR(255),
    tipo_pagamento VARCHAR(50) NOT NULL,
    valor DECIMAL(10,2) CONSTRAINT ck_silver_pagamento_valor CHECK (valor >= 0),
    CONSTRAINT fk_silver_pagamento_viagem FOREIGN KEY (id_viagem) REFERENCES silver_viagem(id_viagem)
);

CREATE TABLE silver_passagem (
    id_passagem SERIAL PRIMARY KEY,
    id_viagem VARCHAR(20) NOT NULL,
    meio_transporte VARCHAR(50),
    pais_origem_ida VARCHAR(60),
    uf_origem_ida VARCHAR(40),
    cidade_origem_ida VARCHAR(80),
    pais_destino_ida VARCHAR(60),
    uf_destino_ida VARCHAR(40),
    cidade_destino_ida VARCHAR(80),
    valor_passagem DECIMAL(10,2) CONSTRAINT ck_silver_passagem_valor CHECK (valor_passagem >= 0),
    taxa_servico DECIMAL(10,2) CONSTRAINT ck_silver_passagem_taxa CHECK (taxa_servico >= 0),
    data_emissao DATE,
    CONSTRAINT fk_silver_passagem_viagem FOREIGN KEY (id_viagem) REFERENCES silver_viagem(id_viagem)
);

CREATE TABLE silver_trecho (
    id_trecho SERIAL PRIMARY KEY,
    id_viagem VARCHAR(20) NOT NULL,
    sequencia_trecho INT,
    origem_data DATE,
    origem_uf VARCHAR(40),
    origem_cidade VARCHAR(80),
    destino_data DATE,
    destino_uf VARCHAR(40),
    destino_cidade VARCHAR(80),
    meio_transporte VARCHAR(50),
    numero_diarias DECIMAL(10,2) CONSTRAINT ck_silver_trecho_diarias CHECK (numero_diarias >= 0),
    CONSTRAINT fk_silver_trecho_viagem FOREIGN KEY (id_viagem) REFERENCES silver_viagem(id_viagem),
    CONSTRAINT uq_silver_trecho_viagem_sequencia UNIQUE (id_viagem, sequencia_trecho)
);

-- Índices úteis para JOINs e análises Gold.
CREATE INDEX idx_silver_pagamento_id_viagem ON silver_pagamento(id_viagem);
CREATE INDEX idx_silver_passagem_id_viagem ON silver_passagem(id_viagem);
CREATE INDEX idx_silver_trecho_id_viagem ON silver_trecho(id_viagem);
CREATE INDEX idx_silver_trecho_destino_uf ON silver_trecho(destino_uf);
CREATE INDEX idx_silver_viagem_orgao ON silver_viagem(nome_orgao_superior);
