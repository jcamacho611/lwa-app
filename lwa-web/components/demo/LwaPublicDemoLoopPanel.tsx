"use client";

/**
 * LwaPublicDemoLoopPanel
 *
 * Client component. No backend calls, no auth, no payments, no crypto.
 * Renders the LWA Public Demo Loop: 9 stages + Signal Sprint mini-round
 * + readiness checklist + persona switcher.
 *
 * Companion data: lwa-web/lib/lwa-public-demo-loop.ts
 * Companion spec: docs/demo/LWA_PUBLIC_DEMO_LOOP_SPEC.md
 */

import { useMemo, useState } from "react";
import {
  LWA_PUBLIC_DEMO_FIRST_STAGE_ID,
  type LwaPublicDemoPersonaId,
  type LwaPublicDemoSignalSprintPrompt,
  type LwaPublicDemoStage,
  type LwaPublicDemoStageId,
  type LwaPublicDemoStatus,
  getNextPublicDemoStage,
  getPublicDemoStageById,
  lwaPublicDemoPersonas,
  lwaPublicDemoReadinessChecks,
  lwaPublicDemoStages,
  lwaSignalSprintDemoChoices,
} from "../../lib/lwa-public-demo-loop";

type SprintAttempt = {
  promptId: string;
  selectedChoiceId: string;
  isCorrect: boolean;
  xpAwarded: number;
  relic: string;
};

const COLOR_INK = "#0a0a0a";
const COLOR_INK_SOFT = "#141014";
const COLOR_GOLD = "#C9A24A";
const COLOR_GOLD_SOFT = "rgba(201, 162, 74, 0.14)";
const COLOR_PURPLE = "#6B2A9E";
const COLOR_PURPLE_SOFT = "rgba(107, 42, 158, 0.18)";
const COLOR_TEXT = "rgba(255, 255, 255, 0.92)";
const COLOR_MUTED = "rgba(255, 255, 255, 0.55)";
const COLOR_FAINT = "rgba(255, 255, 255, 0.35)";
const COLOR_LINE = "rgba(255, 255, 255, 0.08)";

function statusStyle(status: LwaPublicDemoStatus): {
  background: string;
  color: string;
  label: string;
} {
  switch (status) {
    case "live":
      return {
        background: "rgba(201, 162, 74, 0.18)",
        color: COLOR_GOLD,
        label: "LIVE",
      };
    case "local_demo":
      return {
        background: "rgba(107, 42, 158, 0.22)",
        color: "#D9B4FF",
        label: "LOCAL DEMO",
      };
    case "placeholder":
      return {
        background: "rgba(255, 255, 255, 0.08)",
        color: COLOR_MUTED,
        label: "PLACEHOLDER",
      };
    case "disabled":
      return {
        background: "rgba(255, 255, 255, 0.04)",
        color: COLOR_FAINT,
        label: "DISABLED",
      };
    case "blocking":
      return {
        background: "rgba(220, 80, 80, 0.18)",
        color: "#F2A0A0",
        label: "BLOCKING",
      };
  }
}

function StageBadge({ status }: { status: LwaPublicDemoStatus }) {
  const s = statusStyle(status);
  return (
    <span
      style={{
        background: s.background,
        color: s.color,
        fontSize: 10,
        letterSpacing: 1.4,
        fontFamily:
          "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
        padding: "3px 8px",
        borderRadius: 999,
        border: `1px solid ${s.color}33`,
        textTransform: "uppercase",
      }}
    >
      {s.label}
    </span>
  );
}

function StageRow({
  stage,
  active,
  index,
  onSelect,
}: {
  stage: LwaPublicDemoStage;
  active: boolean;
  index: number;
  onSelect: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onSelect}
      style={{
        display: "grid",
        gridTemplateColumns: "32px 1fr auto",
        gap: 14,
        alignItems: "center",
        padding: "12px 14px",
        textAlign: "left",
        background: active ? COLOR_GOLD_SOFT : "transparent",
        border: `1px solid ${active ? COLOR_GOLD : COLOR_LINE}`,
        borderRadius: 10,
        cursor: "pointer",
        color: COLOR_TEXT,
        width: "100%",
        transition: "background 120ms ease, border-color 120ms ease",
      }}
    >
      <span
        style={{
          fontFamily:
            "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
          color: active ? COLOR_GOLD : COLOR_FAINT,
          fontSize: 11,
          letterSpacing: 1.5,
        }}
      >
        {String(index + 1).padStart(2, "0")}
      </span>
      <span
        style={{
          fontWeight: active ? 600 : 500,
          color: active ? "#FFFFFF" : COLOR_TEXT,
          fontSize: 14,
        }}
      >
        {stage.title}
      </span>
      <StageBadge status={stage.demoStatus} />
    </button>
  );
}

