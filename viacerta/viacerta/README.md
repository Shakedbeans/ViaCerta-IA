# ViaCerta IA — Setup local

## 1. Instalar dependências
```
pip install -r requirements.txt
```

## 2. Rodar a ingestão (cria o banco vetorial local)
```
python src/ingest.py
```
Isso cria a pasta `chroma_db/` com os artigos indexados.
Rode de novo sempre que mudar `data/ctb_amostra.json`.

## 3. Testar a busca
```
python src/retrieval.py
```
Deve mostrar os artigos mais relevantes para a pergunta de teste
("Posso estacionar perto de uma esquina?").

## Próximo passo
Passo 4: gerar a resposta final via API da Anthropic (ainda não incluído).
