import { Module } from "@nestjs/common";

import { OrderService } from "./clean-1.js";

@Module({
  providers: [OrderService],
  exports: [OrderService],
})
export class OrderModule {}
