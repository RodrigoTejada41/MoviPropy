import { useState } from "react";
import { Shell, type ViewKey } from "./components/Shell";
import { api } from "./lib/api";
import { clearSession, getUser } from "./lib/session";
import type { User } from "./lib/types";
import { DashboardPage } from "./pages/DashboardPage";
import { LoginPage } from "./pages/LoginPage";
import {
  AuditoriaPage,
  ClientesPage,
  DispositivosPage,
  GoogleDrivePage,
  MidiasPage,
  PlaceholderPage,
  PlaylistsPage,
  UsuariosPage
} from "./pages/ListPages";

export function App() {
  const [user, setUser] = useState<User | null>(() => getUser());
  const [view, setView] = useState<ViewKey>("dashboard");

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
  if (view === "sincronizacoes") {
    return <PlaceholderPage title="Sincronizacoes" subtitle="Tela depende de endpoint administrativo especifico de sincronizacoes." />;
  }
  if (view === "google") {
    return <GoogleDrivePage />;
  }
  return <PlaceholderPage title="Configuracoes" subtitle="Parametros operacionais ainda nao possuem endpoints de alteracao." />;
}
