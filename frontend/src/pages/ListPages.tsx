import { FormEvent, useEffect, useState } from "react";
import { Plus } from "lucide-react";
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
  const [form, setForm] = useState({ id: "", nome: "", documento: "" });
  const [message, setMessage] = useState<string | null>(null);

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
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Falha ao criar cliente.");
    }
  }

  return (
    <section className="page">
      <PageTitle title="Clientes" subtitle={`${list.total} registros encontrados.`} />
      <form className="inlineForm" onSubmit={submit}>
        <input placeholder="id" value={form.id} onChange={(event) => setForm({ ...form, id: event.target.value })} />
        <input placeholder="nome" value={form.nome} onChange={(event) => setForm({ ...form, nome: event.target.value })} />
        <input placeholder="documento" value={form.documento} onChange={(event) => setForm({ ...form, documento: event.target.value })} />
        <button className="primaryButton"><Plus size={16} />Criar</button>
      </form>
      {message && <Status error={message} />}
      <DataTable<Cliente>
        rows={list.rows}
        loading={list.loading}
        error={list.error}
        columns={[
          { key: "id", label: "Id", render: (item) => item.id },
          { key: "nome", label: "Nome", render: (item) => item.nome },
          { key: "documento", label: "Documento", render: (item) => item.documento },
          { key: "ativo", label: "Ativo", render: (item) => item.ativo }
        ]}
      />
    </section>
  );
}

export function DispositivosPage() {
  const list = useList(api.dispositivos);
  const [form, setForm] = useState({ id: "", cliente_id: "", nome: "", codigo_ativacao: "" });
  const [message, setMessage] = useState<string | null>(null);

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

  return (
    <section className="page">
      <PageTitle title="Dispositivos" subtitle={`${list.total} registros encontrados.`} />
      <form className="inlineForm" onSubmit={submit}>
        <input placeholder="id" value={form.id} onChange={(event) => setForm({ ...form, id: event.target.value })} />
        <input placeholder="cliente_id" value={form.cliente_id} onChange={(event) => setForm({ ...form, cliente_id: event.target.value })} />
        <input placeholder="nome" value={form.nome} onChange={(event) => setForm({ ...form, nome: event.target.value })} />
        <input placeholder="codigo" value={form.codigo_ativacao} onChange={(event) => setForm({ ...form, codigo_ativacao: event.target.value })} />
        <button className="primaryButton"><Plus size={16} />Criar</button>
      </form>
      {message && <Status error={message} />}
      <DataTable<Dispositivo>
        rows={list.rows}
        loading={list.loading}
        error={list.error}
        columns={[
          { key: "id", label: "Id", render: (item) => item.id },
          { key: "cliente", label: "Cliente", render: (item) => item.cliente_id },
          { key: "nome", label: "Nome", render: (item) => item.nome },
          { key: "codigo", label: "Codigo", render: (item) => item.codigo_ativacao },
          { key: "bloqueado", label: "Bloqueado", render: (item) => item.bloqueado }
        ]}
      />
    </section>
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

export function PlaceholderPage({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <section className="page">
      <PageTitle title={title} subtitle={subtitle} />
      <div className="state">Funcionalidade aguardando contrato backend ou fase pos-MVP documentada.</div>
    </section>
  );
}
