import psycopg2

class InsertInfo: # Содержит информацию о названии таблицы и столбцов
    def __init__(self, table: str, rows: []):
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
    
    def Select(self, rows: dict, table: str): # Выбрать все строки
        self.cursor.execute(f'SELECT {', '.join(rows.keys())} FROM {table}')
        self.connection.commit()
        return self.cursor.fetchall()
    
    def SelectBy(self, rows: dict, table: str, by: str, value: str): # Выбрать все строки у которых в столбце by значение value
        self.cursor.execute(f'SELECT {', '.join(rows.keys())} FROM {table} WHERE \"{by}\"=%s;', (value,))
        self.connection.commit()
        return self.cursor.fetchall()
    
    def Insert(self, insertInfo: InsertInfo, values: dict): # Вставить новую строку
        self.cursor.execute(f'INSERT INTO {insertInfo.table} ({", ".join(insertInfo.rows)}) VALUES ({", ".join([", ".join("%s" for i in range(len(values.keys())))])});', [values[key] for key in values.keys()])
        self.connection.commit()
    
    def InsertOnConflict(self, insertInfo: InsertInfo, values: dict, conflictRow: str): # Если такой записи нет, то добавить, а если есть, то обновить
        self.cursor.execute(f'INSERT INTO {insertInfo.table} ({", ".join(insertInfo.rows)}) VALUES ({", ".join([", ".join("%s" for i in range(len(values.keys())))])}) ON CONFLICT (\"{conflictRow}\") DO UPDATE SET {", ".join([f"\"{row}\"=EXCLUDED.\"{row}\"" for row in insertInfo.rows])};', [values[key] for key in values.keys()])
        self.connection.commit()

'''
class User:
    def __init__(self, id: int, telegram_id: int, firstname: str, lastname: str, is_answering: bool):
        self.id = id
        self.telegram_id = telegram_id
        self.firstname = firstname
        self.lastname = lastname
        self.is_answering = is_answering

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
    
    def ReadFromLines(self, lines):
        for (line in lines):
            self.TryAdd(self, User(int(line[0]), int(line[1]), line[2], line[3], bool(line[4])))
'''
