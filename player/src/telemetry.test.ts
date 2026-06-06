import { describe, expect, test } from "vitest";
import { flushTelemetry } from "./telemetry";
import type { TelemetryItem } from "./types";

describe("flushTelemetry", () => {
  test("removes sent events in queue order", async () => {
    const items: TelemetryItem[] = [
      { id: 1, endpoint: "/api/player/status", payload: { status: "online" }, created_at: "1" },
      { id: 2, endpoint: "/api/player/logs", payload: { evento: "ok" }, created_at: "2" }
    ];
    const removed: number[] = [];

    const sent = await flushTelemetry({
      items,
      send: async () => undefined,
      remove: async (id) => {
        removed.push(id);
      }
    });

    expect(sent).toBe(2);
    expect(removed).toEqual([1, 2]);
  });

  test("keeps the failed event and stops processing", async () => {
    const items: TelemetryItem[] = [
      { id: 1, endpoint: "/api/player/status", payload: {}, created_at: "1" },
      { id: 2, endpoint: "/api/player/logs", payload: {}, created_at: "2" }
    ];
    const removed: number[] = [];

    const sent = await flushTelemetry({
      items,
      send: async () => {
        throw new Error("offline");
      },
      remove: async (id) => {
        removed.push(id);
      }
    });

    expect(sent).toBe(0);
    expect(removed).toEqual([]);
  });
});
