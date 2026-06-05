import { FormEvent, useState } from "react";
import { LogIn } from "lucide-react";
import { api, ApiError } from "../lib/api";
import { saveSession } from "../lib/session";
import type { User } from "../lib/types";

type LoginPageProps = {
  onLogin: (user: User) => void;
};

export function LoginPage({ onLogin }: LoginPageProps) {
  const [email, setEmail] = useState("admin@moviprogy.local");
  const [senha, setSenha] = useState("moviprogy_admin_dev_password");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    if (!email.trim() || !senha.trim()) {
      setError("Email e senha sao obrigatorios.");
      return;
    }
    setLoading(true);
    try {
      const result = await api.login(email.trim(), senha);
      saveSession(result.access_token, result.usuario);
      onLogin(result.usuario);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "API indisponivel.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="loginPage">
      <form className="loginPanel" onSubmit={submit}>
        <div>
          <span className="eyebrow">MoviProgy</span>
          <h1>Acesso administrativo</h1>
        </div>
        <label>
          Email
          <input
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            type="email"
            autoComplete="username"
          />
        </label>
        <label>
          Senha
          <input
            value={senha}
            onChange={(event) => setSenha(event.target.value)}
            type="password"
            autoComplete="current-password"
          />
        </label>
        {error && <div className="state stateError">{error}</div>}
        <button className="primaryButton" disabled={loading}>
          <LogIn size={18} />
          {loading ? "Entrando..." : "Entrar"}
        </button>
      </form>
    </main>
  );
}
