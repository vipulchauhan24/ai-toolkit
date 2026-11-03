export function A({ list }: { list: string[] }) {
  return <div>{list.length && <span>x</span>}</div>;
}
