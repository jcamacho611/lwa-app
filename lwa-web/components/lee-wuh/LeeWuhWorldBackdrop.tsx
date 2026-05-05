"use client";

export default function LeeWuhWorldBackdrop() {
  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden bg-[#050506]">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_8%,rgba(201,162,74,0.18),transparent_30%),radial-gradient(circle_at_78%_28%,rgba(126,58,242,0.22),transparent_34%),radial-gradient(circle_at_18%_80%,rgba(201,162,74,0.12),transparent_30%)]" />
      <div className="absolute left-1/2 top-[-12%] h-[520px] w-[520px] -translate-x-1/2 rounded-full bg-[#C9A24A]/10 blur-[120px]" />
      <div className="absolute right-[-12%] top-[20%] h-[620px] w-[620px] rounded-full bg-purple-700/15 blur-[130px]" />
      <div className="absolute bottom-[-20%] left-[-10%] h-[520px] w-[520px] rounded-full bg-[#C9A24A]/10 blur-[120px]" />
      <div className="absolute inset-x-0 bottom-0 h-[45vh] bg-gradient-to-t from-black via-black/70 to-transparent" />
      <div className="absolute left-[8%] top-[18%] h-28 w-[1px] bg-gradient-to-b from-transparent via-[#C9A24A]/40 to-transparent" />
      <div className="absolute right-[18%] top-[10%] h-40 w-[1px] bg-gradient-to-b from-transparent via-purple-400/40 to-transparent" />
      <div className="absolute bottom-12 left-1/2 h-[1px] w-[80vw] -translate-x-1/2 bg-gradient-to-r from-transparent via-[#C9A24A]/25 to-transparent" />
    </div>
  );
}
