import {
  Activity,
  Database,
  FileVideo,
  Gauge,
  HardDrive,
  ListVideo,
  LogOut,
  Monitor,
  Settings,
  Shield,
  Users
} from "lucide-react";
import type { ComponentType, ReactNode } from "react";
import type { User } from "../lib/types";

export type ViewKey =
  | "dashboard"
  | "clientes"
  | "dispositivos"
  | "midias"
  | "playlists"
  | "sincronizacoes"
  | "logs"
  | "google"
  | "usuarios"
  | "configuracoes";

const menu: { key: ViewKey; label: string; icon: ComponentType<{ size?: number }> }[] = [
  { key: "dashboard", label: "Dashboard", icon: Gauge },
  { key: "clientes", label: "Clientes", icon: Database },
  { key: "dispositivos", label: "Dispositivos", icon: Monitor },
  { key: "midias", label: "Midias", icon: FileVideo },
  { key: "playlists", label: "Playlists", icon: ListVideo },
  { key: "sincronizacoes", label: "Sincronizacoes", icon: Activity },
  { key: "logs", label: "Logs", icon: Shield },
  { key: "google", label: "Google Drive", icon: HardDrive },
  { key: "usuarios", label: "Usuarios", icon: Users },
  { key: "configuracoes", label: "Configuracoes", icon: Settings }
];

type ShellProps = {
  user: User;
  view: ViewKey;
  onViewChange: (view: ViewKey) => void;
  onLogout: () => void;
  children: ReactNode;
};

export function Shell({ user, view, onViewChange, onLogout, children }: ShellProps) {
  return (
    <div className="appShell">
      <aside className="sidebar">
        <div className="brand">
          <strong>MoviProgy</strong>
          <span>Painel admin</span>
        </div>
        <nav>
          {menu.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.key}
                className={view === item.key ? "navItem active" : "navItem"}
                onClick={() => onViewChange(item.key)}
                title={item.label}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>
      <main className="workspace">
        <header className="topbar">
          <div>
            <strong>{user.nome}</strong>
            <span>{user.email} - {user.perfil}</span>
          </div>
          <button className="iconTextButton" onClick={onLogout}>
            <LogOut size={18} />
            Sair
          </button>
        </header>
        {children}
      </main>
    </div>
  );
}
