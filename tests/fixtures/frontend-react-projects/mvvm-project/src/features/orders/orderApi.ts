import { Order } from './order.types';

export async function fetchOrders(): Promise<Order[]> {
  const res = await fetch('/api/orders');
  return res.json();
}
