import sqlite3

conn = sqlite3.connect("rate_aloc.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS rate_aloc (
        nivel TEXT PRIMARY KEY,
        taxa REAL
    )
""")
for nivel in ["K1", "K2", "K3", "K4", "K5"]:
    cursor.execute("INSERT OR IGNORE INTO rate_aloc (nivel, taxa) VALUES (?, ?)", (nivel, 100.0))
conn.commit()
conn.close()

print("Banco de níveis de alocação criado ou atualizado.")