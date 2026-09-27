"""
Função de embeddings local, sem depender de baixar modelos externos.

Por padrão o ChromaDB tenta baixar um modelo (all-MiniLM-L6-v2) da
internet na primeira vez que roda. Isso pode falhar em ambientes com
rede restrita (como sandboxes) e, mais importante pro seu caso,
adiciona uma dependência de rede/modelo pesado que não é necessária
para uma base pequena de 15-25 documentos.

Aqui usamos TF-IDF (scikit-learn) como "embedding": cada texto vira um
vetor com base na frequência das palavras, ponderada pela raridade
delas na coleção toda. Funciona bem para busca textual em bases
pequenas/médias e roda 100% localmente, sem downloads.

Se no futuro a base crescer muito ou a busca por significado (não só
palavras) ficar importante, dá pra trocar por embeddings de verdade
(ex: API da OpenAI/Anthropic ou um modelo local) sem mudar o resto do
pipeline — só troca essa classe.
"""

from chromadb import EmbeddingFunction, Documents, Embeddings
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pickle
from pathlib import Path

VECTORIZER_PATH = Path(__file__).parent.parent / "chroma_db" / "vectorizer.pkl"


class TfidfEmbeddingFunction(EmbeddingFunction):
    """
    Embedding function baseada em TF-IDF.

    Importante: o vectorizer precisa ser "treinado" (fit) com todos os
    documentos de uma vez (feito em ingest.py). Depois disso, ele é
    salvo em disco para que buscas futuras usem o mesmo vocabulário.
    """

    def __init__(self):
        self.vectorizer = None
        if VECTORIZER_PATH.exists():
            with open(VECTORIZER_PATH, "rb") as f:
                self.vectorizer = pickle.load(f)

    def fit(self, texts: list[str]):
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",
            max_features=3000,
            # Analisador por CARACTERES (não por palavra inteira). Isso é
            # importante em português: sem isso, uma busca por
            # "estacionamento" não bateria com o texto "estacionar" (são
            # palavras diferentes para o TF-IDF padrão), porque não há
            # nenhum stemmer/lematizador envolvido. Usando n-gramas de
            # caracteres, as duas palavras compartilham pedaços como
            # "estacion" e o match funciona mesmo com plural, verbo
            # conjugado, etc.
            analyzer="char_wb",
            ngram_range=(3, 5),
        )
        self.vectorizer.fit(texts)
        VECTORIZER_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(VECTORIZER_PATH, "wb") as f:
            pickle.dump(self.vectorizer, f)

    def __call__(self, input: Documents) -> Embeddings:
        if self.vectorizer is None:
            raise RuntimeError(
                "Vectorizer ainda não foi treinado. Rode ingest.py primeiro."
            )
        matrix = self.vectorizer.transform(input)
        return [row.tolist() for row in matrix.toarray().astype(np.float64)]