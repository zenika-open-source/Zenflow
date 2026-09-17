// Skill ids here map to backend agent ids (see resolve_agent_ids in
// zenflow.core.deployment) and are sent to POST /init/archive to select which
// agents get deployed.

export type SkillMode = "none" | "skill" | "custom";

export interface Skill {
  id: string;
  label: string;
  /** True when this skill has no corresponding backend agent yet — locked to "None". */
  disabled?: boolean;
}

export interface SkillCategory {
  id: string;
  title: string;
  color: string;
  tint: string;
  skills: Skill[];
  /** True when this category isn't backed by anything deployable yet — grayed out and non-interactive. */
  disabled?: boolean;
}
