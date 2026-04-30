from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HookFormula:
    code: str
    name: str
    structure: str
    example: str


HOOK_FORMULAS: tuple[HookFormula, ...] = (
    HookFormula("contrarian_claim", "Contrarian Claim", "Everyone says X, but the opposite is true because Y.", "Stop doing X. It is costing you attention."),
    HookFormula("persona_callout", "Persona Callout", "If you are PERSONA, this is the mistake to avoid.", "If you run a creator page, fix this first."),
    HookFormula("specific_number", "Specific Number", "Use a true number to create concrete curiosity.", "Three edits changed this entire clip."),
    HookFormula("pattern_interrupt", "Pattern Interrupt", "Open mid-action with no greeting.", "Cut directly to the strongest visual."),
    HookFormula("numbered_list", "Numbered List", "N mistakes, rules, steps, or signals.", "Three mistakes that ruin short-form clips."),
    HookFormula("time_compression", "Time Compression", "Here is what took a long time, compressed.", "What took months to learn, in sixty seconds."),
    HookFormula("reverse_hook", "Reverse Hook", "Tell the wrong viewer not to watch.", "Do not watch this if you are happy with average clips."),
    HookFormula("named_comparison", "Named Comparison", "Compare against a known tool or method.", "Most tools stop at clipping. This adds direction."),
    HookFormula("specific_story", "Specific Story", "A named or concrete situation tried X.", "A creator used one source and made five angles."),
    HookFormula("before_after", "Before / After", "Show the gap in the first moment.", "Before: one long video. After: five post-ready clips."),
    HookFormula("unfinished_number", "Unfinished Number", "Start a number story and force curiosity.", "Zero clips to a full campaign in one flow."),
    HookFormula("unexpected_admission", "Unexpected Admission", "Admit a surprising truth.", "I was wrong about what makes clips work."),
    HookFormula("framework_name", "Framework Name", "Name the method.", "The 90/10 Hook Method starts here."),
    HookFormula("implied_secret", "Implied Secret", "Point at a hidden operator tactic.", "Agencies hide this workflow from clients."),
    HookFormula("share_hook", "Share Hook", "Make the hook naturally shareable.", "Send this to someone still posting without hooks."),
    HookFormula("objection_first", "Objection First", "Say what the viewer is thinking.", "You think your niche is too boring. Watch this."),
    HookFormula("paradox", "Paradox", "State a surprising contradiction.", "Posting less can make each clip hit harder."),
    HookFormula("dialogue_cold_open", "Dialogue Cold Open", "Start inside a disagreement.", "One voice says cut it. The other says keep watching."),
    HookFormula("counter_trend", "Counter Trend", "Reject what everyone else is doing.", "Everyone chases templates. Operators build systems."),
    HookFormula("dataset_pattern", "Dataset Pattern", "Claim a pattern from reviewed examples.", "After reviewing the clips, one pattern kept winning."),
)


def list_hook_formulas() -> list[dict[str, str]]:
    return [formula.__dict__.copy() for formula in HOOK_FORMULAS]


def get_hook_formula(code: str) -> HookFormula | None:
    normalized = code.strip().lower().replace("-", "_")
    for formula in HOOK_FORMULAS:
        if formula.code == normalized:
            return formula
    return None
