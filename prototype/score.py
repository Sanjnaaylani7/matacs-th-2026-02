"""Deterministic scoring step of the proposal triage design.

Input : criteria.json (admin-defined) + extracted facts (output of the AI extraction step)
Output: ranked / flagged / ineligible list. No AI is used here, so the same input
        always gives the same output.

Usage: python score.py [criteria.json] [extracted_sample.json] [--out result.json]
"""
import hashlib
import json
import sys
from pathlib import Path


def clamp(x):
    return max(0.0, min(1.0, x))


def s_count_cap(f, c, p):
    return 100 * clamp((f.get("relevant_installs") or 0) / c["cap"])


def s_price(f, c, p):
    v, ceil = f.get("price_cad"), p["budget_ceiling"]
    if v is None or v > ceil:
        return 0.0
    full = ceil * c["full_marks_fraction"]
    return 100 * clamp((ceil - v) / (ceil - full))


def s_weeks(f, c, p):
    v, mx = f.get("weeks"), p["max_weeks"]
    if v is None or v > mx:
        return 0.0
    return 100 * clamp((mx - v) / (mx - c["best_weeks"]))


def s_warranty(f, c, p):
    panel = clamp((f.get("panel_years") or 0) / c["panel_cap_years"])
    work = clamp((f.get("workmanship_years") or 0) / c["workmanship_cap_years"])
    return 100 * (0.5 * panel + 0.5 * work)


def s_checklist(f, c, p):
    return 100 * sum(bool(f.get(i)) for i in c["items"]) / len(c["items"])


METHODS = {
    "count_cap": s_count_cap,
    "price_linear": s_price,
    "weeks_linear": s_weeks,
    "warranty": s_warranty,
    "checklist": s_checklist,
}


def evaluate(crit, facts):
    proj = crit["project"]
    total_weight = sum(c["weight"] for c in crit["weighted"])
    if total_weight != 100:
        raise ValueError(f"Weights must add up to 100, got {total_weight}")

    results = []
    for letter, f in sorted(facts.items()):
        if letter.startswith("_"):
            continue
        breakdown = {}
        for c in crit["weighted"]:
            raw = METHODS[c["method"]](f, c, proj)
            breakdown[c["id"]] = {"score_0_100": round(raw, 1), "weight": c["weight"],
                                  "points": round(raw * c["weight"] / 100, 2)}
        score = round(sum(b["points"] for b in breakdown.values()), 1)

        fails = []
        if not f.get("licence_held"):
            fails.append("licence not held by bidder")
        if not (f.get("wsib") and f.get("liability_5m")):
            fails.append("WSIB or $5M insurance not confirmed")

        flags = []
        if f.get("injection_detected"):
            flags.append("text aimed at automated reviewers")
        if f.get("weeks") is None:
            flags.append("completion time not stated")
        elif f["weeks"] > proj["max_weeks"]:
            flags.append("over the time limit")
        if f.get("price_cad") is None or f["price_cad"] > proj["budget_ceiling"]:
            flags.append("price missing or over ceiling")
        if f.get("window_uncertain"):
            flags.append("experience dates unclear (info only)")
        blocking = [x for x in flags if "info only" not in x]

        status = "ineligible" if fails else "flagged" if blocking else "ranked"
        results.append({"proposal": letter, "status": status, "score": score,
                        "breakdown": breakdown, "fails": fails, "flags": flags,
                        "_exp": breakdown["experience"]["score_0_100"], "_price": f.get("price_cad") or 10**9})

    ranked = sorted([r for r in results if r["status"] == "ranked"],
                    key=lambda r: (-r["score"], -r["_exp"], r["_price"]))  # tie-break: score, experience, price
    for i, r in enumerate(ranked, 1):
        r["rank"] = i
    for r in results:
        r.setdefault("rank", None)
    order = {"ranked": 0, "flagged": 1, "ineligible": 2}
    results.sort(key=lambda r: (order[r["status"]], r["rank"] or 99, r["proposal"]))
    return results


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    crit_path = Path(args[0] if args else "criteria.json")
    facts_path = Path(args[1] if len(args) > 1 else "extracted_sample.json")
    crit = json.loads(crit_path.read_text())
    facts = json.loads(facts_path.read_text())
    results = evaluate(crit, facts)
    crit_hash = hashlib.sha256(crit_path.read_bytes()).hexdigest()[:12]

    print(f"Criteria v{crit['version']} (sha256 {crit_hash})\n")
    for r in results:
        extra = "; ".join(r["fails"] + r["flags"])
        print(f"{r['proposal']}  {r['status']:<10} rank={r['rank']}  score={r['score']:<5} {extra}")

    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
        clean = [{k: v for k, v in r.items() if not k.startswith("_")} for r in results]
        Path(out).write_text(json.dumps({"criteria_version": crit["version"],
                                         "criteria_sha256": crit_hash, "results": clean}, indent=2))


if __name__ == "__main__":
    main()
