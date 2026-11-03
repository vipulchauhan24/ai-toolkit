import { useState } from "react";

export default function Page() {
  const [n] = useState(0);
  return <div>{n}</div>;
}
