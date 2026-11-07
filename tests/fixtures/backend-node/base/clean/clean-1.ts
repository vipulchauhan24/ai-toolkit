export type OrderStatus = "pending" | "paid" | "cancelled";

export interface OrderFields {
  readonly id: string;
  readonly status: OrderStatus;
  readonly totalCents: number;
  readonly createdAt: Date;
}

export class Order {
  readonly id: string;
  readonly status: OrderStatus;
  readonly totalCents: number;
  readonly createdAt: Date;

  constructor(fields: OrderFields) {
    this.id = fields.id;
    this.status = fields.status;
    this.totalCents = fields.totalCents;
    this.createdAt = fields.createdAt;
  }
}
