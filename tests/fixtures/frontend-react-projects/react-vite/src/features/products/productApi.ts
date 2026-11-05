import type { Product } from "./product.types";

export async function fetchProducts(): Promise<Product[]> {
  const res = await fetch("/api/products");
  if (!res.ok) throw new Error(`products failed: ${res.status}`);
  return (await res.json()) as Product[];
}
