// frontend/src/pages/DashboardPage.tsx

import { useState, useEffect, useRef, useCallback } from "react"
import { API_URL } from "../services/api"

// ─── Tipos ────────────────────────────────────────────────────────────────────
// Espelham exatamente o que o backend retorna

type Usuario = {
  id: string
  nome: string
  email: string
}

type Disciplina = {
  id: string
  nome: string
  cor: string | null
  semestre: string | null
  professor: string | null
}

type Mensagem = {
  id: string
  papel: "usuario" | "assistente"
  conteudo: string
}

type SessaoChat = {
  id: string
  titulo: string | null
  disciplina_id: string | null
}

type Material = {
  id: string
  titulo: string
  tipo_arquivo: string
  tamanho_bytes: number | null
  processado: boolean
}

type Flashcard = {
  id: string
  pergunta: string
  resposta: string
  nivel_dificuldade: string
}

type Resumo = {
  id: string
  conteudo: string
}

// ─── Props ────────────────────────────────────────────────────────────────────
type Props = {
  usuario: Usuario
  onLogout: () => void
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

// Gera cor consistente para disciplina quando não tem cor definida
function corDisciplina(id: string): string {
  const cores = ["#7c3aed", "#0284c7", "#059669", "#d97706", "#dc2626", "#db2777"]
  const index = id.charCodeAt(0) % cores.length
  return cores[index]
}

// Formata tamanho em bytes para exibição
function formatarTamanho(bytes: number | null): string {
  if (!bytes) return "—"
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

// Ícone de arquivo por tipo
function iconeArquivo(tipo: string): string {
  const mapa: Record<string, string> = {
    pdf: "📄", docx: "📝", pptx: "📊", txt: "📃", md: "📋"
  }
  return mapa[tipo] || "📁"
}

// ─── Sub-componente: ícone de raio (logo) ─────────────────────────────────────
function IconeRaio({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
    </svg>
  )
}

// ─── Componente principal ─────────────────────────────────────────────────────
export default function DashboardPage({ usuario, onLogout }: Props) {

  // Qual disciplina está selecionada na sidebar
  const [disciplinaSelecionada, setDisciplinaSelecionada] = useState<Disciplina | null>(null)

  // Qual aba está ativa
  const [aba, setAba] = useState<"chat" | "materiais" | "flashcards" | "resumo">("chat")

  // Sidebar aberta/fechada
  const [sidebarAberta, setSidebarAberta] = useState(true)

  // ─── Estados de dados ──────────────────────────────────────────────────────
  const [disciplinas, setDisciplinas]   = useState<Disciplina[]>([])
  const [mensagens, setMensagens]       = useState<Mensagem[]>([])
  const [materiais, setMateriais]       = useState<Material[]>([])
  const [flashcards, setFlashcards]     = useState<Flashcard[]>([])
  const [resumo, setResumo]             = useState<Resumo | null>(null)
  const [sessaoAtual, setSessaoAtual]   = useState<SessaoChat | null>(null)

  // ─── Estados de UI ─────────────────────────────────────────────────────────
  const [inputChat, setInputChat]               = useState("")
  const [enviando, setEnviando]                 = useState(false)
  const [carregando, setCarregando]             = useState(false)
  const [erroChat, setErroChat]                 = useState("")
  const [modalDisciplina, setModalDisciplina]   = useState(false)
  const [nomeDisciplina, setNomeDisciplina]     = useState("")
  const [flashcardVirado, setFlashcardVirado]   = useState<string | null>(null)
  const [uploadArquivo, setUploadArquivo]       = useState<File | null>(null)
  const [enviandoArquivo, setEnviandoArquivo]   = useState(false)
  const [gerandoResumo, setGerandoResumo]       = useState(false)
  const [gerandoFlash, setGerandoFlash]         = useState(false)

  // Referência para auto-scroll do chat
  const fimChatRef = useRef<HTMLDivElement>(null)

  // ─── Funções de API (memoizadas) ──────────────────────────────────────────

  const buscarDisciplinas = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/disciplinas?usuario_id=${usuario.id}`)
      if (res.ok) {
        const data = await res.json()
        setDisciplinas(data)
      }
    } catch {
      // silencioso — sem disciplinas ainda
    }
  }, [usuario.id])

  const criarSessaoChat = useCallback(async () => {
    if (!disciplinaSelecionada) return
    try {
      const res = await fetch(`${API_URL}/sessoes?usuario_id=${usuario.id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ disciplina_id: disciplinaSelecionada.id }),
      })
      if (res.ok) {
        const sessao = await res.json()
        setSessaoAtual(sessao)
        // Mensagem inicial de boas-vindas (local, não vai ao banco)
        setMensagens([{
          id: "boas-vindas",
          papel: "assistente",
          conteudo: `Olá! Sou o assistente do NexaMind para a disciplina "${disciplinaSelecionada.nome}". Envie materiais na aba "Materiais" e depois me faça perguntas sobre eles!`
        }])
      }
    } catch {
      // silencioso
    }
  }, [disciplinaSelecionada, usuario.id])

  const buscarMateriais = useCallback(async () => {
    if (!disciplinaSelecionada) return
    try {
      const res = await fetch(`${API_URL}/materiais?disciplina_id=${disciplinaSelecionada.id}`)
      if (res.ok) setMateriais(await res.json())
    } catch { /* silencioso */ }
  }, [disciplinaSelecionada])

  const buscarFlashcards = useCallback(async () => {
    if (!disciplinaSelecionada) return
    setCarregando(true)
    try {
      // Busca flashcards de todos os materiais da disciplina
      const matRes = await fetch(`${API_URL}/materiais?disciplina_id=${disciplinaSelecionada.id}`)
      if (!matRes.ok) return
      const mats: Material[] = await matRes.json()

      const todos: Flashcard[] = []
      for (const mat of mats) {
        const res = await fetch(`${API_URL}/flashcards?material_id=${mat.id}`)
        if (res.ok) {
          const cards = await res.json()
          todos.push(...cards)
        }
      }
      setFlashcards(todos)
    } catch { /* silencioso */ } finally {
      setCarregando(false)
    }
  }, [disciplinaSelecionada])

  const buscarResumo = useCallback(async () => {
    if (!disciplinaSelecionada) return
    setCarregando(true)
    try {
      // Pega o primeiro material que tem resumo
      const matRes = await fetch(`${API_URL}/materiais?disciplina_id=${disciplinaSelecionada.id}`)
      if (!matRes.ok) return
      const mats: Material[] = await matRes.json()

      for (const mat of mats) {
        const res = await fetch(`${API_URL}/resumos/${mat.id}`)
        if (res.ok) {
          setResumo(await res.json())
          break
        }
      }
    } catch { /* silencioso */ } finally {
      setCarregando(false)
    }
  }, [disciplinaSelecionada])

  // ─── Efeitos ──────────────────────────────────────────────────────────────

  // Busca disciplinas ao montar
  useEffect(() => {
    void buscarDisciplinas()
  }, [buscarDisciplinas])

  // Scroll automático quando chega nova mensagem
  useEffect(() => {
    fimChatRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [mensagens])

  // Quando troca disciplina, carrega dados dela
  useEffect(() => {
    if (!disciplinaSelecionada) return
    void criarSessaoChat()
    void buscarMateriais()
  }, [disciplinaSelecionada, criarSessaoChat, buscarMateriais])

  // Quando entra na aba flashcards ou resumo, busca os dados
  useEffect(() => {
    if (!disciplinaSelecionada) return
    if (aba === "flashcards") void buscarFlashcards()
    if (aba === "resumo") void buscarResumo()
  }, [aba, disciplinaSelecionada, buscarFlashcards, buscarResumo])

  async function criarDisciplina() {
    if (!nomeDisciplina.trim()) return
    try {
      const res = await fetch(`${API_URL}/disciplinas?usuario_id=${usuario.id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nome: nomeDisciplina.trim() }),
      })
      if (res.ok) {
        const nova = await res.json()
        setDisciplinas(prev => [...prev, nova])
        setModalDisciplina(false)
        setNomeDisciplina("")
        setDisciplinaSelecionada(nova)
      }
    } catch {
      alert("Erro ao criar disciplina")
    }
  }

  async function enviarMensagem() {
    if (!inputChat.trim() || !sessaoAtual || enviando) return

    const texto = inputChat.trim()
    setInputChat("")
    setErroChat("")

    // Adiciona mensagem do usuário na tela imediatamente (UX responsiva)
    const msgUsuario: Mensagem = {
      id: Date.now().toString(),
      papel: "usuario",
      conteudo: texto,
    }
    setMensagens(prev => [...prev, msgUsuario])
    setEnviando(true)

    try {
      // POST /sessoes/{id}/mensagens — o backend chama o RAG e responde
      const res = await fetch(`${API_URL}/sessoes/${sessaoAtual.id}/mensagens`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ conteudo: texto }),
      })

      if (!res.ok) throw new Error("Erro na resposta da IA")

      const data = await res.json()
      // data.mensagem_assistente tem a resposta da IA
      setMensagens(prev => [...prev, {
        id: data.mensagem_assistente.id,
        papel: "assistente",
        conteudo: data.mensagem_assistente.conteudo,
      }])
    } catch {
      setErroChat("Erro ao enviar mensagem. Verifique se o backend está rodando.")
    } finally {
      setEnviando(false)
    }
  }

  async function uploadMaterial() {
    if (!uploadArquivo || !disciplinaSelecionada) return
    setEnviandoArquivo(true)
    try {
      // FormData para envio de arquivo (multipart/form-data)
      const form = new FormData()
      form.append("arquivo", uploadArquivo)
      form.append("titulo", uploadArquivo.name.replace(/\.[^/.]+$/, "")) // nome sem extensão

      const res = await fetch(
        `${API_URL}/materiais/upload?disciplina_id=${disciplinaSelecionada.id}`,
        { method: "POST", body: form }
      )
      if (res.ok) {
        await buscarMateriais()
        setUploadArquivo(null)
      } else {
        alert("Erro ao enviar arquivo")
      }
    } catch {
      alert("Erro ao enviar arquivo")
    } finally {
      setEnviandoArquivo(false)
    }
  }

  async function gerarFlashcards(materialId: string) {
    setGerandoFlash(true)
    try {
      const res = await fetch(
        `${API_URL}/flashcards/gerar?material_id=${materialId}&quantidade=10`,
        { method: "POST" }
      )
      if (res.ok) {
        await buscarFlashcards()
        setAba("flashcards")
      } else {
        alert("Erro ao gerar flashcards. Verifique a chave da Groq no .env")
      }
    } catch {
      alert("Erro ao gerar flashcards")
    } finally {
      setGerandoFlash(false)
    }
  }

  async function gerarResumo(materialId: string) {
    setGerandoResumo(true)
    try {
      const res = await fetch(
        `${API_URL}/resumos/gerar?material_id=${materialId}`,
        { method: "POST" }
      )
      if (res.ok) {
        setResumo(await res.json())
        setAba("resumo")
      } else {
        alert("Erro ao gerar resumo. Verifique a chave da Groq no .env")
      }
    } catch {
      alert("Erro ao gerar resumo")
    } finally {
      setGerandoResumo(false)
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      enviarMensagem()
    }
  }

  // ─── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="flex h-screen bg-[#0d0d0d] text-white overflow-hidden">

      {/* ══════════════════════════════════════
          SIDEBAR
      ══════════════════════════════════════ */}
      <aside className={`${sidebarAberta ? "w-64" : "w-0"} flex-shrink-0 transition-all duration-300 overflow-hidden`}>
        <div className="w-64 h-full bg-[#111111] border-r border-white/5 flex flex-col">

          {/* Logo */}
          <div className="flex items-center gap-2.5 px-5 py-5 border-b border-white/5">
            <div className="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center">
              <IconeRaio className="w-4 h-4 text-white" />
            </div>
            <span className="font-semibold text-white">NexaMind</span>
          </div>

          {/* Lista de disciplinas */}
          <div className="flex-1 overflow-y-auto px-3 py-4">
            <p className="text-xs text-gray-500 uppercase tracking-wider px-2 mb-3">
              Minhas Disciplinas
            </p>

            {disciplinas.length === 0 && (
              <p className="text-xs text-gray-600 px-2">Nenhuma disciplina ainda</p>
            )}

            <div className="space-y-1">
              {disciplinas.map(disc => (
                <button
                  key={disc.id}
                  onClick={() => { setDisciplinaSelecionada(disc); setAba("chat") }}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-all ${
                    disciplinaSelecionada?.id === disc.id
                      ? "bg-white/10 text-white"
                      : "text-gray-400 hover:bg-white/5 hover:text-white"
                  }`}
                >
                  {/* Bolinha colorida */}
                  <div
                    className="w-7 h-7 rounded-lg flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
                    style={{ backgroundColor: disc.cor || corDisciplina(disc.id) }}
                  >
                    {disc.nome.slice(0, 2).toUpperCase()}
                  </div>
                  <span className="text-sm truncate">{disc.nome}</span>
                </button>
              ))}
            </div>

            {/* Botão nova disciplina */}
            <button
              onClick={() => setModalDisciplina(true)}
              className="w-full mt-3 flex items-center gap-3 px-3 py-2.5 rounded-xl text-gray-500 hover:text-gray-300 hover:bg-white/5 transition-all text-sm"
            >
              <div className="w-7 h-7 rounded-lg border border-dashed border-gray-600 flex items-center justify-center">
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                </svg>
              </div>
              Nova disciplina
            </button>
          </div>

          {/* Rodapé com usuário */}
          <div className="px-3 py-4 border-t border-white/5">
            <div className="flex items-center gap-3 px-2">
              <div className="w-8 h-8 rounded-full bg-purple-800 flex items-center justify-center text-xs font-bold flex-shrink-0">
                {usuario.nome.slice(0, 2).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white truncate">{usuario.nome}</p>
                <p className="text-xs text-gray-500 truncate">{usuario.email}</p>
              </div>
              {/* Botão logout */}
              <button
                onClick={onLogout}
                title="Sair"
                className="text-gray-600 hover:text-gray-300 transition-colors"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* ══════════════════════════════════════
          ÁREA PRINCIPAL
      ══════════════════════════════════════ */}
      <main className="flex-1 flex flex-col min-w-0">

        {/* Cabeçalho */}
        <header className="flex items-center gap-4 px-6 py-4 border-b border-white/5 flex-shrink-0">
          <button
            onClick={() => setSidebarAberta(!sidebarAberta)}
            className="p-2 rounded-lg hover:bg-white/5 transition-colors text-gray-400 hover:text-white"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <div className="flex-1">
            {disciplinaSelecionada ? (
              <h1 className="font-medium text-white">{disciplinaSelecionada.nome}</h1>
            ) : (
              <h1 className="font-medium text-gray-400">Selecione uma disciplina</h1>
            )}
          </div>

          {/* Abas — só aparecem quando tem disciplina */}
          {disciplinaSelecionada && (
            <nav className="flex gap-1 bg-[#1a1a1a] rounded-xl p-1">
              {([
                { id: "chat",       label: "Chat IA" },
                { id: "materiais",  label: "Materiais" },
                { id: "flashcards", label: "Flashcards" },
                { id: "resumo",     label: "Resumo" },
              ] as const).map(item => (
                <button
                  key={item.id}
                  onClick={() => setAba(item.id)}
                  className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${
                    aba === item.id
                      ? "bg-purple-600 text-white"
                      : "text-gray-400 hover:text-white"
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </nav>
          )}
        </header>

        {/* ──────────────────────────────────────
            TELA INICIAL (sem disciplina)
        ────────────────────────────────────── */}
        {!disciplinaSelecionada && (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center max-w-md">
              <div className="w-16 h-16 bg-purple-600/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <IconeRaio className="w-8 h-8 text-purple-400" />
              </div>
              <h2 className="text-2xl font-semibold text-white mb-3">Bem-vindo, {usuario.nome.split(" ")[0]}!</h2>
              <p className="text-gray-400 leading-relaxed mb-6">
                Selecione uma disciplina na sidebar ou crie uma nova para começar.
              </p>
              <button
                onClick={() => setModalDisciplina(true)}
                className="bg-purple-600 hover:bg-purple-500 text-white font-medium px-6 py-3 rounded-xl transition-colors"
              >
                Criar primeira disciplina
              </button>
            </div>
          </div>
        )}

        {/* ──────────────────────────────────────
            ABA: CHAT
        ────────────────────────────────────── */}
        {disciplinaSelecionada && aba === "chat" && (
          <div className="flex-1 flex flex-col min-h-0">

            {/* Mensagens */}
            <div className="flex-1 overflow-y-auto px-6 py-6 space-y-5">
              {mensagens.map(msg => (
                <div key={msg.id} className={`flex gap-3 ${msg.papel === "usuario" ? "flex-row-reverse" : ""}`}>

                  {/* Avatar */}
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold ${
                    msg.papel === "assistente" ? "bg-purple-600 text-white" : "bg-gray-700 text-gray-300"
                  }`}>
                    {msg.papel === "assistente" ? <IconeRaio className="w-4 h-4" /> : usuario.nome.slice(0, 2).toUpperCase()}
                  </div>

                  {/* Bolha */}
                  <div className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                    msg.papel === "assistente"
                      ? "bg-[#1e1e1e] text-gray-200 rounded-tl-sm"
                      : "bg-purple-600 text-white rounded-tr-sm"
                  }`}>
                    {msg.conteudo}
                  </div>
                </div>
              ))}

              {/* Indicador de "digitando" */}
              {enviando && (
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center flex-shrink-0">
                    <IconeRaio className="w-4 h-4 text-white" />
                  </div>
                  <div className="bg-[#1e1e1e] rounded-2xl rounded-tl-sm px-4 py-3">
                    <div className="flex gap-1">
                      <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                      <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                      <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                    </div>
                  </div>
                </div>
              )}

              {/* Div invisível para scroll automático */}
              <div ref={fimChatRef} />
            </div>

            {/* Input do chat */}
            <div className="px-6 py-4 border-t border-white/5 flex-shrink-0">
              {erroChat && (
                <p className="text-red-400 text-xs mb-2 bg-red-400/10 px-3 py-2 rounded-lg">{erroChat}</p>
              )}
              <div className="flex gap-3 bg-[#1a1a1a] border border-white/10 rounded-2xl px-4 py-3 focus-within:border-purple-500/50 transition-colors">
                <textarea
                  value={inputChat}
                  onChange={e => setInputChat(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={`Pergunte sobre ${disciplinaSelecionada.nome}...`}
                  rows={1}
                  disabled={enviando}
                  className="flex-1 bg-transparent text-white placeholder-gray-600 text-sm resize-none focus:outline-none leading-relaxed disabled:opacity-50"
                />
                <button
                  onClick={enviarMensagem}
                  disabled={!inputChat.trim() || enviando}
                  className="self-end w-8 h-8 bg-purple-600 hover:bg-purple-500 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg flex items-center justify-center transition-colors flex-shrink-0"
                >
                  <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                </button>
              </div>
              <p className="text-xs text-gray-600 text-center mt-2">Enter para enviar · Shift+Enter para nova linha</p>
            </div>
          </div>
        )}

        {/* ──────────────────────────────────────
            ABA: MATERIAIS
        ────────────────────────────────────── */}
        {disciplinaSelecionada && aba === "materiais" && (
          <div className="flex-1 overflow-y-auto px-6 py-6">
            <div className="max-w-2xl mx-auto">

              {/* Upload de arquivo */}
              <div className="bg-[#1a1a1a] border border-white/10 rounded-2xl p-6 mb-6">
                <h3 className="text-sm font-medium text-white mb-4">Enviar material</h3>

                {/* Área de drop de arquivo */}
                <label className="flex flex-col items-center gap-3 border-2 border-dashed border-white/10 rounded-xl p-8 cursor-pointer hover:border-purple-500/50 transition-colors">
                  <svg className="w-8 h-8 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                  </svg>
                  <div className="text-center">
                    <p className="text-sm text-gray-300">
                      {uploadArquivo ? uploadArquivo.name : "Clique para selecionar"}
                    </p>
                    <p className="text-xs text-gray-600 mt-1">PDF, DOCX, TXT ou MD</p>
                  </div>
                  <input
                    type="file"
                    accept=".pdf,.docx,.txt,.md"
                    className="hidden"
                    onChange={e => setUploadArquivo(e.target.files?.[0] || null)}
                  />
                </label>

                <button
                  onClick={uploadMaterial}
                  disabled={!uploadArquivo || enviandoArquivo}
                  className="w-full mt-4 bg-purple-600 hover:bg-purple-500 disabled:bg-gray-700 disabled:cursor-not-allowed text-white text-sm font-medium py-2.5 rounded-xl transition-colors"
                >
                  {enviandoArquivo ? "Enviando e indexando..." : "Enviar material"}
                </button>
              </div>

              {/* Lista de materiais */}
              <h3 className="text-sm font-medium text-gray-400 mb-3">
                {materiais.length > 0 ? `${materiais.length} material(is)` : "Nenhum material ainda"}
              </h3>

              <div className="space-y-3">
                {materiais.map(mat => (
                  <div key={mat.id} className="bg-[#1a1a1a] border border-white/10 rounded-2xl px-5 py-4">
                    <div className="flex items-center gap-4">
                      <span className="text-2xl">{iconeArquivo(mat.tipo_arquivo)}</span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-white truncate">{mat.titulo}</p>
                        <p className="text-xs text-gray-500 mt-0.5">
                          {mat.tipo_arquivo.toUpperCase()} · {formatarTamanho(mat.tamanho_bytes)}
                          {mat.processado && <span className="text-green-400 ml-2">✓ Indexado</span>}
                        </p>
                      </div>
                      {/* Botões de ação */}
                      <div className="flex gap-2 flex-shrink-0">
                        <button
                          onClick={() => gerarResumo(mat.id)}
                          disabled={gerandoResumo}
                          className="text-xs text-purple-400 hover:text-purple-300 px-3 py-1.5 rounded-lg hover:bg-purple-400/10 transition-all disabled:opacity-50"
                        >
                          {gerandoResumo ? "..." : "Resumo"}
                        </button>
                        <button
                          onClick={() => gerarFlashcards(mat.id)}
                          disabled={gerandoFlash}
                          className="text-xs text-purple-400 hover:text-purple-300 px-3 py-1.5 rounded-lg hover:bg-purple-400/10 transition-all disabled:opacity-50"
                        >
                          {gerandoFlash ? "..." : "Flashcards"}
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ──────────────────────────────────────
            ABA: FLASHCARDS
        ────────────────────────────────────── */}
        {disciplinaSelecionada && aba === "flashcards" && (
          <div className="flex-1 overflow-y-auto px-6 py-6">
            <div className="max-w-2xl mx-auto">
              <h2 className="text-lg font-semibold mb-4">
                Flashcards
                {flashcards.length > 0 && (
                  <span className="text-sm font-normal text-gray-400 ml-2">({flashcards.length} cards)</span>
                )}
              </h2>

              {carregando && <p className="text-gray-400 text-sm">Carregando...</p>}

              {!carregando && flashcards.length === 0 && (
                <div className="bg-[#1a1a1a] border border-white/10 rounded-2xl p-8 text-center">
                  <p className="text-gray-400 text-sm">Nenhum flashcard ainda.</p>
                  <p className="text-gray-600 text-xs mt-1">Vá em Materiais e clique em "Flashcards" em um arquivo.</p>
                </div>
              )}

              <div className="grid gap-4">
                {flashcards.map(card => {
                  const virado = flashcardVirado === card.id
                  const corNivel = {
                    facil: "text-green-400 bg-green-400/10",
                    medio: "text-yellow-400 bg-yellow-400/10",
                    dificil: "text-red-400 bg-red-400/10",
                  }[card.nivel_dificuldade] || "text-gray-400 bg-gray-400/10"

                  return (
                    <div
                      key={card.id}
                      onClick={() => setFlashcardVirado(virado ? null : card.id)}
                      className="bg-[#1a1a1a] border border-white/10 rounded-2xl p-6 cursor-pointer hover:border-purple-500/50 transition-all select-none"
                    >
                      <div className="flex items-center justify-between mb-3">
                        <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${corNivel}`}>
                          {card.nivel_dificuldade}
                        </span>
                        <span className="text-xs text-gray-500">
                          {virado ? "Resposta ↑" : "Clique para ver a resposta"}
                        </span>
                      </div>
                      <p className={`text-sm leading-relaxed ${virado ? "text-purple-300" : "text-white"}`}>
                        {virado ? card.resposta : card.pergunta}
                      </p>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        )}

        {/* ──────────────────────────────────────
            ABA: RESUMO
        ────────────────────────────────────── */}
        {disciplinaSelecionada && aba === "resumo" && (
          <div className="flex-1 overflow-y-auto px-6 py-6">
            <div className="max-w-2xl mx-auto">
              <h2 className="text-lg font-semibold mb-4">Resumo</h2>

              {carregando && <p className="text-gray-400 text-sm">Carregando...</p>}

              {!carregando && !resumo && (
                <div className="bg-[#1a1a1a] border border-white/10 rounded-2xl p-8 text-center">
                  <p className="text-gray-400 text-sm">Nenhum resumo ainda.</p>
                  <p className="text-gray-600 text-xs mt-1">Vá em Materiais e clique em "Resumo" em um arquivo.</p>
                </div>
              )}

              {resumo && (
                <div className="bg-[#1a1a1a] border border-white/10 rounded-2xl p-6">
                  {/* Renderiza o markdown simples do resumo */}
                  <div className="text-sm text-gray-200 leading-relaxed whitespace-pre-wrap">
                    {resumo.conteudo}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* ══════════════════════════════════════
          MODAL: Criar disciplina
      ══════════════════════════════════════ */}
      {modalDisciplina && (
        // Fundo escuro clicável para fechar
        <div
          className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 px-4"
          onClick={() => setModalDisciplina(false)}
        >
          {/* Card do modal — stopPropagation impede fechar ao clicar dentro */}
          <div
            className="bg-[#1a1a1a] border border-white/10 rounded-2xl p-6 w-full max-w-sm"
            onClick={e => e.stopPropagation()}
          >
            <h3 className="text-white font-semibold mb-4">Nova disciplina</h3>
            <input
              type="text"
              value={nomeDisciplina}
              onChange={e => setNomeDisciplina(e.target.value)}
              onKeyDown={e => e.key === "Enter" && criarDisciplina()}
              placeholder="Ex: Programação Orientada a Objetos"
              autoFocus
              className="w-full bg-[#0d0d0d] border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 text-sm focus:outline-none focus:border-purple-500 transition-colors mb-4"
            />
            <div className="flex gap-3">
              <button
                onClick={() => setModalDisciplina(false)}
                className="flex-1 border border-white/10 text-gray-400 hover:text-white py-2.5 rounded-xl text-sm transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={criarDisciplina}
                disabled={!nomeDisciplina.trim()}
                className="flex-1 bg-purple-600 hover:bg-purple-500 disabled:bg-gray-700 text-white py-2.5 rounded-xl text-sm font-medium transition-colors"
              >
                Criar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}