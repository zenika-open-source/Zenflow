// Skill-category data is a frontend-only concept for now — the backend deploys
// a fixed set of agents per tool and has no per-skill selection endpoint yet.

export type SkillMode = "none" | "skill" | "custom";

export interface Skill {
  id: string;
  label: string;
  /** Optional second line of text, shown in the same muted style as the "(coming soon)" tag. */
  sublabel?: string;
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
