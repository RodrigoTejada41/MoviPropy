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
  Trash2,
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

  async function toggleCliente(item: Cliente) {
    setMessage(null);
    try {
      await api.atualizarCliente(item.id, { ativo: !item.ativo });
      await list.reload();
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Falha ao atualizar cliente.");
    }
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
                        <button className="secondaryButton compactButton" type="button" onClick={() => toggleCliente(item)}>
                          {item.ativo ? "Inativar" : "Ativar"}
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

  async function toggleBloqueio(item: Dispositivo) {
    setMessage(null);
    try {
      await api.atualizarDispositivo(item.id, { bloqueado: !item.bloqueado });
      await list.reload();
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Falha ao atualizar dispositivo.");
    }
  }

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
                      <button className="secondaryButton compactButton" type="button" onClick={() => toggleBloqueio(item)}>
                        {item.bloqueado ? "Desbloquear" : "Bloquear"}
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
  const clientes = useList(api.clientes);
  const [form, setForm] = useState({ cliente_id: "", tipo: "imagem", duracao: "" });
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function upload(event: FormEvent) {
    event.preventDefault();
    setMessage(null);
    setSuccess(null);
    if (!form.cliente_id || !arquivo) {
      setMessage("Cliente e arquivo sao obrigatorios.");
      return;
    }
    try {
      await api.uploadMidia({
        cliente_id: form.cliente_id,
        tipo: form.tipo,
        duracao_segundos: form.duracao ? Number(form.duracao) : null,
        arquivo
      });
      setArquivo(null);
      await list.reload();
      setSuccess("Midia enviada.");
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Falha no upload.");
    }
  }

  async function toggle(item: Midia) {
    setMessage(null);
    setSuccess(null);
    try {
      await api.atualizarMidia(item.id, { ativo: !item.ativo });
      await list.reload();
      setSuccess(item.ativo ? "Midia inativada." : "Midia ativada.");
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Falha ao atualizar midia.");
    }
  }

  return (
    <section className="page">
      <PageTitle title="Midias" subtitle={`${list.total} registros encontrados.`} />
      <form className="inlineForm" onSubmit={upload}>
        <select value={form.cliente_id} onChange={(event) => setForm({ ...form, cliente_id: event.target.value })}>
          <option value="">Cliente</option>
          {clientes.rows.map((cliente) => <option key={cliente.id} value={cliente.id}>{cliente.nome}</option>)}
        </select>
        <select value={form.tipo} onChange={(event) => setForm({ ...form, tipo: event.target.value })}>
          <option value="imagem">Imagem</option>
          <option value="video">Video</option>
        </select>
        <input type="number" min="0" placeholder="duracao em segundos" value={form.duracao} onChange={(event) => setForm({ ...form, duracao: event.target.value })} />
        <input type="file" accept={form.tipo === "video" ? "video/mp4" : "image/jpeg,image/png,image/webp"} onChange={(event) => setArquivo(event.target.files?.[0] ?? null)} />
        <button className="primaryButton"><UploadCloud size={16} />Enviar</button>
      </form>
      <Status error={message} success={success} />
      <DataTable<Midia>
        rows={list.rows}
        loading={list.loading}
        error={list.error}
        columns={[
          { key: "nome", label: "Nome", render: (item) => item.nome },
          { key: "cliente", label: "Cliente", render: (item) => item.cliente_id },
          { key: "tipo", label: "Tipo", render: (item) => item.tipo },
          { key: "tamanho", label: "Tamanho", render: (item) => formatBytes(item.tamanho) },
          { key: "ativo", label: "Status", render: (item) => item.ativo ? "Ativa" : "Inativa" },
          {
            key: "acoes",
            label: "Acoes",
            render: (item) => (
              <button className="secondaryButton compactButton" type="button" onClick={() => toggle(item)}>
                {item.ativo ? "Inativar" : "Ativar"}
              </button>
            )
          }
        ]}
      />
    </section>
  );
}

