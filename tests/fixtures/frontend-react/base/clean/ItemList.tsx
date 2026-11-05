import { useState } from "react";

type Item = { id: string; name: string };
type Props = { label: string; items: Item[] };

export function ItemList({ label, items }: Props) {
  const [open, setOpen] = useState(false);
  return (
    <section>
      <button type="button" onClick={() => setOpen(!open)}>
        {label}
      </button>
      {open ? (
        <ul>
          {items.map((it) => (
            <li key={it.id}>{it.name}</li>
          ))}
        </ul>
      ) : null}
    </section>
  );
}
