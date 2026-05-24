# NexaMind - Plataforma Inteligente de Estudos com IA

O NexaMind e um MVP academico de uma plataforma web para organizar materiais de estudo por disciplina e usar Inteligencia Artificial para gerar resumos, flashcards e respostas contextualizadas a partir dos arquivos enviados.

O projeto foi desenvolvido para a disciplina de Tecnologias e Programacao Integrada e contempla backend, banco de dados, APIs documentadas, frontend responsivo, containerizacao com Docker e integracao com modelo de linguagem.

## Objetivo do MVP

O sistema busca ajudar estudantes universitarios a transformar materiais extensos, como PDFs, documentos e anotacoes, em conteudos de revisao mais rapidos de consumir.

Funcionalidades principais:

- cadastro e login simplificado de usuarios;
- criacao e listagem de disciplinas;
- upload de materiais academicos por disciplina;
- extracao de texto de arquivos PDF, DOCX, TXT e MD;
- indexacao dos materiais em base vetorial;
- geracao automatica de resumos;
- geracao automatica de flashcards;
- chat com IA usando RAG para responder com base nos materiais enviados.

## Tecnologias

Frontend:

- React
- TypeScript
- Vite
- Tailwind CSS

Backend:

- Python
- FastAPI
- SQLAlchemy
- Pydantic

Banco de dados:

- PostgreSQL

Inteligencia Artificial:

- Groq API para chamadas ao modelo de linguagem
- Sentence Transformers para embeddings
- ChromaDB para armazenamento vetorial
- Pipeline RAG para perguntas e respostas contextualizadas

Containerizacao:

- Docker
- Docker Compose

## Arquitetura

```text
Frontend React
    |
    v
Backend FastAPI
    |
    +--> PostgreSQL
    |       usuarios, disciplinas, materiais, resumos, flashcards e mensagens
    |
    +--> Camada de IA
            extracao de texto
            divisao em chunks
            geracao de embeddings
            armazenamento no ChromaDB
            busca semantica
            resposta via modelo de linguagem
```

Fluxo principal:

1. O usuario acessa o frontend.
2. O frontend consome a API FastAPI.
3. O backend persiste os dados relacionais no PostgreSQL.
4. Ao enviar um material, o backend extrai o texto do arquivo.
5. A camada de IA divide o texto em chunks, gera embeddings e salva no ChromaDB.
6. O chat recupera os trechos mais relevantes e envia ao modelo de linguagem.
7. O modelo retorna uma resposta baseada no conteudo do material.

## Estrutura do Projeto

```text
Nexa_Mind/
|-- ai/
|   |-- core/
|   |-- ingest/
|   |-- pipelines/
|   |-- prompts/
|   `-- vectorstore/
|-- backend/
|   |-- src/
|   |   |-- models/
|   |   |-- routes/
|   |   |-- schemas/
|   |   |-- services/
|   |   |-- database.py
|   |   `-- main.py
|   |-- .env.example
|   `-- requirements.txt
|-- frontend/
|   |-- public/
|   |-- src/
|   |   |-- pages/
|   |   |-- services/
|   |   |-- App.tsx
|   |   |-- index.css
|   |   `-- main.tsx
|   |-- package.json
|   `-- vite.config.ts
|-- .dockerignore
|-- .gitignore
|-- Dockerfile.backend
|-- Dockerfile.frontend
|-- docker-compose.yml
`-- README.md
```

## Execucao com Docker

Esta e a forma recomendada para demonstracao final.

Pre-requisitos:

- Docker Desktop instalado;
- chave da Groq API.

Crie um arquivo `.env` na raiz do projeto com:

```env
GROQ_API_KEY=sua_chave_groq_aqui
VITE_API_URL=http://localhost:8000
```

Suba os containers:

```bash
docker compose up --build
```

Servicos:

- frontend: `http://localhost:5173`
- backend: `http://localhost:8000`
- documentacao Swagger da API: `http://localhost:8000/docs`
- PostgreSQL: porta `5432`

Para encerrar:

```bash
docker compose down
```

Para remover tambem os volumes locais:

```bash
docker compose down -v
```

## Execucao Local sem Docker

Pre-requisitos:

- Python 3.11 ou superior;
- Node.js;
- PostgreSQL;
- chave da Groq API.

Crie e ative o ambiente virtual:

```bash
python -m venv .venv
```

No Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

Instale as dependencias do backend:

```bash
pip install -r backend/requirements.txt
```

Crie o banco PostgreSQL:

```sql
CREATE DATABASE nexamind;
```

Copie o arquivo de exemplo:

```bash
copy backend\.env.example backend\.env
```

Configure `backend/.env`:

```env
DATABASE_URL=postgresql://postgres:sua_senha@localhost:5432/nexamind
GROQ_API_KEY=sua_chave_groq_aqui
GROQ_MODEL=llama-3.1-8b-instant
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHROMA_PATH=./ai/data/chroma
CHUNK_SIZE=1000
CHUNK_OVERLAP=150
RAG_TOP_K=4
```

Execute o backend a partir da raiz:

```bash
python -m uvicorn backend.src.main:app --reload
```

