import os
import json
from openai import OpenAI
from retrieval import buscar_regra, buscar_artigo

MODEL = "gpt-5.6-luna"

# --- Definição das ferramentas (function calling) ---
# Isso é só a "assinatura" que a IA vê. A execução de verdade acontece
# em executar_ferramenta(), chamando as funções reais do retrieval.py.
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "buscar_regra",
            "description": (
                "Busca nos documentos oficiais de trânsito (CTB, resoluções "
                "do CONTRAN) trechos relevantes para uma pergunta em "
                "linguagem natural. Use isso para responder dúvidas gerais "
                "do usuário."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "pergunta": {
                        "type": "string",
                        "description": "A pergunta do usuário, em português.",
                    }
                },
                "required": ["pergunta"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_artigo",
            "description": (
                "Busca o texto exato de um artigo específico, quando o "
                "usuário já menciona um número de artigo (ex: 'Art. 183')."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "numero_artigo": {
                        "type": "string",
                        "description": "Identificador do artigo, ex: 'Art. 183, VIII'.",
                    }
                },
                "required": ["numero_artigo"],
            },
        },
    },
]

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
5. No final, responda SOMENTE com um JSON válido, no formato:
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


def executar_ferramenta(nome: str, entrada: dict):
    """Executa de fato a função que a IA pediu para chamar."""
    if nome == "buscar_regra":
        return buscar_regra(entrada["pergunta"])
    elif nome == "buscar_artigo":
        resultado = buscar_artigo(entrada["numero_artigo"])
        return resultado if resultado else {"erro": "artigo não encontrado"}
    else:
        return {"erro": f"ferramenta desconhecida: {nome}"}


def perguntar(pergunta_usuario: str) -> dict:
    """
    Função principal: recebe a pergunta do usuário e devolve a
    resposta já estruturada (dict), citando a fonte.
    """
    client = OpenAI()  # lê OPENAI_API_KEY do ambiente

    mensagens = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": pergunta_usuario},
    ]

    # Loop de function calling: a IA pode chamar ferramentas várias
    # vezes antes de dar a resposta final.
    for _ in range(4):  # limite de segurança pra não loopar infinito
        resposta = client.chat.completions.create(
            model=MODEL,
            messages=mensagens,
            tools=TOOLS,
            response_format={"type": "json_object"},
            # Nos modelos GPT-5.6, tools + reasoning (que vem ligado por
            # padrão) não são compatíveis no endpoint de chat completions.
            # Precisamos desligar o "raciocínio" explicitamente pra poder
            # usar function calling aqui.
            reasoning_effort="none",
        )

        mensagem = resposta.choices[0].message

        if not mensagem.tool_calls:
            # IA terminou e deu a resposta final (deve ser o JSON)
            try:
                return json.loads(mensagem.content)
            except (json.JSONDecodeError, TypeError):
                return {
                    "erro": "A IA não retornou um JSON válido.",
                    "resposta_bruta": mensagem.content,
                }

        # IA pediu para chamar uma ou mais ferramentas
        mensagens.append(mensagem)

        for chamada in mensagem.tool_calls:
            argumentos = json.loads(chamada.function.arguments)
            resultado = executar_ferramenta(chamada.function.name, argumentos)
            mensagens.append({
                "role": "tool",
                "tool_call_id": chamada.id,
                "content": json.dumps(resultado, ensure_ascii=False),
            })

    return {"erro": "Número máximo de chamadas de ferramenta excedido."}


if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        print("⚠️  Defina a variável de ambiente OPENAI_API_KEY antes de rodar.")
        raise SystemExit(1)

    pergunta = "Posso estacionar perto de uma esquina?"
    print(f"Pergunta: {pergunta}\n")
    resultado = perguntar(pergunta)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))