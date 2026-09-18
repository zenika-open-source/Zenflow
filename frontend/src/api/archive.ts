import { API_BASE_URL } from "@/api/config";
import type { GuidelineSelection, ToolSelection } from "@/types/zenflow";

export async function downloadArchive(
  tools: ToolSelection,
  guidelines: GuidelineSelection,
  skills: string[],
  customSkills: string[],
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/init/archive`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tools, guidelines, skills, custom_skills: customSkills }),
  });

  if (!response.ok) {
    const data = await response.json().catch(() => null);
    const detail = data && typeof data === "object" && "detail" in data ? String(data.detail) : undefined;
    throw new Error(detail ?? `Request failed (${response.status})`);
  }

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "zenflow-setup.zip";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
