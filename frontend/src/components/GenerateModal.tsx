import { useState } from "react";
import { downloadArchive } from "@/api/archive";
import { Button } from "@/components/ui/Button";
import type { SkillMode } from "@/types/skills";
import type { GuidelineSelection, ToolSelection } from "@/types/zenflow";

type Phase = "confirm" | "loading" | "success" | "error";

interface GenerateModalProps {
  open: boolean;
  tools: ToolSelection;
  guidelines: GuidelineSelection;
  skillSelections: Record<string, SkillMode>;
  onClose: () => void;
}

export function GenerateModal({ open, tools, guidelines, skillSelections, onClose }: GenerateModalProps) {
  const [phase, setPhase] = useState<Phase>("confirm");
  const [errorMessage, setErrorMessage] = useState("");

  if (!open) return null;

  function handleClose() {
    setPhase("confirm");
    setErrorMessage("");
    onClose();
  }

  async function handleConfirm() {
    setPhase("loading");
    try {
      const skills = Object.entries(skillSelections)
        .filter(([, mode]) => mode !== "none")
        .map(([skillId]) => skillId);
      await downloadArchive(tools, guidelines, skills);
      setPhase("success");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "Something went wrong");
      setPhase("error");
    }
  }

  return (
    <div
      className="fixed inset-0 z-20 grid place-items-center bg-[rgba(40,15,30,0.35)] p-6"
      onClick={handleClose}
    >
      <div
        className="w-full max-w-[480px] rounded-[24px] bg-white p-7 shadow-[0_30px_60px_-20px_rgba(60,20,50,0.4)]"
        onClick={(e) => e.stopPropagation()}
      >
        {phase === "success" ? (
          <>
            <div className="mb-2 text-xl font-extrabold text-[#161217]">Downloaded!</div>
            <p className="mb-5 text-sm text-[#5c5560]">zenflow-setup.zip should now be in your downloads.</p>
            <div className="flex justify-end">
              <Button variant="primary" onClick={handleClose}>
                Close
              </Button>
            </div>
          </>
        ) : (
          <>
            <div className="mb-2 text-xl font-extrabold text-[#161217]">Generate agent files?</div>
            <p className="mb-4 text-sm text-[#5c5560]">
              This downloads a zip with the files your selected assistant reads on day one.
            </p>
            {phase === "error" && (
              <p className="mb-4 text-sm font-semibold text-[#c81c5c]">{errorMessage}</p>
            )}
            <div className="flex justify-end gap-3">
              <Button variant="secondary" onClick={handleClose}>
                Cancel
              </Button>
              <Button variant="primary" onClick={handleConfirm} disabled={phase === "loading"}>
                {phase === "loading" ? "Generating…" : "Yes"}
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
