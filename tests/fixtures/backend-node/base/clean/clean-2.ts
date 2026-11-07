import { Order } from "./clean-1.js";

export interface OrderRepository {
  save(order: Order): Promise<void>;
}

export class OrderService {
  constructor(private readonly repository: OrderRepository) {}

  async create(id: string, totalCents: number, now: Date): Promise<Order> {
    const order = new Order({ id, status: "pending", totalCents, createdAt: now });
    await this.repository.save(order);
    return order;
  }
}

// A test may hold a fake credential when the line says so.
export const fakePassword = "correct-horse-battery"; // test-only
