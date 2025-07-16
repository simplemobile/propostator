import streamlit as st
from pptx import Presentation
import os
import sqlite3
from datetime import datetime

# ======== BANCO HISTÓRICO ========
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
        data, objetivo, valor_total, horas_mensais, tera_baseline, nivel
    ))
    conn.commit()
    conn.close()

def mostrar_historico(usuario=None):
    conn = sqlite3.connect("historico.db")
    cursor = conn.cursor()
    if usuario:
        cursor.execute("""
            SELECT datahora, tipo, cliente, opp, baseline, horas_mensais, valor_total
            FROM historico_propostas
            WHERE usuario_email = ?
            ORDER BY datahora DESC
            LIMIT 20
        """, (usuario.email,))
    else:
        cursor.execute("""
            SELECT datahora, tipo, cliente, opp, baseline, horas_mensais, valor_total
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
                    "Valor Total": r[6]
                } for r in rows
            ]
        )
    else:
        st.info("Nenhuma proposta gerada ainda.")

def tela_editar_taxas():
    st.header("Edição de Taxas (Administrador)")
        

# ======== FERRAMENTA PRINCIPAL ========
def propostator_tool(usuario=None):
    criar_banco()  # garante banco

    # Limpa sessão de campos se pediu limpar
    if st.session_state.get("limpar_campos", False):
        for k in list(st.session_state.keys()):
            if k.startswith("campo_"):
                del st.session_state[k]
        st.session_state["limpar_campos"] = False

    if usuario:
        if st.button("Logout"):
            st.session_state["logado"] = False
            st.session_state["tela"] = "login"
            st.session_state["usuario_logado"] = None
            st.rerun()
            return
            
        if usuario.admin:
            st.sidebar.success("Acesso: Administrador")
            if st.button("Atualização de Rates"):
                st.session_state["logado"] = False
                st.session_state["tela"] = "login"
                st.session_state["usuario_logado"] = None
                st.rerun()
                return
        else:
            st.sidebar.info("Acesso: Solicitante")
            
    st.title("PROPOSTATOR AMS")

    # --- CAMPO TIPO ---
    tipo = st.selectbox("Tipo de Proposta", ["AMS", "FÁBRICA", "ALOCAÇÃO"], key="campo_tipo")

    comercial = st.text_input("Comercial (nome e sobrenome)", key="campo_comercial")
    email = st.text_input("E-mail Numen", value=usuario.email if usuario else "", disabled=True, key="campo_email")
    cliente = st.text_input("Nome do Cliente", key="campo_cliente")

    OPCAO_O = f"'O' {cliente.replace(' ', '_')}"
    OPCAO_A = f"'A' {cliente.replace(' ', '_')}"
    opcoes_genero = ["", OPCAO_O, OPCAO_A]
    Genero_Cliente = st.selectbox("Gênero Cliente", opcoes_genero, key="campo_genero_cliente")

    # OPP só números e máx 8
    opp_raw = st.text_input("Número da Oportunidade", max_chars=8, key="campo_opp")
    opp = "".join([c for c in opp_raw if c.isdigit()])[:8]
    if opp != opp_raw:
        st.session_state["campo_opp"] = opp

    # --- CAMPOS DINÂMICOS ---
    baseline = ""
    frentes = ""
    data = ""
    objetivo = ""
    horas_mensais = ""
    tera_baseline = ""
    nivel = ""

    if tipo == "AMS":
        frentes = st.text_input("Frentes de Atendimento", key="campo_frentes")
        baseline = st.text_input("Baseline em Horas", key="campo_baseline")
        data = st.date_input("Data", key="campo_data").strftime("%d/%m/%Y")
        objetivo = st.text_area("Objetivo", key="campo_objetivo")

    elif tipo == "FÁBRICA":
        frentes = st.text_input("Frentes de Atendimento", key="campo_frentes")
        tera_baseline = st.selectbox("Terá Baseline?", ["Sim", "Não"], key="campo_tera_baseline")
        if tera_baseline == "Sim":
            baseline = st.text_input("Baseline em Horas", key="campo_baseline")
        data = st.date_input("Data", key="campo_data").strftime("%d/%m/%Y")
        objetivo = st.text_area("Objetivo", key="campo_objetivo")

    elif tipo == "ALOCAÇÃO":
        frentes = st.text_input("Frente de Atendimento", key="campo_frentes")
        nivel = st.selectbox("Nível", ["K1", "K2", "K3", "K4", "K5"], key="campo_nivel")
        horas_mensais = st.text_input("Horas Mensais", key="campo_horas_mensais")
        data = st.date_input("Data", key="campo_data").strftime("%d/%m/%Y")
        objetivo = st.text_area("Objetivo", key="campo_objetivo")

    # --- MODELO POR TIPO ---
    nome_arquivo_modelo = {
        "AMS": "modelo_ams.pptx",
        "FÁBRICA": "modelo_fabrica.pptx",
        "ALOCAÇÃO": "modelo_aloc.pptx"
    }[tipo]
    pptx_modelo = os.path.join("Modelos", nome_arquivo_modelo)

    # --- CAMPOS OBRIGATÓRIOS ---
    campos_obrigatorios = {"Cliente": cliente, "Número da Oportunidade": opp}
    if tipo == "AMS":
        campos_obrigatorios["Baseline em Horas"] = baseline
    elif tipo == "FÁBRICA" and tera_baseline == "Sim":
        campos_obrigatorios["Baseline em Horas"] = baseline
    elif tipo == "ALOCAÇÃO":
        campos_obrigatorios["Horas Mensais"] = horas_mensais
        campos_obrigatorios["Nível"] = nivel
    campos_faltando = [campo for campo, valor in campos_obrigatorios.items() if not valor.strip()]

    # --- BUSCA TAXAS DINÂMICAS ---
    taxa = 220.00  # padrão, mas sobrescreve abaixo
    if tipo == "ALOCAÇÃO" and nivel:
        # Busca no rate_aloc
        try:
            conn = sqlite3.connect("rate_aloc.db")
            c = conn.cursor()
            c.execute("SELECT taxa FROM rate_aloc WHERE nivel = ?", (nivel,))
            res = c.fetchone()
            if res:
                taxa = float(res[0])
            conn.close()
        except Exception as e:
            st.warning("Erro ao buscar taxa de alocação. Usando padrão 220.")

    elif tipo in ["AMS", "FÁBRICA"]:
        try:
            conn = sqlite3.connect("taxas_servico.db")
            c = conn.cursor()
            c.execute("SELECT taxa_media FROM taxas_servico WHERE servico = ?", (tipo,))
            res = c.fetchone()
            if res:
                taxa = float(res[0])
            conn.close()
        except Exception as e:
            st.warning("Erro ao buscar taxa de serviço. Usando padrão 220.")

    # --- CÁLCULO VALOR ---
    valor_monetario = ""
    try:
        if tipo == "ALOCAÇÃO" and horas_mensais.strip():
            resultado = float(horas_mensais.replace(",", ".")) * taxa
        elif tipo == "AMS" and baseline.strip():
            resultado = float(baseline.replace(",", ".")) * taxa
        elif tipo == "FÁBRICA" and tera_baseline == "Sim" and baseline.strip():
            resultado = float(baseline.replace(",", ".")) * taxa
        else:
            resultado = None
        if resultado is not None:
            valor_monetario = "R$ {:,.2f}".format(resultado).replace(",", "X").replace(".", ",").replace("X", ".")
            st.write(f"Valor Mensal da Proposta: {valor_monetario}")
    except ValueError:
        st.warning("Digite um valor numérico válido para baseline ou horas.")

    # --- SUBSTITUIÇÃO E GERAR ---
    def substituir_campos(pptx_modelo, substituicoes, saida_nome):
        prs = Presentation(pptx_modelo)
        for slide in prs.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        for run in paragraph.runs:
                            for marcador, valor in substituicoes.items():
                                if marcador in run.text:
                                    run.text = run.text.replace(marcador, str(valor))
        prs.save(saida_nome)

    col1, col2 = st.columns([2, 1])
    with col1:
        gerar = st.button("Gerar apresentação")
    with col2:
        limpar = st.button("Limpar campos")

    if limpar:
        st.session_state["limpar_campos"] = True
        st.rerun()

    if gerar:
        if campos_faltando:
            st.error(f"Preencha os seguintes campos obrigatórios: {', '.join(campos_faltando)}")
        elif not os.path.exists(pptx_modelo):
            st.error(f"Arquivo modelo não encontrado: {pptx_modelo}")
        else:
            substituicoes = {
                "{{CLIENTE}}": cliente,
                "{{DATA}}": data,
                "{{FRENTES}}": frentes,
                "{{VALOR}}": valor_monetario,
                "{{OPP}}": opp,
                "{{GENERO_CLIENTE}}": Genero_Cliente,
                "{{BASELINE}}": baseline,
                "{{COMERCIAL}}": comercial,
                "{{EMAIL}}": email,
                "{{OBJETIVO}}": objetivo,
                "{{HORAS_MENSAIS}}": horas_mensais,
                "{{TERA_BASELINE}}": tera_baseline,
                "{{NIVEL}}": nivel
            }
            saida_nome = f"{tipo}_PT_{opp}_{cliente.replace(' ', '_')}_{data.replace('/', '-')}.pptx"
            substituir_campos(pptx_modelo, substituicoes, saida_nome)
            with open(saida_nome, "rb") as file:
                st.success("Apresentação gerada com sucesso!")
                st.download_button(
                    label="Baixar apresentação personalizada",
                    data=file,
                    file_name=saida_nome,
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )
            # --- Salva LOG no banco ---
            salvar_proposta_log(
                usuario, tipo, comercial, email, cliente, Genero_Cliente, opp,
                frentes, baseline, data, objetivo, valor_monetario, horas_mensais, tera_baseline, nivel
            )

    # --- HISTÓRICO ---
    mostrar_historico(usuario)
