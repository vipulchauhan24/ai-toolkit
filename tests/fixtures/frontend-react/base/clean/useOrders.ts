import { useEffect, useState } from "react";

export function useOrders(url: string) {
  const [orders, setOrders] = useState<string[]>([]);

  useEffect(() => {
    const controller = new AbortController();
    setOrders([url]);
    return () => controller.abort();
  }, [url]);

  return orders;
}
