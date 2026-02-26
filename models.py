import sqlite3
import os
from datetime import datetime, date

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ponto.db')


def get_db():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Initialize the database with all tables."""
    conn = get_db()
    cursor = conn.cursor()

    # Tabela de colaboradores (horário flexível)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS colaboradores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT DEFAULT '',
            cargo TEXT DEFAULT '',
            departamento TEXT DEFAULT '',
            primeiro_acesso INTEGER DEFAULT 1,
            max_horas_semana REAL DEFAULT 40.0,
            horas_dia_normal REAL DEFAULT 8.0,
            horas_dia_especial REAL DEFAULT 6.0,
            folgas_semana INTEGER DEFAULT 2,
            is_gestor INTEGER DEFAULT 0,
            ativo INTEGER DEFAULT 1,
            data_cadastro TEXT DEFAULT (datetime('now', 'localtime'))
        )
    ''')

    # Tabela de registros de ponto
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registros_ponto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            colaborador_id INTEGER NOT NULL,
            data TEXT NOT NULL,
            entrada TEXT,
            saida_almoco TEXT,
            retorno_almoco TEXT,
            saida TEXT,
            horas_trabalhadas REAL DEFAULT 0,
            tipo_dia TEXT DEFAULT 'normal',
            status TEXT DEFAULT 'incompleto',
            observacao TEXT DEFAULT '',
            FOREIGN KEY (colaborador_id) REFERENCES colaboradores(id),
            UNIQUE(colaborador_id, data)
        )
    ''')

    # Tabela de justificativas (atestados, faltas)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS justificativas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            colaborador_id INTEGER NOT NULL,
            data_inicio TEXT NOT NULL,
            data_fim TEXT NOT NULL,
            tipo TEXT NOT NULL,
            descricao TEXT DEFAULT '',
            arquivo_atestado TEXT DEFAULT '',
            dias INTEGER DEFAULT 1,
            status TEXT DEFAULT 'pendente',
            aprovado_por INTEGER,
            data_aprovacao TEXT,
            data_registro TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (colaborador_id) REFERENCES colaboradores(id),
            FOREIGN KEY (aprovado_por) REFERENCES colaboradores(id)
        )
    ''')

    # Tabela de feriados
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feriados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT UNIQUE NOT NULL,
            descricao TEXT DEFAULT ''
        )
    ''')

    # Tabela de configurações do sistema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracoes (
            chave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
        )
    ''')

    # Inserir configurações padrão
    configs_padrao = [
        ('tolerancia_minutos', '10'),
        ('nome_empresa', 'Piticas'),
    ]
    for chave, valor in configs_padrao:
        cursor.execute('''
            INSERT OR IGNORE INTO configuracoes (chave, valor) VALUES (?, ?)
        ''', (chave, valor))

    # Inserir feriados nacionais de 2026
    feriados_2026 = [
        ('2026-01-01', 'Confraternização Universal'),
        ('2026-02-16', 'Carnaval'),
        ('2026-02-17', 'Carnaval'),
        ('2026-04-03', 'Sexta-feira Santa'),
        ('2026-04-21', 'Tiradentes'),
        ('2026-05-01', 'Dia do Trabalho'),
        ('2026-06-04', 'Corpus Christi'),
        ('2026-09-07', 'Independência do Brasil'),
        ('2026-10-12', 'Nossa Sra. Aparecida'),
        ('2026-11-02', 'Finados'),
        ('2026-11-15', 'Proclamação da República'),
        ('2026-12-25', 'Natal'),
    ]
    for dt, desc in feriados_2026:
        cursor.execute('''
            INSERT OR IGNORE INTO feriados (data, descricao) VALUES (?, ?)
        ''', (dt, desc))

    # Criar gestor padrão (admin/admin123)
    cursor.execute("SELECT id FROM colaboradores WHERE email = 'admin@empresa.com'")
    if not cursor.fetchone():
        from werkzeug.security import generate_password_hash
        cursor.execute('''
            INSERT INTO colaboradores (nome, email, senha, cargo, is_gestor, primeiro_acesso)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            'Administrador',
            'admin@empresa.com',
            generate_password_hash('admin123'),
            'Gestor',
            1,
            0
        ))

    conn.commit()
    conn.close()
    print("Banco de dados inicializado com sucesso!")
    print("Usuário padrão: admin@empresa.com / admin123")


if __name__ == '__main__':
    init_db()
