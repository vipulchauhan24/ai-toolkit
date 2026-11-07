import type { Express } from "express";

export function register(app: Express): void {
  app.get("/orders", (_req, res) => {
    res.json([]);
  });
}
