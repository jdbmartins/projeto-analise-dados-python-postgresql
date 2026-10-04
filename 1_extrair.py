"""Fase 1: download, extração e carga fiel dos quatro CSVs na camada Raw."""

import csv
import zipfile
from pathlib import Path

import gdown

from banco import conectar, inserir_em_lote
from config import ARQUIVOS, CSV_ENCODING, CSV_SEPARADOR, DRIVE_FILE_ID, PASTA_DADOS, TAMANHO_BLOCO


COLUNAS_RAW = {
    "viagem": [
        "id_viagem", "num_proposta", "situacao", "viagem_urgente",
        "justificativa_urgencia_viagem", "cod_orgao_superior",
        "nome_orgao_superior", "cod_orgao_solicitante",
        "nome_orgao_solicitante", "cpf_viajante", "nome_viajante", "cargo",
        "funcao", "descricao_funcao", "data_inicio", "data_fim", "destinos",
        "motivo", "valor_diarias", "valor_passagens", "valor_devolucao",
        "valor_outros_gastos",
    ],
    "pagamento": [
        "id_viagem", "num_proposta", "cod_orgao_superior", "nome_orgao_superior",
        "cod_orgao_pagador", "nome_orgao_pagador", "cod_unidade_gestora_pagadora",
        "nome_unidade_gestora_pagadora", "tipo_pagamento", "valor",
    ],
    "passagem": [
        "id_viagem", "num_proposta", "meio_transporte", "pais_origem_ida",
        "uf_origem_ida", "cidade_origem_ida", "pais_destino_ida", "uf_destino_ida",
        "cidade_destino_ida", "pais_origem_volta", "uf_origem_volta",
        "cidade_origem_volta", "pais_destino_volta", "uf_destino_volta",
        "cidade_destino_volta", "valor_passagem", "taxa_servico", "data_emissao",
        "hora_emissao",
    ],
    "trecho": [
        "id_viagem", "num_proposta", "sequencia_trecho", "origem_data", "origem_pais",
        "origem_uf", "origem_cidade", "destino_data", "destino_pais", "destino_uf",
        "destino_cidade", "meio_transporte", "numero_diarias", "missao",
    ],
}


def baixar_zip():
    """Baixa o ZIP do Google Drive somente quando ele ainda não está localmente."""
    PASTA_DADOS.mkdir(parents=True, exist_ok=True)
    destino = PASTA_DADOS / "viagens_2025_6meses.zip"

    if destino.exists() and destino.stat().st_size > 0:
        print(f"ZIP local encontrado: {destino}")
        return destino

    if not DRIVE_FILE_ID or DRIVE_FILE_ID == "COLE_AQUI_O_ID_DO_ARQUIVO_NO_DRIVE":
        raise RuntimeError(
            "DRIVE_FILE_ID não configurado em config.py. "
            "Cole o ID do arquivo do Google Drive para permitir o download automático."
        )

    url = f"https://drive.google.com/uc?id={DRIVE_FILE_ID}"
    print("Baixando o ZIP do Google Drive...")
    caminho = gdown.download(url, str(destino), quiet=False)
    if not caminho:
        raise RuntimeError("Falha no download do arquivo do Google Drive.")
    return Path(caminho)


def extrair_csvs(caminho_zip):
    """Extrai os quatro CSVs para data/extraido e retorna seus caminhos."""
    pasta = PASTA_DADOS / "extraido"
    pasta.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(caminho_zip) as arquivo_zip:
        nomes = set(arquivo_zip.namelist())
        esperados = {item["csv"] for item in ARQUIVOS.values()}
        faltantes = esperados - nomes
        if faltantes:
            raise RuntimeError(f"CSV(s) ausente(s) no ZIP: {sorted(faltantes)}")
        for nome in esperados:
            arquivo_zip.extract(nome, pasta)
    return {chave: pasta / item["csv"] for chave, item in ARQUIVOS.items()}


def carregar_raw(conexao, tipo, caminho_csv):
    """Lê um CSV em blocos e insere o conteúdo sem alterar seus valores."""
    tabela = ARQUIVOS[tipo]["tabela_raw"]
    colunas = COLUNAS_RAW[tipo]
    placeholders = ", ".join(["%s"] * len(colunas))
    sql = f"INSERT INTO {tabela} ({', '.join(colunas)}) VALUES %s"

    total = 0
    with open(caminho_csv, "r", encoding=CSV_ENCODING, newline="") as arquivo:
        leitor = csv.reader(arquivo, delimiter=CSV_SEPARADOR)
        cabecalho = next(leitor)
        bloco = []
        for numero_linha, linha in enumerate(leitor, start=2):
            if len(linha) != len(colunas):
                raise ValueError(
                    f"{caminho_csv.name}: linha {numero_linha} possui "
                    f"{len(linha)} campos; esperado {len(colunas)}."
                )
            bloco.append(tuple(linha))
            if len(bloco) >= TAMANHO_BLOCO:
                inserir_em_lote(conexao, sql, bloco)
                total += len(bloco)
                bloco.clear()
                print(f"  {tabela}: {total:,} registros")
        if bloco:
            inserir_em_lote(conexao, sql, bloco)
            total += len(bloco)

    return total


def main():
    try:
        caminho_zip = baixar_zip()
        csvs = extrair_csvs(caminho_zip)
        conexao = conectar()
        try:
            # Idempotência: uma nova execução sempre começa com Raw vazia.
            with conexao.cursor() as cursor:
                cursor.execute(
                    "TRUNCATE TABLE raw_pagamento, raw_passagem, raw_trecho, raw_viagem;"
                )
            conexao.commit()

            for tipo in ("viagem", "pagamento", "passagem", "trecho"):
                print(f"Carregando {tipo}...")
                total = carregar_raw(conexao, tipo, csvs[tipo])
                conexao.commit()
                print(f"OK: {total:,} registros em {ARQUIVOS[tipo]['tabela_raw']}.\n")
        finally:
            conexao.close()
    except Exception as erro:
        print(f"ERRO na extração/carga Raw: {erro}")
        raise


if __name__ == "__main__":
    main()
