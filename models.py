import sqlite3
import os
from datetime import datetime, date

DATA_DIR = os.environ.get('DATA_DIR', os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(DATA_DIR, 'ponto.db')


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

    # Tabela de lojas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lojas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            endereco TEXT DEFAULT '',
            ativo INTEGER DEFAULT 1
        )
    ''')

    # Tabela de colaboradores (horário flexível)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS colaboradores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT DEFAULT '',
            cargo TEXT DEFAULT '',
            departamento TEXT DEFAULT '',
            loja_id INTEGER,
            primeiro_acesso INTEGER DEFAULT 1,
            max_horas_semana REAL DEFAULT 40.0,
            horas_dia_normal REAL DEFAULT 8.0,
            horas_dia_especial REAL DEFAULT 6.0,
            folgas_semana INTEGER DEFAULT 2,
            is_gestor INTEGER DEFAULT 0,
            ativo INTEGER DEFAULT 1,
            data_cadastro TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (loja_id) REFERENCES lojas(id)
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
            editado_por INTEGER,
            editado_em TEXT,
            motivo_edicao TEXT DEFAULT '',
            FOREIGN KEY (colaborador_id) REFERENCES colaboradores(id),
            FOREIGN KEY (editado_por) REFERENCES colaboradores(id),
            UNIQUE(colaborador_id, data)
        )
    ''')

    # Tabela de histórico de edições (audit trail)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico_edicoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            registro_id INTEGER NOT NULL,
            colaborador_id INTEGER NOT NULL,
            editado_por INTEGER NOT NULL,
            data_edicao TEXT NOT NULL,
            acao TEXT NOT NULL,
            campo TEXT,
            valor_anterior TEXT,
            valor_novo TEXT,
            motivo TEXT DEFAULT '',
            FOREIGN KEY (registro_id) REFERENCES registros_ponto(id),
            FOREIGN KEY (colaborador_id) REFERENCES colaboradores(id),
            FOREIGN KEY (editado_por) REFERENCES colaboradores(id)
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

    # Tabela de banco de horas (acumulado mensal)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS banco_horas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            colaborador_id INTEGER NOT NULL,
            mes TEXT NOT NULL,
            horas_trabalhadas REAL DEFAULT 0,
            horas_justificadas REAL DEFAULT 0,
            horas_esperadas REAL DEFAULT 0,
            saldo REAL DEFAULT 0,
            fechado INTEGER DEFAULT 0,
            FOREIGN KEY (colaborador_id) REFERENCES colaboradores(id),
            UNIQUE(colaborador_id, mes)
        )
    ''')

    # Migração: adicionar loja_id em colaboradores se não existir
    try:
        cursor.execute("SELECT loja_id FROM colaboradores LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE colaboradores ADD COLUMN loja_id INTEGER REFERENCES lojas(id)")

    # Migração: adicionar colunas de auditoria em registros_ponto se não existirem
    for col, coldef in [('editado_por', 'INTEGER'), ('editado_em', 'TEXT'), ('motivo_edicao', 'TEXT DEFAULT \'\' ')]:
        try:
            cursor.execute(f"SELECT {col} FROM registros_ponto LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute(f"ALTER TABLE registros_ponto ADD COLUMN {col} {coldef}")

    # Migração: criar tabela historico_edicoes se não existir (já criada acima pelo CREATE IF NOT EXISTS)

    # Inserir loja padrão se não existir nenhuma
    cursor.execute("SELECT id FROM lojas LIMIT 1")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO lojas (nome, endereco) VALUES (?, ?)",
                       ('Loja Principal', 'Endereço da loja'))

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
