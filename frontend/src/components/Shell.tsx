import {
  Activity,
  Bell,
  Database,
  FileVideo,
  Gauge,
  HardDrive,
  HelpCircle,
  ListVideo,
  LogOut,
  Monitor,
  Search,
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
          <span>Console administrativo</span>
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
        <div className="sideProfile">
          <div className="avatar">{user.nome.slice(0, 1).toUpperCase()}</div>
          <div>
            <strong>{user.nome}</strong>
            <span>{user.perfil}</span>
          </div>
        </div>
      </aside>
      <main className="workspace">
        <header className="topbar">
          <div className="topSearch">
            <Search size={18} />
            <input placeholder="Buscar dispositivos, clientes, playlists..." type="search" />
          </div>
          <div className="topActions">
            <button className="iconTextButton topGhost" type="button" disabled>
              <HelpCircle size={18} />
              Suporte
            </button>
            <button className="roundButton" type="button" disabled title="Notificacoes">
              <Bell size={18} />
              <span></span>
            </button>
            <div className="topUser">
              <strong>{user.nome}</strong>
              <span>{user.email}</span>
            </div>
            <button className="iconTextButton" onClick={onLogout}>
              <LogOut size={18} />
              Sair
            </button>
          </div>
        </header>
        {children}
      </main>
    </div>
  );
}
