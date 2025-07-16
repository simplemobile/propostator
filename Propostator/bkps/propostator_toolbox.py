import streamlit as st
import sqlite3
from pptx import Presentation
import os
from datetime import datetime

# ====== Banco de Usuários (com admin) ======
def criar_banco_usuarios():
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            posicao TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL,
            admin INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def cadastrar_usuario(nome, posicao, email, senha_hash):
    try:
        conn = sqlite3.connect("usuarios.db")
        c = conn.cursor()
        c.execute("INSERT INTO usuarios (nome, posicao, email, senha_hash, admin) VALUES (?, ?, ?, ?, 0)",
                  (nome, posicao, email, senha_hash))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def autenticar_usuario(email, senha_hash):
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("SELECT nome, posicao, email, admin FROM usuarios WHERE email = ? AND senha_hash = ?", (email, senha_hash))
    user = c.fetchone()
    conn.close()
    return user

def listar_usuarios():
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("SELECT id, nome, email, admin FROM usuarios")
    rows = c.fetchall()
    conn.close()
    return rows

def set_admin(user_id, admin_value):
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("UPDATE usuarios SET admin = ? WHERE id = ?", (admin_value, user_id))
    conn.commit()
    conn.close()

import hashlib
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def email_valido(email):
    return email.endswith("@numenit.com")

class Usuario:
    def __init__(self, nome, posicao, email, admin=0):
        self.nome = nome
        self.posicao = posicao
        self.email = email
        self.admin = admin == 1

