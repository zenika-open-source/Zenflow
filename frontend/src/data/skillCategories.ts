import type { SkillCategory } from "@/types/skills";

export const SKILL_CATEGORIES: SkillCategory[] = [
  {
    id: "discovery",
    title: "Product and Design",
    color: "#c81c5c",
    tint: "#fbe7ee",
    skills: [
      { id: "prd-generation", label: "PRD generation", sublabel: "product requirements document" },
      { id: "low-fi-design", label: "Low-fi design", sublabel: "greyscale wireframes" },
      { id: "dynamic-prototyping", label: "Dynamic prototyping", sublabel: "Proof Of Concept with real data, using html and Javascript" },
    ],
  },
  {
    id: "developer",
    title: "Development",
    color: "#1c8a5c",
    tint: "#e6f5ee",
    skills: [
      { id: "backend", label: "Backend", sublabel: "backend agent" },
      { id: "frontend", label: "Frontend", sublabel: "frontend agent" },
      { id: "documentation", label: "Documentation", sublabel: "documentation agent" },
      { id: "tech-migration", label: "Tech Migration", disabled: true }, // no backend agent
      { id: "code-review", label: "Code review", sublabel: "reviewer agent" },
    ],
  },
  {
    id: "qa",
    title: "QA",
    color: "#7c4fd6",
    tint: "#efe9fc",
    disabled: true, // no backend support yet
    skills: [
      { id: "playwright-scripts", label: "Script generation with Playwright" },
      { id: "playwright-exploratory", label: "Exploratory testing with Playwright" },
    ],
  },
];
