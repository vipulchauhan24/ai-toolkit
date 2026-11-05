import { useProductList } from "./useProductList";

export function ProductList() {
  const { products } = useProductList();
  return (
    <ul>
      {products.map((p) => (
        <li key={p.id}>{p.name}</li>
      ))}
    </ul>
  );
}
