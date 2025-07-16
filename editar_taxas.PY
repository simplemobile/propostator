import streamlit as st
import sqlite3

st.set_page_config(page_title="Gerenciar Taxas", layout="centered")
st.title("Gestão de Taxas - Propostator")

# ---- BANCO RATE_ALOC ----
def get_alocacoes():
    conn = sqlite3.connect("rate_aloc.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nivel, taxa FROM rate_aloc ORDER BY nivel")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_aloc(nivel, taxa):
    conn = sqlite3.connect("rate_aloc.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE rate_aloc SET taxa = ? WHERE nivel = ?", (taxa, nivel))
    conn.commit()
    conn.close()

# ---- BANCO TAXAS_SERVICO ----
def get_servicos():
    conn = sqlite3.connect("taxas_servico.db")
    cursor = conn.cursor()
    cursor.execute("SELECT servico, taxa_media FROM taxas_servico ORDER BY servico")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_servico(servico, taxa_media):
    conn = sqlite3.connect("taxas_servico.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE taxas_servico SET taxa_media = ? WHERE servico = ?", (taxa_media, servico))
    conn.commit()
    conn.close()

st.header("Taxas por Nível de Alocação")
aloc_rows = get_alocacoes()
cols = st.columns(5)
edited = False

for idx, (nivel, taxa) in enumerate(aloc_rows):
    with cols[idx % 5]:
        nova_taxa = st.number_input(f"Taxa {nivel}", min_value=0.0, max_value=10000.0, value=float(taxa), step=1.0, key=f"aloc_{nivel}")
        if nova_taxa != taxa:
            if st.button(f"Salvar {nivel}"):
                update_aloc(nivel, nova_taxa)
                st.success(f"Taxa de {nivel} atualizada para R$ {nova_taxa:.2f}")
                edited = True

if edited:
    st.rerun()

st.markdown("---")
st.header("Taxas por Serviço")
servico_rows = get_servicos()
cols2 = st.columns(len(servico_rows))
edited2 = False

for idx, (servico, taxa_media) in enumerate(servico_rows):
    with cols2[idx]:
        nova_taxa = st.number_input(f"Taxa {servico}", min_value=0.0, max_value=10000.0, value=float(taxa_media), step=1.0, key=f"servico_{servico}")
        if nova_taxa != taxa_media:
            if st.button(f"Salvar {servico}"):
                update_servico(servico, nova_taxa)
                st.success(f"Taxa de {servico} atualizada para R$ {nova_taxa:.2f}")
                edited2 = True

if edited2:
    st.rerun()

st.info("Pronto! Todas as taxas podem ser atualizadas rapidamente por aqui.")
