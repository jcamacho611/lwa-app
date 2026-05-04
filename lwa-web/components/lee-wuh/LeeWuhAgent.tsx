"use client";

import { useState, useEffect, useRef } from "react";
import { LeeWuhCharacter, LeeWuhAvatar } from "./LeeWuhCharacter";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  actions?: Array<{
    label: string;
    action: string;
    params?: Record<string, string>;
  }>;
}

interface ToolCall {
  tool: string;
  params: Record<string, unknown>;
}

const TOOL_DEFINITIONS = {
  generate_clips: {
    description: "Generate clips from a video URL",
    parameters: {
      video_url: "string - The video URL to process",
      platform: "string - Target platform (tiktok, youtube, instagram)",
    },
  },
  find_opportunities: {
    description: "Find paid clip jobs and opportunities",
    parameters: {
      skill_level: "string - beginner, intermediate, expert",
      platform: "string - Preferred platform",
    },
  },
  navigate_to: {
    description: "Navigate to a specific page",
    parameters: {
      page: "string - The page to navigate to",
    },
  },
  get_clip_status: {
    description: "Check the status of clip generation",
    parameters: {
      job_id: "string - The job ID to check",
    },
  },
  save_to_proof_vault: {
    description: "Save a clip to the proof vault",
    parameters: {
      clip_id: "string - The clip ID to save",
    },
  },
};

