import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { mediaId, PlayerApi } from "./api";
import { nextMediaIndex } from "./domain";
import { IndexedDbPlayerStorage } from "./storage";
import { synchronizePlayer } from "./sync";
import { flushTelemetry } from "./telemetry";
import type { DeviceSession, MediaFile, PlaylistManifest, TelemetryItem } from "./types";

type PlayerState = "loading" | "activation" | "syncing" | "playing" | "empty" | "error";

const api = new PlayerApi();
const storage = new IndexedDbPlayerStorage();

export function App() {
  const [device, setDevice] = useState<DeviceSession | null>(null);
  const [manifest, setManifest] = useState<PlaylistManifest | null>(null);
  const [state, setState] = useState<PlayerState>("loading");
  const [message, setMessage] = useState("Inicializando player");
  const [activationCode, setActivationCode] = useState("");
  const [currentIndex, setCurrentIndex] = useState(0);
  const [mediaUrl, setMediaUrl] = useState<string | null>(null);
  const [online, setOnline] = useState(navigator.onLine);
  const [diagnostics, setDiagnostics] = useState(false);

  const currentMedia = manifest?.files[currentIndex] ?? null;

  const queueTelemetry = useCallback(async (
    endpoint: TelemetryItem["endpoint"],
    payload: Record<string, unknown>
  ) => {
    await storage.enqueueTelemetry({
      endpoint,
      payload,
      created_at: new Date().toISOString()
    });
  }, []);

  const flushQueue = useCallback(async (session: DeviceSession) => {
    if (!navigator.onLine) return 0;
    return flushTelemetry({
      items: await storage.listTelemetry(),
      send: (item) => api.sendTelemetry(item, session.token).then(() => undefined),
      remove: (id) => storage.removeTelemetry(id)
    });
  }, []);

  const sync = useCallback(async (session: DeviceSession, force = false) => {
    const active = await storage.getActiveManifest();
    if (!navigator.onLine) {
      if (active) {
        setManifest(active);
        setState("playing");
        setMessage("Offline - reproduzindo cache local");
      } else {
        setState("empty");
        setMessage("Sem conexao e sem playlist local");
      }
      return;
    }

    try {
      setState("syncing");
      setMessage("Verificando atualizacoes");
      const update = await api.checkUpdate(active?.version ?? 0, session.token);
      if (force || !active || update.possui_atualizacao) {
        const remote = await api.getManifest(session.token);
        const result = await synchronizePlayer({
          manifest: remote,
          storage,
          download: (media) => api.downloadMedia(mediaId(media), session.token)
        });
        await queueTelemetry("/api/player/sincronizacao/confirmar", {
          playlist_id: remote.playlist_id,
          versao: remote.version,
          arquivos_baixados: result.downloaded,
          status: result.status
        });
      }

      const synchronized = await storage.getActiveManifest();
      setManifest(synchronized);
      setCurrentIndex(0);
      setState(synchronized?.files.length ? "playing" : "empty");
      setMessage(synchronized?.files.length ? "Reproduzindo" : "Playlist sem midias");
      await queueTelemetry("/api/player/status", {
        status: "online",
        playlist_atual: synchronized?.playlist_id ?? null,
        versao_player: "0.1.0"
      });
      await flushQueue(session);
    } catch (error) {
      const fallback = await storage.getActiveManifest();
      if (fallback?.files.length) {
        setManifest(fallback);
        setState("playing");
        setMessage("Atualizacao falhou - mantendo playlist anterior");
      } else {
        setState("error");
        setMessage(error instanceof Error ? error.message : "Falha de sincronizacao");
      }
      await queueTelemetry("/api/player/logs", {
        nivel: "erro",
        evento: "sincronizacao_falhou",
        dados: { mensagem: error instanceof Error ? error.message : "erro desconhecido" }
      });
    }
  }, [flushQueue, queueTelemetry]);

  useEffect(() => {
    let active = true;
    storage.getDevice().then(async (savedDevice) => {
      if (!active) return;
      if (!savedDevice) {
        setState("activation");
        setMessage("Informe o codigo de ativacao");
        return;
      }
      setDevice(savedDevice);
      await sync(savedDevice);
    });
    return () => {
      active = false;
    };
  }, [sync]);

  useEffect(() => {
    const updateConnection = () => {
      setOnline(navigator.onLine);
      if (navigator.onLine && device) void sync(device);
    };
    const toggleDiagnostics = (event: KeyboardEvent) => {
      if (event.key.toLowerCase() === "d") setDiagnostics((value) => !value);
    };
    window.addEventListener("online", updateConnection);
    window.addEventListener("offline", updateConnection);
    window.addEventListener("keydown", toggleDiagnostics);
    return () => {
      window.removeEventListener("online", updateConnection);
      window.removeEventListener("offline", updateConnection);
      window.removeEventListener("keydown", toggleDiagnostics);
    };
  }, [device, sync]);

  useEffect(() => {
    if (!device) return;
    const timer = window.setInterval(() => void sync(device), 60_000);
    return () => window.clearInterval(timer);
  }, [device, sync]);

  useEffect(() => {
    let objectUrl: string | null = null;
    if (!currentMedia?.media_id) {
      setMediaUrl(null);
      return;
    }
    storage.getMedia(currentMedia.media_id).then((blob) => {
      if (!blob) return;
      objectUrl = URL.createObjectURL(blob);
      setMediaUrl(objectUrl);
    });
    return () => {
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [currentMedia]);

  useEffect(() => {
    if (!currentMedia || currentMedia.media_type !== "imagem") return;
    const timer = window.setTimeout(
      () => setCurrentIndex((index) => nextMediaIndex(index, manifest?.files.length ?? 0)),
      Math.max(currentMedia.duration_seconds ?? 10, 1) * 1000
    );
    return () => window.clearTimeout(timer);
  }, [currentMedia, manifest]);

  async function activate(event: FormEvent) {
    event.preventDefault();
    if (!activationCode.trim()) return;
    try {
      setState("syncing");
      setMessage("Ativando dispositivo");
      const session = await api.activate(activationCode.trim(), hardwareId());
      await storage.saveDevice(session);
      setDevice(session);
      setActivationCode("");
      await sync(session, true);
    } catch (error) {
      setState("activation");
      setMessage(error instanceof Error ? error.message : "Falha de ativacao");
    }
  }

  async function resetPlayer() {
    await storage.clearDevice();
    setDevice(null);
    setManifest(null);
    setMediaUrl(null);
    setState("activation");
    setMessage("Player redefinido");
  }

  const diagnosticsData = useMemo(() => ({
    dispositivo: device?.device_id ?? "nao ativado",
    conexao: online ? "online" : "offline",
    playlist: manifest?.playlist_id ?? "nenhuma",
    versao: manifest?.version ?? 0,
    midias: manifest?.files.length ?? 0
  }), [device, manifest, online]);

  if (state === "activation") {
    return (
      <main className="activationScreen">
        <section className="activationPanel">
          <img src="/moviprogy-brand.webp" alt="MoviProgy" />
          <div>
            <span className="eyebrow">PLAYER DE MIDIA INDOOR</span>
            <h1>Ativar dispositivo</h1>
            <p>Digite o codigo gerado no painel administrativo.</p>
          </div>
          <form onSubmit={activate}>
            <label htmlFor="activationCode">Codigo de ativacao</label>
            <input
              id="activationCode"
              value={activationCode}
              onChange={(event) => setActivationCode(event.target.value.toUpperCase())}
              placeholder="MOVI-XXXX-XXX"
              autoComplete="off"
              autoFocus
            />
            <button type="submit">Ativar player</button>
          </form>
          <p className="statusMessage">{message}</p>
        </section>
      </main>
    );
  }

  return (
    <main className="playerScreen">
      {state === "playing" && currentMedia && mediaUrl ? (
        currentMedia.media_type === "video" ? (
          <video
            key={mediaUrl}
            src={mediaUrl}
            autoPlay
            muted
            playsInline
            onEnded={() => setCurrentIndex((index) =>
              nextMediaIndex(index, manifest?.files.length ?? 0)
            )}
            onError={() => setCurrentIndex((index) =>
              nextMediaIndex(index, manifest?.files.length ?? 0)
            )}
          />
        ) : (
          <img src={mediaUrl} alt="" />
        )
      ) : (
        <section className="operationalState">
          <img src="/moviprogy-brand.webp" alt="" />
          <span className={`connectionDot ${online ? "online" : "offline"}`} />
          <h1>{state === "syncing" ? "Sincronizando" : "MoviProgy Player"}</h1>
          <p>{message}</p>
        </section>
      )}

      {!online && <div className="offlineBadge">OFFLINE</div>}

      {diagnostics && (
        <aside className="diagnostics">
          <strong>Diagnostico local</strong>
          {Object.entries(diagnosticsData).map(([key, value]) => (
            <div key={key}><span>{key}</span><b>{value}</b></div>
          ))}
          <button type="button" onClick={() => device && sync(device, true)}>Sincronizar</button>
          <button type="button" className="danger" onClick={resetPlayer}>Redefinir</button>
        </aside>
      )}
    </main>
  );
}

function hardwareId(): string {
  const key = "moviprogy-hardware-id";
  const existing = localStorage.getItem(key);
  if (existing) return existing;
  const generated = crypto.randomUUID();
  localStorage.setItem(key, generated);
  return generated;
}
