# 🚦 ViaCerta IA — Assistente de Regras de Trânsito

> Assistente inteligente que responde dúvidas sobre trânsito em linguagem simples, sempre citando a fonte oficial.


**Equipe:** Paul, Yuri


## 📑 Sumário

- [Problema](#-problema)
- [Solução](#-solução)
- [Dados e conhecimento](#-dados-e-conhecimento)
- [Como cada técnica entra](#-como-cada-técnica-entra)
- [Riscos e limites](#-riscos-e-limites)
- [Fora do escopo](#-fora-do-escopo)
- [Cloud (opcional)](#-cloud-opcional)
- [Diferencial](#-diferencial)

---

## 🎯 Problema

Quem está estudando para tirar a CNH precisa consultar muitas regras de
trânsito, que muitas vezes estão espalhadas em documentos extensos e
difíceis de entender.

## 💡 Solução

O **ViaCerta IA** é um assistente que responde dúvidas sobre regras de
trânsito em linguagem simples.

O usuário pode perguntar, por exemplo:

> *"Posso estacionar perto de uma esquina?"*

O sistema responde com:

- ✅ resposta objetiva
- 📖 explicação simples
- 📄 artigo ou regra correspondente
- 🔍 trecho da fonte utilizada

Também pode gerar perguntas para ajudar nos estudos da prova teórica da CNH.

## 📚 Dados e conhecimento

A base é formada por documentos públicos e oficiais, como:

- Código de Trânsito Brasileiro (**CTB**)
- Resoluções do **CONTRAN**
- Materiais educativos oficiais de trânsito

| | |
|---|---|
| **Quantidade estimada** | 15 a 25 documentos |
| **Formato** | PDF, texto e documentos convertidos para consulta |

## ⚙️ Como cada técnica entra

| Técnica | Papel no projeto |
|---|---|
| **Prompt engineering** | Define que a IA responde de forma simples, educativa e somente com base nos documentos cadastrados |
| **Structured output** | Organiza a resposta em campos: resposta, explicação, fonte, artigo, trecho utilizado |
| **Function calling** | `buscar_regra()`, `buscar_artigo()`, `gerar_questao()` |
| **RAG** | Técnica principal — busca os trechos relevantes nos documentos e envia à IA para gerar a resposta |

**Fluxo:**

```
Pergunta → Busca nos documentos → Trecho encontrado → IA → Resposta com fonte
```

## ⚠️ Riscos e limites

- **Risco:** a IA pode inventar informações.
  **Mitigação:** responder apenas com base nos documentos e informar quando não encontrar uma resposta.
- **Risco:** utilizar uma regra desatualizada.
  **Mitigação:** os documentos terão data ou versão identificada.

> O sistema tem finalidade **educacional** e não substitui órgãos oficiais de trânsito.

## 🚫 Fora do escopo

Na primeira versão **não** serão incluídos:

- [ ] Consulta de multas
- [ ] Consulta de pontos da CNH
- [ ] Login de usuários
- [ ] Integração com DETRAN
- [ ] Defesa de multas
- [ ] Aplicativo para celular

## ☁️ Cloud (opcional)

Inicialmente o sistema roda **localmente**.

**Tecnologias possíveis:**

`Python` · `Streamlit` · `API de IA` · `LangChain` / `LlamaIndex` · `FAISS` / `ChromaDB`

## ⭐ Diferencial

O principal diferencial é entregar não apenas uma resposta, mas também a
fonte utilizada:

```
Pergunta → Resposta → Explicação → Fonte → Trecho da regra
```
