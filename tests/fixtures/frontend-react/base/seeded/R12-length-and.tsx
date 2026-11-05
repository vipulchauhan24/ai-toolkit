export function Items({ list }: { list: string[] }) {
  return <div>{list.length && <p>items</p>}</div>;
}
