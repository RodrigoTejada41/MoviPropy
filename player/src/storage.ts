import type {
  DeviceSession,
  PlayerStorage,
  PlaylistManifest,
  TelemetryItem
} from "./types";

const META_STORE = "meta";
const MEDIA_STORE = "media";
const TELEMETRY_STORE = "telemetry";

export class IndexedDbPlayerStorage implements PlayerStorage {
  constructor(
    private readonly databaseName = "moviprogy-player",
    private readonly telemetryLimit = 500
  ) {}

  async getDevice(): Promise<DeviceSession | null> {
    return this.getMeta<DeviceSession>("device");
  }

  async saveDevice(device: DeviceSession): Promise<void> {
    await this.putMeta("device", device);
  }

  async clearDevice(): Promise<void> {
    const db = await this.open();
    await transactionDone(db, [META_STORE, MEDIA_STORE, TELEMETRY_STORE], "readwrite", (tx) => {
      tx.objectStore(META_STORE).clear();
      tx.objectStore(MEDIA_STORE).clear();
      tx.objectStore(TELEMETRY_STORE).clear();
    });
  }

  async getActiveManifest(): Promise<PlaylistManifest | null> {
    return this.getMeta<PlaylistManifest>("active_manifest");
  }

  async getMedia(mediaId: string): Promise<Blob | null> {
    const db = await this.open();
    return requestResult<StoredMedia | undefined>(db, MEDIA_STORE, "readonly", (store) =>
      store.get(mediaId)
    ).then((value) => value ? new Blob([value.bytes], { type: value.type }) : null);
  }

  async promote(manifest: PlaylistManifest, media: Map<string, Blob>): Promise<void> {
    const serialized = new Map<string, StoredMedia>();
    for (const [mediaId, blob] of media) {
      serialized.set(mediaId, {
        bytes: await blob.arrayBuffer(),
        type: blob.type
      });
    }
    const db = await this.open();
    await transactionDone(db, [META_STORE, MEDIA_STORE], "readwrite", (tx) => {
      const mediaStore = tx.objectStore(MEDIA_STORE);
      mediaStore.clear();
      for (const [mediaId, value] of serialized) mediaStore.put(value, mediaId);
      tx.objectStore(META_STORE).put(manifest, "active_manifest");
    });
  }

  async enqueueTelemetry(item: TelemetryItem): Promise<void> {
    const db = await this.open();
    await transactionDone(db, [TELEMETRY_STORE], "readwrite", (tx) => {
      tx.objectStore(TELEMETRY_STORE).add(item);
    });
    const items = await this.listTelemetry(this.telemetryLimit + 1);
    const excess = Math.max(items.length - this.telemetryLimit, 0);
    for (const oldItem of items.slice(0, excess)) {
      if (oldItem.id !== undefined) await this.removeTelemetry(oldItem.id);
    }
  }

  async listTelemetry(limit = 200): Promise<TelemetryItem[]> {
    const db = await this.open();
    return requestResult<TelemetryItem[]>(db, TELEMETRY_STORE, "readonly", (store) =>
      store.getAll(undefined, limit)
    );
  }

  async removeTelemetry(id: number): Promise<void> {
    const db = await this.open();
    await transactionDone(db, [TELEMETRY_STORE], "readwrite", (tx) => {
      tx.objectStore(TELEMETRY_STORE).delete(id);
    });
  }

  private async getMeta<T>(key: string): Promise<T | null> {
    const db = await this.open();
    return requestResult<T | undefined>(db, META_STORE, "readonly", (store) =>
      store.get(key)
    ).then((value) => value ?? null);
  }

  private async putMeta(key: string, value: unknown): Promise<void> {
    const db = await this.open();
    await transactionDone(db, [META_STORE], "readwrite", (tx) => {
      tx.objectStore(META_STORE).put(value, key);
    });
  }

  private open(): Promise<IDBDatabase> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.databaseName, 1);
      request.onupgradeneeded = () => {
        const db = request.result;
        if (!db.objectStoreNames.contains(META_STORE)) db.createObjectStore(META_STORE);
        if (!db.objectStoreNames.contains(MEDIA_STORE)) db.createObjectStore(MEDIA_STORE);
        if (!db.objectStoreNames.contains(TELEMETRY_STORE)) {
          db.createObjectStore(TELEMETRY_STORE, {
            keyPath: "id",
            autoIncrement: true
          });
        }
      };
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }
}

interface StoredMedia {
  bytes: ArrayBuffer;
  type: string;
}

function requestResult<T>(
  db: IDBDatabase,
  storeName: string,
  mode: IDBTransactionMode,
  action: (store: IDBObjectStore) => IDBRequest<T>
): Promise<T> {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(storeName, mode);
    const request = action(transaction.objectStore(storeName));
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
    transaction.oncomplete = () => db.close();
    transaction.onerror = () => {
      db.close();
      reject(transaction.error);
    };
  });
}

function transactionDone(
  db: IDBDatabase,
  stores: string[],
  mode: IDBTransactionMode,
  action: (transaction: IDBTransaction) => void
): Promise<void> {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(stores, mode);
    action(transaction);
    transaction.oncomplete = () => {
      db.close();
      resolve();
    };
    transaction.onerror = () => {
      db.close();
      reject(transaction.error);
    };
    transaction.onabort = () => {
      db.close();
      reject(transaction.error ?? new Error("transacao IndexedDB abortada"));
    };
  });
}
