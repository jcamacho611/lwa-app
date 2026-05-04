"use client";

import { useEffect, useState } from "react";
import { getAdminOpsStatus, getAdminMetrics, getRecentLwaEvents, type RecentEvent, type SystemMetric } from "../../lib/api";

export function AdminOpsPanel() {
  const [status, setStatus] = useState<{
    system_healthy: boolean;
    event_tracking_enabled: boolean;
    recent_event_count: number;
    api_status: string;
    checked_at: string;
  } | null>(null);
  const [metrics, setMetrics] = useState<SystemMetric[]>([]);
  const [events, setEvents] = useState<RecentEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState(60);

  useEffect(() => {
    loadData();
    const interval = setInterval(() => loadData(), 30000); // Refresh every 30s
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [timeRange]);

  async function loadData() {
    try {
      setLoading(true);
      setError(null);

      const [statusRes, metricsRes, eventsRes] = await Promise.all([
        getAdminOpsStatus(),
        getAdminMetrics(),
        getRecentLwaEvents(timeRange, null, 50),
      ]);

      setStatus(statusRes);
      setMetrics(metricsRes.metrics);
      setEvents(eventsRes.events);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load admin data");
    } finally {
      setLoading(false);
    }
  }

  const healthy = status?.system_healthy ?? false;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Admin / Ops</h2>
          <p className="text-sm text-white/60">Operator observability and system health</p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`inline-flex h-3 w-3 rounded-full ${healthy ? "bg-green-500" : "bg-red-500"}`} />
          <span className="text-sm text-white/80">
            {healthy ? "System Healthy" : "System Issues"}
          </span>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-4">
          <p className="text-sm text-red-300">{error}</p>
        </div>
      )}

      {/* System Status Cards */}
      {status && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard
            label="API Status"
            value={status.api_status}
            status={status.api_status === "operational" ? "good" : "warning"}
          />
          <StatCard
            label="Event Tracking"
            value={status.event_tracking_enabled ? "Enabled" : "Disabled"}
            status={status.event_tracking_enabled ? "good" : "warning"}
          />
          <StatCard
            label="Recent Events (1h)"
            value={status.recent_event_count.toString()}
            status="neutral"
          />
          <StatCard
            label="Last Check"
            value={new Date(status.checked_at).toLocaleTimeString()}
            status="neutral"
          />
        </div>
      )}

      {/* Metrics */}
      {metrics.length > 0 && (
        <div className="rounded-xl border border-white/10 bg-white/[0.02] p-4">
          <h3 className="mb-4 text-lg font-semibold text-white">System Metrics</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {metrics.map((m, i) => (
              <div key={i} className="rounded-lg bg-white/5 p-3">
                <p className="text-xs text-white/50 uppercase tracking-wider">{m.metric_name}</p>
                <p className="mt-1 text-xl font-bold text-white">
                  {m.unit === "bytes" ? formatBytes(m.value) : Math.round(m.value).toLocaleString()}
                </p>
                <p className="text-xs text-white/40">{m.unit}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Events */}
      <div className="rounded-xl border border-white/10 bg-white/[0.02] p-4">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-white">Recent Events</h3>
          <div className="flex items-center gap-2">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(Number(e.target.value))}
              className="rounded bg-white/10 px-3 py-1 text-sm text-white border border-white/20"
            >
              <option value={5}>Last 5 min</option>
              <option value={15}>Last 15 min</option>
              <option value={60}>Last hour</option>
              <option value={360}>Last 6 hours</option>
            </select>
            <button
              onClick={loadData}
              disabled={loading}
              className="rounded bg-[#C9A24A]/20 px-3 py-1 text-sm text-[#C9A24A] hover:bg-[#C9A24A]/30 disabled:opacity-50"
            >
              {loading ? "Loading..." : "Refresh"}
            </button>
          </div>
        </div>

        {events.length === 0 ? (
          <p className="text-sm text-white/40">No events in selected time range</p>
        ) : (
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {events.map((e) => (
              <div key={e.event_id} className="flex items-center gap-3 rounded-lg bg-white/5 p-3 text-sm">
                <EventBadge type={e.event_type} />
                <div className="flex-1 min-w-0">
                  <p className="text-white truncate">{e.event_type}</p>
                  <p className="text-white/40 text-xs">
                    {e.clip_id ? `Clip: ${e.clip_id.slice(0, 8)}...` : "System event"}
                  </p>
                </div>
                <p className="text-white/40 text-xs whitespace-nowrap">
                  {new Date(e.timestamp).toLocaleTimeString()}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="rounded-xl border border-white/10 bg-white/[0.02] p-4">
        <h3 className="mb-4 text-lg font-semibold text-white">Quick Actions</h3>
        <div className="flex flex-wrap gap-2">
          <ActionButton onClick={loadData} label="Refresh All Data" />
          <ActionButton onClick={() => setTimeRange(5)} label="View Last 5m" />
          <ActionButton onClick={() => setTimeRange(60)} label="View Last Hour" />
        </div>
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  status,
}: {
  label: string;
  value: string;
  status: "good" | "warning" | "neutral";
}) {
  const statusColors = {
    good: "border-green-500/30 bg-green-500/10",
    warning: "border-yellow-500/30 bg-yellow-500/10",
    neutral: "border-white/10 bg-white/[0.02]",
  };

  const textColors = {
    good: "text-green-400",
    warning: "text-yellow-400",
    neutral: "text-white",
  };

  return (
    <div className={`rounded-lg border p-3 ${statusColors[status]}`}>
      <p className="text-xs text-white/50 uppercase tracking-wider">{label}</p>
      <p className={`mt-1 text-lg font-semibold ${textColors[status]}`}>{value}</p>
    </div>
  );
}

function EventBadge({ type }: { type: string }) {
  const colors: Record<string, string> = {
    clip_view: "bg-blue-500/20 text-blue-400",
    clip_save: "bg-green-500/20 text-green-400",
    clip_share: "bg-purple-500/20 text-purple-400",
    clip_export: "bg-[#C9A24A]/20 text-[#C9A24A]",
    generate_start: "bg-cyan-500/20 text-cyan-400",
    generate_complete: "bg-emerald-500/20 text-emerald-400",
    generate_error: "bg-red-500/20 text-red-400",
    page_view: "bg-white/10 text-white/60",
  };

  const color = colors[type] || "bg-white/10 text-white/60";

  return (
    <span className={`inline-flex rounded px-2 py-0.5 text-xs font-medium ${color}`}>
      {type.split("_").pop()}
    </span>
  );
}

function ActionButton({ onClick, label }: { onClick: () => void; label: string }) {
  return (
    <button
      onClick={onClick}
      className="rounded-full border border-white/20 bg-white/[0.04] px-4 py-2 text-sm text-white/80 transition hover:border-[#C9A24A]/50 hover:text-[#C9A24A]"
    >
      {label}
    </button>
  );
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
}
