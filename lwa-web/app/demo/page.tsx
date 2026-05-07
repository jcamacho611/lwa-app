import type { Metadata } from "next";
import LwaPublicDemoLoopPanel from "../../components/demo/LwaPublicDemoLoopPanel";

/**
 * /demo
 *
 * Public, no-auth, no-backend route. Renders the LWA Public Demo Journey:
 * the complete first-user experience (Lee-Wuh mission → source → clip
 * result → recovery/proof → Signal Sprint moment → marketplace teaser →
 * next action). Designed to explain LWA in 60 seconds.
 *
 * This page does not call /generate, does not import the Brain Panel,
 * does not touch command-center, and performs no payments / payouts /
 * crypto operations.
 */

export const metadata: Metadata = {
  title: "LWA · Public Demo Journey",
  description:
    "The first-user LWA experience in 60 seconds: Lee-Wuh-guided creator workflow plus a creator-skill game layer. No backend, no auth, no payments.",
  robots: { index: false, follow: false },
};

export default function PublicDemoPage() {
  return <LwaPublicDemoLoopPanel />;
}
