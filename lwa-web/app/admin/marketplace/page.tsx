import { AdminMarketplace } from "../../../components/worlds/AdminMarketplace";
import { LwaShell } from "../../../components/worlds/LwaShell";
import { listFraudFlags, listModerationQueue, listRightsClaims } from "../../../lib/worlds/api";
import { mockAdminQueue } from "../../../lib/worlds/mock-data";
import type { AdminQueueItem } from "../../../lib/worlds/types";

async function getAdminQueue(): Promise<AdminQueueItem[]> {
  try {
    const [moderation, fraud, rights] = await Promise.all([
      listModerationQueue(),
      listFraudFlags(),
      listRightsClaims(),
    ]);

    const items: AdminQueueItem[] = [
      ...moderation.map((m) => ({
        id: m.id,
        type: "submission_review" as const,
        title: `Moderation: ${m.targetType} ${m.targetId.slice(0, 8)}`,
        status: m.status === "pending" ? ("open" as const) : ("in_review" as const),
        priority: "medium" as const,
        createdAt: m.createdAt,
        owner: m.reviewer,
      })),
      ...fraud.map((f) => ({
        id: f.id,
        type: "fraud_flag" as const,
        title: `Fraud: ${f.flagType} on ${f.targetType}`,
        status: f.status === "open" ? ("open" as const) : ("in_review" as const),
        priority: (f.severity === "critical" || f.severity === "high" ? f.severity : "medium") as AdminQueueItem["priority"],
        createdAt: f.createdAt,
        owner: f.reviewer,
      })),
      ...rights.map((r) => ({
        id: r.id,
        type: "rights_claim" as const,
        title: `Rights claim: ${r.claimantName} — ${r.targetType}`,
        status: r.status === "open" ? ("open" as const) : ("in_review" as const),
        priority: "high" as const,
        createdAt: r.createdAt,
      })),
    ];

    return items.length > 0 ? items : mockAdminQueue;
  } catch {
    return mockAdminQueue;
  }
}

export default async function AdminMarketplacePage() {
  const queue = await getAdminQueue();
  return (
    <LwaShell title="Admin Marketplace">
      <AdminMarketplace queue={queue} />
    </LwaShell>
  );
}
