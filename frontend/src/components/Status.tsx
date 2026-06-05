type StatusProps = {
  loading?: boolean;
  error?: string | null;
  empty?: boolean;
  emptyText?: string;
};

export function Status({ loading, error, empty, emptyText = "Nenhum registro encontrado." }: StatusProps) {
  if (loading) return <div className="state">Carregando...</div>;
  if (error) return <div className="state stateError">{error}</div>;
  if (empty) return <div className="state">{emptyText}</div>;
  return null;
}
