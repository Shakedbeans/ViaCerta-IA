"""
Passo 4: Geração da resposta final com a API do Gemini (Google).

Usamos o Gemini em vez da API da Anthropic porque o Gemini tem um
nível gratuito de verdade (sem cartão de crédito), o que é melhor para
um projeto de estudos como este. A arquitetura é a mesma:

- Function calling: a IA decide sozinha quando chamar buscar_regra()
  ou buscar_artigo() (o SDK do Gemini até executa a função Python
  automaticamente pra gente, sem precisarmos escrever um loop manual).
- RAG: as funções chamadas buscam nos documentos reais (via retrieval.py).
- Prompt engineering: o system prompt trava a IA para responder SOMENTE
  com base no que foi encontrado, em linguagem simples.
- Structured output: a resposta final é sempre um JSON com os campos
  resposta, explicacao, documento, artigo, trecho.

Como conseguir a chave grátis:
  1. Acesse https://aistudio.google.com
  2. Entre com uma conta Google
  3. Clique em "Get API key" -> "Create API key"
  4. Copie a chave e defina como variável de ambiente GEMINI_API_KEY
"""

import os
import json
from google import genai
from google.genai import types
from retrieval import buscar_regra, buscar_artigo

MODEL = "gemini-3.8-flash"

SYSTEM_PROMPT = """\
Você é o ViaCerta IA, um assistente educacional sobre regras de \
trânsito brasileiras, feito para ajudar quem está estudando para a \
prova teórica da CNH.

Regras que você deve seguir sempre:
1. Responda APENAS com base nos trechos retornados pelas ferramentas \
buscar_regra ou buscar_artigo. Nunca invente artigos, números ou \
penalidades de memória.
2. Sempre use uma das ferramentas antes de responder, mesmo se achar \
que já sabe a resposta.
3. Se as ferramentas não retornarem nada relevante, diga claramente \
que não encontrou essa informação nos documentos disponíveis — não \
tente adivinhar.
4. Explique em linguagem simples, como se estivesse explicando para \
alguém que nunca leu o CTB.
5. No final, responda SOMENTE com um JSON válido (sem texto antes ou \
depois, sem ```), no formato:
{
  "resposta": "sim/não/depende, de forma direta e objetiva",
  "explicacao": "explicação em linguagem simples do que a regra significa",
  "documento": "nome do documento fonte",
  "artigo": "identificador do artigo",
  "trecho": "o trecho exato retornado pela ferramenta, sem alterar"
}

Se nenhum trecho relevante for encontrado, responda com:
{
  "resposta": "não encontrado",
  "explicacao": "Não encontrei essa informação nos documentos disponíveis.",
  "documento": null,
  "artigo": null,
  "trecho": null
}
"""


def perguntar(pergunta_usuario: str) -> dict:
    """
    Função principal: recebe a pergunta do usuário e devolve a
    resposta já estruturada (dict), citando a fonte.
    """
    client = genai.Client()  # lê GEMINI_API_KEY do ambiente

    resposta = client.models.generate_content(
        model=MODEL,
        contents=pergunta_usuario,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            # passamos as funções Python de verdade: o SDK do Gemini
            # decide quando chamá-las e já executa automaticamente
            tools=[buscar_regra, buscar_artigo],
        ),
    )

    texto_final = resposta.text.strip()
    # às vezes o modelo ainda envolve o JSON em ```json ... ```, mesmo
    # pedindo pra não fazer isso — removemos por garantia
    if texto_final.startswith("```"):
        texto_final = texto_final.strip("`")
        if texto_final.startswith("json"):
            texto_final = texto_final[4:].strip()

    try:
        return json.loads(texto_final)
    except json.JSONDecodeError:
        return {
            "erro": "A IA não retornou um JSON válido.",
            "resposta_bruta": texto_final,
        }


if __name__ == "__main__":
    if not os.environ.get("GEMINI_API_KEY"):
        print("⚠️  Defina a variável de ambiente GEMINI_API_KEY antes de rodar.")
        raise SystemExit(1)

    pergunta = "Posso estacionar perto de uma esquina?"
    print(f"Pergunta: {pergunta}\n")
    resultado = perguntar(pergunta)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))