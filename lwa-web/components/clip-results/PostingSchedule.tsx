"use client";

import { Calendar, Clock, CheckCircle2 } from "lucide-react";

export interface PostingScheduleProps {
  clips: Array<{
    clip_id: string;
    hook: string;
    score: number;
    rank: number;
  }>;
}

export function PostingSchedule({ clips }: PostingScheduleProps) {
  // Take top 3 clips for schedule
  const topClips = clips.slice(0, 3);
  
  const schedule = [
    { day: "Today", time: "6:00 PM", label: "Prime time", reason: "Highest engagement window" },
    { day: "Tomorrow", time: "12:00 PM", label: "Lunch scroll", reason: "Midday content break" },
    { day: "Day 3", time: "9:00 AM", label: "Morning boost", reason: "Fresh start energy" },
  ];
  
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-6">
      <div className="mb-4 flex items-center gap-2">
        <Calendar className="h-5 w-5 text-[#C9A24A]" />
        <h3 className="font-semibold text-white">Your Posting Schedule</h3>
      </div>
      
      <p className="mb-4 text-sm text-white/60">
        Space out your best clips for maximum reach. Here&apos;s your optimal schedule:
      </p>
      
      <div className="space-y-3">
        {topClips.map((clip, index) => {
          const slot = schedule[index];
          if (!slot) return null;
          
          return (
            <div
              key={clip.clip_id}
              className={`flex items-center gap-4 rounded-xl border p-4 ${
                index === 0
                  ? "border-[#C9A24A]/50 bg-[#C9A24A]/10"
                  : "border-white/10 bg-white/5"
              }`}
            >
              <div className="flex h-12 w-12 flex-col items-center justify-center rounded-lg bg-white/10">
                <span className="text-xs font-bold text-[#C9A24A]">{slot.day}</span>
                <Clock className="h-3 w-3 text-white/50" />
              </div>
              
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-white">
                    {slot.time}
                  </span>
                  <span className="rounded-full bg-white/10 px-2 py-0.5 text-xs text-white/60">
                    {slot.label}
                  </span>
                  {index === 0 && (
                    <span className="rounded-full bg-[#C9A24A] px-2 py-0.5 text-xs font-semibold text-black">
                      POST FIRST
                    </span>
                  )}
                </div>
                <p className="text-sm text-white/60">
                  &quot;{clip.hook.slice(0, 50)}...&quot;
                </p>
                <p className="text-xs text-white/40">
                  {slot.reason}
                </p>
              </div>
              
              {index === 0 && (
                <CheckCircle2 className="h-5 w-5 text-[#C9A24A]" />
              )}
            </div>
          );
        })}
      </div>
      
      <div className="mt-4 rounded-lg bg-white/5 p-3 text-center">
        <p className="text-sm text-white/60">
          <span className="text-[#C9A24A]">Pro tip:</span> Posting 3 clips over 3 days beats posting all at once
        </p>
      </div>
    </div>
  );
}
