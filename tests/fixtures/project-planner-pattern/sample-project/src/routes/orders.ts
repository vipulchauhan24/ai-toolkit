import { Router } from 'express';
import { getOrder, placeOrder } from '../services/orderService';

export const ordersRouter = Router();

ordersRouter.post('/orders', (req, res) => {
  const { customerId, totalCents } = req.body;
  res.status(201).json(placeOrder(customerId, totalCents));
});

ordersRouter.get('/orders/:id', (req, res) => {
  const order = getOrder(req.params.id);
  if (!order) {
    res.status(404).json({ error: 'not found' });
    return;
  }
  res.json(order);
});
