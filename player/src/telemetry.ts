import type { TelemetryItem } from "./types";

interface FlushOptions {
  items: TelemetryItem[];
  send(item: TelemetryItem): Promise<void>;
  remove(id: number): Promise<void>;
}

export async function flushTelemetry({
  items,
  send,
  remove
}: FlushOptions): Promise<number> {
  let sent = 0;
  for (const item of items) {
    try {
      await send(item);
      if (item.id !== undefined) await remove(item.id);
      sent += 1;
    } catch {
      break;
    }
  }
  return sent;
}
