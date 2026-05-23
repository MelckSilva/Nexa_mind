# NexaMind - Plataforma Inteligente de Estudos com IA

O NexaMind é uma plataforma inteligente de estudos voltada para estudantes universitários. A aplicação centraliza materiais acadêmicos por disciplina e utiliza Inteligência Artificial para transformar conteúdos como PDFs, documentos e anotações em resumos, flashcards e respostas contextualizadas por meio de um chat.

Este projeto foi desenvolvido como trabalho acadêmico da disciplina de Tecnologias e Programação Integrada, com foco na construção de uma solução funcional, organizada e alinhada a um problema real do ambiente universitário.

## Problema

Estudantes universitários lidam com um grande volume de materiais, como slides, PDFs, artigos, documentos e anotações. Muitas vezes, esses conteúdos ficam espalhados, são difíceis de revisar e exigem muito tempo para serem resumidos ou transformados em material de estudo.

O NexaMind busca reduzir esse problema ao oferecer uma plataforma onde o estudante pode organizar seus materiais por disciplina e utilizar IA para apoiar a revisão e a compreensão do conteúdo.

## Objetivo

Criar um MVP funcional de uma plataforma de estudos com IA capaz de:

- cadastrar usuários;
- organizar disciplinas;
- receber upload de materiais acadêmicos;
- extrair texto dos materiais enviados;
- gerar resumos automáticos;
- gerar flashcards de revisão;
- permitir perguntas e respostas com base no conteúdo armazenado.

## Tecnologias Utilizadas

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic

### Banco de Dados

- PostgreSQL

### Inteligência Artificial

- Groq API para chamadas ao modelo de linguagem
- ChromaDB para armazenamento vetorial
- Sentence Transformers para geração de embeddings
- Pipeline de RAG para perguntas e respostas baseadas nos materiais

### Processamento de Arquivos

- pypdf para extração de texto de PDFs
- python-docx para extração de texto de arquivos DOCX
- suporte a arquivos TXT e MD

## Funcionalidades do MVP

- Cadastro e entrada simplificada de usuário.
- Criação e listagem de disciplinas.
- Upload de materiais por disciplina.
- Indexação dos materiais em base vetorial.
- Geração automática de resumos.
- Geração automática de flashcards.
- Chat com IA usando recuperação de contexto dos materiais.
- Persistência de dados relacionais no PostgreSQL.
- Interface web responsiva para uso local.

## Arquitetura

A aplicação é organizada em três camadas principais:

```text
Frontend React
    |
    v
Backend FastAPI
    |
    +--> PostgreSQL: usuários, disciplinas, materiais, resumos, flashcards e mensagens
    |
    +--> Camada de IA
            |
            +--> Extração de texto
            +--> Divisão em chunks
            +--> Geração de embeddings
            +--> Armazenamento no ChromaDB
            +--> Consulta RAG
            +--> Resposta via modelo de IA
```

Fluxo simplificado:

1. O usuário acessa o frontend em React.
2. O frontend envia requisições para a API FastAPI.
3. O backend salva os dados principais no PostgreSQL.
4. Ao enviar um material, o backend extrai o texto e envia para a camada de IA.
5. A camada de IA divide o conteúdo em partes menores, gera embeddings e salva no ChromaDB.
6. No chat, a pergunta do usuário é comparada com os trechos indexados.
7. Os trechos mais relevantes são enviados ao modelo de IA para gerar uma resposta contextualizada.

## Estrutura do Projeto

```text
Nexa_Mind/
├── ai/
│   ├── core/
│   ├── ingest/
│   ├── pipelines/
│   ├── prompts/
│   └── vectorstore/
├── backend/
│   ├── src/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── database.py
│   │   └── main.py
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── app.tsx
│   │   └── main.tsx
│   └── package.json
├── .gitignore
└── README.md
```

## Pré-requisitos

Antes de executar o projeto, é necessário ter instalado:

- Python 3.11 ou superior;
- Node.js;
- PostgreSQL;
- uma chave da Groq API.

## Configuração do Backend

Crie o ambiente virtual e instale as dependências:

```bash
python -m venv .venv
```

No Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
pip install -r backend/requirements.txt
```

Crie o banco de dados PostgreSQL:

```sql
CREATE DATABASE nexamind;
```

Copie o arquivo de exemplo:

```bash
copy backend\.env.example backend\.env
```

Configure o arquivo `backend/.env` com os dados locais:

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

Execute o backend a partir da raiz do projeto:

```bash
python -m uvicorn backend.src.main:app --reload
```

A API ficará disponível em:

```text
http://localhost:8000
```

A documentação automática da API ficará disponível em:

```text
http://localhost:8000/docs
```

## Configuração do Frontend

Em outro terminal, acesse a pasta do frontend:

```bash
cd frontend
```

Instale as dependências:

```bash
npm install
```

Execute a aplicação:

```bash
npm.cmd run dev
```

O frontend ficará disponível em:

```text
http://localhost:5173
```

## Como Testar o Fluxo Principal

Para validar o MVP, siga este fluxo:

1. Acesse o frontend.
2. Crie uma conta ou entre com um usuário existente.
3. Crie uma disciplina.
4. Envie um material em PDF, DOCX, TXT ou MD.
5. Gere um resumo a partir do material.
6. Gere flashcards.
7. Faça uma pergunta no chat sobre o conteúdo enviado.

Para apresentação, recomenda-se utilizar um arquivo pequeno em TXT ou MD, pois isso reduz o risco de falhas de extração de texto durante a demonstração.

## Verificações Técnicas

Comandos úteis para validação:

```bash
python -m compileall backend ai
```

```bash
cd frontend
npm.cmd run lint
npm.cmd run build
```

## Observações de Segurança

O arquivo `backend/.env` não deve ser enviado ao repositório ou ao arquivo zipado de entrega, pois contém credenciais locais e chaves de API.

Envie apenas o arquivo `backend/.env.example`, que contém os nomes das variáveis necessárias sem valores sensíveis.

Também não é recomendado enviar:

- `.venv/`;
- `node_modules/`;
- arquivos de upload locais;
- base vetorial local do ChromaDB;
- arquivos com chaves de API.

## Limitações do MVP

Por se tratar de uma versão acadêmica e inicial, algumas decisões foram simplificadas:

- a autenticação ainda é simplificada e não utiliza JWT;
- a aplicação depende de uma chave externa da Groq API;
- a qualidade das respostas depende da qualidade do texto extraído dos materiais;
- não há deploy em produção;
- não há testes automatizados completos;
- o foco principal está no fluxo de IA, organização de materiais e demonstração funcional.

## Melhorias Futuras

Possíveis evoluções do projeto:

- autenticação com JWT;
- recuperação de senha;
- dashboard com métricas de estudo;
- revisão espaçada para flashcards;
- filtros e busca avançada por disciplina/material;
- suporte ampliado a slides e imagens;
- testes automatizados;
- deploy com Docker;
- controle de permissões por usuário;
- histórico completo de conversas por disciplina.

## Equipe

Integrantes:

- Carlos Eduardo Rodrigues Silva
- Daniel Lucarelli Cerri
- Melck Silva de Oliveira Nascimento
- Murilo Moretto Marques

Orientador:

- Prof. Victor Hugo Braguim Canto

## Contexto Acadêmico

Projeto desenvolvido para a disciplina de Tecnologias e Programação Integrada.

Universidade Sagrado Coração (Unisagrado)

Curso de Ciência da Computação
