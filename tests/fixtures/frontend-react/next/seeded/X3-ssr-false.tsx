import dynamic from "next/dynamic";

const A = dynamic(() => import("./a"), { ssr: false });

export default A;
