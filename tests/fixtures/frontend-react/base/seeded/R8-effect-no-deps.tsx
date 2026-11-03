import { useEffect } from "react";

function run() {}

export function A() {
  useEffect(() => {
    run();
  });
  return null;
}
