import sqlite3


class DatabaseDriver(object):
    """
    Database driver for the Venmo (Full) app.
    Handles with reading and writing data with the database.
    """

    def __init__(self):
        self.conn = sqlite3.connect("venmo.db", check_same_thread=False)
        self.create_user_table()

    def create_user_table(self):
        try:
            self.conn.execute(
                """
                CREATE TABLE user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    username TEXT NOT NULL,
                    balance INTEGER
                );
                """
            )
            self.conn.commit()
        except Exception as e:
            print(e)

    def delete_user_table(self):
        self.conn.execute(
            """
            DROP TABLE IF EXISTS user;
            """
        )
        self.commit()

    def get_all_users(self):
        cursor = self.conn.execute(
            """
            SELECT id, name, username FROM user;
            """
        )
        users = []
        for row in cursor:
            users.append(
                {
                    "id": row[0],
                    "name": row[1],
                    "username": row[2]
                }
            )
        return users

    def insert_user_table(self, name, username, balance):
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO user (name, username, balance) VALUES (?, ?, ?);
            """,
            (name, username, balance)
        )
        self.conn.commit()
        return cur.lastrowid

    def get_user_by_id(self, id):
        cur = self.conn.execute(
            """
            SELECT id, name, username, balance FROM user WHERE id = ?;
            """,
            (id,)
        )
        for row in cur:
            return {
                "id": row[0],
                "name": row[1],
                "username": row[2],
                "balance": row[3]
            }
        return None

    def delete_user_by_id(self, id):
        self.conn.execute(
            """
            DELETE FROM user WHERE id = ?;
            """,
            (id,)
        )

    def update_user_by_id(self, id, fbalance):
        self.conn.execute(
            """
            UPDATE user SET balance = ? WHERE id = ?;
            """,
            (fbalance, id)
        )
        self.conn.commit()

    def create_transactions_table(self):
        try:
            self.conn.execute(
                """
                CREATE TABLE txn (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    sender_id INTEGER SECONDARY KEY NOT NULL,
                    receiver_id INTEGER SECONDARY KEY NOT NULL,
                    amount INTEGER NOT NULL,
                    message TEXT,
                    accepted INTEGER
                );
                """
            )
        except Exception as e:
            print(e)

    def delete_transactions_table(self):
        self.conn.execute(
            """
            DROP TABLE IF EXISTS txn;
            """
        )
        self.commit()

    def get_all_transactions(self):
        cursor = self.conn.execute(
            """
            SELECT * FROM txn;
            """
        )
        transactions = []
        for row in cursor:
            transactions.append(
                {
                    "id": row[0],
                    "timestamp": row[1],
                    "sender_id": row[2],
                    "receiver_id": row[3],
                    "amount": row[4],
                    "message": row[5],
                    "accepted": row[6]
                }
            )
        return transactions

    def insert_transaction(self, timestamp, sender_id, receiver_id, amount, message, accepted):
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO txn (timestamp, sender_id, receiver_id, amount, message, accepted) VALUES (?, ?, ?, ?, ?, ?);
            """,
            (timestamp, sender_id, receiver_id, amount, message, accepted)
        )
        self.conn.commit()
        return cur.lastrowid

    def get_transaction_by_id(self, id):
        cur = self.conn.execute(
            """
            SELECT * FROM txn WHERE id = ?;
            """,
            (id,)
        )
        for row in cur:
            return {
                "id": row[0],
                "timestamp": row[1],
                "sender_id": row[2],
                "receiver_id": row[3],
                "amount": row[4],
                "message": row[5],
                "accepted": row[6]
            }
        return None

    def get_transactions_of_user(self, id):
        cur = self.conn.execute(
            """
            SELECT * FROM txn WHERE sender_id = ? or receiver_id = ?;
            """,
            (id, id)
        )
        transactions = []
        for row in cur:
            transactions.append(
                {
                    "id": row[0],
                    "timestamp": row[1],
                    "sender_id": row[2],
                    "receiver_id": row[3],
                    "amount": row[4],
                    "message": row[5],
                    "accepted": row[6]
                }
            )
        return transactions

    def update_transaction_by_id(self, id, timestamp, accepted):
        self.conn.execute(
            """
            UPDATE txn SET timestamp = ?, accepted = ? WHERE id = ?;
            """,
            (timestamp, accepted, id)
        )
        self.conn.commit()
