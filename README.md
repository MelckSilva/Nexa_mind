# NexaMind - Plataforma Inteligente de Estudos com IA 

O **NexaMind** é uma solução tecnológica em desenvolvimento para auxiliar estudantes universitários na organização e otimização de seus estudos. A plataforma utiliza Inteligência Artificial para transformar materiais acadêmicos densos em conteúdos estruturados, como resumos e flashcards, facilitando a preparação para avaliações.

## 📝 Definição do Problema
No cenário acadêmico atual, os alunos enfrentam um volume massivo de materiais (slides, PDFs, artigos). A dificuldade em consolidar essas informações de forma rápida e eficiente gera perda de produtividade, problema que o NexaMind busca resolver através da automação inteligente.

## 🚀 Tecnologias e Ferramentas
O projeto foi construído utilizando uma stack moderna focada em performance e escalabilidade:

> ⚠️ **Observação:** Como o projeto ainda está em fase de desenvolvimento, as tecnologias utilizadas podem sofrer alterações ao longo do processo.

* **Frontend:** React (Interface do usuário responsiva).
* **Backend:** FastAPI (Python) para uma API rápida e assíncrona.
* **Inteligência Artificial:** LangChain + LLM para processamento de linguagem natural e RAG.
* **Banco de Dados:** PostgreSQL para armazenamento de dados relacionais.
* **Infraestrutura:** Docker para padronização do ambiente de desenvolvimento.



## ✨ Principais Funcionalidades 
* **Gestão de Disciplinas:** Organização de materiais por matéria e semestre.
* **Processamento de Documentos:** Upload de arquivos PDF e extração automática de texto.
* **Resumos Automáticos:** Geração de sínteses dos materiais enviados via IA.
* **Flashcards:** Criação de cards de estudo para auxílio na memorização.
* **Agente de IA:** Chat interativo para tirar dúvidas específicas sobre o conteúdo dos materiais.

## 🏗️ Arquitetura do Sistema
A aplicação segue um modelo de arquitetura em camadas:

- **Client-side:** O usuário interage com o Frontend em React.
- **Server-side:** O Backend (FastAPI) processa requisições e gerencia o fluxo de dados.
- **IA Service:** O motor de IA (LangChain) analisa os textos e gera os conteúdos inteligentes.
- **Persistence:** Os dados são armazenados de forma segura no PostgreSQL.

## 📂 Estrutura do Repositório
```text
meu-projeto/
├── frontend/             
├── backend/              
├── ai/                   
├── .env.example          
├── .gitignore            
├── README.md             

## 👥 Equipe

**Integrantes:**
- Carlos Eduardo Rodrigues Silva  
- Daniel Lucarelli Cerri  
- Melck Silva de Oliveira Nascimento  
- Murilo Moretto Marques  

**Orientador:** Prof. Victor Hugo Braguim Canto  

---

## 🎓 Contexto Acadêmico

Projeto desenvolvido para a disciplina de Tecnologias e Programação Integrada  
**Universidade Sagrado Coração (Unisagrado)**  

Este projeto é parte integrante do curso de Ciência da Computação.