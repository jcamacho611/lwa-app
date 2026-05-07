"use client";

import { useMemo, useState } from "react";
import { ArrowRight, BadgeCheck, RefreshCw, ShieldAlert, Sparkles, Trophy } from "lucide-react";
import {
  getBlockingDemoChecks,
  getDemoNarrativeForPersona,
  getNextPublicDemoStage,
  getPublicDemoStageById,
  lwaDemoReadinessChecks,
  lwaPublicDemoPersonas,
  lwaPublicDemoStages,
  lwaSignalSprintDemoChoices,
  type LwaPublicDemoPersonaId,
  type LwaPublicDemoStageId,
} from "../../lib/lwa-public-demo-loop";

export default function LwaPublicDemoLoopPanel() {
  const [stageId, setStageId] = useState<LwaPublicDemoStageId>("landing");
  const [personaId, setPersonaId] = useState<LwaPublicDemoPersonaId>("creator_beginner");
  const [promptIndex, setPromptIndex] = useState(0);
  const [selectedChoiceId, setSelectedChoiceId] = useState<string>("");
  const [resultLine, setResultLine] = useState<string>("Choose the best move to see your demo score.");
  const [scoreLine, setScoreLine] = useState<string>("XP 0");
  const [relicLine, setRelicLine] = useState<string>("No relic yet");

  const stage = getPublicDemoStageById(stageId);
  const prompt = lwaSignalSprintDemoChoices[promptIndex] ?? lwaSignalSprintDemoChoices[0];
  const blockingChecks = getBlockingDemoChecks();

  const narrative = useMemo(() => getDemoNarrativeForPersona(personaId), [personaId]);

  const advanceStage = () => {
    const nextStage = getNextPublicDemoStage(stageId);
    if (!nextStage) {
      setStageId("landing");
      setPromptIndex(0);
      setSelectedChoiceId("");
      setResultLine("Demo reset for another loop.");
      setScoreLine("XP 0");
      setRelicLine("No relic yet");
      return;
    }

    setStageId(nextStage.id);
    setSelectedChoiceId("");
    setResultLine(`Moved to ${nextStage.title}.`);
  };

  const resetDemo = () => {
    setStageId("landing");
    setPromptIndex(0);
    setSelectedChoiceId("");
    setResultLine("Demo reset for another loop.");
    setScoreLine("XP 0");
    setRelicLine("No relic yet");
  };

  const handleChoice = (choiceId: string) => {
    setSelectedChoiceId(choiceId);
    const selected = prompt.choices.find((item) => item.id === choiceId);
    const isCorrect = prompt.correctChoiceId === choiceId;
    const xp = isCorrect ? prompt.xpReward : Math.max(15, Math.round((selected?.score ?? 0) / 2));

    setScoreLine(`XP ${xp}`);
    setRelicLine(isCorrect ? prompt.relicReward : "Practice Shard");
    setResultLine(
      selected
        ? `${isCorrect ? "Best move." : "Useful, but not the best move."} ${selected.explanation}`
        : "Choice not found.",
    );
  };

  return (
    <section className="overflow-hidden rounded-[28px] border border-violet-300/20 bg-[#08050d] text-white shadow-2xl shadow-violet-950/30">
      <div className="border-b border-white/10 bg-gradient-to-r from-violet-950/60 via-black to-amber-950/20 px-6 py-5">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div className="max-w-3xl">
            <p className="text-[11px] uppercase tracking-[0.34em] text-amber-200/70">Public Demo Loop</p>
            <h1 className="mt-2 text-3xl font-black tracking-tight md:text-4xl">LWA public demo loop</h1>
            <p className="mt-3 text-sm text-white/65">
              This route shows the first-session creator loop, the guide, the recovery story, and the game layer without pretending payouts or posting automation are live.
            </p>
          </div>
          <div className="rounded-2xl border border-amber-300/20 bg-amber-300/10 px-4 py-3 text-sm text-amber-100">
            {stage.demoStatus.toUpperCase()} · {stage.title}
          </div>
        </div>
      </div>

      <div className="grid gap-6 p-6 xl:grid-cols-[1.15fr_0.85fr]">
        <div className="space-y-6">
          <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
            <div className="flex flex-wrap items-center gap-2 text-[11px] uppercase tracking-[0.2em] text-white/45">
              <span className="rounded-full border border-amber-300/20 bg-amber-300/10 px-2.5 py-1 text-amber-100">Persona</span>
              {lwaPublicDemoPersonas.map((persona) => (
                <button
                  key={persona.id}
                  type="button"
                  onClick={() => setPersonaId(persona.id)}
                  className={`rounded-full border px-3 py-1 transition ${
                    personaId === persona.id
                      ? "border-amber-300/50 bg-amber-300/15 text-amber-100"
                      : "border-white/10 bg-black/20 text-white/60 hover:border-white/20"
                  }`}
                >
                  {persona.title}
                </button>
              ))}
            </div>
            <p className="mt-4 text-sm text-white/70">{narrative}</p>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-3xl border border-white/10 bg-black/30 p-5">
              <p className="text-xs uppercase tracking-[0.3em] text-violet-200/60">Current stage</p>
              <h2 className="mt-2 text-2xl font-black">{stage.title}</h2>
              <p className="mt-3 text-sm text-white/65">{stage.leeWuhLine}</p>
              <div className="mt-4 space-y-3 text-sm text-white/60">
                <p><span className="text-white/80">User sees:</span> {stage.userSees}</p>
                <p><span className="text-white/80">User action:</span> {stage.userAction}</p>
                <p><span className="text-white/80">Engine connection:</span> {stage.engineConnection}</p>
              </div>
              <div className="mt-5 flex flex-wrap gap-2 text-[11px]">
                <span className="rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1 text-emerald-100">
                  {stage.demoStatus}
                </span>
                <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-white/60">
                  {stage.id}
                </span>
              </div>
              <div className="mt-5 flex flex-wrap gap-3">
                <button
                  type="button"
                  onClick={advanceStage}
                  className="inline-flex items-center gap-2 rounded-full bg-amber-300 px-4 py-2.5 text-sm font-bold text-black transition hover:bg-amber-200"
                >
                  Next stage
                  <ArrowRight className="h-4 w-4" />
                </button>
                <button
                  type="button"
                  onClick={resetDemo}
                  className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-4 py-2.5 text-sm font-semibold text-white/80 transition hover:border-white/25 hover:bg-white/10"
                >
                  <RefreshCw className="h-4 w-4" />
                  Reset demo
                </button>
              </div>
            </div>

            <div className="rounded-3xl border border-white/10 bg-black/30 p-5">
              <p className="text-xs uppercase tracking-[0.3em] text-violet-200/60">Signal Sprint</p>
              <h3 className="mt-2 text-2xl font-black">Mini decision round</h3>
              <p className="mt-3 text-sm text-white/65">{prompt.scenario}</p>
              <p className="mt-3 text-sm text-amber-100/90">{prompt.leeWuhLine}</p>
              <div className="mt-4 space-y-2">
                {prompt.choices.map((choice) => (
                  <button
                    key={choice.id}
                    type="button"
                    onClick={() => handleChoice(choice.id)}
                    className={`w-full rounded-2xl border px-4 py-3 text-left transition ${
                      selectedChoiceId === choice.id
                        ? "border-amber-300/60 bg-amber-300/10"
                        : "border-white/10 bg-white/[0.03] hover:border-white/20 hover:bg-white/[0.05]"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-3">
                      <span className="font-semibold">{choice.label}</span>
                      <span className="rounded-full border border-white/10 bg-black/20 px-2 py-1 text-[10px] uppercase tracking-[0.2em] text-white/55">
                        {choice.kind}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
              <div className="mt-5 grid gap-3 sm:grid-cols-3">
                <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-3">
                  <p className="text-[11px] uppercase tracking-[0.2em] text-white/40">Result</p>
                  <p className="mt-1 text-sm text-white/80">{resultLine}</p>
                </div>
                <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-3">
                  <p className="text-[11px] uppercase tracking-[0.2em] text-white/40">Score</p>
                  <p className="mt-1 text-lg font-bold text-amber-100">{scoreLine}</p>
                </div>
                <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-3">
                  <p className="text-[11px] uppercase tracking-[0.2em] text-white/40">Reward</p>
                  <p className="mt-1 text-lg font-bold text-violet-100">{relicLine}</p>
                </div>
              </div>
              <p className="mt-4 text-sm text-white/55">
                After this round, the next action should point back into generate, proof, export, or another source.
              </p>
            </div>
          </div>
        </div>

        <aside className="space-y-4">
          <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-amber-100" />
              <h3 className="text-sm font-bold uppercase tracking-[0.2em] text-white/70">What is live vs placeholder</h3>
            </div>
            <div className="mt-4 space-y-2 text-sm">
              {lwaPublicDemoStages.map((demoStage) => (
                <div key={demoStage.id} className="flex items-center justify-between gap-3 rounded-2xl border border-white/8 bg-black/20 px-3 py-2">
                  <div>
                    <p className="font-medium text-white">{demoStage.title}</p>
                    <p className="text-xs text-white/45">{demoStage.engineConnection}</p>
                  </div>
                  <span className={`rounded-full px-2.5 py-1 text-[10px] uppercase tracking-[0.18em] ${
                    demoStage.demoStatus === "live"
                      ? "bg-emerald-400/10 text-emerald-100"
                      : demoStage.demoStatus === "local_demo"
                        ? "bg-violet-400/10 text-violet-100"
                        : demoStage.demoStatus === "placeholder"
                          ? "bg-amber-300/10 text-amber-100"
                          : "bg-white/5 text-white/45"
                  }`}>
                    {demoStage.demoStatus}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
            <div className="flex items-center gap-2">
              <ShieldAlert className="h-4 w-4 text-amber-100" />
              <h3 className="text-sm font-bold uppercase tracking-[0.2em] text-white/70">Readiness checks</h3>
            </div>
            <div className="mt-4 space-y-2">
              {lwaDemoReadinessChecks.map((check) => (
                <div key={check.id} className="rounded-2xl border border-white/8 bg-black/20 p-3">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-medium text-white">{check.label}</p>
                    {check.status === "pass" ? (
                      <BadgeCheck className="h-4 w-4 text-emerald-300" />
                    ) : (
                      <ShieldAlert className="h-4 w-4 text-amber-200" />
                    )}
                  </div>
                  <p className="mt-1 text-xs text-white/45">{check.note}</p>
                </div>
              ))}
            </div>
            <div className="mt-4 rounded-2xl border border-amber-300/20 bg-amber-300/10 p-3 text-sm text-amber-100">
              {blockingChecks.length} blocker(s) remain intentionally visible: marketplace claims stay teaser-only until the real backend path exists.
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
            <div className="flex items-center gap-2">
              <Trophy className="h-4 w-4 text-amber-100" />
              <h3 className="text-sm font-bold uppercase tracking-[0.2em] text-white/70">Current mission card</h3>
            </div>
            <p className="mt-3 text-sm text-white/70">
              {narrative}
            </p>
            <div className="mt-4 rounded-2xl border border-white/10 bg-black/20 p-3 text-sm text-white/60">
              The demo loop should feel like a real first session, not a feature catalog.
            </div>
          </div>
        </aside>
      </div>
    </section>
  );
}
