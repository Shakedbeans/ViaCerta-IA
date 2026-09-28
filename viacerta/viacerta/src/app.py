import re
import streamlit as st
from answer import perguntar
from quiz import gerar_questao

st.set_page_config(page_title="ViaCerta IA", page_icon="🚦", layout="centered")

# --- Estilo customizado -----------------------------------------------
# Paleta inspirada no semáforo, mas usada com moderação: azul como cor
# principal (transmite "oficial"/confiável) e vermelho/amarelo/verde
# reservados só para indicar a gravidade da infração, que é uma
# informação de verdade do CTB — não é só decoração.
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700&display=swap');

    h1, h2, h3 { font-family: 'Poppins', sans-serif; }

    .fonte-card {
        border-left: 5px solid #1565C0;
        background-color: #F4F6F8;
        padding: 0.9rem 1.1rem;
        border-radius: 8px;
        margin-top: 0.5rem;
    }
    .badge {
        display: inline-block;
        padding: 0.15rem 0.7rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        color: white;
        margin-bottom: 0.4rem;
    }
    .badge-leve { background-color: #2E7D32; }       /* verde */
    .badge-media { background-color: #F9A825; }       /* amarelo/âmbar */
    .badge-grave { background-color: #EF6C00; }        /* laranja */
    .badge-gravissima { background-color: #C62828; }   /* vermelho */
    .badge-indefinida { background-color: #616161; }   /* cinza */
    </style>
    """,
    unsafe_allow_html=True,
)


def badge_gravidade(texto: str) -> str:
    """
    Lê o trecho do artigo e devolve um badge HTML colorido com a
    gravidade da infração (leve/média/grave/gravíssima), do jeito que
    o próprio CTB classifica. É uma leitura simples de texto, não uma
    nova informação — só deixa a gravidade mais visível de primeira.
    """
    texto_lower = (texto or "").lower()
    if "gravíssima" in texto_lower:
        return '<span class="badge badge-gravissima">⛔ Infração gravíssima</span>'
    if "grave" in texto_lower:
        return '<span class="badge badge-grave">⚠️ Infração grave</span>'
    if "média" in texto_lower or "media" in texto_lower:
        return '<span class="badge badge-media">🟡 Infração média</span>'
    if "leve" in texto_lower:
        return '<span class="badge badge-leve">🟢 Infração leve</span>'
    return '<span class="badge badge-indefinida">Gravidade não especificada</span>'


# --- Cabeçalho ----------------------------------------------------------
col_logo, col_titulo = st.columns([1, 6])
with col_logo:
    st.markdown("<div style='font-size:3rem;'>🚦</div>", unsafe_allow_html=True)
with col_titulo:
    st.title("ViaCerta IA")
    st.caption(
        "Assistente educacional sobre regras de trânsito brasileiras — "
        "sempre citando a fonte oficial."
    )

st.info(
    "📚 Finalidade educacional. Não substitui os órgãos oficiais de trânsito "
    "(DETRAN, CONTRAN).",
    icon="ℹ️",
)

# --- Barra lateral --------------------------------------------------------
with st.sidebar:
    st.header("🚦 ViaCerta IA")
    st.caption("Equipe: Paul, Yuri")
    st.markdown("---")
    st.markdown(
        "**Como funciona:**\n"
        "1. Sua pergunta é buscada nos documentos oficiais (RAG)\n"
        "2. A IA usa *function calling* para consultar os trechos certos\n"
        "3. A resposta final vem estruturada, sempre citando artigo e fonte"
    )
    st.markdown("---")
    st.markdown("**Base de conhecimento:**")
    st.caption("CTB (Lei 9.503/1997) + Resoluções do CONTRAN")
    st.markdown("---")
    st.caption("Powered by OpenAI GPT-5.6 Luna · ChromaDB · Streamlit")

# --- Abas -----------------------------------------------------------------
aba_duvida, aba_questao = st.tabs(["💬 Tirar dúvida", "📝 Questão de estudo"])

# --- Aba 1: tirar dúvida (estilo chat) ------------------------------------
with aba_duvida:
    if "historico" not in st.session_state:
        st.session_state["historico"] = []

    for pergunta_hist, resultado_hist in st.session_state["historico"]:
        with st.chat_message("user"):
            st.write(pergunta_hist)
        with st.chat_message("assistant", avatar="🚦"):
            if resultado_hist.get("erro"):
                st.error(resultado_hist["erro"])
            elif resultado_hist.get("resposta") == "não encontrado":
                st.warning(resultado_hist.get("explicacao"))
            else:
                st.markdown(badge_gravidade(resultado_hist.get("trecho")), unsafe_allow_html=True)
                st.markdown(f"**{resultado_hist.get('resposta')}**")
                st.write(resultado_hist.get("explicacao"))
                with st.expander("📄 Ver fonte utilizada"):
                    st.markdown(
                        f"<div class='fonte-card'>"
                        f"<b>Documento:</b> {resultado_hist.get('documento')}<br>"
                        f"<b>Artigo:</b> {resultado_hist.get('artigo')}<br><br>"
                        f"{resultado_hist.get('trecho')}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

    pergunta = st.chat_input("Pergunte sobre uma regra de trânsito...")

    if pergunta:
        with st.chat_message("user"):
            st.write(pergunta)

        with st.chat_message("assistant", avatar="🚦"):
            with st.spinner("Buscando nos documentos e gerando a resposta..."):
                try:
                    resultado = perguntar(pergunta)
                except Exception as e:
                    resultado = {"erro": f"Erro ao consultar a IA: {e}"}

            if resultado.get("erro"):
                st.error(resultado["erro"])
                if resultado.get("resposta_bruta"):
                    st.code(resultado["resposta_bruta"])
            elif resultado.get("resposta") == "não encontrado":
                st.warning(resultado.get("explicacao"))
            else:
                st.markdown(badge_gravidade(resultado.get("trecho")), unsafe_allow_html=True)
                st.markdown(f"**{resultado.get('resposta')}**")
                st.write(resultado.get("explicacao"))
                with st.expander("📄 Ver fonte utilizada"):
                    st.markdown(
                        f"<div class='fonte-card'>"
                        f"<b>Documento:</b> {resultado.get('documento')}<br>"
                        f"<b>Artigo:</b> {resultado.get('artigo')}<br><br>"
                        f"{resultado.get('trecho')}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

        st.session_state["historico"].append((pergunta, resultado))

    exemplos = [
        "Posso estacionar perto de uma esquina?",
        "Qual a penalidade por dirigir bêbado?",
        "É obrigatório usar cinto de segurança?",
    ]
    if not st.session_state["historico"]:
        st.caption("Experimente perguntar:")
        cols = st.columns(len(exemplos))
        for col, ex in zip(cols, exemplos):
            col.button(ex, use_container_width=True, disabled=True, help="Digite no campo abaixo ⬇️")

# --- Aba 2: questão de estudo (com placar) --------------------------------
with aba_questao:
    if "acertos" not in st.session_state:
        st.session_state["acertos"] = 0
        st.session_state["tentativas"] = 0
        st.session_state["questao_num"] = 0

    col_placar1, col_placar2 = st.columns(2)
    col_placar1.metric("✅ Acertos", st.session_state["acertos"])
    col_placar2.metric("📋 Tentativas", st.session_state["tentativas"])

    st.markdown("---")

    tema = st.text_input(
        "Tema (opcional):",
        placeholder="ex: estacionamento, velocidade, álcool — deixe em branco para sortear",
        key="tema_questao",
    )

    if st.button("🎲 Gerar questão", type="primary"):
        with st.spinner("Gerando questão..."):
            try:
                st.session_state["questao"] = gerar_questao(tema if tema.strip() else None)
                st.session_state["questao_num"] += 1
                st.session_state["respondida"] = False
            except Exception as e:
                st.error(f"Erro ao gerar questão: {e}")
                st.session_state["questao"] = None

    questao = st.session_state.get("questao")

    if questao:
        if questao.get("erro"):
            st.error(questao["erro"])
        else:
            with st.container(border=True):
                st.markdown(f"**{questao['pergunta']}**")

                escolha = st.radio(
                    "Escolha uma alternativa:",
                    options=list(questao["alternativas"].keys()),
                    format_func=lambda k: f"{k}) {questao['alternativas'][k]}",
                    index=None,
                    # a key muda a cada questão nova, pra garantir que o
                    # radio "esqueça" a seleção anterior
                    key=f"escolha_{st.session_state['questao_num']}",
                )

                if st.button("Confirmar resposta"):
                    if escolha is None:
                        st.warning("Escolha uma alternativa primeiro.")
                    else:
                        if not st.session_state.get("respondida"):
                            st.session_state["tentativas"] += 1
                            if escolha == questao["resposta_correta"]:
                                st.session_state["acertos"] += 1
                            st.session_state["respondida"] = True

                        if escolha == questao["resposta_correta"]:
                            st.success("✅ Certo!")
                        else:
                            st.error(
                                f"❌ Errado. A resposta certa é a "
                                f"**{questao['resposta_correta']}**."
                            )

                        st.write(questao["explicacao"])
                        st.caption(
                            f"📄 Fonte: {questao.get('documento')} — {questao.get('artigo')}"
                        )