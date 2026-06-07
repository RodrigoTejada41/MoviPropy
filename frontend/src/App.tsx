import { useEffect, useState } from "react";
import { Shell, type ViewKey } from "./components/Shell";
import { api, SESSION_EXPIRED_EVENT } from "./lib/api";
import { clearSession, getUser } from "./lib/session";
import type { User } from "./lib/types";
import { DashboardPage } from "./pages/DashboardPage";
import { LoginPage } from "./pages/LoginPage";
import {
  AuditoriaPage,
  ClientesPage,
  ConfiguracoesPage,
  DispositivosPage,
  GoogleDrivePage,
  MidiasPage,
  PlaceholderPage,
  PlaylistsPage,
  SincronizacoesPage,
  UsuariosPage
} from "./pages/ListPages";

export function App() {
  const [user, setUser] = useState<User | null>(() => getUser());
  const [view, setView] = useState<ViewKey>("dashboard");

  useEffect(() => {
    function expireSession() {
      setUser(null);
      setView("dashboard");
    }
    window.addEventListener(SESSION_EXPIRED_EVENT, expireSession);
    return () => window.removeEventListener(SESSION_EXPIRED_EVENT, expireSession);
  }, []);

  async function logout() {
    await api.logout().catch(() => undefined);
    clearSession();
    setUser(null);
  }

  if (!user) return <LoginPage onLogin={setUser} />;

  return (
    <Shell user={user} view={view} onViewChange={setView} onLogout={logout}>
      {renderView(view)}
    </Shell>
  );
}

function renderView(view: ViewKey) {
  if (view === "dashboard") return <DashboardPage />;
  if (view === "clientes") return <ClientesPage />;
  if (view === "dispositivos") return <DispositivosPage />;
  if (view === "midias") return <MidiasPage />;
  if (view === "playlists") return <PlaylistsPage />;
  if (view === "usuarios") return <UsuariosPage />;
  if (view === "logs") return <AuditoriaPage />;
  if (view === "sincronizacoes") return <SincronizacoesPage />;
  if (view === "google") {
    return <GoogleDrivePage />;
  }
  return <ConfiguracoesPage />;
}
