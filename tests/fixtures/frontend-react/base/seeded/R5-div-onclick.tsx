export function Box({ f }: { f: () => void }) {
  return <div onClick={f}>x</div>;
}
