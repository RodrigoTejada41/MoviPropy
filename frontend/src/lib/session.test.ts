// @vitest-environment jsdom

import { beforeEach, describe, expect, it } from "vitest";
import { clearSession, getToken, getUser, saveSession } from "./session";

describe("admin session", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("persists and clears token and user", () => {
    const user = {
      id: "admin",
      nome: "Admin",
      email: "admin@example.com",
      perfil: "admin"
    };

    saveSession("token", user);

    expect(getToken()).toBe("token");
    expect(getUser()).toEqual(user);

    clearSession();
    expect(getToken()).toBeNull();
    expect(getUser()).toBeNull();
  });

  it("clears invalid persisted user data", () => {
    localStorage.setItem("moviprogy.admin.token", "token");
    localStorage.setItem("moviprogy.admin.user", "{invalid");

    expect(getUser()).toBeNull();
    expect(getToken()).toBeNull();
  });
});
