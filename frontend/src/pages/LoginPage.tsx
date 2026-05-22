// frontend/src/pages/LoginPage.tsx

import { useState } from "react"
import { API_URL } from "../services/api"

// ─── Tipos ────────────────────────────────────────────────────────────────────
// Dizem ao TypeScript qual formato de dado esperar
type Props = {
  onLogin: (usuario: { id: string; nome: string; email: string }) => void
}

// ─── Componente ───────────────────────────────────────────────────────────────
export default function LoginPage({ onLogin }: Props) {

  // useState = variável que, quando muda, re-renderiza a tela
  const [isLogin, setIsLogin]       = useState(true)
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro]             = useState("")

  const [form, setForm] = useState({
    nome: "",
    email: "",
    senha: "",
  })

  // Atualiza só o campo que mudou, mantendo o resto igual
  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setErro("")
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  // ─── Cadastro ──────────────────────────────────────────────────────────────
  async function cadastrar() {
    const res = await fetch(`${API_URL}/usuarios`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        nome: form.nome,
        email: form.email,
        senha: form.senha,
      }),
    })

    if (!res.ok) {
      const data = await res.json()
      throw new Error(data.detail || "Erro ao criar conta")
    }

    return res.json()
  }

  // ─── Login ─────────────────────────────────────────────────────────────────
  // Tenta criar usuário — se o email já existe, verifica a senha (login)
  async function logar() {
    const res = await fetch(`${API_URL}/usuarios`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        nome: "Usuário",
        email: form.email,
        senha: form.senha,
      }),
    })

    if (res.ok) return res.json()

    const data = await res.json()
    throw new Error(data.detail || "Email ou senha inválidos")
  }

  // ─── Submit ────────────────────────────────────────────────────────────────
  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setErro("")

    if (!form.email || !form.senha) { setErro("Preencha e-mail e senha"); return }
    if (!isLogin && !form.nome)     { setErro("Preencha seu nome"); return }
    if (form.senha.length < 8)      { setErro("Senha precisa ter pelo menos 8 caracteres"); return }

    setCarregando(true)
    try {
      const usuario = isLogin ? await logar() : await cadastrar()
      onLogin(usuario)
    } catch (err) {
      const mensagem = err instanceof Error ? err.message : "Erro desconhecido"
      setErro(mensagem)
    } finally {
      setCarregando(false)
    }
  }

  // ─── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-[#0d0d0d] flex items-center justify-center px-4">

      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-purple-700/20 blur-[120px] rounded-full pointer-events-none" />

      <div className="relative z-10 w-full max-w-md">

        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-purple-600 mb-4">
            <svg className="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">NexaMind</h1>
          <p className="text-gray-400 mt-1 text-sm">Plataforma inteligente de estudos</p>
        </div>

        <div className="bg-[#1a1a1a] border border-white/10 rounded-2xl p-8">

          <div className="flex bg-[#0d0d0d] rounded-xl p-1 mb-6">
            {(["login", "cadastro"] as const).map((aba) => (
              <button
                key={aba}
                onClick={() => { setIsLogin(aba === "login"); setErro("") }}
                className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
                  (aba === "login") === isLogin
                    ? "bg-purple-600 text-white shadow"
                    : "text-gray-400 hover:text-white"
                }`}
              >
                {aba === "login" ? "Entrar" : "Criar conta"}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">

            {!isLogin && (
              <div>
                <label className="block text-sm text-gray-400 mb-1.5">Nome completo</label>
                <input
                  type="text" name="nome" value={form.nome} onChange={handleChange}
                  placeholder="Seu nome"
                  className="w-full bg-[#0d0d0d] border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 text-sm focus:outline-none focus:border-purple-500 transition-colors"
                />
              </div>
            )}

            <div>
              <label className="block text-sm text-gray-400 mb-1.5">E-mail</label>
              <input
                type="email" name="email" value={form.email} onChange={handleChange}
                placeholder="seu@email.com"
                className="w-full bg-[#0d0d0d] border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 text-sm focus:outline-none focus:border-purple-500 transition-colors"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1.5">Senha</label>
              <input
                type="password" name="senha" value={form.senha} onChange={handleChange}
                placeholder="mínimo 8 caracteres"
                className="w-full bg-[#0d0d0d] border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-600 text-sm focus:outline-none focus:border-purple-500 transition-colors"
              />
            </div>

            {erro && (
              <p className="text-red-400 text-sm bg-red-400/10 border border-red-400/20 rounded-xl px-4 py-3">
                {erro}
              </p>
            )}

            <button
              type="submit" disabled={carregando}
              className="w-full bg-purple-600 hover:bg-purple-500 disabled:bg-purple-800 disabled:cursor-not-allowed text-white font-medium py-3 rounded-xl transition-colors mt-2"
            >
              {carregando ? "Aguarde..." : isLogin ? "Entrar" : "Criar conta"}
            </button>
          </form>

          <p className="text-center text-gray-500 text-sm mt-6">
            {isLogin ? "Não tem conta? " : "Já tem conta? "}
            <button
              onClick={() => { setIsLogin(!isLogin); setErro("") }}
              className="text-purple-400 hover:text-purple-300 transition-colors"
            >
              {isLogin ? "Criar conta" : "Entrar"}
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}
