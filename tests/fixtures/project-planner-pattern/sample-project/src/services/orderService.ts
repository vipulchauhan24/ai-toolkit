import { Order } from '../models/order';
import { findOrder, saveOrder } from '../repositories/orderRepository';

export function getOrder(id: string): Order | undefined {
  return findOrder(id);
}

export function placeOrder(customerId: string, totalCents: number): Order {
  const order: Order = { id: crypto.randomUUID(), customerId, totalCents, status: 'placed' };
  saveOrder(order);
  return order;
}
