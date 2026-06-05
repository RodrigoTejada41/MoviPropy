import { useEffect, useState } from "react";
import { api } from "../lib/api";
import type { Cliente, Dispositivo, Midia, Playlist } from "../lib/types";

type DashboardState = {
  clientes: Cliente[];
  dispositivos: Dispositivo[];
  midias: Midia[];
  playlists: Playlist[];
};

export function DashboardPage() {
  const [data, setData] = useState<DashboardState>({
    clientes: [],
    dispositivos: [],
    midias: [],
    playlists: []
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.clientes(), api.dispositivos(), api.midias(), api.playlists()])
      .then(([clientes, dispositivos, midias, playlists]) => {
        setData({
          clientes: clientes.items,
          dispositivos: dispositivos.items,
          midias: midias.items,
          playlists: playlists.items
        });
      })
      .catch(() => setError("Falha ao carregar indicadores."))
      .finally(() => setLoading(false));
  }, []);

  const stats = [
    ["Clientes ativos", data.clientes.filter((item) => item.ativo).length],
    ["Dispositivos", data.dispositivos.length],
    ["Bloqueados", data.dispositivos.filter((item) => item.bloqueado).length],
    ["Playlists ativas", data.playlists.filter((item) => item.ativa).length],
    ["Midias", data.midias.length],
    ["Falhas recentes", 0]
  ];

  return (
    <section className="page">
      <PageTitle title="Dashboard" subtitle="Visao operacional dos dados reais disponiveis na API." />
      {loading && <div className="state">Carregando indicadores...</div>}
      {error && <div className="state stateError">{error}</div>}
      {!loading && !error && (
        <>
          <div className="metricGrid">
            {stats.map(([label, value]) => (
              <div className="metric" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
          <div className="split">
            <div>
              <h2>Dispositivos recentes</h2>
              <ul className="plainList">
                {data.dispositivos.slice(0, 5).map((item) => (
                  <li key={item.id}>{item.nome} - {item.bloqueado ? "bloqueado" : "ativo"}</li>
                ))}
                {data.dispositivos.length === 0 && <li>Nenhum dispositivo cadastrado.</li>}
              </ul>
            </div>
            <div>
              <h2>Playlists</h2>
              <ul className="plainList">
                {data.playlists.slice(0, 5).map((item) => (
                  <li key={item.id}>{item.nome} - versao {item.versao}</li>
                ))}
                {data.playlists.length === 0 && <li>Nenhuma playlist cadastrada.</li>}
              </ul>
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
