import psycopg2

class InsertInfo: # Содержит информацию о названии таблицы и столбцов
    def __init__(self, table: str, rows: str):
        self.table = table
        self.rows = rows

class DBWorker: # Нужен для работы с базой данных
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

        self.connection = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )

        self.cursor = self.connection.cursor()
    
    def Select(self, rows: str, table: str): # Выбрать все строки
        self.cursor.execute(f'SELECT {rows} FROM {table}')
        self.connection.commit()
        return self.cursor.fetchall()
    
    def SelectBy(self, rows: str, table: str, by: str, value: str): # Выбрать все строки у которых в столбце by значение value
        self.cursor.execute(f'SELECT {rows} FROM {table} WHERE \"{by}\"=%s;', (value,))
        self.connection.commit()
        return self.cursor.fetchall()
    
    def Insert(self, insertInfo: InsertInfo, values: str): # Вставить новую строку
        self.cursor.execute(f'INSERT INTO {insertInfo.table} ({insertInfo.rows}) VALUES ({values});')
        self.connection.commit()

class User:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

class Users:
    def __init__(self):
        self.users = {}
    
    def Add(self, user: User):
        if (self.Contain(user.id)):
            raise ValueError(f"User with id='{user.id} already exists'")
        
        self.users[user.id] = user
    
    def TryAdd(self, user: User):
        if (self.ContainById(user.id) == False):
            self.users[user.id] = user
    
    def Remove(self, user):
        self.users.pop(user)

    def Get(self, id: int):
        return self.users.get(id).name

    def Contain(self, id: int):
        return id in self.users