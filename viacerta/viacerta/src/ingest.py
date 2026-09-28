import json
import chromadb
from pathlib import Path
from embeddings import TfidfEmbeddingFunction

DB_PATH = Path(__file__).parent.parent / "chroma_db"
DATA_PATH = Path(__file__).parent.parent / "data" / "ctb_amostra.json"
COLLECTION_NAME = "regras_transito"


def get_client():
    return chromadb.PersistentClient(path=str(DB_PATH))


def get_collection(client, embedding_function):
    # cria a coleção se não existir, ou reaproveita a existente
    return client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=embedding_function
    )


def ingest():
    with open(DATA_PATH, encoding="utf-8") as f:
        artigos = json.load(f)

    client = get_client()

    # zera a coleção a cada ingestão, pra evitar duplicar ao rodar de novo
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    ids = []
    documents = []
    metadatas = []

    for i, item in enumerate(artigos):
        ids.append(f"artigo_{i}")
        documents.append(item["texto"])
        metadatas.append({
            "documento": item["documento"],
            "artigo": item["artigo"],
            "tema": item["tema"],
        })

    # treina o TF-IDF com TODOS os textos de uma vez (precisa ver o
    # vocabulário inteiro antes de virar vetores)
    embedder = TfidfEmbeddingFunction()
    embedder.fit(documents)

    collection = get_collection(client, embedder)
    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    print(f"✅ {len(ids)} artigos indexados em {DB_PATH}")


if __name__ == "__main__":
    ingest()
