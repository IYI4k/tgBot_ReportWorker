import psycopg2

class Table: # Содержит информацию о названии таблицы и столбцов
    def __init__(self, table: str, rows: []):
        self.table = table
        self.rows = {row: None for row in rows}
        self.rows_no_id = {row: None for row in rows[1:]}

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
    
    def Select(self, table: Table, rows: dict): # Выбрать все строки
        self.cursor.execute(f'SELECT {', '.join(rows.keys())} FROM {table.table}')
        self.connection.commit()
        return self.cursor.fetchall()
    
    def SelectBy(self, table: Table, rows: dict, by: str, value: str): # Выбрать все строки у которых в столбце by значение value
        self.cursor.execute(f'SELECT {', '.join(rows.keys())} FROM {table.table} WHERE \"{by}\"=%s;', (value,))
        self.connection.commit()
        return self.cursor.fetchall()
    
    def SelectOneBy(self, table: Table, rows: dict, by: str, value: str): # Выбрать одну строку у которой в столбце by значение value
        self.cursor.execute(f'SELECT {', '.join(rows.keys())} FROM {table.table} WHERE \"{by}\"=%s LIMIT 1;', (value,))
        self.connection.commit()
        return self.cursor.fetchone()
    
    def SelectLastByReportBy(self, table: Table, rows: dict, by: str, value: str, reportBy: str): # Выбрать последнюю запись, у которой в столбце by значение value, а отсортированы они были по столбцу reportBy
        self.cursor.execute(f'SELECT {', '.join(rows)} FROM {table.table} WHERE \"{by}\"=%s ORDER BY {reportBy} DESC LIMIT 1;', (value,))
        self.connection.commit()
        return self.cursor.fetchone()
    
    def Insert(self, table: Table, values: dict): # Вставить новую строку
        self.cursor.execute(f'INSERT INTO {table.table} ({", ".join(table.rows_no_id.keys())}) VALUES ({", ".join([", ".join("%s" for i in range(len(values.keys())))])});', [values[key] for key in values.keys()])
        self.connection.commit()
    
    def InsertOnConflict(self, table: Table, values: dict, conflictRow: str): # Если такой записи нет, то добавить, а если есть, то обновить
        self.cursor.execute(f'INSERT INTO {table.table} ({", ".join(table.rows_no_id.keys())}) VALUES ({", ".join([", ".join("%s" for i in range(len(values.keys())))])}) ON CONFLICT (\"{conflictRow}\") DO UPDATE SET {", ".join([f"\"{row}\"=EXCLUDED.\"{row}\"" for row in table.rows_no_id])};', [values[key] for key in values.keys()])
        self.connection.commit()

class ReportSender():
    def __init__(self, dbWorker: DBWorker, table_UserReportGroups: Table):
        self.dbWorker = dbWorker
        self.table_UserReportGroups = table_UserReportGroups
    
    def GetRecipients(self, telegram_id: int):
        recipients = []

        reportGroups = self.dbWorker.SelectBy(self.table_UserReportGroups, {"report_groups": None}, "telegram_id", str(telegram_id))
        for reportGroup in reportGroups:
            print(reportGroup)
            splittedReportGroup = reportGroup[0].split('_')

            if (splittedReportGroup[1]=="sender"):
                recipients += self.GetRecipientsByReportGroup(f"{splittedReportGroup[0]}_recipient")
        
        return set(recipients)
    
    def GetRecipientsByReportGroup(self, reportGroup: str):
        recipients = self.dbWorker.SelectBy(self.table_UserReportGroups, {"telegram_id": None}, "report_groups", reportGroup)
        return ([recipient[0] for recipient in recipients])

'''
class User:
    def __init__(self, telegram_id: int, first_name: str, last_name: str, is_answering: bool):
        self.telegram_id = telegram_id
        self.first_name = first_name
        self.last_name = last_name
        self.is_answering = is_answering
    
    def ToDict(self):
        return {"telegram_id": self.telegram_id, "first_name": self.first_name, "last_name": self.last_name, "is_answering": self.is_answering}

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
