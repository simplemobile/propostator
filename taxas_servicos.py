import sqlite3

conn = sqlite3.connect("taxas_servico.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS taxas_servico (
        servico TEXT PRIMARY KEY,
        taxa_media REAL
    )
""")
for servico in ["AMS", "FÁBRICA"]:
    cursor.execute("INSERT OR IGNORE INTO taxas_servico (servico, taxa_media) VALUES (?, ?)", (servico, 100.0))
conn.commit()
conn.close()
print("Banco de taxas de serviço criado ou atualizado.")
