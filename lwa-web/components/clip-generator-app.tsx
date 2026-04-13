"use client";

import { useMemo, useRef, useState } from "react";
import { HeroSection } from "./hero-section";
import { InputSection } from "./input-section";
import { LoadingState } from "./loading-state";
import { ResultsSection } from "./results-section";
import type { ClipResponse, GenerateState, PlatformCode } from "@/lib/types";

export function ClipGeneratorApp() {
  const [url, setUrl] = useState("");
  const [platform, setPlatform] = useState<PlatformCode>("TikTok");
  const [state, setState] = useState<GenerateState>({ status: "idle" });
  const inputRef = useRef<HTMLDivElement | null>(null);

  const result = useMemo<ClipResponse | null>(() => {
    if (state.status !== "success") {
      return null;
    }
    return state.data;
  }, [state]);

  async function handleGenerate() {
    const trimmed = url.trim();

    if (!trimmed) {
      setState({
        status: "error",
        message: "Paste a public video URL before generating clips.",
      });
      return;
    }

    setState({ status: "loading" });

    try {
      const response = await fetch("/api/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url: trimmed,
          platform,
        }),
      });

      const payload = (await response.json()) as ClipResponse & { message?: string };

      if (!response.ok) {
        throw new Error(payload.message ?? "The backend could not generate clips.");
      }

      setState({
        status: "success",
        data: payload,
      });
    } catch (error) {
      setState({
        status: "error",
        message:
          error instanceof Error
            ? error.message
            : "Something went wrong while generating clips.",
      });
    }
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-7xl flex-col gap-8 px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
      <HeroSection
        onStart={() => inputRef.current?.scrollIntoView({ behavior: "smooth", block: "start" })}
      />

      <div ref={inputRef} className="space-y-5">
        <InputSection
          url={url}
          platform={platform}
          loading={state.status === "loading"}
          onUrlChange={setUrl}
          onPlatformChange={setPlatform}
          onSubmit={handleGenerate}
        />

        {state.status === "loading" ? <LoadingState /> : null}

        {state.status === "error" ? (
          <section className="glass-panel rounded-[1.75rem] px-5 py-6 sm:px-6">
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-red-300">
              Request failed
            </p>
            <h2 className="mt-2 text-xl font-semibold text-white">
              We couldn&apos;t generate the clip pack
            </h2>
            <p className="mt-2 text-sm text-muted sm:text-base">{state.message}</p>
          </section>
        ) : null}

        {result ? <ResultsSection result={result} /> : null}
      </div>
    </main>
  );
}
