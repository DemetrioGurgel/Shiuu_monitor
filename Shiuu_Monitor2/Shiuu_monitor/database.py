import sqlite3

class BancoDeDados:
    def __init__(self, db_name: str):
        """Inicializa a conexão com o banco de dados e cria as tabelas se não existirem."""
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.create_tables()  # Cria as tabelas ao instanciar a classe

    def create_tables(self):
        """Cria as tabelas no banco de dados se não existirem."""
        try:
            self.connect()  # Conecta ao banco

            #Tabela dos usuários
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                cargo INTEGER NOT NULL,
                senha TEXT NOT NULL
            );
            """)

            # Tabela dos ambientes
            self.cursor.execute("""
                        CREATE TABLE IF NOT EXISTS ambientes (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nome TEXT NOT NULL UNIQUE,
                            dispositivo_id INTEGER NOT NULL,
                            dispositivo_ip TEXT NOT NULL,
                            dispositivo_port INTEGER NOT NULL
                        );
                        """)

            # Tabela dos niveis
            self.cursor.execute("""
                        CREATE TABLE IF NOT EXISTS niveis (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nome TEXT NOT NULL UNIQUE,
                            limite INTEGER NOT NULL,
                            alerta TEXT NOT NULL
                        );
                        """)

            # Tabela do relacionamento entre Usuário e Ambiente
            self.cursor.execute("""
                        CREATE TABLE IF NOT EXISTS usuario_ambientes (
                            id_usuario INTEGER NOT NULL,
                            id_ambiente INTEGER NOT NULL,
                            PRIMARY KEY (id_usuario, id_ambiente),
                            FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE,
                            FOREIGN KEY (id_ambiente) REFERENCES ambientes(id) ON DELETE CASCADE
                        );

                        """)

            # Tabela do relacionamento entre Ambiente e Nivel
            self.cursor.execute("""
                        CREATE TABLE IF NOT EXISTS ambiente_niveis (
                            id_ambiente INTEGER NOT NULL,
                            id_nivel INTEGER NOT NULL,
                            PRIMARY KEY (id_ambiente, id_nivel),
                            FOREIGN KEY (id_ambiente) REFERENCES ambientes(id) ON DELETE CASCADE,
                            FOREIGN KEY (id_nivel) REFERENCES niveis(id) ON DELETE CASCADE
                        );

                        """)

            #Tabela dos Dispositivos
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS dispositivo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dispositivo_ip INTEGER NOT NULL,
                dispositivo_port INTEGER NOT NULL,
                dado_gerado INTEGER NOT NULL,
                hora_envio INTEGER NOT NULL
            );
            """)

            # Inserir usuário admin se ele ainda não existir
            self.cursor.execute("""
            INSERT OR IGNORE INTO usuarios (nome, email, cargo, senha) 
            VALUES ('admin', 'admin', 1, '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918');
            """)
            self.conn.commit()  # Confirma a criação das tabelas
        except sqlite3.Error as e:
            print(f"Erro ao criar tabelas: {e}")
        finally:
            self.close()


    def connect(self):
        """Conecta ao banco de dados."""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def close(self):
        """Fecha a conexão com o banco de dados."""
        if self.conn:
            self.conn.close()

    def execute_query(self, query: str, params: tuple = ()):
        """Executa uma query no banco de dados."""
        try:
            self.connect()  # Conecta ao banco
            self.cursor.execute(query, params)  # Executa a query com parâmetros
            self.conn.commit()  # Confirma as alterações
        except sqlite3.Error as e:
            print(f"Erro ao executar query: {e}")
        finally:
            self.close()  # Fecha a conexão

    def insert(self, table: str, data: dict):
        """Função generalizada para inserção em qualquer tabela."""
        columns = ', '.join(data.keys())  # Extrai as colunas do dicionário
        placeholders = ', '.join(['?'] * len(data))  # Adiciona placeholders (?, ?, ?)
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        try:
            self.connect()  # Conecta ao banco
            self.cursor.execute(query, tuple(data.values()))  # Executa a query com os valores
            self.conn.commit()  # Confirma a inserção
        except sqlite3.Error as e:
            print(f"Erro ao inserir dados: {e}")
        finally:
            self.close()  # Fecha a conexão

    def delete(self, table: str, column: str, data):
        """Função generalizada para inserção em qualquer tabela."""
        query = f"DELETE FROM {table} WHERE {column} = ?"
        try:
            self.connect()  # Conecta ao banco
            self.cursor.execute(query, (data,))  # Executa a query com os valores
            self.conn.commit()  # Confirma a inserção
        except sqlite3.Error as e:
            print(f"Erro ao inserir dados: {e}")
        finally:
            self.close()  # Fecha a conexão

    def update(self, table: str, columnedit: str, column: str, dataedit, data):
        """Função generalizada para inserção em qualquer tabela."""
        query = f"UPDATE {table} SET {columnedit} = ? WHERE {column} = ?"
        try:
            self.connect()  # Conecta ao banco
            self.cursor.execute(query, (dataedit, data,))  # Executa a query com os valores
            self.conn.commit()  # Confirma a inserção
        except sqlite3.Error as e:
            print(f"Erro ao inserir dados: {e}")
        finally:
            self.close()  # Fecha a conexão

    def fetch_all(self, table):
        """Executa uma query de seleção e retorna os resultados como uma lista de dicionários."""
        query = f"SELECT * FROM {table}"
        try:
            self.connect()
            self.cursor.row_factory = sqlite3.Row  # Configura o cursor para retornar os dados como dicionários
            self.cursor.execute(query)
            rows = self.cursor.fetchall()

            # Converte cada linha em um dicionário
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Erro ao buscar dados: {e}")
            return []
        finally:
            self.close()

    def fetch_one(self, table, column, data=None):
        """Executa uma query de seleção e retorna um único resultado."""
        query = f"SELECT * FROM {table} WHERE {column} = ?"
        try:
            self.connect()
            self.cursor.execute(query, (data,))
            result = self.cursor.fetchone()
            if result:
                # Cria um dicionário associando os nomes das colunas aos valores
                columns = [description[0] for description in self.cursor.description]
                return dict(zip(columns, result))  # Cria um dicionário
            return None
        except sqlite3.Error as e:
            print(f"Erro ao buscar dado: {e}")
        finally:
            self.close()


