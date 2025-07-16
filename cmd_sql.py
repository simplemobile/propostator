import sqlite3

conn = sqlite3.connect("usuarios.db")
cursor = conn.cursor()

cursor.execute("UPDATE usuarios SET admin = 1 WHERE email = ?", ("gustavo.ribeiro@numenit.com",))
conn.commit()
conn.close()
