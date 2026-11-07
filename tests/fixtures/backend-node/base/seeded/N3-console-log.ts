export function total(items: readonly number[]): number {
  const sum = items.reduce((a, b) => a + b, 0);
  console.log(sum);
  return sum;
}
