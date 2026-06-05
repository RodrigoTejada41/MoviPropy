import { Status } from "./Status";

type Column<T> = {
  key: string;
  label: string;
  render: (item: T) => string | number | boolean | null | undefined;
};

type DataTableProps<T> = {
  columns: Column<T>[];
  rows: T[];
  loading?: boolean;
  error?: string | null;
  emptyText?: string;
};

export function DataTable<T>({ columns, rows, loading, error, emptyText }: DataTableProps<T>) {
  const state = <Status loading={loading} error={error} empty={!loading && !error && rows.length === 0} emptyText={emptyText} />;
  if (loading || error || rows.length === 0) return state;

  return (
    <div className="tableWrap">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key}>{column.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {columns.map((column) => (
                <td key={column.key}>{formatCell(column.render(row))}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function formatCell(value: string | number | boolean | null | undefined) {
  if (typeof value === "boolean") return value ? "Sim" : "Nao";
  if (value === null || value === undefined || value === "") return "-";
  return String(value);
}
