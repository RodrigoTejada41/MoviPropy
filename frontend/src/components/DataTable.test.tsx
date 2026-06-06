// @vitest-environment jsdom

import "@testing-library/jest-dom/vitest";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DataTable } from "./DataTable";

type Row = {
  name: string;
  active: boolean;
};

const columns = [
  { key: "name", label: "Nome", render: (item: Row) => item.name },
  { key: "active", label: "Ativo", render: (item: Row) => item.active }
];

describe("DataTable", () => {
  it("renders loading, error and empty states", () => {
    const { rerender } = render(<DataTable<Row> rows={[]} columns={columns} loading />);
    expect(screen.getByText("Carregando...")).toBeInTheDocument();

    rerender(<DataTable<Row> rows={[]} columns={columns} error="Falha controlada" />);
    expect(screen.getByText("Falha controlada")).toBeInTheDocument();

    rerender(<DataTable<Row> rows={[]} columns={columns} emptyText="Sem dados" />);
    expect(screen.getByText("Sem dados")).toBeInTheDocument();
  });

  it("renders values and interactive actions", () => {
    const onClick = vi.fn();
    render(
      <DataTable<Row>
        rows={[{ name: "Cliente A", active: true }]}
        columns={[
          ...columns,
          { key: "action", label: "Acao", render: () => <button onClick={onClick}>Editar</button> }
        ]}
      />
    );

    expect(screen.getByText("Cliente A")).toBeInTheDocument();
    expect(screen.getByText("Sim")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Editar" }));
    expect(onClick).toHaveBeenCalledOnce();
  });
});
