"""
Passo 5: Gerador de questões de estudo (gerar_questao), agora usando
a API da OpenAI.

Mesma arquitetura do answer.py, só que em vez de responder uma pergunta
do usuário, a IA cria uma questão de múltipla escolha no estilo da
prova teórica da CNH, baseada em um artigo real dos documentos.

Fluxo:
  Usuário pede uma questão (opcionalmente sobre um tema)
    -> buscar_regra(tema) encontra um artigo relevante
    -> IA gera a questão em cima DESSE artigo específico
    -> resposta estruturada: pergunta, alternativas, resposta certa,
       explicação e a fonte usada
"""

import os
import json
import random
from openai import OpenAI
from retrieval import buscar_regra
from ingest import DATA_PATH

MODEL = "gpt-5.6-luna"

SYSTEM_PROMPT = """\
Você é o ViaCerta IA, um gerador de questões de estudo para a prova \
teórica da CNH (Carteira Nacional de Habilitação), baseado nas regras \
de trânsito brasileiras.

Você vai receber um trecho de um artigo oficial (CTB ou CONTRAN) como \
referência. Sua tarefa é criar UMA questão de múltipla escolha sobre \
esse trecho, no estilo das provas do DETRAN.

Regras:
1. A questão deve ser respondível SOMENTE com base no trecho fornecido \
— não invente detalhes que não estão lá.
2. Crie exatamente 4 alternativas (A, B, C, D), sendo apenas uma correta.
3. As alternativas erradas devem ser plausíveis (erros comuns que uma \
pessoa estudando poderia cometer), não absurdas.
4. Linguagem clara e objetiva, como nas provas reais.
5. Responda SOMENTE com um JSON válido, no formato:
{
  "pergunta": "texto da pergunta",
  "alternativas": {
    "A": "texto da alternativa A",
    "B": "texto da alternativa B",
    "C": "texto da alternativa C",
    "D": "texto da alternativa D"
  },
  "resposta_correta": "A",
  "explicacao": "por que essa é a resposta certa, em linguagem simples",
  "documento": "nome do documento fonte",
  "artigo": "identificador do artigo"
}
"""


def _escolher_trecho_base(tema: str | None) -> dict:
    """
    Escolhe o trecho que vai servir de base para a questão:
    - se um tema foi passado, busca o trecho mais relevante pra ele
    - se não, sorteia um artigo aleatório da base (bom pra "me dá uma
      questão qualquer pra estudar")
    """
    if tema:
        resultados = buscar_regra(tema, n_resultados=1)
        if resultados:
            return resultados[0]

    with open(DATA_PATH, encoding="utf-8") as f:
        artigos = json.load(f)
    escolhido = random.choice(artigos)
    return {
        "trecho": escolhido["texto"],
        "documento": escolhido["documento"],
        "artigo": escolhido["artigo"],
        "tema": escolhido["tema"],
    }


def gerar_questao(tema: str | None = None) -> dict:
    """
    Gera uma questão de múltipla escolha.

    tema: assunto opcional (ex: "estacionamento", "velocidade"). Se
    omitido, sorteia um artigo aleatório dos documentos.
    """
    base = _escolher_trecho_base(tema)

    client = OpenAI()

    prompt_usuario = (
        f"Trecho de referência:\n"
        f"Documento: {base['documento']}\n"
        f"Artigo: {base['artigo']}\n"
        f"Texto: {base['trecho']}\n\n"
        f"Crie a questão de múltipla escolha a partir deste trecho."
    )

    resposta = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt_usuario},
        ],
        response_format={"type": "json_object"},
    )

    texto_final = resposta.choices[0].message.content

    try:
        return json.loads(texto_final)
    except (json.JSONDecodeError, TypeError):
        return {
            "erro": "A IA não retornou um JSON válido.",
            "resposta_bruta": texto_final,
        }


if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        print("⚠️  Defina a variável de ambiente OPENAI_API_KEY antes de rodar.")
        raise SystemExit(1)

    print("Gerando uma questão sobre 'estacionamento'...\n")
    questao = gerar_questao("estacionamento")
    print(json.dumps(questao, ensure_ascii=False, indent=2))