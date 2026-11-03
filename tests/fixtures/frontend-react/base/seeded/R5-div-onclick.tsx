export function A({ f }: { f: () => void }) {
  return <div onClick={f}>x</div>;
}