Em outro terminal, execute o frontend:

```bash
cd frontend
npm install
npm.cmd run dev
```

URLs locais:

- frontend: `http://localhost:5173`
- backend: `http://localhost:8000`
- documentacao da API: `http://localhost:8000/docs`

## Documentacao da API

O backend usa FastAPI, portanto a documentacao interativa e gerada automaticamente em:

```text
http://localhost:8000/docs
```

Principais endpoints:

Usuarios:

- `POST /usuarios`
- `POST /usuarios/login`
- `GET /usuarios/{usuario_id}`
- `PUT /usuarios/{usuario_id}`
- `DELETE /usuarios/{usuario_id}`

Disciplinas:

- `POST /disciplinas`
- `GET /disciplinas`
- `GET /disciplinas/{disciplina_id}`
- `PUT /disciplinas/{disciplina_id}`
- `DELETE /disciplinas/{disciplina_id}`

Materiais:

- `POST /materiais`
- `POST /materiais/upload`
- `GET /materiais`
- `GET /materiais/{material_id}`
- `PATCH /materiais/{material_id}/processado`
- `DELETE /materiais/{material_id}`

Resumos:

- `POST /resumos`
- `POST /resumos/gerar`
- `GET /resumos/{material_id}`
- `PUT /resumos/{material_id}`
- `DELETE /resumos/{material_id}`

Flashcards:

- `POST /flashcards`
- `POST /flashcards/gerar`
- `GET /flashcards`
- `GET /flashcards/revisar`
- `POST /flashcards/{flashcard_id}/resposta`
- `DELETE /flashcards/{flashcard_id}`

Chat:

- `POST /sessoes`
- `GET /sessoes`
- `GET /sessoes/{sessao_id}`
- `PATCH /sessoes/{sessao_id}/titulo`
- `DELETE /sessoes/{sessao_id}`
- `POST /sessoes/{sessao_id}/mensagens`
- `GET /sessoes/{sessao_id}/mensagens`

## Roteiro de Demonstracao

Para demonstrar o MVP em funcionamento:

1. Inicie o sistema com `docker compose up --build`.
2. Acesse `http://localhost:5173`.
3. Crie uma conta ou entre com um usuario existente.
4. Crie uma disciplina.
5. Envie um arquivo pequeno em TXT, MD, PDF ou DOCX.
6. Aguarde o processamento e a indexacao do material.
7. Gere um resumo.
8. Gere flashcards.
9. Abra o chat e faca uma pergunta sobre o conteudo enviado.
10. Mostre a documentacao da API em `http://localhost:8000/docs` ou `http://127.0.0.1:8000/docs`.

Para reduzir riscos na apresentacao, recomenda-se usar um arquivo TXT ou MD pequeno e com conteudo claro.

## Verificacoes Tecnicas

Comandos usados para validar o projeto:

```bash
cd frontend
npm.cmd run lint
npm.cmd run build
```

```bash
python -m compileall backend ai
```

```bash
docker compose config
```

## Atendimento aos Criterios da Entrega

- Backend estruturado: implementado com FastAPI, rotas, schemas, models e services.
- Banco de dados: PostgreSQL integrado via SQLAlchemy.
- APIs documentadas: Swagger automatico do FastAPI em `/docs`.
- Docker: `Dockerfile.backend`, `Dockerfile.frontend` e `docker-compose.yml`.
- Interface responsiva: frontend React com Tailwind CSS.
- Inteligencia Artificial: Groq API, embeddings, ChromaDB e pipeline RAG.
- Documentacao tecnica: este README descreve arquitetura, execucao, endpoints e demonstracao.

## Seguranca e Arquivos que Nao Devem Ser Enviados

Nao envie arquivos com credenciais reais.

Arquivos e pastas ignorados:

- `.env`
- `backend/.env`
- `.venv/`
- `node_modules/`
- `frontend/dist/`
- `backend/uploads/`
- `ai/data/chroma/`
- `__pycache__/`

Envie apenas os exemplos de configuracao, como `backend/.env.example`.

## Limitacoes do MVP

- Autenticacao simplificada, sem JWT.
- Dependencia de chave externa da Groq API.
- Qualidade das respostas depende da extracao de texto do material.
- Nao ha deploy em producao.
- Nao ha suite completa de testes automatizados.
- O foco esta no fluxo funcional de estudo com IA.

## Melhorias Futuras

- Autenticacao com JWT.
- Recuperacao de senha.
- Dashboard com metricas de estudo.
- Revisao espacada para flashcards.
- Busca avancada por disciplina e material.
- Suporte ampliado a slides e imagens.
- Testes automatizados.
- Deploy em ambiente de producao.
- Controle de permissoes por usuario.

## Equipe

- Carlos Eduardo Rodrigues Silva
- Daniel Lucarelli Cerri
- Melck Silva de Oliveira Nascimento
- Murilo Moretto Marques

Orientador:

- Prof. Victor Hugo Braguim Canto

Contexto academico:

- Universidade Sagrado Coracao (Unisagrado)
- Curso de Ciencia da Computacao
- Disciplina de Tecnologias e Programacao Integrada
