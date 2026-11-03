export function PricingCard({ name, price }: { name: string; price: string }) {
  return (
    <section className="bg-surface text-primary p-4 rounded-md border border-default">
      <h2 className="text-lg font-semibold">{name}</h2>
      <p className="text-secondary">{price}</p>
    </section>
  );
}
