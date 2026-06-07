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
