import { expect, test } from "@playwright/test";

const emptyPage = { items: [], limit: 50, offset: 0, total: 0 };

test("authenticates, navigates and logs out", async ({ page }) => {
  await page.route("**/api/**", async (route) => {
    const request = route.request();
    const path = new URL(request.url()).pathname;

    if (path === "/api/auth/login" && request.method() === "POST") {
      await route.fulfill({
        json: {
          access_token: "e2e-token",
          token_type: "bearer",
          usuario: {
            id: "admin-e2e",
            nome: "Admin E2E",
            email: "admin@example.com",
            perfil: "admin"
          }
        }
      });
      return;
    }

    if (path === "/api/auth/logout" && request.method() === "POST") {
      await route.fulfill({ json: { status: "logout efetuado" } });
      return;
    }

    if (request.method() === "GET") {
      await route.fulfill({ json: emptyPage });
      return;
    }

    await route.fulfill({ status: 404, json: { detail: "Rota E2E nao simulada" } });
  });

  await page.goto("/");
  await expect(page.getByRole("img", { name: "MoviProgy Tecnologia" })).toBeVisible();

  await page.getByLabel("Email").fill("admin@example.com");
  await page.getByLabel("Senha").fill("senha-e2e");
  await page.getByRole("button", { name: "Entrar" }).click();

  await expect(page.getByRole("heading", { name: "Visao geral da infraestrutura" })).toBeVisible();
  await expect(page.getByText("Admin E2E").first()).toBeVisible();

  await page.getByRole("button", { name: "Clientes" }).click();
  await expect(page.getByRole("heading", { name: "Gestao de clientes" })).toBeVisible();

  await page.getByRole("button", { name: "Sair" }).click();
  await expect(page.getByRole("button", { name: "Entrar" })).toBeVisible();
  await expect(page.getByLabel("Email")).toHaveValue("");
});

test("assigns a published playlist to a device", async ({ page }) => {
  const clientes = {
    items: [{ id: "cliente-1", nome: "Cliente Um", ativo: true }],
    limit: 50,
    offset: 0,
    total: 1
  };
  let dispositivo = {
    id: "device-1",
    cliente_id: "cliente-1",
    nome: "TV Recepcao",
    codigo_ativacao: "MOVI-TESTE-000001",
    bloqueado: false,
    playlist_atual_id: null
  };

  await page.route("**/api/**", async (route) => {
    const request = route.request();
    const path = new URL(request.url()).pathname;

    if (path === "/api/auth/login" && request.method() === "POST") {
      await route.fulfill({
        json: {
          access_token: "e2e-token",
          token_type: "bearer",
          usuario: {
            id: "admin-e2e",
            nome: "Admin E2E",
            email: "admin@example.com",
            perfil: "admin"
          }
        }
      });
      return;
    }

    if (path === "/api/admin/clientes" && request.method() === "GET") {
      await route.fulfill({ json: clientes });
      return;
    }

    if (path === "/api/admin/dispositivos" && request.method() === "GET") {
      await route.fulfill({
        json: { items: [dispositivo], limit: 50, offset: 0, total: 1 }
      });
      return;
    }

    if (path === "/api/admin/playlists" && request.method() === "GET") {
      await route.fulfill({
        json: {
          items: [
            { id: "playlist-1", cliente_id: "cliente-1", nome: "Videos Recepcao", versao: 1, ativa: true },
            { id: "playlist-rascunho", cliente_id: "cliente-1", nome: "Rascunho", versao: 1, ativa: false }
          ],
          limit: 50,
          offset: 0,
          total: 2
        }
      });
      return;
    }

    if (path === "/api/admin/midias" && request.method() === "GET") {
      await route.fulfill({ json: emptyPage });
      return;
    }

    if (path === "/api/admin/auditoria/acessos" && request.method() === "GET") {
      await route.fulfill({ json: emptyPage });
      return;
    }

    if (path === "/api/admin/dispositivos/device-1" && request.method() === "PATCH") {
      const payload = JSON.parse(request.postData() ?? "{}");
      dispositivo = { ...dispositivo, ...payload };
      await route.fulfill({ json: dispositivo });
      return;
    }

    await route.fulfill({ status: 404, json: { detail: "Rota E2E nao simulada" } });
  });

  await page.goto("/");
  await page.getByLabel("Email").fill("admin@example.com");
  await page.getByLabel("Senha").fill("senha-e2e");
  await page.getByRole("button", { name: "Entrar" }).click();
  await page.getByRole("button", { name: "Dispositivos" }).click();

  const playlistSelect = page.getByLabel("Playlist atual de TV Recepcao");
  await expect(playlistSelect).toBeVisible();
  await expect(playlistSelect).not.toContainText("Rascunho");

  await playlistSelect.selectOption("playlist-1");
  await expect(page.getByText("Playlist vinculada ao dispositivo.")).toBeVisible();
});