export function LeeWuhAgent() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Hey! I'm Lee-Wuh. I can help you make clips, find paid work, or navigate LWA. What are we doing today?",
      timestamp: new Date(),
      actions: [
        { label: "🎬 Make Clips", action: "navigate_to", params: { page: "/generate" } },
        { label: "💰 Find Paid Work", action: "navigate_to", params: { page: "/opportunities" } },
        { label: "📊 View Command Center", action: "navigate_to", params: { page: "/command-center" } },
      ],
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [mood, setMood] = useState<"idle" | "analyzing" | "confident" | "helping" | "playful" | "focused" | "victory" | "error" | "rendering" | "complete">("idle");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Auto-mood cycling when idle
  useEffect(() => {
    if (!isOpen) return;
    
    const interval = setInterval(() => {
      if (!isLoading) {
        const moods: Array<"idle" | "playful" | "confident"> = ["idle", "playful", "confident"];
        const randomMood = moods[Math.floor(Math.random() * moods.length)];
        setMood(randomMood);
      }
    }, 8000);

    return () => clearInterval(interval);
  }, [isOpen, isLoading]);

  // Handle tool execution
  async function executeTool(toolCall: ToolCall): Promise<string> {
    switch (toolCall.tool) {
      case "generate_clips":
        const { video_url, platform } = toolCall.params;
        // Redirect to generate page with URL
        window.location.href = `/generate?url=${encodeURIComponent(video_url as string)}&platform=${platform}`;
        return "Taking you to clip generation...";

      case "find_opportunities":
        window.location.href = "/opportunities";
        return "Opening the opportunities board...";

      case "navigate_to":
        const { page } = toolCall.params;
        window.location.href = page as string;
        return `Navigating to ${page}...`;

      case "get_clip_status":
        const { job_id } = toolCall.params;
        // Call backend to check status
        const statusRes = await fetch(`/api/jobs/${job_id}/status`);
        const status = await statusRes.json();
        return `Job ${job_id} is ${status.status}. ${status.progress}% complete.`;

      case "save_to_proof_vault":
        const { clip_id } = toolCall.params;
        // Call backend to save
        await fetch("/api/proof-vault/assets", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ clip_id }),
        });
        return "Saved to your Proof Vault! I'll use this to improve future recommendations.";

      default:
        return "I don't know how to do that yet, but I'm learning!";
    }
  }

  // Send message to Lee-Wuh AI
  async function sendMessage() {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);
    setMood("analyzing");

    try {
      // Call AI backend
      const response = await fetch("/api/ai/lee-wuh", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMessage.content,
          history: messages.map((m) => ({ role: m.role, content: m.content })),
          tools: TOOL_DEFINITIONS,
          userContext: {
            currentPage: window.location.pathname,
            hasSubscription: false, // Get from auth context
            clipCount: 0, // Get from user stats
          },
        }),
      });

      const data = await response.json();

      // Check if AI wants to use a tool
      if (data.tool_call) {
        const toolResult = await executeTool(data.tool_call);
        
        // Add AI message with tool result
        const aiMessage: ChatMessage = {
          id: `ai-${Date.now()}`,
          role: "assistant",
          content: `${data.message}\n\n${toolResult}`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, aiMessage]);
      } else {
        // Regular response
        const aiMessage: ChatMessage = {
          id: `ai-${Date.now()}`,
          role: "assistant",
          content: data.message,
          timestamp: new Date(),
          actions: data.suggested_actions,
        };
        setMessages((prev) => [...prev, aiMessage]);
      }

      setMood("confident");
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        role: "assistant",
        content: "Hmm, something went wrong. Let me try again...",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
      setMood("idle");
    } finally {
      setIsLoading(false);
    }
  }

  // Quick action button handler
  function handleAction(action: string, params?: Record<string, string>) {
    executeTool({ tool: action, params: params || {} });
  }

  return (
    <>
      {/* Floating Toggle Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="group fixed bottom-6 right-6 z-50"
          aria-label="Open Lee-Wuh assistant"
        >
          <div className="flex items-center gap-3 rounded-full border border-[#C9A24A]/30 bg-[#09090d]/95 px-4 py-3 shadow-2xl shadow-black/40 backdrop-blur-xl transition hover:scale-[1.03] hover:border-[#C9A24A]/60">
            <div className="relative">
              <LeeWuhAvatar mood={mood} size="md" />
              <span className="absolute -right-1 -top-1 flex h-3 w-3">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#C9A24A] opacity-75" />
                <span className="relative inline-flex h-3 w-3 rounded-full bg-[#C9A24A]" />
              </span>
            </div>
            <div className="hidden text-left sm:block">
              <p className="text-sm font-black text-white">Ask Lee-Wuh</p>
              <p className="text-xs text-white/45">Mascot + clip guide</p>
            </div>
          </div>
        </button>
      )}

      {/* Chat Panel */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 z-50 w-96">
          <div className="rounded-3xl border border-[#C9A24A]/30 bg-[#0A0A0B] shadow-2xl overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between border-b border-white/10 bg-[#C9A24A]/10 p-4">
              <div className="flex items-center gap-3">
                <LeeWuhAvatar mood={isLoading ? "analyzing" : (mood as any)} size="md" />
                <div>
                  <h3 className="font-bold text-white">Lee-Wuh</h3>
                  <p className="text-xs text-white/50">
                    {isLoading ? "Thinking..." : mood}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="rounded-full p-2 text-white/50 hover:bg-white/10"
              >
                ✕
              </button>
            </div>

            {/* Messages */}
            <div className="h-80 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${
                    message.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                      message.role === "user"
                        ? "bg-[#C9A24A] text-black"
                        : "bg-white/[0.04] text-white border border-white/10"
                    }`}
                  >
                    <p className="text-sm">{message.content}</p>
                    
                    {/* Action Buttons */}
                    {message.actions && (
                      <div className="mt-3 flex flex-wrap gap-2">
                        {message.actions.map((action, idx) => (
                          <button
                            key={idx}
                            onClick={() => handleAction(action.action, action.params)}
                            className="rounded-full bg-[#C9A24A]/20 px-3 py-1 text-xs text-[#E9C77B] hover:bg-[#C9A24A]/30 transition"
                          >
                            {action.label}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="flex justify-start">
                  <div className="rounded-2xl bg-white/[0.04] border border-white/10 px-4 py-3">
                    <div className="flex items-center gap-2">
                      <LeeWuhAvatar mood="analyzing" size="xs" />
                      <span className="text-sm text-white/60">Lee-Wuh is thinking...</span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="border-t border-white/10 p-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                  placeholder="Ask Lee-Wuh anything..."
                  className="flex-1 rounded-xl border border-white/10 bg-black/40 px-4 py-2 text-sm text-white outline-none placeholder:text-white/30 focus:border-[#C9A24A]"
                />
                <button
                  onClick={sendMessage}
                  disabled={isLoading || !input.trim()}
                  className="rounded-xl bg-[#C9A24A] px-4 py-2 text-sm font-bold text-black transition hover:bg-[#E9C77B] disabled:opacity-50"
                >
                  {isLoading ? "..." : "→"}
                </button>
              </div>
              
              {/* Quick Actions */}
              <div className="mt-3 flex flex-wrap gap-2">
                <button
                  onClick={() => {
                    setInput("Generate clips from this video");
                    sendMessage();
                  }}
                  className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs text-white/60 hover:bg-white/[0.08]"
                >
                  🎬 Make clips
                </button>
                <button
                  onClick={() => {
                    setInput("Find me paid work");
                    sendMessage();
                  }}
                  className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs text-white/60 hover:bg-white/[0.08]"
                >
                  💰 Find work
                </button>
                <button
                  onClick={() => {
                    setInput("How do I use Proof Vault?");
                    sendMessage();
                  }}
                  className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs text-white/60 hover:bg-white/[0.08]"
                >
                  ❓ Help
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
