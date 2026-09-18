import type { SkillCategory } from "@/types/skills";

export const SKILL_CATEGORIES: SkillCategory[] = [
  {
    id: "discovery",
    title: "Product and Design",
    color: "#c81c5c",
    tint: "#fbe7ee",
    skills: [
      { id: "product-requirements", label: "Product Requirements", sublabel: "generate/update PRD documents" }, // -> product-requirements agent
      { id: "static-prototyping", label: "Static prototyping", sublabel: "greyscale wireframes, low-fidelity" }, // -> static-prototyping agent
      { id: "dynamic-prototyping", label: "Dynamic prototyping", sublabel: "interactive, high-fidelity, html and Javascript only" }, // -> dynamic-prototyping agent
    ],
  },
  {
    id: "developer",
    title: "Development",
    color: "#1c8a5c",
    tint: "#e6f5ee",
    skills: [
      { id: "backend", label: "Backend" }, // -> backend agent
      { id: "frontend", label: "Frontend" }, // -> frontend agent
      { id: "documentation", label: "Documentation" }, // -> documentation agent
      { id: "tech-migration", label: "Tech Migration", disabled: true }, // no backend agent
      { id: "code-review", label: "Code review" }, // -> reviewer agent
      { id: "orchestrator", label: "Full-stack orchestration" }, // -> orchestrator agent
      { id: "retrodoc-architecture", label: "Retrodoc - Architecture", sublabel: "Agent relies on goretex.ai, goretex should be installed before using this agent" }, // -> retrodoc-architecture agent
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