export function PlaylistsPage() {
  const list = useList(api.playlists);
  const clientes = useList(api.clientes);
  const midias = useList(api.midias);
  const [form, setForm] = useState({ id: "", cliente_id: "", nome: "" });
  const [selectedId, setSelectedId] = useState("");
  const [items, setItems] = useState<Awaited<ReturnType<typeof api.playlistMidias>>>([]);
  const [itemForm, setItemForm] = useState({ midia_id: "", ordem: "1", duracao: "" });
  const [message, setMessage] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function loadItems(id: string) {
    setSelectedId(id);
    setItems(id ? await api.playlistMidias(id) : []);
  }

  async function create(event: FormEvent) {
    event.preventDefault();
    setMessage(null);
    setSuccess(null);
    if (!form.id.trim() || !form.cliente_id || !form.nome.trim()) {
      setMessage("Id, cliente e nome sao obrigatorios.");
      return;
    }
    try {
      await api.criarPlaylist({ ...form, versao: 1, ativa: false });
      setForm({ id: "", cliente_id: "", nome: "" });
      await list.reload();
      setSuccess("Playlist criada.");
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Falha ao criar playlist.");
    }
  }

  async function toggle(playlist: Playlist) {
    try {
      await api.atualizarPlaylist(playlist.id, { ativa: !playlist.ativa });
      await list.reload();
      setSuccess(playlist.ativa ? "Playlist inativada." : "Playlist publicada.");
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Falha ao atualizar playlist.");
    }
  }

  async function addItem(event: FormEvent) {
    event.preventDefault();
    if (!selectedId || !itemForm.midia_id) return;
    try {
      await api.vincularMidia(selectedId, {
        midia_id: itemForm.midia_id,
        ordem: Number(itemForm.ordem),
        duracao_override: itemForm.duracao ? Number(itemForm.duracao) : null
      });
      await loadItems(selectedId);
      await list.reload();
      setSuccess("Midia vinculada.");
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Falha ao vincular midia.");
    }
  }

  async function removeItem(midiaId: string) {
    if (!selectedId) return;
    try {
      await api.removerMidia(selectedId, midiaId);
      await loadItems(selectedId);
      await list.reload();
      setSuccess("Midia removida.");
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Falha ao remover midia.");
    }
  }

  const selected = list.rows.find((item) => item.id === selectedId);
  const availableMedia = midias.rows.filter((item) => !selected || item.cliente_id === selected.cliente_id);

  return (
    <section className="page">
      <PageTitle title="Playlists" subtitle={`${list.total} registros encontrados.`} />
      <form className="inlineForm" onSubmit={create}>
        <input placeholder="id" value={form.id} onChange={(event) => setForm({ ...form, id: event.target.value })} />
        <select value={form.cliente_id} onChange={(event) => setForm({ ...form, cliente_id: event.target.value })}>
          <option value="">Cliente</option>
          {clientes.rows.map((cliente) => <option key={cliente.id} value={cliente.id}>{cliente.nome}</option>)}
        </select>
        <input placeholder="nome" value={form.nome} onChange={(event) => setForm({ ...form, nome: event.target.value })} />
        <button className="primaryButton"><Plus size={16} />Criar</button>
      </form>
      <Status error={message} success={success} />
      <DataTable<Playlist>
        rows={list.rows}
        loading={list.loading}
        error={list.error}
        columns={[
          { key: "nome", label: "Nome", render: (item) => item.nome },
          { key: "cliente", label: "Cliente", render: (item) => item.cliente_id },
          { key: "versao", label: "Versao", render: (item) => item.versao },
          { key: "ativa", label: "Status", render: (item) => item.ativa ? "Publicada" : "Rascunho" },
          {
            key: "acoes",
            label: "Acoes",
            render: (item) => (
              <div className="tableActions">
                <button className="secondaryButton compactButton" type="button" onClick={() => loadItems(item.id)}>Editar</button>
                <button className="secondaryButton compactButton" type="button" onClick={() => toggle(item)}>{item.ativa ? "Inativar" : "Publicar"}</button>
              </div>
            )
          }
        ]}
      />
      {selected && (
        <section className="editorSection">
          <div className="sectionHeader">
            <div><h2>{selected.nome}</h2><p>Versao {selected.versao}</p></div>
            <button className="tableIconButton" type="button" title="Fechar editor" onClick={() => loadItems("")}><RotateCcw size={18} /></button>
          </div>
          <form className="inlineForm" onSubmit={addItem}>
            <select value={itemForm.midia_id} onChange={(event) => setItemForm({ ...itemForm, midia_id: event.target.value })}>
              <option value="">Midia</option>
              {availableMedia.map((item) => <option key={item.id} value={item.id}>{item.nome}</option>)}
            </select>
            <input type="number" min="1" value={itemForm.ordem} onChange={(event) => setItemForm({ ...itemForm, ordem: event.target.value })} />
            <input type="number" min="0" placeholder="duracao" value={itemForm.duracao} onChange={(event) => setItemForm({ ...itemForm, duracao: event.target.value })} />
            <button className="primaryButton"><Plus size={16} />Adicionar</button>
          </form>
          <DataTable
            rows={items}
            columns={[
              { key: "ordem", label: "Ordem", render: (item) => item.ordem },
              { key: "midia", label: "Midia", render: (item) => midias.rows.find((media) => media.id === item.midia_id)?.nome ?? item.midia_id },
              { key: "duracao", label: "Duracao", render: (item) => item.duracao_override ?? "Padrao" },
              { key: "acoes", label: "Acoes", render: (item) => <button className="tableIconButton" type="button" title="Remover" onClick={() => removeItem(item.midia_id)}><Trash2 size={17} /></button> }
            ]}
          />
        </section>
      )}
    </section>
  );
}

