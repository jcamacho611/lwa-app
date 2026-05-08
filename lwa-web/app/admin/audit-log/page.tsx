import { AdminAuditLog } from "../../../components/worlds/AdminAuditLog";
import { LwaShell } from "../../../components/worlds/LwaShell";
import { listAuditLog } from "../../../lib/worlds/api";

async function getAuditLog() {
  try {
    return await listAuditLog();
  } catch {
    return [];
  }
}

export default async function AdminAuditLogPage() {
  const entries = await getAuditLog();

  return (
    <LwaShell title="Admin · Audit Log">
      <AdminAuditLog entries={entries} />
    </LwaShell>
  );
}
