import { FormEvent, ReactNode, useEffect, useState } from "react";
import {
  AlertTriangle,
  Building2,
  CheckCircle2,
  Cloud,
  Download,
  Filter,
  Folder,
  Monitor,
  MoreVertical,
  PlayCircle,
  Plus,
  QrCode,
  RefreshCw,
  RotateCcw,
  Search,
  ShieldCheck,
  Tv,
  UploadCloud,
  Users
} from "lucide-react";
import { api, ApiError } from "../lib/api";
import { DataTable } from "../components/DataTable";
import { Status } from "../components/Status";
import type { AdminAudit, Cliente, Dispositivo, Midia, PageResult, Playlist, User } from "../lib/types";
import { PageTitle } from "./DashboardPage";

function useList<T>(loader: () => Promise<PageResult<T>>) {
  const [rows, setRows] = useState<T[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const result = await loader();
      setRows(result.items);
      setTotal(result.total);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Falha ao carregar dados.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return { rows, total, loading, error, reload: load };
}

export function ClientesPage() {
  const list = useList(api.clientes);
  const devices = useList(api.dispositivos);
  const [form, setForm] = useState({ id: "", nome: "", documento: "" });
  const [message, setMessage] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("todos");

  async function submit(event: FormEvent) {
    event.preventDefault();
    setMessage(null);
    if (!form.id.trim() || !form.nome.trim()) {
      setMessage("Id e nome sao obrigatorios.");
      return;
    }
    try {
      await api.criarCliente({ id: form.id.trim(), nome: form.nome.trim(), documento: form.documento || null, ativo: true });
      setForm({ id: "", nome: "", documento: "" });
      await list.reload();
      await devices.reload();
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Falha ao criar cliente.");
    }
  }

  const filteredRows = list.rows.filter((item) => {
    const term = search.trim().toLowerCase();
    const matchesSearch = !term || [item.id, item.nome, item.documento ?? ""].some((value) => value.toLowerCase().includes(term));
    const matchesStatus =
      statusFilter === "todos" ||
      (statusFilter === "ativos" && item.ativo) ||
      (statusFilter === "inativos" && !item.ativo);
    return matchesSearch && matchesStatus;
  });
  const activeClients = list.rows.filter((item) => item.ativo).length;
  const activeDevices = devices.rows.filter((item) => !item.bloqueado).length;
  const blockedDevices = devices.rows.filter((item) => item.bloqueado).length;
  const clientsWithDevices = list.rows.filter((client) => devices.rows.some((device) => device.cliente_id === client.id)).length;

  function countDevices(clienteId: string) {
    return devices.rows.filter((device) => device.cliente_id === clienteId).length;
  }

  function initials(name: string) {
    return name
      .split(" ")
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase())
      .join("") || "CL";
  }

  return (
    <section className="page clientsPage">
      <div className="clientsHeader">
        <div>
          <div className="breadcrumb">
            <span>Console</span>
            <span>/</span>
            <strong>Clientes</strong>
          </div>
          <h1>Gestao de clientes</h1>
          <p>Controle a base de contratantes e o vinculo operacional dos dispositivos.</p>
        </div>
        <div className="clientActions">
          <button className="secondaryButton" type="button" disabled><Download size={17} />Exportar</button>
          <a className="primaryButton" href="#novo-cliente"><Plus size={17} />Adicionar cliente</a>
        </div>
      </div>

      <div className="clientStats">
        <ClientStat icon={<Users size={22} />} label="Total de clientes" value={list.total} tone="primary" />
        <ClientStat icon={<CheckCircle2 size={22} />} label="Clientes ativos" value={activeClients} tone="success" />
        <ClientStat icon={<Monitor size={22} />} label="Dispositivos ativos" value={activeDevices} tone="neutral" />
        <ClientStat icon={<AlertTriangle size={22} />} label="Dispositivos bloqueados" value={blockedDevices} tone="danger" />
      </div>

      <form className="clientForm" id="novo-cliente" onSubmit={submit}>
        <div>
          <h2>Novo cliente</h2>
          <p>Cadastre o identificador usado nas rotas administrativas e no isolamento de dados.</p>
        </div>
        <input placeholder="id" value={form.id} onChange={(event) => setForm({ ...form, id: event.target.value })} />
        <input placeholder="nome" value={form.nome} onChange={(event) => setForm({ ...form, nome: event.target.value })} />
        <input placeholder="documento" value={form.documento} onChange={(event) => setForm({ ...form, documento: event.target.value })} />
        <button className="primaryButton"><Plus size={16} />Criar</button>
      </form>
      {message && <Status error={message} />}

      <div className="clientTableCard">
        <div className="clientTableHeader">
          <div>
            <strong>Clientes cadastrados</strong>
            <span>{filteredRows.length} exibidos de {list.total}. {clientsWithDevices} com dispositivo vinculado.</span>
          </div>
          <div className="clientFilters">
            <label className="clientSearch">
              <Search size={17} />
              <input
                placeholder="Buscar por nome, id ou documento"
                type="search"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
              />
            </label>
            <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
              <option value="todos">Todos os status</option>
              <option value="ativos">Ativos</option>
              <option value="inativos">Inativos</option>
            </select>
            <button className="secondaryButton" type="button" disabled><Filter size={17} />Regiao indisponivel</button>
          </div>
        </div>
        <Status
          loading={list.loading || devices.loading}
          error={list.error ?? devices.error}
          empty={!list.loading && !devices.loading && !list.error && !devices.error && filteredRows.length === 0}
        />
        {!list.loading && !devices.loading && !list.error && !devices.error && filteredRows.length > 0 && (
          <div className="clientTableWrap">
            <table className="clientTable">
              <thead>
                <tr>
                  <th>Cliente</th>
                  <th>Status</th>
                  <th>Dispositivos</th>
                  <th>Sincronizacao</th>
                  <th>Documento</th>
                  <th>Acoes</th>
                </tr>
              </thead>
              <tbody>
                {filteredRows.map((item) => {
                  const totalDevices = countDevices(item.id);
                  return (
                    <tr key={item.id}>
                      <td>
                        <div className="clientName">
                          <div className="clientAvatar">{initials(item.nome)}</div>
                          <div>
                            <strong>{item.nome}</strong>
                            <span>ID: {item.id}</span>
                          </div>
                        </div>
                      </td>
                      <td>
                        <span className={item.ativo ? "statusPill success" : "statusPill danger"}>
                          <i></i>{item.ativo ? "Ativo" : "Inativo"}
                        </span>
                      </td>
                      <td>
                        <div className="deviceMeter">
                          <Building2 size={18} />
                          <strong>{totalDevices}</strong>
                          <span>{totalDevices === 1 ? "dispositivo" : "dispositivos"}</span>
                        </div>
                      </td>
                      <td><span className="mutedCell">Nao informado</span></td>
                      <td>{item.documento || <span className="mutedCell">Nao informado</span>}</td>
                      <td>
                        <button className="tableIconButton" type="button" disabled title="Detalhes dependem de endpoint de atualizacao">
                          <MoreVertical size={18} />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
        <div className="clientPager">
          <span>Pagina unica com limite atual da API.</span>
          <div>
            <button type="button" disabled>Anterior</button>
            <button type="button" disabled>Proxima</button>
          </div>
        </div>
      </div>
    </section>
  );
}

function ClientStat({ icon, label, value, tone }: { icon: ReactNode; label: string; value: number; tone: "primary" | "success" | "danger" | "neutral" }) {
  return (
    <div className={`clientStat ${tone}`}>
      <div>{icon}</div>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

export function DispositivosPage() {
  const list = useList(api.dispositivos);
  const [form, setForm] = useState({ id: "", cliente_id: "", nome: "", codigo_ativacao: "" });
  const [message, setMessage] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    setMessage(null);
    if (!form.id.trim() || !form.cliente_id.trim() || !form.nome.trim() || !form.codigo_ativacao.trim()) {
      setMessage("Id, cliente, nome e codigo sao obrigatorios.");
      return;
    }
    try {
      await api.criarDispositivo({ ...form, bloqueado: false, playlist_atual_id: null });
      setForm({ id: "", cliente_id: "", nome: "", codigo_ativacao: "" });
      await list.reload();
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Falha ao criar dispositivo.");
    }
  }

  const filteredRows = list.rows.filter((item) => {
    const term = search.trim().toLowerCase();
    if (!term) return true;
    return [item.id, item.nome, item.cliente_id, item.codigo_ativacao, item.playlist_atual_id ?? ""]
      .some((value) => value.toLowerCase().includes(term));
  });
  const blocked = list.rows.filter((item) => item.bloqueado).length;
  const active = list.rows.length - blocked;
  const withPlaylist = list.rows.filter((item) => item.playlist_atual_id).length;
  const withoutPlaylist = list.rows.length - withPlaylist;

  return (
    <section className="page fleetPage">
      <div className="fleetHeader">
        <div>
          <div className="breadcrumb">
            <span>Inventario</span>
            <span>/</span>
            <strong>Dispositivos</strong>
          </div>
          <h1>Gestao da frota de dispositivos</h1>
          <p>Monitore, cadastre e acompanhe players do sistema de midia indoor.</p>
        </div>
        <div className="fleetActions">
          <button className="secondaryButton" type="button" disabled><Filter size={17} />Filtros</button>
          <button className="secondaryButton" type="button" disabled><Download size={17} />Exportar</button>
          <a className="primaryButton" href="#novo-dispositivo"><Plus size={17} />Cadastrar</a>
        </div>
      </div>

      <div className="fleetStats">
        <FleetStat label="Total cadastrado" value={list.total} tone="primary" />
        <FleetStat label="Ativos" value={active} tone="success" />
        <FleetStat label="Bloqueados" value={blocked} tone="danger" />
        <FleetStat label="Sem playlist" value={withoutPlaylist} tone="neutral" />
      </div>

      <form className="fleetForm" id="novo-dispositivo" onSubmit={submit}>
        <div>
          <h2>Novo dispositivo</h2>
          <p>Use codigo unico de ativacao gerado para o player.</p>
        </div>
        <input placeholder="id" value={form.id} onChange={(event) => setForm({ ...form, id: event.target.value })} />
        <input placeholder="cliente_id" value={form.cliente_id} onChange={(event) => setForm({ ...form, cliente_id: event.target.value })} />
        <input placeholder="nome" value={form.nome} onChange={(event) => setForm({ ...form, nome: event.target.value })} />
        <input placeholder="codigo_ativacao" value={form.codigo_ativacao} onChange={(event) => setForm({ ...form, codigo_ativacao: event.target.value })} />
        <button className="primaryButton"><Plus size={16} />Criar</button>
      </form>
      {message && <Status error={message} />}

      <div className="fleetTableCard">
        <div className="fleetTableHeader">
          <div>
            <strong>Frota ativa</strong>
            <span>{filteredRows.length} exibidos de {list.total}</span>
          </div>
          <input
            className="fleetSearch"
            placeholder="Buscar por nome, id, cliente ou codigo"
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>
        <Status loading={list.loading} error={list.error} empty={!list.loading && !list.error && filteredRows.length === 0} />
        {!list.loading && !list.error && filteredRows.length > 0 && (
          <div className="fleetTableWrap">
            <table className="fleetTable">
              <thead>
                <tr>
                  <th>Nome e ID</th>
                  <th>Cliente</th>
                  <th>Codigo</th>
                  <th>Playlist atual</th>
                  <th>Ultimo acesso</th>
                  <th>Status</th>
                  <th>Acoes</th>
                </tr>
              </thead>
              <tbody>
                {filteredRows.map((item) => (
                  <tr key={item.id} className={item.bloqueado ? "blockedRow" : ""}>
                    <td>
                      <div className="deviceName">
                        <div className={item.bloqueado ? "deviceIcon danger" : "deviceIcon"}>
                          {item.bloqueado ? <RotateCcw size={20} /> : <Tv size={20} />}
                        </div>
                        <div>
                          <strong>{item.nome}</strong>
                          <span>ID: {item.id}</span>
                        </div>
                      </div>
                    </td>
                    <td>{item.cliente_id}</td>
                    <td><code>{item.codigo_ativacao}</code></td>
                    <td>
                      {item.playlist_atual_id ? (
                        <span className="playlistPill"><PlayCircle size={17} />{item.playlist_atual_id}</span>
                      ) : (
                        <span className="mutedCell">Sem playlist</span>
                      )}
                    </td>
                    <td><span className="mutedCell">Nao informado</span></td>
                    <td>
                      <span className={item.bloqueado ? "statusPill danger" : "statusPill success"}>
                        <i></i>{item.bloqueado ? "Bloqueado" : "Ativo"}
                      </span>
                    </td>
                    <td>
                      <button className="tableIconButton" type="button" disabled title="Configuracoes pendentes">
                        <Monitor size={18} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="fleetHelpGrid">
        <div className="fleetHelp">
          <QrCode size={28} />
          <h2>Provisionamento em lote</h2>
          <p>Importacao CSV e app de provisionamento ainda dependem de contrato backend.</p>
          <button type="button" disabled>Planejado</button>
        </div>
        <div className="fleetHelp">
          <ShieldCheck size={28} />
          <h2>Politica de seguranca</h2>
          <p>Dispositivos bloqueados nao ativam pelo fluxo real do backend.</p>
          <button type="button" disabled>Somente leitura</button>
        </div>
      </div>
    </section>
  );
}

function FleetStat({ label, value, tone }: { label: string; value: number; tone: "primary" | "success" | "danger" | "neutral" }) {
  return (
    <div className={`fleetStat ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

export function MidiasPage() {
  const list = useList(api.midias);
  return (
    <section className="page">
      <PageTitle title="Midias" subtitle={`${list.total} registros encontrados. Upload fisico sera a proxima acao da tela.`} />
      <DataTable<Midia>
        rows={list.rows}
        loading={list.loading}
        error={list.error}
        columns={[
          { key: "id", label: "Id", render: (item) => item.id },
          { key: "cliente", label: "Cliente", render: (item) => item.cliente_id },
          { key: "nome", label: "Nome", render: (item) => item.nome },
          { key: "tipo", label: "Tipo", render: (item) => item.tipo },
          { key: "tamanho", label: "Tamanho", render: (item) => item.tamanho },
          { key: "ativo", label: "Ativo", render: (item) => item.ativo }
        ]}
      />
    </section>
  );
}

export function PlaylistsPage() {
  const list = useList(api.playlists);
  return (
    <section className="page">
      <PageTitle title="Playlists" subtitle={`${list.total} registros encontrados.`} />
      <DataTable<Playlist>
        rows={list.rows}
        loading={list.loading}
        error={list.error}
        columns={[
          { key: "id", label: "Id", render: (item) => item.id },
          { key: "cliente", label: "Cliente", render: (item) => item.cliente_id },
          { key: "nome", label: "Nome", render: (item) => item.nome },
          { key: "versao", label: "Versao", render: (item) => item.versao },
          { key: "ativa", label: "Ativa", render: (item) => item.ativa }
        ]}
      />
    </section>
  );
}

export function UsuariosPage() {
  const list = useList(api.usuarios);
  return (
    <section className="page">
      <PageTitle title="Usuarios e permissoes" subtitle={`${list.total} usuarios encontrados.`} />
      <DataTable<User>
        rows={list.rows}
        loading={list.loading}
        error={list.error}
        columns={[
          { key: "id", label: "Id", render: (item) => item.id },
          { key: "nome", label: "Nome", render: (item) => item.nome },
          { key: "email", label: "Email", render: (item) => item.email },
          { key: "perfil", label: "Perfil", render: (item) => item.perfil },
          { key: "ativo", label: "Ativo", render: (item) => item.ativo }
        ]}
      />
    </section>
  );
}

export function AuditoriaPage() {
  const list = useList(api.auditoria);
  return (
    <section className="page">
      <PageTitle title="Logs" subtitle={`${list.total} eventos administrativos encontrados.`} />
      <DataTable<AdminAudit>
        rows={list.rows}
        loading={list.loading}
        error={list.error}
        columns={[
          { key: "user", label: "Usuario", render: (item) => item.user_id },
          { key: "recurso", label: "Recurso", render: (item) => item.recurso },
          { key: "acao", label: "Acao", render: (item) => item.acao },
          { key: "status", label: "Status", render: (item) => item.status },
          { key: "data", label: "Data", render: (item) => item.created_at }
        ]}
      />
    </section>
  );
}

export function GoogleDrivePage() {
  const clientes = useList(api.clientes);
  const [statusData, setStatusData] = useState<Awaited<ReturnType<typeof api.googleDriveStatus>> | null>(null);
  const [folders, setFolders] = useState<Awaited<ReturnType<typeof api.googleDriveFolders>>["items"]>([]);
  const [files, setFiles] = useState<Awaited<ReturnType<typeof api.googleDriveFiles>>["items"]>([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<string | null>(null);
  const [rootForm, setRootForm] = useState({ folder_id: "", folder_name: "MoviProgy_Midias", create_if_missing: true });
  const [clientFolderForm, setClientFolderForm] = useState({ cliente_id: "", folder_id: "", folder_name: "" });
  const [importForm, setImportForm] = useState({
    cliente_id: "",
    file_id: "",
    tipo: "video",
    nome: "",
    tamanho: "",
    sha256: "",
    folder_id: "",
    google_drive_mime_type: "",
    google_drive_web_view_link: ""
  });

  async function load() {
    setLoading(true);
    setMessage(null);
    try {
      const [statusResult, folderResult, fileResult] = await Promise.all([
        api.googleDriveStatus(),
        api.googleDriveFolders().catch(() => ({ items: [] })),
        api.googleDriveFiles().catch(() => ({ items: [] }))
      ]);
      setStatusData(statusResult);
      setFolders(folderResult.items);
      setFiles(fileResult.items);
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Falha ao carregar Google Drive.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function connect() {
    setMessage(null);
    try {
      const result = await api.googleDriveConnect();
      window.location.href = result.authorization_url;
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Falha ao iniciar OAuth.");
    }
  }

  async function disconnect() {
    setMessage(null);
    try {
      await api.googleDriveDisconnect();
      await load();
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Falha ao desconectar.");
    }
  }

  async function validate() {
    setMessage(null);
    try {
      const result = await api.googleDriveValidate();
      setStatusData(result);
      setMessage("Validacao concluida.");
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Falha ao validar acesso.");
    }
  }

  async function saveRootFolder(event: FormEvent) {
    event.preventDefault();
    setMessage(null);
    try {
      await api.googleDriveRootFolder({
        folder_id: rootForm.folder_id || null,
        folder_name: rootForm.folder_name,
        create_if_missing: rootForm.create_if_missing
      });
      await load();
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Falha ao salvar pasta raiz.");
    }
  }

  async function saveClientFolder(event: FormEvent) {
    event.preventDefault();
    setMessage(null);
    if (!clientFolderForm.cliente_id) {
      setMessage("Cliente e obrigatorio.");
      return;
    }
    try {
      await api.googleDriveClientFolder({
        cliente_id: clientFolderForm.cliente_id,
        folder_id: clientFolderForm.folder_id || null,
        folder_name: clientFolderForm.folder_name || null
      });
      setClientFolderForm({ cliente_id: "", folder_id: "", folder_name: "" });
      await load();
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Falha ao salvar pasta do cliente.");
    }
  }

  async function importMedia(event: FormEvent) {
    event.preventDefault();
    setMessage(null);
    try {
      await api.googleDriveImportMedia({
        cliente_id: importForm.cliente_id,
        file_id: importForm.file_id,
        tipo: importForm.tipo,
        nome: importForm.nome,
        tamanho: Number(importForm.tamanho),
        sha256: importForm.sha256,
        folder_id: importForm.folder_id || null,
        google_drive_mime_type: importForm.google_drive_mime_type || null,
        google_drive_web_view_link: importForm.google_drive_web_view_link || null
      });
      setImportForm({ ...importForm, file_id: "", nome: "", tamanho: "", sha256: "", google_drive_web_view_link: "" });
      await load();
      setMessage("Midia importada.");
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Falha ao importar midia.");
    }
  }

  const connected = statusData?.connected === true;

  return (
    <section className="page drivePage">
      <div className="driveHeader">
        <div>
          <div className="breadcrumb">
            <span>Integracoes</span>
            <span>/</span>
            <strong>Google Drive</strong>
          </div>
          <h1>Google Drive / Armazenamento</h1>
          <p>Conecte uma conta Google, organize pastas por cliente e importe arquivos para midias.</p>
        </div>
        <div className="driveActions">
          <button className="secondaryButton" type="button" onClick={validate} disabled={!connected || loading}><RefreshCw size={17} />Validar</button>
          {connected ? (
            <button className="secondaryButton" type="button" onClick={disconnect}><Cloud size={17} />Desconectar</button>
          ) : (
            <button className="primaryButton" type="button" onClick={connect}><Cloud size={17} />Conectar</button>
          )}
        </div>
      </div>

      {message && <Status error={message} />}
      <Status loading={loading} empty={!loading && !statusData} />

      <div className="driveStatusGrid">
        <div className={connected ? "driveStatusCard connected" : "driveStatusCard"}>
          <div className="driveStatusIcon"><Cloud size={28} /></div>
          <span>Status</span>
          <strong>{statusData?.status ?? "desconectado"}</strong>
          <p>{statusData?.email ?? "Nenhuma conta conectada."}</p>
        </div>
        <div className={statusData?.oauth_configured ? "driveStatusCard connected" : "driveStatusCard"}>
          <div className="driveStatusIcon"><ShieldCheck size={28} /></div>
          <span>OAuth</span>
          <strong>{statusData?.oauth_simulated ? "Simulado" : statusData?.oauth_configured ? "Configurado" : "Incompleto"}</strong>
          <p>
            {statusData?.missing_config?.length
              ? `Falta: ${statusData.missing_config.join(", ")}`
              : "Config do Google pronta no backend."}
          </p>
        </div>
        <div className="driveStatusCard">
          <div className="driveStatusIcon"><Folder size={28} /></div>
          <span>Pasta raiz</span>
          <strong>{statusData?.root_folder_name ?? "Nao definida"}</strong>
          <p>{statusData?.root_folder_id ?? "Selecione ou crie a pasta raiz."}</p>
        </div>
        <div className="driveStatusCard">
          <div className="driveStatusIcon"><RefreshCw size={28} /></div>
          <span>Ultima validacao</span>
          <strong>{statusData?.last_validation_at ? new Date(statusData.last_validation_at).toLocaleString() : "Nao informado"}</strong>
          <p>Tokens e pastas sao validados pelo backend.</p>
        </div>
      </div>

      <div className="driveGrid">
        <form className="drivePanel" onSubmit={saveRootFolder}>
          <h2>Pasta raiz</h2>
          <input placeholder="folder_id existente" value={rootForm.folder_id} onChange={(event) => setRootForm({ ...rootForm, folder_id: event.target.value })} />
          <input placeholder="nome da pasta" value={rootForm.folder_name} onChange={(event) => setRootForm({ ...rootForm, folder_name: event.target.value })} />
          <label className="checkLabel">
            <input type="checkbox" checked={rootForm.create_if_missing} onChange={(event) => setRootForm({ ...rootForm, create_if_missing: event.target.checked })} />
            Criar id local para simulacao
          </label>
          <button className="primaryButton" disabled={!connected}><Folder size={16} />Salvar raiz</button>
        </form>

        <form className="drivePanel" onSubmit={saveClientFolder}>
          <h2>Pasta do cliente</h2>
          <select value={clientFolderForm.cliente_id} onChange={(event) => setClientFolderForm({ ...clientFolderForm, cliente_id: event.target.value })}>
            <option value="">Cliente</option>
            {clientes.rows.map((cliente) => <option key={cliente.id} value={cliente.id}>{cliente.nome}</option>)}
          </select>
          <input placeholder="folder_id opcional" value={clientFolderForm.folder_id} onChange={(event) => setClientFolderForm({ ...clientFolderForm, folder_id: event.target.value })} />
          <input placeholder="nome opcional" value={clientFolderForm.folder_name} onChange={(event) => setClientFolderForm({ ...clientFolderForm, folder_name: event.target.value })} />
          <button className="primaryButton" disabled={!connected}><Folder size={16} />Salvar pasta</button>
        </form>
      </div>

      <form className="driveImportPanel" onSubmit={importMedia}>
        <div>
          <h2>Importar arquivo do Drive</h2>
          <p>Use metadados conhecidos do arquivo. O player baixara sempre pelo backend.</p>
        </div>
        <select value={importForm.cliente_id} onChange={(event) => setImportForm({ ...importForm, cliente_id: event.target.value })}>
          <option value="">Cliente</option>
          {clientes.rows.map((cliente) => <option key={cliente.id} value={cliente.id}>{cliente.nome}</option>)}
        </select>
        <select value={importForm.tipo} onChange={(event) => setImportForm({ ...importForm, tipo: event.target.value })}>
          <option value="video">Video</option>
          <option value="imagem">Imagem</option>
        </select>
        <input placeholder="file_id" value={importForm.file_id} onChange={(event) => setImportForm({ ...importForm, file_id: event.target.value })} />
        <input placeholder="nome" value={importForm.nome} onChange={(event) => setImportForm({ ...importForm, nome: event.target.value })} />
        <input placeholder="tamanho bytes" type="number" value={importForm.tamanho} onChange={(event) => setImportForm({ ...importForm, tamanho: event.target.value })} />
        <input placeholder="sha256" value={importForm.sha256} onChange={(event) => setImportForm({ ...importForm, sha256: event.target.value })} />
        <input placeholder="folder_id" value={importForm.folder_id} onChange={(event) => setImportForm({ ...importForm, folder_id: event.target.value })} />
        <input placeholder="mime type" value={importForm.google_drive_mime_type} onChange={(event) => setImportForm({ ...importForm, google_drive_mime_type: event.target.value })} />
        <input placeholder="web view link" value={importForm.google_drive_web_view_link} onChange={(event) => setImportForm({ ...importForm, google_drive_web_view_link: event.target.value })} />
        <button className="primaryButton" disabled={!connected}><UploadCloud size={16} />Importar</button>
      </form>

      <div className="driveGrid">
        <div className="driveTableCard">
          <div className="fleetTableHeader">
            <div>
              <strong>Pastas registradas</strong>
              <span>{folders.length} registros locais da integracao</span>
            </div>
          </div>
          {folders.length === 0 ? <div className="emptyPanel">Nenhuma pasta registrada.</div> : (
            <div className="fleetTableWrap">
              <table className="driveTable">
                <thead><tr><th>Nome</th><th>ID</th><th>Cliente</th><th>Status</th></tr></thead>
                <tbody>
                  {folders.map((folder) => (
                    <tr key={`${folder.id}-${folder.cliente_id ?? "root"}`}>
                      <td>{folder.name}</td>
                      <td><code>{folder.id}</code></td>
                      <td>{folder.cliente_id ?? <span className="mutedCell">Raiz</span>}</td>
                      <td><span className="statusPill success"><i></i>{folder.status}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
        <div className="driveTableCard">
          <div className="fleetTableHeader">
            <div>
              <strong>Arquivos importados</strong>
              <span>{files.length} midias com origem Google Drive</span>
            </div>
          </div>
          {files.length === 0 ? <div className="emptyPanel">Nenhum arquivo importado.</div> : (
            <div className="fleetTableWrap">
              <table className="driveTable">
                <thead><tr><th>Nome</th><th>ID</th><th>Cliente</th><th>Link</th></tr></thead>
                <tbody>
                  {files.map((file) => (
                    <tr key={file.id}>
                      <td>{file.name}</td>
                      <td><code>{file.id}</code></td>
                      <td>{file.cliente_id}</td>
                      <td>{file.web_view_link ? <a href={file.web_view_link} target="_blank" rel="noreferrer">Abrir</a> : <span className="mutedCell">Nao informado</span>}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

export function PlaceholderPage({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <section className="page">
      <PageTitle title={title} subtitle={subtitle} />
      <div className="state">Funcionalidade aguardando contrato backend ou fase pos-MVP documentada.</div>
    </section>
  );
}
