import type { Metadata } from "next";
import BackendEngineRoomPanel from "../../components/engines/BackendEngineRoomPanel";

export const metadata: Metadata = {
  title: "LWA Engine Room",
  description: "Actual backend engine status for the LWA platform.",
};

export default function EnginesPage() {
  return (
    <main className="min-h-screen bg-[#07030f] px-5 py-10 text-white md:px-10">
      <div className="mx-auto max-w-7xl">
        <div className="mb-8 rounded-[2rem] border border-white/10 bg-white/[0.03] p-6">
          <p className="text-xs uppercase tracking-[0.35em] text-violet-200/70">Actual backend truth</p>
          <h1 className="mt-3 text-4xl font-black tracking-tight md:text-6xl">LWA Engine Room</h1>
          <p className="mt-4 max-w-4xl text-base text-white/65">
            This route separates real backend engines from frontend demos. Railway services are deployable boxes; backend engines are modules inside the API until they are intentionally split into workers or services.
          </p>
        </div>
        <BackendEngineRoomPanel />
      </div>
    </main>
  );
}
