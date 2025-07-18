import streamlit as st
import sqlite3
import hashlib
from propostator_toolbox import propostator_tool

# ================= BANCO DE DADOS =====================

def criar_banco():
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            posicao TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,      -- use 'senha' se for igual ao restante do seu código
            admin INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def cadastrar_usuario(nome, posicao, email, senha_hash):
    try:
        conn = sqlite3.connect("usuarios.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nome, posicao, email, senha) VALUES (?, ?, ?, ?)", 
                       (nome, posicao, email, senha_hash))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # E-mail já existe

def autenticar_usuario(email, senha_hash):
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nome, posicao, email, admin FROM usuarios WHERE email = ? AND senha = ?", (email, senha_hash))
    user = cursor.fetchone()
    conn.close()
    return user

def email_valido(email):
    return email.endswith("@numenit.com")

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# ===================== CLASSES ========================

class Usuario:
    def __init__(self, nome, posicao, email, admin=0):
        self.nome = nome
        self.posicao = posicao
        self.email = email
        self.admin = admin == 1

class PropostatorApp:
    def __init__(self):
        criar_banco()
        # Recupera o usuário logado do session_state se existir
        if "usuario_logado" in st.session_state and st.session_state["usuario_logado"]:
            self.usuario_logado = Usuario(*st.session_state["usuario_logado"])
        else:
            self.usuario_logado = None

    def tela_login(self):
        st.subheader("Login - Propostator AMS")
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
                    self.usuario_logado = Usuario(*user)
                    st.session_state["logado"] = True
                    st.session_state["tela"] = "ferramenta"
                    # Salva também no session_state (para sobreviver ao rerun)
                    st.session_state["usuario_logado"] = user
                    st.success(f"Bem-vindo(a), {self.usuario_logado.nome}!")
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
        if st.button("Cadastrar nova conta"):
            st.session_state["tela"] = "cadastro"


    def tela_cadastro(self):
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
                    st.success("Cadastro realizado com sucesso! Faça login.")
                    st.session_state["tela"] = "login"
                else:
                    st.error("E-mail já cadastrado.")
        if st.button("Já tenho conta"):
            st.session_state["tela"] = "login"

    def tela_ferramenta(self):
        if not self.usuario_logado:
            st.warning("Você precisa estar logado para acessar esta área!")
            st.session_state["logado"] = False
            st.session_state["tela"] = "login"
            st.session_state["usuario_logado"] = None  # <-- Limpa o usuário logado
            st.rerun()
            return
        st.success(f"Logado como: {self.usuario_logado.nome} ({self.usuario_logado.posicao})")
        propostator_tool(usuario=self.usuario_logado)

# ===================== APP PRINCIPAL ==================

def main():
    st.set_page_config(page_title="Propostator AMS", layout="centered")
    app = PropostatorApp()

    # Estado da tela
    if "tela" not in st.session_state:
        st.session_state["tela"] = "login"
    if "logado" not in st.session_state:
        st.session_state["logado"] = False

    # Telas
    if not st.session_state["logado"]:
        if st.session_state["tela"] == "login":
            app.tela_login()
        else:
            app.tela_cadastro()
    else:
        if getattr(app, 'usuario_logado', None) is not None:
            app.tela_ferramenta()
        else:
            st.session_state["logado"] = False
            st.session_state["tela"] = "login"
            st.warning("Sessão expirada, faça login novamente.")
            app.tela_login()

if __name__ == "__main__":
    main()
