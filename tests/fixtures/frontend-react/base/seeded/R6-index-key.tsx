export function List({ items }: { items: string[] }) {
  return <ul>{items.map((it, i) => <li key={i}>{it}</li>)}</ul>;
}