export function UsuariosPage() {
  const list = useList(api.usuarios);
  const [form, setForm] = useState({ nome: "", email: "", senha: "", perfil: "operador" });
  const [message, setMessage] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function create(event: FormEvent) {
    event.preventDefault();
    setMessage(null);
    setSuccess(null);
    if (!form.nome.trim() || !form.email.trim() || form.senha.length < 8) {
      setMessage("Nome, email e senha com no minimo 8 caracteres sao obrigatorios.");
      return;
    }
    try {
      await api.criarUsuario({ ...form, ativo: true });
      setForm({ nome: "", email: "", senha: "", perfil: "operador" });
      await list.reload();
      setSuccess("Usuario criado.");
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Falha ao criar usuario.");
    }
  }

  async function toggle(item: User) {
    setMessage(null);
    setSuccess(null);
    try {
      await api.atualizarUsuario(item.id, { ativo: !item.ativo });
      await list.reload();
      setSuccess(item.ativo ? "Usuario inativado." : "Usuario ativado.");
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Falha ao atualizar usuario.");
    }
  }

  return (
    <section className="page">
      <PageTitle title="Usuarios e permissoes" subtitle={`${list.total} usuarios encontrados.`} />
      <form className="inlineForm" onSubmit={create}>
        <input placeholder="nome" value={form.nome} onChange={(event) => setForm({ ...form, nome: event.target.value })} />
        <input type="email" placeholder="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} />
        <input type="password" minLength={8} placeholder="senha" value={form.senha} onChange={(event) => setForm({ ...form, senha: event.target.value })} />
        <select value={form.perfil} onChange={(event) => setForm({ ...form, perfil: event.target.value })}>
          <option value="operador">Operador</option>
          <option value="cliente">Cliente</option>
          <option value="admin">Administrador</option>
        </select>
        <button className="primaryButton"><Plus size={16} />Criar</button>
      </form>
      <Status error={message} success={success} />
      <DataTable<User>
        rows={list.rows}
        loading={list.loading}
        error={list.error}
        columns={[
          { key: "id", label: "Id", render: (item) => item.id },
          { key: "nome", label: "Nome", render: (item) => item.nome },
          { key: "email", label: "Email", render: (item) => item.email },
          { key: "perfil", label: "Perfil", render: (item) => item.perfil },
          { key: "ativo", label: "Status", render: (item) => item.ativo ? "Ativo" : "Inativo" },
          {
            key: "acoes",
            label: "Acoes",
            render: (item) => (
              <button className="secondaryButton compactButton" type="button" onClick={() => toggle(item)}>
                {item.ativo ? "Inativar" : "Ativar"}
              </button>
            )
          }
        ]}
      />
    </section>
  );
}

