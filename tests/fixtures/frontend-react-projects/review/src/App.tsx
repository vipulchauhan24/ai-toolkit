import { useEffect, useState } from "react";

export function App({ data }: { data: any }) {
  const [rows, setRows] = useState<string[]>([]);
  useEffect(() => {
    setRows(data.rows);
  });
  console.log("render", rows.length);
  return (
    <div onClick={() => setRows([])}>
      {rows.map((r, i) => (
        <p key={i}>{r}</p>
      ))}
    </div>
  );
}
