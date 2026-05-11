"""
Build "session.json" for the fMRI experiment on MATLAB/PTB.

Make sure your generated stimulus dataset has:
- at least 2 rules in each family
- at least twice many decision trials as rule number (in each family)
- at least half many stimuli in each rule as decision trials
"""

import json
import random
from pathlib import Path


def build_session(
        out_root: str = "out",
        session_path: str = "session.json",
        participant: str = "p002",
        seed: int = 2,
        number_of_mix_blocks: int = 0,
        number_of_decision_trials_per_phase: int = 6,
) -> None:
    """
    Main entry: loads stimulus pools and writes a randomized block/phase structure to session.json
    """

    rng = random.Random(seed)

    out_root_path = Path(out_root).resolve()
    session_file_path = Path(session_path).resolve()
    base_dir = session_file_path.parent.resolve()
    base_dir.mkdir(parents=True, exist_ok=True)

    # Collect pools: pools[family][rule] -> list of stimulus records (each record points to its combined image)
    pools: dict[str, dict[str, list[dict]]] = {}

    for rule_directory in out_root_path.iterdir():
        for row in map(json.loads, (rule_directory / "stimuli.jsonl").read_text(encoding="utf-8").splitlines()):
            family = row["family"]
            rule = row["rule"]
            if family not in pools:
                pools[family] = {}
            if rule not in pools[family]:
                pools[family][rule] = []
            pools[family][rule].append(
                {
                    "id": row["id"],
                    "seed": row["seed"],
                    "combined_path": rule_directory / f'{row["id"]}.combined.png',
                    "params": row["params"],
                }
            )

    families = list(pools)
    rng.shuffle(families)  # so that family blocks are shuffled

    # Hardcoded UI bits (MATLAB runner uses these strings directly)
    keys = {"same": "4$", "different": "3#"}
    tip_ready = "←   Ready          Ready   →"
    tip_memorized = "←   Memorized      Memorized   →"
    tip_decide = "←   Same          Different   →"
    inference_background, inference_hint, inference_start_hint = "yellow", "Previous rule", "First rule"
    application_background, application_hint, application_start_hint = "cyan", "Memorized rule", "Memorize this rule"

    # Swap background colors for even numbered participants
    if seed % 2 == 0:
        inference_background, application_background = application_background, inference_background

    def relative_path(image_path: Path) -> str:
        """
        Convert absolute file paths to paths relative to the session file location (portable across machines)
        """
        return str(image_path.resolve().relative_to(base_dir)).replace("\\", "/")

    def pick_pair(stimulus_pool: list[dict], used_stimulus_ids: set[str]) -> tuple[dict, dict]:
        """
        Draw two unique stimuli from a rule pool (no reuse within the current block).
        """
        unused_records = [record for record in stimulus_pool if record["id"] not in used_stimulus_ids]
        rng.shuffle(unused_records)  # Randomize which unused items are selected.

        # detect if this is color attraction via params
        has_bigger_block = any("bigger_block" in r.get("params", {}) for r in unused_records)
        if has_bigger_block:
            red_records = [r for r in unused_records if r["params"]["bigger_block"] == "red"]
            blue_records = [r for r in unused_records if r["params"]["bigger_block"] == "blue"]

            first = red_records[0]
            second = blue_records[0]

        else:
            first, second = unused_records[0], unused_records[1]

        used_stimulus_ids.add(first["id"])
        used_stimulus_ids.add(second["id"])
        return first, second

    def make_labels(number_of_decisions: int, max_run: int = 3) -> list[str]:
        """
        Generate a balanced same/different label sequence with a cap on repeated labels (prevents long streaks)
        """
        number_of_same_trials = number_of_decisions // 2
        number_of_different_trials = number_of_decisions - number_of_same_trials
        labels = ["same"] * number_of_same_trials + ["different"] * number_of_different_trials

        while True:
            rng.shuffle(labels)
            run_length = 1
            valid = True
            for i in range(1, len(labels)):
                if labels[i] == labels[i - 1]:
                    run_length += 1
                    if run_length > max_run:
                        valid = False
                        break
                else:
                    run_length = 1
            if valid:
                return labels

    def build_rule_path(allowed_rules: list[tuple[str, str]], number_of_decisions: int) -> list[tuple[str, str]]:
        """
        Build the per-phase rule sequence: respects same/different label counts and prefers unused rules for coverage
        """
        rules = allowed_rules[:]
        rng.shuffle(rules)  # randomize rule priority (affects coverage order)

        labels = make_labels(number_of_decisions, max_run=3)

        rule_path = [rng.choice(rules)]
        used_rules = {rule_path[0]}

        for label in labels:
            previous_rule = rule_path[-1]

            if label == "same":
                rule_path.append(previous_rule)
                continue

            # label == "different": prefer a rule not used yet in this phase, but never repeat previous
            candidates = [r for r in rules if r != previous_rule and r not in used_rules]
            if not candidates:
                candidates = [r for r in rules if r != previous_rule]  # all rules used: just pick any other rule

            next_rule = rng.choice(candidates)
            rule_path.append(next_rule)
            used_rules.add(next_rule)

        return rule_path

    def make_trial_entry(family: str, rule: str, first: dict, second: dict, correct: str | None) -> dict:
        """
        Create the JSON trial entry
        """
        trial = {
            "imgs": [
                relative_path(first["combined_path"]),
                relative_path(second["combined_path"])
            ],
            "family": family,
            "rule": rule,
            "stimuli": [
                {
                    "id": first["id"],
                    "seed": first.get("seed"),
                    "params": first.get("params"),
                    "difficulty": first.get("difficulty"),
                },
                {
                    "id": second["id"],
                    "seed": second.get("seed"),
                    "params": second.get("params"),
                    "difficulty": second.get("difficulty"),
                },
            ],
        }

        if correct in ("same", "different"):  # only decision trials have a correct answer, phase starts don't
            trial["correct"] = correct
        return trial

    def build_phase(
            phase_name: str,
            allowed_contexts: list[tuple[str, str]],
            used_stimulus_ids: set[str],
            background: str,
            start_hint: str,
            decision_hint: str,
            start_tip: str,
            decision_tip: str
    ) -> list[dict]:
        """
        Build a phase consisting of one phase_start trial + a list of decision trials
        """
        rule_path = build_rule_path(allowed_contexts, number_of_decision_trials_per_phase)

        # phase_start uses the first rule to establish context (no response recorded here)
        start_family, start_rule = rule_path[0]
        first, second = pick_pair(pools[start_family][start_rule], used_stimulus_ids)
        phase_start = {
            "phase": "phase_start",
            "bg": background,
            "hint": start_hint,
            "tip": start_tip,
            "trial": [make_trial_entry(start_family, start_rule, first, second, correct=None)],
        }

        # Decision trials: correct label is derived from whether rule changed vs previous trial
        decision_trials = []
        for index in range(1, len(rule_path)):
            family, rule = rule_path[index]
            previous_context = rule_path[index - 1]
            correct_label = "same" if (family, rule) == previous_context else "different"

            first, second = pick_pair(pools[family][rule], used_stimulus_ids)
            decision_trials.append(make_trial_entry(family, rule, first, second, correct=correct_label))

        decision_phase = {
            "phase": phase_name,
            "bg": background,
            "hint": decision_hint,
            "tip": decision_tip,
            "trials": decision_trials,
        }
        return [phase_start, decision_phase]

    def build_block(block_id: int, restrict_family: str | None) -> dict:
        """
        Build one block: either a single-family block or a mix block drawing from all families
        """
        used_stimulus_ids: set[str] = set()

        if restrict_family is None:
            allowed_contexts = [(family, rule) for family, family_pool in pools.items() for rule in family_pool]
            family_label = "mix"
        else:
            allowed_contexts = [(restrict_family, rule) for rule in pools.get(restrict_family, {})]
            family_label = restrict_family

        phases = []
        phases += build_phase(
            "inference",
            allowed_contexts,
            used_stimulus_ids,
            inference_background,
            inference_start_hint,
            inference_hint,
            tip_ready,
            tip_decide
        )
        phases += build_phase(
            "application",
            allowed_contexts,
            used_stimulus_ids,
            application_background,
            application_start_hint,
            application_hint,
            tip_memorized,
            tip_decide
        )

        return {"block_id": block_id, "family": family_label, "phases": phases}

    # Build the full session: family blocks first (shuffled), then a few mix blocks at the end
    blocks: list[dict] = []
    next_block_id = 1

    for family in families:
        blocks.append(build_block(next_block_id, restrict_family=family))
        next_block_id += 1

    for _ in range(number_of_mix_blocks):
        blocks.append(build_block(next_block_id, restrict_family=None))
        next_block_id += 1

    session = {"participant": participant, "keys": keys, "blocks": blocks}
    session_file_path.write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    build_session()
