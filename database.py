import sqlite3

DATABASE_FILE = 'currency_conversion.db'

class DatabaseHandler:
    def create_tables(self):
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        # Create a table to store transaction details
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                source_currency TEXT,
                amount REAL,
                target_currency TEXT,
                converted_amount REAL,
                exchange_rate REAL,
                timestamp DATETIME
        )
        ''')

        conn.commit()
        conn.close()

    def insert_transaction(self, user_id, source_currency, amount, target_currency, converted_amount, exchange_rate, timestamp):
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO transactions (user_id, source_currency, amount, target_currency, converted_amount, exchange_rate, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, source_currency, amount, target_currency, converted_amount, exchange_rate, timestamp))

        transaction_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return transaction_id

if __name__ == '__main__':
    dbh = DatabaseHandler()
    dbh.create_tables()