function ReadinessRow({
  label,
  status,
  assertion,
}: {
  label: string;
  status: LwaPublicDemoStatus;
  assertion: string;
}) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "1fr auto",
        gap: 10,
        padding: "10px 12px",
        borderBottom: `1px solid ${COLOR_LINE}`,
      }}
    >
      <div>
        <div style={{ color: COLOR_TEXT, fontSize: 13, fontWeight: 500 }}>
          {label}
        </div>
        <div style={{ color: COLOR_MUTED, fontSize: 12, marginTop: 2 }}>
          {assertion}
        </div>
      </div>
      <StageBadge status={status} />
    </div>
  );
}

export default function LwaPublicDemoLoopPanel() {
  const [stageId, setStageId] = useState<LwaPublicDemoStageId>(
    LWA_PUBLIC_DEMO_FIRST_STAGE_ID,
  );
  const [personaId, setPersonaId] =
    useState<LwaPublicDemoPersonaId>("creator_beginner");
  const [sprintIndex, setSprintIndex] = useState(0);
  const [sprintAttempt, setSprintAttempt] = useState<SprintAttempt | null>(
    null,
  );

  const stage = useMemo(() => getPublicDemoStageById(stageId), [stageId]);
  const stageOrderIndex = useMemo(
    () => lwaPublicDemoStages.findIndex((s) => s.id === stageId),
    [stageId],
  );
  const persona = useMemo(
    () => lwaPublicDemoPersonas.find((p) => p.id === personaId),
    [personaId],
  );
  const sprintPrompt: LwaPublicDemoSignalSprintPrompt | undefined =
    lwaSignalSprintDemoChoices[sprintIndex];

  const advanceStage = () => {
    if (!stage) return;
    const next = getNextPublicDemoStage(stage.id);
    if (next) {
      setStageId(next.id);
    }
  };

  const resetDemo = () => {
    setStageId(LWA_PUBLIC_DEMO_FIRST_STAGE_ID);
    setSprintIndex(0);
    setSprintAttempt(null);
  };

  const onSprintChoice = (choiceId: string) => {
    if (!sprintPrompt) return;
    const isCorrect = choiceId === sprintPrompt.correctChoiceId;
    setSprintAttempt({
      promptId: sprintPrompt.id,
      selectedChoiceId: choiceId,
      isCorrect,
      xpAwarded: isCorrect ? sprintPrompt.xpReward : Math.floor(sprintPrompt.xpReward / 3),
      relic: isCorrect ? sprintPrompt.relicReward : "Practice mark",
    });
  };

  const nextSprintPrompt = () => {
    setSprintAttempt(null);
    setSprintIndex((prev) => (prev + 1) % lwaSignalSprintDemoChoices.length);
  };

  const isFinalStage = stage?.nextStageId === null;
  const isSignalSprintStage = stageId === "signal_sprint";

  return (
    <div
      style={{
        background: COLOR_INK,
        color: COLOR_TEXT,
        minHeight: "100vh",
        padding: "48px 24px",
        fontFamily:
          'ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
      }}
    >
      <div style={{ maxWidth: 1120, margin: "0 auto" }}>
        {/* Header */}
        <header style={{ marginBottom: 28 }}>
          <div
            style={{
              fontFamily:
                "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
              color: COLOR_GOLD,
              letterSpacing: 3,
              fontSize: 11,
              marginBottom: 10,
            }}
          >
            LWA · PUBLIC DEMO LOOP
          </div>
          <h1
            style={{
              fontSize: 30,
              fontWeight: 600,
              color: "#FFFFFF",
              margin: 0,
              letterSpacing: -0.5,
            }}
          >
            One source. One loop. One realm.
          </h1>
          <p
            style={{
              color: COLOR_MUTED,
              marginTop: 10,
              maxWidth: 720,
              lineHeight: 1.55,
              fontSize: 15,
            }}
          >
            Lee-Wuh-guided creator workflow plus a creator-skill game layer. No backend writes, no auth, no payments — this is the public demo lane.
          </p>
        </header>

        {/* Persona switcher */}
        <section
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 8,
            marginBottom: 24,
          }}
        >
          {lwaPublicDemoPersonas.map((p) => {
            const active = p.id === personaId;
            return (
              <button
                key={p.id}
                type="button"
                onClick={() => setPersonaId(p.id)}
                style={{
                  background: active ? COLOR_PURPLE_SOFT : "transparent",
                  color: active ? "#FFFFFF" : COLOR_MUTED,
                  border: `1px solid ${active ? COLOR_PURPLE : COLOR_LINE}`,
                  borderRadius: 999,
                  padding: "8px 14px",
                  fontSize: 12,
                  cursor: "pointer",
                  letterSpacing: 0.4,
                }}
              >
                {p.label}
              </button>
            );
          })}
        </section>

        {/* Persona framing */}
        {persona && (
          <div
            style={{
              border: `1px solid ${COLOR_LINE}`,
              background: COLOR_INK_SOFT,
              borderRadius: 12,
              padding: "14px 18px",
              color: COLOR_MUTED,
              fontSize: 13,
              marginBottom: 28,
            }}
          >
            <span
              style={{
                fontFamily:
                  "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
                color: COLOR_GOLD,
                letterSpacing: 1.6,
                fontSize: 10,
                marginRight: 10,
                textTransform: "uppercase",
              }}
            >
              persona · {persona.tone.replace("_", " ")}
            </span>
            {persona.framing}
          </div>
        )}

        {/* Two-column grid */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "minmax(280px, 1fr) 1.6fr",
            gap: 24,
          }}
        >
          {/* Stage rail */}
          <aside style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            <div
              style={{
                fontFamily:
                  "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
                color: COLOR_FAINT,
                letterSpacing: 1.6,
                fontSize: 10,
                marginBottom: 6,
                textTransform: "uppercase",
              }}
            >
              stages · 1 of 9
            </div>
            {lwaPublicDemoStages.map((s, idx) => (
              <StageRow
                key={s.id}
                stage={s}
                active={s.id === stageId}
                index={idx}
                onSelect={() => {
                  setStageId(s.id);
                  setSprintAttempt(null);
                }}
              />
            ))}
          </aside>

          {/* Active stage detail */}
          <section style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {stage && (
              <article
                style={{
                  background: COLOR_INK_SOFT,
                  border: `1px solid ${COLOR_LINE}`,
                  borderRadius: 14,
                  padding: 24,
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                    gap: 16,
                  }}
                >
                  <div>
                    <div
                      style={{
                        fontFamily:
                          "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
                        color: COLOR_GOLD,
                        letterSpacing: 1.8,
                        fontSize: 10,
                        marginBottom: 8,
                        textTransform: "uppercase",
                      }}
                    >
                      stage {String(stageOrderIndex + 1).padStart(2, "0")} · {stage.id}
                    </div>
                    <h2
                      style={{
                        fontSize: 24,
                        fontWeight: 600,
                        color: "#FFFFFF",
                        margin: 0,
                      }}
                    >
                      {stage.title}
                    </h2>
                  </div>
                  <StageBadge status={stage.demoStatus} />
                </div>

                {/* Lee-Wuh line */}
                <div
                  style={{
                    marginTop: 22,
                    padding: "16px 18px",
                    borderLeft: `2px solid ${COLOR_GOLD}`,
                    background: COLOR_GOLD_SOFT,
                    borderRadius: "0 8px 8px 0",
                  }}
                >
                  <div
                    style={{
                      fontFamily:
                        "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
                      color: COLOR_GOLD,
                      letterSpacing: 1.6,
                      fontSize: 10,
                      marginBottom: 6,
                      textTransform: "uppercase",
                    }}
                  >
                    lee-wuh
                  </div>
                  <div
                    style={{
                      color: "#FFFFFF",
                      fontSize: 17,
                      lineHeight: 1.45,
                      fontStyle: "italic",
                    }}
                  >
                    “{stage.leeWuhLine}”
                  </div>
                </div>

                {/* Body */}
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: 16,
                    marginTop: 22,
                  }}
                >
                  <div>
                    <div
                      style={{
                        color: COLOR_FAINT,
                        fontSize: 11,
                        letterSpacing: 1.4,
                        textTransform: "uppercase",
                        marginBottom: 6,
                        fontFamily:
                          "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
                      }}
                    >
                      user sees
                    </div>
                    <div style={{ fontSize: 14, color: COLOR_TEXT, lineHeight: 1.5 }}>
                      {stage.userSees}
                    </div>
                  </div>
                  <div>
                    <div
                      style={{
                        color: COLOR_FAINT,
                        fontSize: 11,
                        letterSpacing: 1.4,
                        textTransform: "uppercase",
                        marginBottom: 6,
                        fontFamily:
                          "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
                      }}
                    >
                      engine connection
                    </div>
                    <div
                      style={{
                        fontSize: 13,
                        color: COLOR_MUTED,
                        lineHeight: 1.5,
                        fontFamily:
                          "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
                      }}
                    >
                      {stage.engineConnection}
                    </div>
                  </div>
                </div>

                <div
                  style={{
                    marginTop: 18,
                    color: COLOR_MUTED,
                    fontSize: 13,
                    lineHeight: 1.55,
                  }}
                >
                  <span
                    style={{
                      color: COLOR_FAINT,
                      fontSize: 11,
                      letterSpacing: 1.4,
                      textTransform: "uppercase",
                      marginRight: 8,
                      fontFamily:
                        "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
                    }}
                  >
                    why
                  </span>
                  {stage.rationale}
                </div>

                {/* Stage actions */}
                <div
                  style={{
                    display: "flex",
                    gap: 10,
                    marginTop: 26,
                    flexWrap: "wrap",
                  }}
                >
                  <button
                    type="button"
                    onClick={advanceStage}
                    disabled={isFinalStage}
                    style={{
                      background: COLOR_GOLD,
                      color: COLOR_INK,
                      border: "none",
                      borderRadius: 10,
                      padding: "12px 18px",
                      fontWeight: 600,
                      fontSize: 14,
                      cursor: isFinalStage ? "default" : "pointer",
                      opacity: isFinalStage ? 0.4 : 1,
                      letterSpacing: 0.3,
                    }}
                  >
                    {isFinalStage ? "Loop complete" : `Next · ${stage.userAction.label}`}
                  </button>
                  <button
                    type="button"
                    onClick={resetDemo}
                    style={{
                      background: "transparent",
                      color: COLOR_TEXT,
                      border: `1px solid ${COLOR_LINE}`,
                      borderRadius: 10,
                      padding: "12px 16px",
                      fontSize: 13,
                      cursor: "pointer",
                    }}
                  >
                    Reset demo
                  </button>
                </div>

                <div
                  style={{
                    marginTop: 14,
                    color: COLOR_FAINT,
                    fontSize: 12,
                  }}
                >
                  Action meaning: {stage.userAction.meaning}
                </div>
              </article>
            )}

            {/* Signal Sprint mini-round (always visible, highlighted on its stage) */}
            {sprintPrompt && (
              <article
                style={{
                  background: COLOR_INK_SOFT,
                  border: `1px solid ${
                    isSignalSprintStage ? COLOR_PURPLE : COLOR_LINE
                  }`,
                  borderRadius: 14,
                  padding: 22,
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                    gap: 16,
                    marginBottom: 14,
                  }}
                >
                  <div>
                    <div
                      style={{
                        fontFamily:
                          "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
                        color: COLOR_PURPLE === "#6B2A9E" ? "#D9B4FF" : COLOR_PURPLE,
                        letterSpacing: 1.8,
                        fontSize: 10,
                        marginBottom: 6,
                        textTransform: "uppercase",
                      }}
                    >
                      signal sprint · skill: {sprintPrompt.skill}
                    </div>
                    <h3
                      style={{
                        fontSize: 18,
                        fontWeight: 600,
                        color: "#FFFFFF",
                        margin: 0,
                      }}
                    >
                      Choose the lane that earns attention.
                    </h3>
                  </div>
                  <StageBadge status="local_demo" />
                </div>

                <div
                  style={{
                    color: COLOR_TEXT,
                    fontSize: 14,
                    lineHeight: 1.55,
                    marginBottom: 16,
                  }}
                >
                  {sprintPrompt.scenario}
                </div>

                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr",
                    gap: 8,
                  }}
                >
                  {sprintPrompt.choices.map((c) => {
                    const picked = sprintAttempt?.selectedChoiceId === c.id;
                    const showCorrect =
                      sprintAttempt && c.id === sprintPrompt.correctChoiceId;
                    const showWrong =
                      sprintAttempt && picked && !sprintAttempt.isCorrect;
                    return (
                      <button
                        key={c.id}
                        type="button"
                        onClick={() => onSprintChoice(c.id)}
                        disabled={Boolean(sprintAttempt)}
                        style={{
                          textAlign: "left",
                          padding: "12px 14px",
                          background: showCorrect
                            ? "rgba(201, 162, 74, 0.18)"
                            : showWrong
                            ? "rgba(220, 80, 80, 0.16)"
                            : "transparent",
                          color: COLOR_TEXT,
                          border: `1px solid ${
                            showCorrect
                              ? COLOR_GOLD
                              : showWrong
                              ? "#C25656"
                              : COLOR_LINE
                          }`,
                          borderRadius: 10,
                          cursor: sprintAttempt ? "default" : "pointer",
                          fontSize: 14,
                        }}
                      >
                        {c.label}
                        {sprintAttempt && (showCorrect || picked) && (
                          <div
                            style={{
                              marginTop: 6,
                              color: COLOR_MUTED,
                              fontSize: 12,
                              fontStyle: "italic",
                            }}
                          >
                            {c.reaction}
                          </div>
                        )}
                      </button>
                    );
                  })}
                </div>

                {sprintAttempt && (
                  <div
                    style={{
                      marginTop: 16,
                      padding: "12px 14px",
                      background: sprintAttempt.isCorrect
                        ? COLOR_GOLD_SOFT
                        : "rgba(255, 255, 255, 0.04)",
                      border: `1px solid ${
                        sprintAttempt.isCorrect ? COLOR_GOLD : COLOR_LINE
                      }`,
                      borderRadius: 10,
                    }}
                  >
                    <div
                      style={{
                        fontFamily:
                          "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
                        color: sprintAttempt.isCorrect ? COLOR_GOLD : COLOR_MUTED,
                        letterSpacing: 1.6,
                        fontSize: 10,
                        textTransform: "uppercase",
                        marginBottom: 6,
                      }}
                    >
                      result · +{sprintAttempt.xpAwarded} xp · {sprintAttempt.relic}
                    </div>
                    <div
                      style={{ color: COLOR_TEXT, fontSize: 13, lineHeight: 1.5 }}
                    >
                      {sprintPrompt.explanation}
                    </div>
                    <button
                      type="button"
                      onClick={nextSprintPrompt}
                      style={{
                        marginTop: 12,
                        background: "transparent",
                        color: COLOR_GOLD,
                        border: `1px solid ${COLOR_GOLD}`,
                        borderRadius: 10,
                        padding: "8px 14px",
                        fontSize: 13,
                        cursor: "pointer",
                      }}
                    >
                      Next prompt
                    </button>
                  </div>
                )}
              </article>
            )}

            {/* Readiness checklist */}
            <article
              style={{
                background: COLOR_INK_SOFT,
                border: `1px solid ${COLOR_LINE}`,
                borderRadius: 14,
                padding: "8px 4px 0",
              }}
            >
              <div
                style={{
                  padding: "14px 16px 6px",
                  borderBottom: `1px solid ${COLOR_LINE}`,
                }}
              >
                <div
                  style={{
                    fontFamily:
                      "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
                    color: COLOR_GOLD,
                    letterSpacing: 1.8,
                    fontSize: 10,
                    marginBottom: 4,
                    textTransform: "uppercase",
                  }}
                >
                  readiness · {lwaPublicDemoReadinessChecks.length} checks
                </div>
                <div style={{ color: COLOR_TEXT, fontSize: 14 }}>
                  What is live, what is local-only, and what is intentionally disabled.
                </div>
              </div>
              <div style={{ padding: "0 12px" }}>
                {lwaPublicDemoReadinessChecks.map((c) => (
                  <ReadinessRow
                    key={c.id}
                    label={c.label}
                    status={c.status}
                    assertion={c.assertion}
                  />
                ))}
              </div>
            </article>
          </section>
        </div>

        {/* Footer */}
        <footer
          style={{
            marginTop: 36,
            paddingTop: 18,
            borderTop: `1px solid ${COLOR_LINE}`,
            color: COLOR_FAINT,
            fontSize: 12,
            display: "flex",
            justifyContent: "space-between",
            flexWrap: "wrap",
            gap: 10,
          }}
        >
          <span>
            LWA Public Demo Loop · additive lane · no backend, no auth, no payments
          </span>
          <span
            style={{
              fontFamily:
                "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
              letterSpacing: 1.4,
            }}
          >
            persona: {persona?.id ?? "—"} · stage: {stage?.id ?? "—"}
          </span>
        </footer>
      </div>
    </div>
  );
}
