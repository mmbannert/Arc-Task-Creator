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

if __name__ == "__main__":

    out_root: str = "out"
    session_path: str = "session.json"
    participant: str = "p01"  # max 3 chars

    number_of_sessions: int = 10  # alternating: odd = family, even = mix, so choose even numbers for balance
    number_of_blocks_per_session: int = 5  # must be >= 5 to guarantee all families are covered in family sessions.
    number_of_decision_trials_per_phase: int = 4

    # ------------------------------------------------------------------ #
    # Setup                                                              #
    # ------------------------------------------------------------------ #

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

    # (family, rule) -> stimulus type, e.g. ("arithmetic", "dot_majority_recolor") -> "dots"
    # Assumes "stimulus" is constant across all instances of a given rule.
    rule_stimulus_type: dict[tuple[str, str], str] = {
        (family, rule): records[0]["params"]["stimulus"]
        for family, family_pool in pools.items()
        for rule, records in family_pool.items()
    }

    inference_background = "yellow"
    application_background = "cyan"

    # Counterbalance phase colors based on participant number parity
    if int(participant.removeprefix("p")) % 2 == 0:
        inference_background, application_background = application_background, inference_background


    # ------------------------------------------------------------------ #
    # Nested functions                                                   #
    # ------------------------------------------------------------------ #

    def build_block(block_id: int, restrict_family: str | None) -> dict:
        """
        Build one block: either a single-family block or a mix block drawing from all families
        """
        used_stimulus_ids: set[str] = set()

        if restrict_family is None:
            rules = [(family, rule) for family, family_pool in pools.items() for rule in family_pool]
            family_label = "mix"
        else:
            rules = [(restrict_family, rule) for rule in pools.get(restrict_family, {})]
            family_label = restrict_family

        phases = (
                build_phase("inference", rules, used_stimulus_ids, inference_background) +
                build_phase("application", rules, used_stimulus_ids, application_background)
        )

        return {"block_id": block_id, "family": family_label, "phases": phases}


    def build_phase(
            phase: str,
            rules: list[tuple[str, str]],
            used_stimulus_ids: set[str],
            background: str,
    ) -> list[dict]:
        """
        Build a phase consisting of one phase_start trial + a list of decision trials
        Inference (swap): each trial is compared to the previous rule.
        Application (stable): each trial is compared to the memorized rule (rule_path[0]).
        """
        rule_path = build_rule_path(rules, number_of_decision_trials_per_phase, phase)

        # Phase_start uses the first rule to establish context (no response recorded here)
        start_family, start_rule = rule_path[0]
        first, second = pick_pair(pools[start_family][start_rule], used_stimulus_ids)
        phase_start = {
            "phase": f"{phase}_start",
            "bg": background,
            "trial": [make_trial_entry(start_family, start_rule, first, second, correct=None)],
        }

        # Decision trials: correct label is derived from whether rule changed vs previous trial
        decision_trials = []
        for index in range(1, len(rule_path)):
            family, rule = rule_path[index]
            compare_to = rule_path[0] if phase == "application" else rule_path[index - 1]
            correct_label = "same" if (family, rule) == compare_to else "different"

            first, second = pick_pair(pools[family][rule], used_stimulus_ids)
            decision_trials.append(make_trial_entry(family, rule, first, second, correct=correct_label))

        return [phase_start, {"phase": phase, "bg": background, "trials": decision_trials}]


    def build_rule_path(
            rules: list[tuple[str, str]],
            number_of_decisions: int,
            phase: str,  # "inference" or "application"
    ) -> list[tuple[str, str]]:
        """
        Build the per-phase rule sequence: respects same/different label counts and prefers unused rules for coverage
        The first "different" in a phase keeps the same stimulus type (e.g. dots, cross_plus, occluding blocks)
        as the rule it differs from; subsequent "different"s are free to switch stimulus type.
        """
        rng.shuffle(rules)  # randomize rule priority (affects coverage order)

        labels = make_labels(number_of_decisions, max_run=3)

        first_rule = rng.choice(rules)
        rule_path = [first_rule]
        used_rules = {first_rule}

        # For Stimulus Alignment
        stimulus_alignment = True  # the first "different" in the phase must match stimulus type

        for label in labels:
            previous_rule = rule_path[-1]
            compare_target = first_rule if phase == "application" else previous_rule

            if label == "same":
                rule_path.append(compare_target)

            elif label == "different":

                # Three criteria
                # 1. different rule from compare target
                # 2. stimulus alignment with compare target
                # 3. prefer unused rules for coverage

                if stimulus_alignment:
                    candidates = [
                        r for r in rules
                        if rule_stimulus_type[r] == rule_stimulus_type[
                            compare_target] and r != compare_target and r not in used_rules
                    ]
                    if not candidates:
                        # no unused rule with same stimulus type -> relax stimulus alignment, prefer other unused rules
                        candidates = [r for r in rules if r != compare_target and r not in used_rules]

                    if not candidates:
                        # all rules used, then enforce stimulus type
                        candidates = [r for r in rules if
                                      r != compare_target and rule_stimulus_type[r] == rule_stimulus_type[
                                          compare_target]]

                    stimulus_alignment = False

                else:
                    candidates = [r for r in rules if r != compare_target and r not in used_rules]
                    if not candidates:
                        candidates = [r for r in rules if r != compare_target]

                    stimulus_alignment = True

                next_rule = rng.choice(candidates)
                rule_path.append(next_rule)
                used_rules.add(next_rule)

        return rule_path


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


    def pick_pair(stimulus_pool: list[dict], used_stimulus_ids: set[str]) -> tuple[dict, dict]:
        """
        Draw two unique stimuli from a rule pool (no reuse within the current block).
        """
        unused_records = [record for record in stimulus_pool if record["id"] not in used_stimulus_ids]
        rng.shuffle(unused_records)  # Randomize which unused items are selected.

        # detect if this is color attraction via params
        has_bigger_block = any("bigger_block" in r.get("params", {}) for r in unused_records)
        if has_bigger_block:
            first = next(r for r in unused_records if r["params"]["bigger_block"] == "red")
            second = next(r for r in unused_records if r["params"]["bigger_block"] == "blue")
        else:
            first, second = unused_records[0], unused_records[1]

        used_stimulus_ids.add(first["id"])
        used_stimulus_ids.add(second["id"])
        return first, second


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
                },
                {
                    "id": second["id"],
                    "seed": second.get("seed"),
                    "params": second.get("params"),
                },
            ],
        }

        if correct in ("same", "different"):  # only decision trials have a correct answer, phase starts don't
            trial["correct"] = correct
        return trial


    def relative_path(image_path: Path) -> str:
        """
        Convert absolute file paths to paths relative to the session file location (portable across machines)
        """
        return str(image_path.resolve().relative_to(base_dir)).replace("\\", "/")


    def family_block_sequence(n: int) -> list[str]:
        """
        Balanced cycling: every 5 blocks covers each family exactly once, then reshuffles.
        Guarantees equal family representation in any multiple-of-5 interval.
        """
        sequence = []
        while len(sequence) < n:
            batch = families[:]
            rng.shuffle(batch)
            sequence.extend(batch)
        return sequence[:n]


    # ------------------------------------------------------------------ #
    # Execution                                                          #
    # ------------------------------------------------------------------ #

    for session_index in range(1, number_of_sessions + 1):
        is_family_session = session_index % 2 == 1  # odd = family, even = mix

        session_filename = f"session_{session_index:02d}.json"
        session_file_path = base_dir / session_filename
        base_dir = session_file_path.parent.resolve()

        seed = int(participant.removeprefix("p")) * 100 + session_index
        rng = random.Random(seed)

        blocks = []
        next_block_id = 1

        if is_family_session:
            rng.shuffle(families)  # so that family blocks are shuffled
            for family in family_block_sequence(number_of_blocks_per_session):
                blocks.append(build_block(next_block_id, restrict_family=family))
                next_block_id += 1
        else:  # mixup_session
            for _ in range(number_of_blocks_per_session):
                blocks.append(build_block(next_block_id, restrict_family=None))
                next_block_id += 1

        number_of_trials_per_block = 2 + 2 * number_of_decision_trials_per_phase
        number_of_trials_total = number_of_blocks_per_session * number_of_trials_per_block

        session = {
            "participant": participant,
            "seed": seed,
            "session": session_index,
            "type": "family" if is_family_session else "mix",
            "number_of_decision_trials_per_phase": number_of_decision_trials_per_phase,
            "number_of_trials_per_block": number_of_trials_per_block,
            "number_of_blocks": number_of_blocks_per_session,
            "number_of_trials_total": number_of_trials_total,
            "blocks": blocks,
        }

        session_file_path.write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")
