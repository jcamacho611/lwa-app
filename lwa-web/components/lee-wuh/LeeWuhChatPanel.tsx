"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useMemo, useState } from "react";
import { getLeeWuhAnimationState, type LeeWuhAnimationState } from "./leeWuhAnimationStates";
import {
  getLeeWuhRouteIntelligence,
  resolveLeeWuhChatResponse,
  type LeeWuhChatResponse,
} from "./leeWuhIntelligence";
import type { LeeWuhMove } from "./leeWuhMoves";

type ChatMessage = {
  id: string;
  role: "user" | "lee-wuh";
  text: string;
  state: LeeWuhAnimationState;
  moves?: LeeWuhMove[];
};

type LeeWuhChatPanelProps = {
  onClose?: () => void;
  className?: string;
};

export default function LeeWuhChatPanel({ onClose, className = "" }: LeeWuhChatPanelProps) {
  const pathname = usePathname() || "/";
  const route = useMemo(() => getLeeWuhRouteIntelligence(pathname), [pathname]);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "intro",
      role: "lee-wuh",
      text: route.intro,
      state: route.state,
      moves: route.moves,
    },
  ]);

  function addResponse(query: string) {
    const trimmed = query.trim();
    if (!trimmed) return;

    const response: LeeWuhChatResponse = resolveLeeWuhChatResponse(trimmed, pathname);
    setMessages((current) => [
      ...current,
      {
        id: `user-${Date.now()}`,
        role: "user",
        text: trimmed,
        state: "speak",
      },
      {
        id: `lee-wuh-${Date.now()}`,
        role: "lee-wuh",
        text: response.message,
        state: response.state,
        moves: response.moves,
      },
    ]);
    setInput("");
  }

  return (
    <section
      className={[
        "rounded-[28px] border border-[#C9A24A]/25 bg-[#08080A]/95 p-4 text-[#F5F1E8] shadow-[0_24px_90px_rgba(0,0,0,0.55)] backdrop-blur",
        className,
      ].join(" ")}
    >
      <div className="flex items-start justify-between gap-4 border-b border-white/10 pb-4">
        <div>
          <p className="font-mono text-xs uppercase tracking-[0.24em] text-[#E9C77B]">
            Lee-Wuh // Local AI shell
          </p>
          <h2 className="mt-2 text-xl font-semibold text-white">{route.title}</h2>
          <p className="mt-1 text-sm leading-6 text-white/55">
            Rule-based first. Provider AI can enhance later.
          </p>
        </div>
        {onClose ? (
          <button
            type="button"
            onClick={onClose}
            className="rounded-full border border-white/10 px-3 py-1 text-sm text-white/60 transition hover:border-[#C9A24A]/40 hover:text-white"
          >
            Close
          </button>
        ) : null}
      </div>

      <div className="mt-4 max-h-[420px] space-y-3 overflow-y-auto pr-1">
        {messages.map((message) => {
          const state = getLeeWuhAnimationState(message.state);
          return (
            <div
              key={message.id}
              className={[
                "rounded-2xl border p-4",
                message.role === "user"
                  ? "ml-auto max-w-[88%] border-[#C9A24A]/25 bg-[#C9A24A]/10"
                  : "border-white/10 bg-white/[0.04]",
              ].join(" ")}
            >
              <div className="flex items-center justify-between gap-3">
                <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-white/35">
                  {message.role === "user" ? "You" : state.label}
                </p>
                <span className="h-2 w-2 rounded-full bg-[#C9A24A]" />
              </div>
              <p className="mt-2 text-sm leading-6 text-white/75">{message.text}</p>

              {message.moves?.length ? (
                <div className="mt-4 grid gap-2">
                  {message.moves.map((move) => (
                    <Link
                      key={move.id}
                      href={move.href}
                      className="group rounded-2xl border border-white/10 bg-black/25 p-3 transition hover:border-[#C9A24A]/40 hover:bg-[#C9A24A]/10"
                    >
                      <div className="flex items-center justify-between gap-3">
                        <span className="text-sm font-semibold text-white">{move.label}</span>
                        <span className="text-[#E9C77B] transition group-hover:translate-x-1">-&gt;</span>
                      </div>
                      <p className="mt-1 text-xs leading-5 text-white/50">{move.detail}</p>
                    </Link>
                  ))}
                </div>
              ) : null}
            </div>
          );
        })}
      </div>

      <div className="mt-4 border-t border-white/10 pt-4">
        <form
          className="flex gap-2"
          onSubmit={(event) => {
            event.preventDefault();
            addResponse(input);
          }}
        >
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Ask about clips, money, game, Blender..."
            className="min-w-0 flex-1 rounded-2xl border border-white/10 bg-black/35 px-4 py-3 text-sm text-white outline-none placeholder:text-white/30 focus:border-[#C9A24A]/60"
          />
          <button
            type="submit"
            className="rounded-2xl bg-[#C9A24A] px-4 py-3 text-sm font-bold text-black transition hover:bg-[#E9C77B]"
          >
            Send
          </button>
        </form>

        <div className="mt-3 flex flex-wrap gap-2">
          {route.suggestions.map((suggestion) => (
            <button
              key={suggestion}
              type="button"
              onClick={() => addResponse(suggestion)}
              className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1.5 text-xs text-white/60 transition hover:border-[#C9A24A]/40 hover:text-white"
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
