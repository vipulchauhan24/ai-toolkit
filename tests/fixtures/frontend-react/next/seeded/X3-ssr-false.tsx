import dynamic from "next/dynamic";

const Chart = dynamic(() => import("./a"), { ssr: false });

export function Panel() {
  return <Chart />;
}
