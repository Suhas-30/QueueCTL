from queuectl.dbConnection import getConnection

class ConfigRepo:
    def setConfig(self, key:str, value:str):
        with getConnection() as conn:
            cur = conn.cursor()
            cur.execute("""
                            INSERT INTO config (key, value)
                            VALUES (?, ?)
                            ON CONFLICT(key) DO UPDATE SET value = excluded.value
                        """, (key, value))
    
    def getConfig(self, key:str, default=None):
        with getConnection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT value FROM config WHERE key = ?", (key,))
            row = cur.fetchone()
            return row["value"] if row else default
    
    def getAll(self):
        with getConnection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT key, value FROM config")
            rows = cur.fetchall()
            return {row["key"]:row["value"] for row in rows}