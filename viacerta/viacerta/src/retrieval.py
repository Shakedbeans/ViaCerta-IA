"""
Passo 3: Funções de busca (RAG).

Estas são as funções que a IA vai "chamar" via function calling:

- buscar_regra(pergunta): busca semântica livre — usada quando o
  usuário faz uma pergunta em linguagem natural.
- buscar_artigo(numero): busca direta por número de artigo — usada
  quando o usuário (ou a IA) já sabe qual artigo quer conferir.
"""

import chromadb
from pathlib import Path
from embeddings import TfidfEmbeddingFunction
from ingest import DB_PATH, COLLECTION_NAME


def _get_collection():
    client = chromadb.PersistentClient(path=str(DB_PATH))
    embedder = TfidfEmbeddingFunction()
    return client.get_collection(name=COLLECTION_NAME, embedding_function=embedder)


def buscar_regra(pergunta: str, n_resultados: int = 3) -> list[dict]:
    """
    Busca os trechos mais relevantes para uma pergunta em linguagem
    natural. Retorna uma lista de trechos com seus metadados (fonte).
    """
    collection = _get_collection()
    resultados = collection.query(query_texts=[pergunta], n_results=n_resultados)

    trechos = []
    for texto, meta, distancia in zip(
        resultados["documents"][0],
        resultados["metadatas"][0],
        resultados["distances"][0],
    ):
        trechos.append({
            "trecho": texto,
            "documento": meta["documento"],
            "artigo": meta["artigo"],
            "tema": meta["tema"],
            # transforma distância (0 = idêntico, cresce sem limite) em um
            # score de 0 a 1, sempre decrescente com a distância
            "relevancia": round(1 / (1 + distancia), 3),
        })
    return trechos


def buscar_artigo(numero_artigo: str) -> dict | None:
    """
    Busca direta por número/identificador de artigo (ex: "Art. 183, VIII").
    Retorna o trecho exato se encontrado, senão None.
    """
    collection = _get_collection()
    resultados = collection.get(where={"artigo": numero_artigo})

    if not resultados["ids"]:
        return None

    return {
        "trecho": resultados["documents"][0],
        "documento": resultados["metadatas"][0]["documento"],
        "artigo": resultados["metadatas"][0]["artigo"],
        "tema": resultados["metadatas"][0]["tema"],
    }


if __name__ == "__main__":
    # teste rápido com a pergunta de exemplo do projeto
    pergunta = "Posso estacionar perto de uma esquina?"
    print(f"Pergunta: {pergunta}\n")
    for r in buscar_regra(pergunta):
        print(f"[{r['relevancia']}] {r['artigo']} — {r['tema']}")
        print(f"  {r['trecho']}\n")
