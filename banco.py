"""Funções de acesso ao PostgreSQL usadas pelo pipeline."""

import psycopg2
from psycopg2 import Error
from psycopg2.extras import execute_values

from config import POSTGRES_CONFIG


def conectar():
    """Abre uma conexão com o PostgreSQL configurado no .env."""
    try:
        return psycopg2.connect(**POSTGRES_CONFIG)
    except Error as erro:
        raise RuntimeError(
            "Não foi possível conectar ao PostgreSQL em "
            f"{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']} / "
            f"database '{POSTGRES_CONFIG['dbname']}'. "
            "Verifique o .env e se o PostgreSQL está em execução. "
            f"Detalhe: {erro}"
        ) from erro


def executar(conexao, sql):
    """Executa um comando SQL e confirma a transação."""
    with conexao.cursor() as cursor:
        cursor.execute(sql)
    conexao.commit()


def inserir_em_lote(conexao, sql_insert, linhas, page_size=5000):
    """Insere uma lista de tuplas em lotes eficientes."""
    if not linhas:
        return
    with conexao.cursor() as cursor:
        execute_values(cursor, sql_insert, linhas, page_size=page_size)


def contar(conexao, tabela):
    """Retorna a quantidade de registros de uma tabela."""
    with conexao.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) FROM {tabela};")
        return cursor.fetchone()[0]
