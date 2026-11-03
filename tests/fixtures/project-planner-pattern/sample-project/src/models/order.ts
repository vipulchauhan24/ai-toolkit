export type OrderStatus = 'placed' | 'shipped';

export interface Order {
  id: string;
  customerId: string;
  totalCents: number;
  status: OrderStatus;
}
