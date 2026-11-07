import { Inject, Injectable } from "@nestjs/common";

export interface OrderRepository {
  count(): Promise<number>;
}

export const ORDER_REPOSITORY = Symbol("ORDER_REPOSITORY");

@Injectable()
export class OrderService {
  constructor(@Inject(ORDER_REPOSITORY) private readonly repository: OrderRepository) {}

  total(): Promise<number> {
    return this.repository.count();
  }
}
