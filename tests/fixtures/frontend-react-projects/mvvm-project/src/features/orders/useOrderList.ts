import { useEffect, useState } from 'react';
import { fetchOrders } from './orderApi';
import { Order } from './order.types';

export function useOrderList() {
  const [orders, setOrders] = useState<Order[]>([]);
  useEffect(() => {
    fetchOrders().then(setOrders);
  }, []);
  return { orders };
}
