import { useEffect, useState } from "react";
import type { ComponentType } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Cloud,
  Database,
  FileVideo,
  Monitor,
  Router,
  ShieldAlert,
  Users
} from "lucide-react";
import { api } from "../lib/api";
import type { AdminAudit, Cliente, Dispositivo, Midia, Playlist } from "../lib/types";

type DashboardState = {
  clientes: Cliente[];
  dispositivos: Dispositivo[];
  midias: Midia[];
  playlists: Playlist[];
  auditoria: AdminAudit[];
};

export function DashboardPage() {
  const [data, setData] = useState<DashboardState>({
    clientes: [],
    dispositivos: [],
    midias: [],
    playlists: [],
    auditoria: []
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.clientes(), api.dispositivos(), api.midias(), api.playlists(), api.auditoria()])
      .then(([clientes, dispositivos, midias, playlists, auditoria]) => {
        setData({
          clientes: clientes.items,
          dispositivos: dispositivos.items,
          midias: midias.items,
          playlists: playlists.items,
          auditoria: auditoria.items
        });
      })
      .catch(() => setError("Falha ao carregar indicadores."))
      .finally(() => setLoading(false));
  }, []);

  const activeClientes = data.clientes.filter((item) => item.ativo).length;
  const activeDevices = data.dispositivos.filter((item) => !item.bloqueado).length;
  const blockedDevices = data.dispositivos.filter((item) => item.bloqueado);
  const activePlaylists = data.playlists.filter((item) => item.ativa).length;
  const inactiveMedia = data.midias.filter((item) => !item.ativo).length;
  const noPlaylistDevices = data.dispositivos.filter((item) => !item.playlist_atual_id);
  const deniedAudits = data.auditoria.filter((item) => item.status !== "permitido");

  return (
    <section className="page overviewPage">
      <div className="overviewHeader">
        <div>
          <h1>Visao geral da infraestrutura</h1>
          <p>Indicadores operacionais calculados a partir dos dados reais da API.</p>
        </div>
        <div className="systemBadge">
          <span></span>
          API conectada
        </div>
      </div>
      {loading && <div className="state">Carregando indicadores...</div>}
      {error && <div className="state stateError">{error}</div>}
      {!loading && !error && (
        <>
          <div className="overviewMetrics">
            <OverviewCard
              icon={Users}
              label="Clientes ativos"
              value={activeClientes}
              helper={`${data.clientes.length} clientes cadastrados`}
              tone="primary"
            />
            <OverviewCard
              icon={CheckCircle2}
              label="Playlists ativas"
              value={activePlaylists}
              helper={`${data.playlists.length} playlists cadastradas`}
              tone="success"
            />
            <OverviewCard
              icon={Router}
              label="Dispositivos ativos"
              value={activeDevices}
              helper={`${data.dispositivos.length} dispositivos cadastrados`}
              tone="neutral"
            />
            <OverviewCard
              icon={ShieldAlert}
              label="Bloqueados"
              value={blockedDevices.length}
              helper="Dispositivos impedidos de ativar"
              tone="danger"
            />
          </div>

          <div className="overviewGrid">
            <div className="overviewPanel wide">
              <div className="panelHeader">
                <div>
                  <h2>Ultimos eventos administrativos</h2>
                  <p>Fonte: auditoria RBAC do backend.</p>
                </div>
                <button type="button" disabled>Ver logs</button>
              </div>
              {data.auditoria.length === 0 ? (
                <div className="emptyPanel">Nenhum evento de auditoria encontrado.</div>
              ) : (
                <div className="eventTableWrap">
                  <table className="eventTable">
                    <thead>
                      <tr>
                        <th>Evento</th>
                        <th>Usuario</th>
                        <th>Status</th>
                        <th>Data</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.auditoria.slice(0, 6).map((item, index) => (
                        <tr key={`${item.user_id}-${item.recurso}-${item.acao}-${index}`}>
                          <td>
                            <span className="eventIcon"><Database size={18} /></span>
                            {item.recurso}:{item.acao}
                          </td>
                          <td><code>{item.user_id}</code></td>
                          <td>
                            <span className={item.status === "permitido" ? "eventStatus ok" : "eventStatus danger"}>
                              {item.status}
                            </span>
                          </td>
                          <td>{formatDate(item.created_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            <div className="overviewPanel">
              <div className="panelHeader compact">
                <div>
                  <h2>Alertas recentes</h2>
                  <p>Somente dados verificaveis.</p>
                </div>
                <span>{blockedDevices.length + noPlaylistDevices.length + inactiveMedia + deniedAudits.length}</span>
              </div>
              <div className="alertList">
                {blockedDevices.slice(0, 2).map((item) => (
                  <AlertItem
                    key={`blocked-${item.id}`}
                    icon={AlertTriangle}
                    title="Dispositivo bloqueado"
                    text={`${item.nome} nao pode ativar enquanto estiver bloqueado.`}
                    tone="danger"
                  />
                ))}
                {noPlaylistDevices.slice(0, 2).map((item) => (
                  <AlertItem
                    key={`playlist-${item.id}`}
                    icon={Monitor}
                    title="Sem playlist vinculada"
                    text={`${item.nome} ainda nao possui playlist atual.`}
                    tone="primary"
                  />
                ))}
                {inactiveMedia > 0 && (
                  <AlertItem
                    icon={FileVideo}
                    title="Midias inativas"
                    text={`${inactiveMedia} midia(s) estao inativas no cadastro.`}
                    tone="neutral"
                  />
                )}
                {deniedAudits.length > 0 && (
                  <AlertItem
                    icon={ShieldAlert}
                    title="Acesso negado registrado"
                    text={`${deniedAudits.length} evento(s) de auditoria com status diferente de permitido.`}
                    tone="danger"
                  />
                )}
                {blockedDevices.length + noPlaylistDevices.length + inactiveMedia + deniedAudits.length === 0 && (
                  <div className="emptyPanel">Nenhum alerta operacional nos dados carregados.</div>
                )}
              </div>
              <div className="geoPanel">
                <Cloud size={32} />
                <div>
                  <strong>Distribuicao geografica</strong>
                  <span>Mapa depende de endpoint de localizacao dos players.</span>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </section>
  );
}

export function PageTitle({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className="pageTitle">
      <h1>{title}</h1>
      <p>{subtitle}</p>
    </div>
  );
}

function OverviewCard({
  icon: Icon,
  label,
  value,
  helper,
  tone
}: {
  icon: ComponentType<{ size?: number }>;
  label: string;
  value: number;
  helper: string;
  tone: "primary" | "success" | "danger" | "neutral";
}) {
  return (
    <div className={`overviewCard ${tone}`}>
      <div className="overviewIcon"><Icon size={28} /></div>
      <span>{label}</span>
      <strong>{value}</strong>
      <p>{helper}</p>
      <svg viewBox="0 0 100 24" preserveAspectRatio="none" aria-hidden="true">
        <path d="M0 18 Q12 8 24 15 T48 10 T72 16 T100 7" />
      </svg>
    </div>
  );
}

function AlertItem({
  icon: Icon,
  title,
  text,
  tone
}: {
  icon: ComponentType<{ size?: number }>;
  title: string;
  text: string;
  tone: "primary" | "danger" | "neutral";
}) {
  return (
    <div className={`alertItem ${tone}`}>
      <Icon size={22} />
      <div>
        <strong>{title}</strong>
        <p>{text}</p>
      </div>
    </div>
  );
}

function formatDate(value?: string | null) {
  if (!value) return "Nao informado";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Nao informado";
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short"
  }).format(date);
}
