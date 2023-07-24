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

    def get_user_transactions(self, user_id):
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM transactions WHERE user_id = ?
        ''', (user_id,))

        raw_transactions = cursor.fetchall()

        # Convert the fetched data to a list of dictionaries
        transactions_dict_list = []
        for t in raw_transactions:
            transaction_dict = {
                'transaction_id': t[0],
                'user_id': t[1],
                'source_currency': t[2],
                'amount': t[3],
                'target_currency': t[4],
                'converted_amount': t[5],
                'exchange_rate': t[6],
                'timestamp': t[7]
            }
            transactions_dict_list.append(transaction_dict)

        conn.close()
        return transactions_dict_list

if __name__ == '__main__':
    dbh = DatabaseHandler()
    dbh.create_tables()
