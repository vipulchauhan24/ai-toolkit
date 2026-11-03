import { useOrderList } from './useOrderList';

export function OrderList() {
  const { orders } = useOrderList();
  return (
    <ul>
      {orders.map((o) => (
        <li key={o.id}>{o.totalCents}</li>
      ))}
    </ul>
  );
}
