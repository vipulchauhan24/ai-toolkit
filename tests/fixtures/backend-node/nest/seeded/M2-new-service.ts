import { OrderService } from "./order.service.js";

export function build(): OrderService {
  return new OrderService({ count: async () => 0 });
}
