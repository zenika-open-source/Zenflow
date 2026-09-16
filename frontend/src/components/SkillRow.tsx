import { RadioDot } from "@/components/ui/RadioDot";
import type { Skill, SkillMode } from "@/types/skills";

interface SkillRowProps {
  skill: Skill;
  mode: SkillMode;
  color: string;
  onChange: (mode: SkillMode) => void;
}

export function SkillRow({ skill, mode, color, onChange }: SkillRowProps) {
  const disabled = skill.disabled ?? false;
  const effectiveMode = disabled ? "none" : mode;

  return (
    <div
      className="grid items-center gap-2 border-b border-[#f6f0f3] py-2.5"
      style={{ gridTemplateColumns: "1fr 56px 56px 76px" }}
    >
      <div className={effectiveMode === "none" ? "opacity-40" : ""}>
        <div className="text-[13px] font-bold">
          {skill.label}
          {disabled && <span className="ml-2 text-xs font-semibold text-[#8a8290]">(coming soon)</span>}
        </div>
        {skill.sublabel && <div className="text-xs font-semibold text-[#433c47]">{skill.sublabel}</div>}
      </div>
      <RadioDot
        name={skill.id}
        color="#8a8290"
        checked={effectiveMode === "none"}
        onSelect={() => onChange("none")}
        disabled={disabled}
      />
      <RadioDot
        name={skill.id}
        color={color}
        checked={effectiveMode === "skill"}
        onSelect={() => onChange("skill")}
        disabled={disabled}
      />
      <RadioDot
        name={skill.id}
        color={color}
        checked={effectiveMode === "custom"}
        onSelect={() => onChange("custom")}
        disabled={disabled}
      />
    </div>
  );
}