# ======= Banco Histórico (já com campo nível, atualizado) =======
def criar_banco():
    conn = sqlite3.connect("historico.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_propostas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_nome TEXT,
            usuario_email TEXT,
            usuario_posicao TEXT,
            datahora TEXT,
            tipo TEXT,
            comercial TEXT,
            email TEXT,
            cliente TEXT,
            genero_cliente TEXT,
            opp TEXT,
            frentes TEXT,
            baseline TEXT,
            data_proposta TEXT,
            objetivo TEXT,
            valor_total TEXT,
            horas_mensais TEXT,
            tera_baseline TEXT,
            nivel TEXT
        )
    """)
    conn.commit()
    conn.close()

def salvar_proposta_log(
    usuario, tipo, comercial, email, cliente, genero_cliente, opp,
    frentes, baseline, data, objetivo, valor_total, horas_mensais, tera_baseline, nivel
):
    conn = sqlite3.connect("historico.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO historico_propostas (
            usuario_nome, usuario_email, usuario_posicao, datahora, tipo,
            comercial, email, cliente, genero_cliente, opp, frentes, baseline,
            data_proposta, objetivo, valor_total, horas_mensais, tera_baseline, nivel
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        usuario.nome if usuario else None,
        usuario.email if usuario else None,
        usuario.posicao if usuario else None,
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        tipo, comercial, email, cliente, genero_cliente, opp, frentes, baseline,
        data, objetivo, valor_monetario, horas_mensais, tera_baseline, nivel
    ))
    conn.commit()
    conn.close()

def mostrar_historico(usuario=None):
    conn = sqlite3.connect("historico.db")
    cursor = conn.cursor()
    if usuario:
        cursor.execute("""
            SELECT datahora, tipo, cliente, opp, baseline, horas_mensais, valor_total, objetivo, nivel
            FROM historico_propostas
            WHERE usuario_email = ?
            ORDER BY datahora DESC
            LIMIT 20
        """, (usuario.email,))
    else:
        cursor.execute("""
            SELECT datahora, tipo, cliente, opp, baseline, horas_mensais, valor_total, objetivo, nivel
            FROM historico_propostas
            ORDER BY datahora DESC
            LIMIT 20
        """)
    rows = cursor.fetchall()
    conn.close()
    if rows:
        st.subheader("Histórico de Propostas")
        st.dataframe(
            [
                {
                    "Data/Hora": r[0],
                    "Tipo": r[1],
                    "Cliente": r[2],
                    "OPP": r[3],
                    "Baseline": r[4],
                    "Horas Mensais": r[5],
                    "Valor Total": r[6],
                    "Objetivo": r[7],
                    "Nível": r[8]
                } for r in rows
            ]
        )
    else:
        st.info("Nenhuma proposta gerada ainda.")

# ======= Telas principais =======

def tela_login():
    st.subheader("Login")
    email = st.text_input("E-mail", key="login_email")
    senha = st.text_input("Senha", type="password", key="login_senha")
    if st.button("Entrar"):
        if not email or not senha:
            st.warning("Preencha todos os campos.")
        elif not email_valido(email):
            st.error("Use um e-mail @numenit.com")
        else:
            user = autenticar_usuario(email, hash_senha(senha))
            if user:
                usuario = Usuario(*user)
                st.session_state["logado"] = True
                st.session_state["tela"] = "proposta"
                st.session_state["usuario_logado"] = user
                st.success(f"Bem-vindo(a), {usuario.nome}!")
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
    if st.button("Cadastrar nova conta"):
        st.session_state["tela"] = "cadastro"

def tela_cadastro():
    st.subheader("Cadastro")
    nome = st.text_input("Nome completo", key="cad_nome")
    posicao = st.selectbox("Posição", ["Comercial", "Operação", "Elo Executivo"])
    email = st.text_input("E-mail", key="cad_email")
    senha = st.text_input("Senha", type="password", key="cad_senha")
    conf_senha = st.text_input("Confirme a senha", type="password", key="cad_conf_senha")
    if st.button("Cadastrar"):
        if not nome or not email or not senha or not conf_senha:
            st.warning("Preencha todos os campos.")
        elif not email_valido(email):
            st.error("O e-mail precisa ser do domínio @numenit.com")
        elif senha != conf_senha:
            st.error("As senhas não conferem.")
        else:
            ok = cadastrar_usuario(nome, posicao, email, hash_senha(senha))
            if ok:
                st.success("Cadastro realizado! Faça login.")
                st.session_state["tela"] = "login"
            else:
                st.error("E-mail já cadastrado.")
    if st.button("Já tenho conta"):
        st.session_state["tela"] = "login"

# ======= Tela Principal da Ferramenta =======
def propostator_tool(usuario=None):
    from propostator_toolbox import propostator_tool as ferramenta
    ferramenta(usuario=usuario)

# ======= Telas de Administração =======
def tela_administracao(usuario):
    st.header("Administração do Sistema")
    st.subheader("Gerenciar Administradores")
    users = listar_usuarios()
    for user_id, nome, email, admin in users:
        col1, col2, col3 = st.columns([4, 3, 2])
        with col1:
            st.write(f"{nome} ({email})")
        with col2:
            if admin:
                st.success("Administrador")
            else:
                st.info("Usuário comum")
        with col3:
            if usuario.email != email:
                if admin:
                    if st.button(f"Remover Admin [{email}]", key=f"rem_{user_id}"):
                        set_admin(user_id, 0)
                        st.success(f"{email} agora é usuário comum.")
                        st.experimental_rerun()
                else:
                    if st.button(f"Promover Admin [{email}]", key=f"prom_{user_id}"):
                        set_admin(user_id, 1)
                        st.success(f"{email} agora é administrador.")
                        st.experimental_rerun()
    st.markdown("---")
    st.subheader("Edição de Taxas")
    if st.button("Acessar Tela de Edição de Taxas"):
        st.session_state["tela"] = "editar_taxas"
        st.experimental_rerun()

def tela_editar_taxas():
    import sqlite3
    st.header("Edição de Taxas (Administrador)")
    # -- Alocação --
    st.subheader("Taxas por Nível de Alocação")
    conn = sqlite3.connect("rate_aloc.db")
    c = conn.cursor()
    c.execute("SELECT nivel, taxa FROM rate_aloc ORDER BY nivel")
    alocacoes = c.fetchall()
    conn.close()
    cols = st.columns(5)
    for idx, (nivel, taxa) in enumerate(alocacoes):
        with cols[idx % 5]:
            nova_taxa = st.number_input(f"Taxa {nivel}", min_value=0.0, max_value=10000.0, value=float(taxa), step=1.0, key=f"aloc_{nivel}")
            if nova_taxa != taxa:
                if st.button(f"Salvar {nivel}"):
                    conn = sqlite3.connect("rate_aloc.db")
                    cur = conn.cursor()
                    cur.execute("UPDATE rate_aloc SET taxa = ? WHERE nivel = ?", (nova_taxa, nivel))
                    conn.commit()
                    conn.close()
                    st.success(f"Taxa de {nivel} atualizada para R$ {nova_taxa:.2f}")
                    st.experimental_rerun()
    st.markdown("---")
    # -- Serviços --
    st.subheader("Taxas por Serviço")
    conn = sqlite3.connect("taxas_servico.db")
    c = conn.cursor()
    c.execute("SELECT servico, taxa_media FROM taxas_servico ORDER BY servico")
    servicos = c.fetchall()
    conn.close()
    cols2 = st.columns(len(servicos))
    for idx, (servico, taxa_media) in enumerate(servicos):
        with cols2[idx]:
            nova_taxa = st.number_input(f"Taxa {servico}", min_value=0.0, max_value=10000.0, value=float(taxa_media), step=1.0, key=f"servico_{servico}")
            if nova_taxa != taxa_media:
                if st.button(f"Salvar {servico}"):
                    conn = sqlite3.connect("taxas_servico.db")
                    cur = conn.cursor()
                    cur.execute("UPDATE taxas_servico SET taxa_media = ? WHERE servico = ?", (nova_taxa, servico))
                    conn.commit()
                    conn.close()
                    st.success(f"Taxa de {servico} atualizada para R$ {nova_taxa:.2f}")
                    st.experimental_rerun()

# ======= MAIN =======
def main():
    st.set_page_config(page_title="Propostator AMS", layout="centered")
    criar_banco_usuarios()
    criar_banco()

    if "tela" not in st.session_state:
        st.session_state["tela"] = "login"
    if "logado" not in st.session_state:
        st.session_state["logado"] = False

    usuario = None
    if "usuario_logado" in st.session_state and st.session_state["usuario_logado"]:
        usuario = Usuario(*st.session_state["usuario_logado"])

    # MENU lateral ADMIN
    if st.session_state.get("logado") and usuario and usuario.admin:
        st.sidebar.success("Acesso: Administrador")
        admin_tela = st.sidebar.radio("Painel Admin", ["Propostas", "Administração", "Edição de Taxas"])
        if admin_tela == "Propostas":
            st.session_state["tela"] = "proposta"
        elif admin_tela == "Administração":
            st.session_state["tela"] = "admin"
        elif admin_tela == "Edição de Taxas":
            st.session_state["tela"] = "editar_taxas"

    # TELAS
    if not st.session_state.get("logado", False):
        if st.session_state["tela"] == "login":
            tela_login()
        elif st.session_state["tela"] == "cadastro":
            tela_cadastro()
    else:
        if st.session_state["tela"] == "proposta":
            propostator_tool(usuario)
        elif st.session_state["tela"] == "admin":
            tela_administracao(usuario)
        elif st.session_state["tela"] == "editar_taxas":
            tela_editar_taxas()
        else:
            propostator_tool(usuario)

if __name__ == "__main__":
    main()