export function SincronizacoesPage() {
  const list = useList(api.sincronizacoes);
  return (
    <section className="page">
      <PageTitle title="Sincronizacoes" subtitle={`${list.total} confirmacoes recebidas dos players.`} />
      <DataTable
        rows={list.rows}
        loading={list.loading}
        error={list.error}
        columns={[
          { key: "device", label: "Dispositivo", render: (item) => item.device_id },
          { key: "cliente", label: "Cliente", render: (item) => item.cliente_id },
          { key: "playlist", label: "Playlist", render: (item) => `${item.playlist_id} v${item.versao}` },
          { key: "arquivos", label: "Arquivos", render: (item) => item.arquivos_baixados.length },
          { key: "status", label: "Status", render: (item) => item.status },
          { key: "data", label: "Recebida em", render: (item) => new Date(item.created_at).toLocaleString() }
        ]}
      />
    </section>
  );
}

export function ConfiguracoesPage() {
  const [data, setData] = useState<Awaited<ReturnType<typeof api.configuracoes>> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.configuracoes()
      .then(setData)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Falha ao carregar configuracoes."));
  }, []);

  return (
    <section className="page">
      <PageTitle title="Configuracoes" subtitle="Parametros operacionais efetivos do backend." />
      <Status loading={!data && !error} error={error} />
      {data && (
        <div className="metricGrid settingsGrid">
          <div className="metric"><span>Storage ativo</span><strong>{data.storage_provider}</strong></div>
          <div className="metric"><span>Upload local maximo</span><strong>{formatBytes(data.max_upload_bytes)}</strong></div>
          <div className="metric"><span>Operacao offline</span><strong>{data.offline_first ? "Ativa" : "Inativa"}</strong></div>
        </div>
      )}
      <div className="state">Alteracoes sensiveis permanecem bloqueadas e devem ser feitas por configuracao de ambiente com auditoria.</div>
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
  const [success, setSuccess] = useState<string | null>(null);
  const [rootForm, setRootForm] = useState({ folder_name: "MoviProgy_Midias" });
  const [clientFolderForm, setClientFolderForm] = useState({ cliente_id: "" });
  const [importForm, setImportForm] = useState({ cliente_id: "", tipo: "video" });
  const [uploadFile, setUploadFile] = useState<File | null>(null);

  async function load() {
    setLoading(true);
    setMessage(null);
    setSuccess(null);
    try {
      const statusResult = await api.googleDriveStatus();
      const [folderResult, fileResult] = await Promise.all([
        api.googleDriveFolders().catch(() => ({ items: [] })),
        api.googleDriveFiles({ folderId: statusResult.root_folder_id ?? undefined }).catch(() => ({ items: [] }))
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
    setSuccess(null);
    try {
      const result = await api.googleDriveConnect();
      window.location.href = result.authorization_url;
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Falha ao iniciar OAuth.");
    }
  }

  async function disconnect() {
    setMessage(null);
    setSuccess(null);
    try {
      await api.googleDriveDisconnect();
      await load();
      setSuccess("Google Drive desconectado.");
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Falha ao desconectar.");
    }
  }

  async function validate() {
    setMessage(null);
    setSuccess(null);
    try {
      const result = await api.googleDriveValidate();
      setStatusData(result);
      setSuccess("Validacao concluida.");
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Falha ao validar acesso.");
    }
  }

  async function saveRootFolder(event: FormEvent) {
    event.preventDefault();
    setMessage(null);
    setSuccess(null);
    try {
      if (!connected) {
        setMessage("Google Drive desconectado.");
        return;
      }
      await api.googleDriveRootFolder({ folder_name: rootForm.folder_name.trim() || "MoviProgy_Midias" });
      const result = await api.googleDriveValidate();
      setStatusData(result);
      await load();
      setSuccess("Pasta raiz salva e validada.");
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Falha ao salvar pasta raiz.");
    }
  }

  async function saveClientFolder(event: FormEvent) {
    event.preventDefault();
    setMessage(null);
    setSuccess(null);
    if (!clientFolderForm.cliente_id) {
      setMessage("Cliente e obrigatorio.");
      return;
    }
    try {
      await api.googleDriveClientFolder({
        cliente_id: clientFolderForm.cliente_id,
        folder_name: null
      });
      setClientFolderForm({ cliente_id: "" });
      await load();
      setSuccess("Pasta do cliente salva.");
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Falha ao salvar pasta do cliente.");
    }
  }

  async function importMedia(fileId: string) {
    setMessage(null);
    setSuccess(null);
    if (!importForm.cliente_id) {
      setMessage("Cliente e obrigatorio para importar.");
      return;
    }
    try {
      await api.googleDriveImportMedia({
        cliente_id: importForm.cliente_id,
        file_id: fileId,
        tipo: importForm.tipo
      });
      await load();
      setSuccess("Midia importada.");
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Falha ao importar midia.");
    }
  }

  async function uploadMedia() {
    setMessage(null);
    setSuccess(null);
    if (!importForm.cliente_id) {
      setMessage("Cliente e obrigatorio para enviar.");
      return;
    }
    if (!uploadFile) {
      setMessage("Arquivo e obrigatorio.");
      return;
    }
    try {
      await api.googleDriveUploadMedia({
        cliente_id: importForm.cliente_id,
        tipo: importForm.tipo,
        arquivo: uploadFile
      });
      setUploadFile(null);
      await load();
      setSuccess("Arquivo enviado e midia cadastrada.");
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Falha ao enviar arquivo.");
    }
  }

  const connected = statusData?.connected === true;
  const rootFolderId = statusData?.root_folder_id ?? undefined;

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

      <Status error={message} success={success} />
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
          <p>{statusData?.root_folder_name ? "Selecionada e salva no backend." : "Selecione ou crie a pasta raiz."}</p>
        </div>
        <div className="driveStatusCard">
          <div className="driveStatusIcon"><RefreshCw size={28} /></div>
          <span>Ultima validacao</span>
          <strong>{statusData?.last_validation_at ? new Date(statusData.last_validation_at).toLocaleString() : "Nao informado"}</strong>
          <p>Tokens e pastas sao validados pelo backend.</p>
        </div>
      </div>

      <div className="driveQuotaGrid">
        <div><span>Espaco usado</span><strong>{formatBytes(statusData?.storage_used_bytes)}</strong></div>
        <div><span>Espaco disponivel</span><strong>{formatBytes(statusData?.storage_available_bytes)}</strong></div>
        <div><span>Capacidade total</span><strong>{formatBytes(statusData?.storage_limit_bytes)}</strong></div>
        <div><span>Arquivos</span><strong>{statusData?.file_count ?? "Nao informado"}</strong></div>
      </div>

      <div className="driveGrid">
        <form className="drivePanel" onSubmit={saveRootFolder}>
          <h2>Pasta raiz</h2>
          <input placeholder="MoviProgy_Midias" value={rootForm.folder_name} onChange={(event) => setRootForm({ folder_name: event.target.value })} />
          <button className="primaryButton" disabled={!connected || loading}><Folder size={16} />Salvar pasta raiz</button>
        </form>

        <form className="drivePanel" onSubmit={saveClientFolder}>
          <h2>Pasta do cliente</h2>
          <select value={clientFolderForm.cliente_id} onChange={(event) => setClientFolderForm({ ...clientFolderForm, cliente_id: event.target.value })}>
            <option value="">Cliente</option>
            {clientes.rows.map((cliente) => <option key={cliente.id} value={cliente.id}>{cliente.nome}</option>)}
          </select>
          <p className="mutedCell">Nome e ID da pasta sao definidos automaticamente pelo backend.</p>
          <button className="primaryButton" disabled={!connected || loading}><Folder size={16} />Salvar pasta</button>
        </form>
      </div>

      <div className="driveImportPanel">
        <div>
          <h2>Importar arquivo do Drive</h2>
          <p>Selecione o cliente para importar arquivos encontrados ou enviar novo arquivo.</p>
        </div>
        <select value={importForm.cliente_id} onChange={(event) => setImportForm({ ...importForm, cliente_id: event.target.value })}>
          <option value="">Cliente</option>
          {clientes.rows.map((cliente) => <option key={cliente.id} value={cliente.id}>{cliente.nome}</option>)}
        </select>
        <select value={importForm.tipo} onChange={(event) => setImportForm({ ...importForm, tipo: event.target.value })}>
          <option value="video">Video</option>
          <option value="imagem">Imagem</option>
        </select>
        <button className="secondaryButton" type="button" disabled={!connected || !rootFolderId} onClick={load}><RefreshCw size={16} />Atualizar arquivos</button>
        <input type="file" onChange={(event) => setUploadFile(event.target.files?.[0] ?? null)} />
        <button className="primaryButton" type="button" disabled={!connected || !rootFolderId || !uploadFile} onClick={uploadMedia}><UploadCloud size={16} />Enviar</button>
      </div>

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
                <thead><tr><th>Nome</th><th>Tipo</th><th>Cliente</th><th>Status</th></tr></thead>
                <tbody>
                  {folders.map((folder) => (
                    <tr key={`${folder.id}-${folder.cliente_id ?? "root"}`}>
                      <td>{folder.name}</td>
                      <td>{folder.cliente_id ? "Cliente" : "Raiz"}</td>
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
              <strong>Arquivos encontrados</strong>
              <span>{files.length} arquivos encontrados</span>
            </div>
          </div>
          {files.length === 0 ? <div className="emptyPanel">Nenhum arquivo encontrado.</div> : (
            <div className="fleetTableWrap">
              <table className="driveTable">
                <thead><tr><th>Nome</th><th>Tipo</th><th>Tamanho</th><th>Atualizado</th><th>Acoes</th></tr></thead>
                <tbody>
                  {files.map((file) => (
                    <tr key={file.id}>
                      <td>{file.name}</td>
                      <td>{file.mime_type ?? <span className="mutedCell">Nao informado</span>}</td>
                      <td>{formatBytes(file.size)}</td>
                      <td>{file.modified_at ? new Date(file.modified_at).toLocaleString() : <span className="mutedCell">Nao informado</span>}</td>
                      <td>
                        <button className="tableIconButton" type="button" onClick={() => importMedia(file.id)} disabled={!connected || !importForm.cliente_id} title="Importar arquivo">
                          <UploadCloud size={18} />
                        </button>
                      </td>
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

function formatBytes(value?: number | null) {
  if (value === undefined || value === null) return "Nao informado";
  if (value < 1024) return `${value} B`;
  const units = ["KB", "MB", "GB", "TB"];
  let size = value / 1024;
  let unit = 0;
  while (size >= 1024 && unit < units.length - 1) {
    size /= 1024;
    unit += 1;
  }
  return `${size.toFixed(size >= 10 ? 1 : 2)} ${units[unit]}`;
}
