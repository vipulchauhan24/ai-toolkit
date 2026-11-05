import { useEffect, useState } from "react";
import { fetchProducts } from "./productApi";
import type { Product } from "./product.types";

export function useProductList() {
  const [products, setProducts] = useState<Product[]>([]);
  useEffect(() => {
    let live = true;
    fetchProducts().then((p) => {
      if (live) setProducts(p);
    });
    return () => {
      live = false;
    };
  }, []);
  return { products };
}
