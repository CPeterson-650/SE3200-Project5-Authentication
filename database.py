import sqlite3


class AppDatabase:

    def __init__(self, database_name="rapture.db"):
        self.database_name = database_name
        self.create_tables()


    def connect(self):
        return sqlite3.connect(self.database_name)


    def create_tables(self):
        connection = self.connect()
        cursor = connection.cursor()


        # -------------------------
        # USERS
        # -------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL
            )
        """)


        # -------------------------
        # SUPPLIES
        # -------------------------

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS supplies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                location TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                status TEXT NOT NULL
            )
        """)


        connection.commit()
        connection.close()


    # -------------------------
    # USER DATABASE METHODS
    # -------------------------

    def get_user_by_email(self, email):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                first_name,
                last_name,
                email,
                password_hash,
                password_salt
            FROM users
            WHERE email = ?
        """, (email,))

        row = cursor.fetchone()

        connection.close()

        if row is None:
            return None

        return {
            "id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "email": row[3],
            "password_hash": row[4],
            "password_salt": row[5]
        }


    def create_user(
        self,
        first_name,
        last_name,
        email,
        password_hash,
        password_salt
    ):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO users (
                first_name,
                last_name,
                email,
                password_hash,
                password_salt
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            first_name,
            last_name,
            email,
            password_hash,
            password_salt
        ))

        connection.commit()

        user_id = cursor.lastrowid

        connection.close()

        return user_id

    # -------------------------
    # SUPPLY DATABASE METHODS
    # -------------------------

    def get_all_supplies(self):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                category,
                location,
                quantity,
                status
            FROM supplies
        """)

        rows = cursor.fetchall()
        connection.close()

        supplies = []

        for row in rows:
            supplies.append({
                "id": row[0],
                "name": row[1],
                "category": row[2],
                "location": row[3],
                "quantity": row[4],
                "status": row[5]
            })

        return supplies


    def get_supply(self, supply_id):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                category,
                location,
                quantity,
                status
            FROM supplies
            WHERE id = ?
        """, (supply_id,))

        row = cursor.fetchone()
        connection.close()

        if row is None:
            return None

        return {
            "id": row[0],
            "name": row[1],
            "category": row[2],
            "location": row[3],
            "quantity": row[4],
            "status": row[5]
        }


    def create_supply(self, supply):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO supplies (
                name,
                category,
                location,
                quantity,
                status
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            supply["name"],
            supply["category"],
            supply["location"],
            supply["quantity"],
            supply["status"]
        ))

        connection.commit()

        supply_id = cursor.lastrowid

        connection.close()

        return supply_id


    def update_supply(self, supply_id, supply):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE supplies

            SET
                name = ?,
                category = ?,
                location = ?,
                quantity = ?,
                status = ?

            WHERE id = ?
        """, (
            supply["name"],
            supply["category"],
            supply["location"],
            supply["quantity"],
            supply["status"],
            supply_id
        ))

        connection.commit()

        updated = cursor.rowcount > 0

        connection.close()

        return updated


    def delete_supply(self, supply_id):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM supplies
            WHERE id = ?
        """, (supply_id,))

        connection.commit()

        deleted = cursor.rowcount > 0

        connection.close()

        return deleted