import { useEffect, useState } from "react";

export function BadList({ source }: { source: any }) {
  const [rows, setRows] = useState([]);
  useEffect(() => {
    fetch(source).then((r) => r.json()).then(setRows);
  });
  console.log(rows);
  return (
    <ul>
      {rows.map((row: any, i) => (
        <li key={i} onClick={() => alert(row.id)}>{row.name}</li>
      ))}
    </ul>
  );
}
