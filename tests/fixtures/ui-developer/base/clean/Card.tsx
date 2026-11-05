export function Card({ title }: { title: string }) {
  return (
    <section className="rounded-md bg-surface p-4">
      <h2 className="text-lg font-semibold text-primary">{title}</h2>
    </section>
  );
}
