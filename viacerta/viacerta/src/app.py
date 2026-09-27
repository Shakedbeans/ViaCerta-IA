"""
Passo 6: Interface web com Streamlit.

Junta tudo que foi construído nos passos anteriores em uma interface
simples de usar, com duas abas:

1. "Tirar dúvida" -> usa answer.py (pergunta + RAG + function calling
   + resposta estruturada com fonte)
2. "Questão de estudo" -> usa quiz.py (gerar_questao)

Para rodar:
    streamlit run src/app.py
"""

import streamlit as st
from answer import perguntar
from quiz import gerar_questao

st.set_page_config(page_title="ViaCerta IA", page_icon="🚦", layout="centered")

st.title("🚦 ViaCerta IA")
st.caption(
    "Assistente educacional sobre regras de trânsito brasileiras — "
    "sempre citando a fonte oficial. Não substitui órgãos de trânsito."
)

aba_duvida, aba_questao = st.tabs(["💬 Tirar dúvida", "📝 Questão de estudo"])

# --- Aba 1: tirar dúvida ---
with aba_duvida:
    st.subheader("Pergunte sobre uma regra de trânsito")

    exemplo = "Posso estacionar perto de uma esquina?"
    pergunta = st.text_input("Sua pergunta:", placeholder=exemplo)

    if st.button("Perguntar", type="primary"):
        if not pergunta.strip():
            st.warning("Digite uma pergunta primeiro.")
        else:
            with st.spinner("Buscando nos documentos e gerando a resposta..."):
                try:
                    resultado = perguntar(pergunta)
                except Exception as e:
                    st.error(f"Erro ao consultar a IA: {e}")
                    resultado = None

            if resultado:
                if resultado.get("erro"):
                    st.error(resultado["erro"])
                    if resultado.get("resposta_bruta"):
                        st.code(resultado["resposta_bruta"])
                elif resultado.get("resposta") == "não encontrado":
                    st.warning(resultado.get("explicacao"))
                else:
                    st.success(f"**Resposta:** {resultado.get('resposta')}")
                    st.write(resultado.get("explicacao"))

                    with st.expander("📄 Ver fonte utilizada"):
                        st.markdown(f"**Documento:** {resultado.get('documento')}")
                        st.markdown(f"**Artigo:** {resultado.get('artigo')}")
                        st.markdown("**Trecho:**")
                        st.info(resultado.get("trecho"))

# --- Aba 2: questão de estudo ---
with aba_questao:
    st.subheader("Gere uma questão para estudar")

    tema = st.text_input(
        "Tema (opcional):",
        placeholder="ex: estacionamento, velocidade, álcool — deixe em branco para sortear",
        key="tema_questao",
    )

    if st.button("Gerar questão", type="primary"):
        with st.spinner("Gerando questão..."):
            try:
                st.session_state["questao"] = gerar_questao(tema if tema.strip() else None)
                st.session_state["resposta_selecionada"] = None
            except Exception as e:
                st.error(f"Erro ao gerar questão: {e}")
                st.session_state["questao"] = None

    questao = st.session_state.get("questao")

    if questao:
        if questao.get("erro"):
            st.error(questao["erro"])
        else:
            st.markdown(f"**{questao['pergunta']}**")

            escolha = st.radio(
                "Escolha uma alternativa:",
                options=list(questao["alternativas"].keys()),
                format_func=lambda k: f"{k}) {questao['alternativas'][k]}",
                index=None,
                key="escolha_radio",
            )

            if st.button("Confirmar resposta"):
                if escolha is None:
                    st.warning("Escolha uma alternativa primeiro.")
                elif escolha == questao["resposta_correta"]:
                    st.success("✅ Certo!")
                else:
                    st.error(
                        f"❌ Errado. A resposta certa é a **{questao['resposta_correta']}**."
                    )

                st.write(questao["explicacao"])
                with st.expander("📄 Ver fonte utilizada"):
                    st.markdown(f"**Documento:** {questao.get('documento')}")
                    st.markdown(f"**Artigo:** {questao.get('artigo')}")