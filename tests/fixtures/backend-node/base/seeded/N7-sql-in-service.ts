export function findOrderQuery(id: string): string {
  return "SELECT id, status FROM orders WHERE id = '" + id + "'";
}
