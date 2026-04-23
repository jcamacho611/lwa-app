import Link from "next/link";

type RoutePlaceholderProps = {
  title: string;
};

export function RoutePlaceholder({ title }: RoutePlaceholderProps) {
  return (
    <section className="px-4 py-6 sm:px-6 lg:px-8">
      <div className="mx-auto flex min-h-[calc(100vh-3rem)] w-full max-w-3xl flex-col items-center justify-center text-center">
        <div className="rounded-[30px] border border-[var(--gold-border)] bg-black/35 px-8 py-10 backdrop-blur-md">
          <p className="section-kicker">{title}</p>
          <h1 className="mt-4 text-4xl font-semibold text-ink sm:text-5xl">{title}</h1>
          <p className="mt-4 text-base leading-8 text-subtext">
            Coming soon. Focus on Generate for now.
          </p>
          <Link
            href="/generate"
            className="primary-button mt-8 inline-flex min-h-[44px] items-center justify-center rounded-full px-6 py-3 text-sm font-semibold"
          >
            Back to Generate
          </Link>
        </div>
      </div>
    </section>
  );
}
