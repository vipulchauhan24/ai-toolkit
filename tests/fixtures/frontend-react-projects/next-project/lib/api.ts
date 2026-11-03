export interface Order {
  id: string;
  totalCents: number;
}

export interface Customer {
  id: string;
  name: string;
}

export async function fetchOrders(): Promise<Order[]> {
  const res = await fetch("https://api.example.test/orders", { cache: "no-store" });
  return (await res.json()) as Order[];
}

export async function fetchCustomer(): Promise<Customer> {
  const res = await fetch("https://api.example.test/customer", { cache: "no-store" });
  return (await res.json()) as Customer;
}
