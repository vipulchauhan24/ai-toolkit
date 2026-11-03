interface OrderRowProps {
  items: { id: string; label: string }[];
  onSelect: (id: string) => void;
}

export function OrderRow({ items, onSelect }: OrderRowProps) {
  return (
    <ul>
      {items.map((item) => (
        <li key={item.id}>
          <button type="button" onClick={() => onSelect(item.id)}>
            {item.label}
          </button>
        </li>
      ))}
    </ul>
  );
}
