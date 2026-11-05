export type Order = { id: string; total: number };
export type Notification = { id: string; text: string };

export async function getOrders(): Promise<Order[]> {
  const res = await fetch("https://api.example.test/orders");
  return (await res.json()) as Order[];
}

export async function getNotifications(): Promise<Notification[]> {
  const res = await fetch("https://api.example.test/notifications");
  return (await res.json()) as Notification[];
}
