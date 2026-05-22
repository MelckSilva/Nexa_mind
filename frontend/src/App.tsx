// frontend/src/App.tsx
// Componente raiz — controla qual página mostrar

import { useState } from "react"
import LoginPage from "./pages/LoginPage"
import DashboardPage from "./pages/DashboardPage"

// Tipo do usuário logado — passamos para o Dashboard saber quem é
type Usuario = {
  id: string
  nome: string
  email: string
}

export default function App() {
  // null = não logado, objeto = logado
  const [usuario, setUsuario] = useState<Usuario | null>(null)

  // Se não tem usuário, mostra o login
  if (!usuario) {
    return <LoginPage onLogin={(u) => setUsuario(u)} />
  }

  // Usuário logado — mostra o dashboard
  return <DashboardPage usuario={usuario} onLogout={() => setUsuario(null)} />
}
