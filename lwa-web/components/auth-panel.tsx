"use client";

import { FormEvent, useState } from "react";
import { UserProfile } from "../lib/types";

type AuthMode = "login" | "signup";

type AuthPanelProps = {
  isOpen: boolean;
  mode: AuthMode;
  onClose: () => void;
  onSwitchMode: (mode: AuthMode) => void;
  onAuthenticated: (payload: { token: string; user: UserProfile }) => void;
};

export function AuthPanel({ isOpen, mode, onClose, onSwitchMode, onAuthenticated }: AuthPanelProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) {
    return null;
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch(`/api/auth/${mode}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });
      const data = (await response.json()) as {
        detail?: string;
        access_token?: string;
        user?: UserProfile;
      };
      if (!response.ok || !data.access_token || !data.user) {
        throw new Error(data.detail || "Authentication failed.");
      }
      onAuthenticated({
        token: data.access_token,
        user: data.user,
      });
      setEmail("");
      setPassword("");
      onClose();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Authentication failed.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4 backdrop-blur-sm">
      <div className="glass-panel w-full max-w-md rounded-[32px] p-6 sm:p-7">
        <div className="mb-6 flex items-start justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-muted">Account</p>
            <h3 className="mt-2 text-2xl font-semibold text-ink">
              {mode === "login" ? "Sign in to your workspace" : "Create your workspace"}
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-sm text-ink/70 transition hover:bg-white/[0.08]"
          >
            Close
          </button>
        </div>

        <form onSubmit={onSubmit} className="space-y-4">
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-ink/80">Email</span>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-ink outline-none transition focus:border-accent/40"
              placeholder="you@example.com"
              required
            />
          </label>
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-ink/80">Password</span>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-ink outline-none transition focus:border-accent/40"
              placeholder="At least 8 characters"
              minLength={8}
              required
            />
          </label>

          {error ? (
            <div className="rounded-2xl border border-red-400/20 bg-red-400/8 px-4 py-3 text-sm text-red-100">
              {error}
            </div>
          ) : null}

          <button
            type="submit"
            disabled={isSubmitting}
            className="inline-flex w-full items-center justify-center rounded-full bg-gradient-to-r from-accent to-accentSoft px-6 py-3.5 text-sm font-semibold text-white shadow-glow transition disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSubmitting ? "Working..." : mode === "login" ? "Sign In" : "Create Account"}
          </button>
        </form>

        <div className="mt-5 text-sm text-ink/64">
          {mode === "login" ? "Need an account?" : "Already have an account?"}{" "}
          <button
            type="button"
            onClick={() => onSwitchMode(mode === "login" ? "signup" : "login")}
            className="font-medium text-accent"
          >
            {mode === "login" ? "Create one" : "Sign in"}
          </button>
        </div>
      </div>
    </div>
  );
}
