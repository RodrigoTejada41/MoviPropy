import { FormEvent, useState } from "react";
import { ArrowRight, Cloud, Eye, EyeOff, LockKeyhole, Mail, ShieldCheck } from "lucide-react";
import { api, ApiError } from "../lib/api";
import { saveSession } from "../lib/session";
import type { User } from "../lib/types";

type LoginPageProps = {
  onLogin: (user: User) => void;
};

export function LoginPage({ onLogin }: LoginPageProps) {
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);

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
      <section className="loginStage" aria-label="Acesso administrativo MoviProgy">
        <div className="loginColumn">
          <div className="loginBrand">
            <img className="loginLogo" src="/moviprogy-brand.webp" alt="MoviProgy Tecnologia" />
            <h1>MoviProgy</h1>
            <p>Console administrativo SaaS</p>
          </div>

          <form className="loginPanel" onSubmit={submit}>
            <label>
              Email
              <span className="inputIcon">
                <Mail size={19} aria-hidden="true" />
                <input
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  type="email"
                  autoComplete="username"
                  placeholder="admin@moviprogy.local"
                />
              </span>
            </label>
            <label>
              Senha
              <span className="inputIcon">
                <LockKeyhole size={19} aria-hidden="true" />
                <input
                  value={senha}
                  onChange={(event) => setSenha(event.target.value)}
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  placeholder="senha"
                />
                <button
                  className="inputAction"
                  onClick={() => setShowPassword((current) => !current)}
                  type="button"
                  title={showPassword ? "Ocultar senha" : "Mostrar senha"}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </span>
            </label>

            <div className="loginOptions">
              <label className="checkLabel">
                <input type="checkbox" />
                Manter conectado
              </label>
              <button className="linkButton" type="button" disabled>
                Recuperar senha
              </button>
            </div>

            {error && <div className="state stateError">{error}</div>}

            <button className="primaryButton loginSubmit" disabled={loading}>
              {loading ? "Autenticando..." : "Entrar"}
              <ArrowRight size={18} />
            </button>

            <div className="loginDivider">
              <span>SSO futuro</span>
            </div>

            <div className="ssoGrid">
              <button type="button" disabled>Google</button>
              <button type="button" disabled>Meta</button>
            </div>
          </form>

          <div className="loginBadges" aria-label="Caracteristicas operacionais">
            <span><ShieldCheck size={16} /> Seguro</span>
            <span><Cloud size={16} /> Online</span>
          </div>
        </div>

        <aside className="loginVisual" aria-label="Orquestracao de midia indoor">
          <img className="loginHeroImage" src="/moviprogy-brand.webp" alt="" aria-hidden="true" />
          <blockquote>
            <p>Orquestracao de campanhas, playlists e dispositivos em uma operacao centralizada.</p>
            <footer>MoviProgy Admin</footer>
          </blockquote>
        </aside>
      </section>
    </main>
  );
}
