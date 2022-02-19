import sqlite3


class Database():
    def __init__(self, path: str) -> None:
        self.path = path
        self.connection = None
        self.cursor = None

    def setup(self):
        self.connection = sqlite3.connect(self.path)
        self.cursor = self.connection.cursor()

    def close(self):
        self.connection.close()

    def execute(self, query: str):
        self.cursor.execute(query)

    def commit(self):
        self.connection.commit()
