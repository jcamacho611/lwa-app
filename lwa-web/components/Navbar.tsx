import Link from "next/link";

type NavbarProps = {
  signedIn?: boolean;
};

export default function Navbar({ signedIn = false }: NavbarProps) {
  return (
    <div className="flex items-center justify-between gap-4 rounded-full border border-white/10 bg-black/30 px-5 py-4 backdrop-blur-xl">
      <Link href="/" className="text-xl font-bold text-neonPurple">
        LWA
      </Link>

      <div className="hidden items-center gap-6 text-sm text-white/70 md:flex">
        <Link href="/generate" className="transition hover:text-white">
          Generate
        </Link>
        <Link href="/history" className="transition hover:text-white">
          History
        </Link>
        <Link href="/dashboard" className="transition hover:text-white">
          Dashboard
        </Link>
      </div>

      <div className="text-sm text-white/60">{signedIn ? "Workspace" : "Web app"}</div>
    </div>
  );
}
