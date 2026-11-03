import { Order } from '../models/order';

const orders = new Map<string, Order>();

export function findOrder(id: string): Order | undefined {
  return orders.get(id);
}

export function saveOrder(order: Order): void {
  orders.set(order.id, order);
}
