#!/usr/bin/env python3
"""Deterministic CLI helper for the `epistemic-fork` skill.

Zero external dependencies (Python 3.9+ stdlib only).

Subcommands:
  sweep           Compute distributional statistics, threshold crossings, and
                  marginal fork leverage (Delta_j + single-factor R^2_j) across
                  a grid of specification runs (JSON or CSV), or generate a
                  Cartesian/fractional specification grid from axis definitions.
  scan-defaults   Scan source/config files (.py, .R, .json, .yaml, .toml, .sh)
                  for candidate silent defaults (magic numbers, weighting/metric
                  flags, dropna/filtering calls, estimators, RNG seeds).
  lint-neutrality Scan drafted prose/markdown for asymmetric first-person
                  advocacy markers or "sensitivity check" demotion framing.
  --self-test     Run deterministic built-in verification suite.
"""

from __future__ import annotations

import argparse
import ast
import csv
import itertools
import json
import math
import pathlib
import re
import statistics
import sys
from typing import Any


# ---------------------------------------------------------------------------
# 1. `sweep`: Multiverse & Marginal Fork Leverage Decomposition
# ---------------------------------------------------------------------------

def _classify_band(
    estimate: float,
    ci_low: float | None,
    ci_high: float | None,
    t_min: float | None,
    t_max: float | None,
) -> str:
    if t_min is None and t_max is None:
        return "UNBOUNDED"
    lo = ci_low if ci_low is not None else estimate
    hi = ci_high if ci_high is not None else estimate
    low_bound = t_min if t_min is not None else -math.inf
    high_bound = t_max if t_max is not None else math.inf

    if lo > high_bound:
        return "ABOVE_BAND"
    if hi < low_bound:
        return "BELOW_BAND"
    if lo >= low_bound and hi <= high_bound:
        return "INSIDE_BAND"
    return "STRADDLES_BAND"


def compute_sweep_leverage(
    runs: list[dict[str, Any]],
    *,
    estimate_key: str = "estimate",
    ci_low_key: str = "ci_low",
    ci_high_key: str = "ci_high",
    axis_keys: list[str] | None = None,
    t_min: float | None = None,
    t_max: float | None = None,
) -> dict[str, Any]:
    """Decompose a specification grid into distributional summary and marginal leverage."""
    if not runs:
        raise ValueError("Specification run list is empty.")

    reserved = {estimate_key, ci_low_key, ci_high_key, "id", "spec_id", "label", "notes"}
    if axis_keys is None:
        first = runs[0]
        axis_keys = [k for k in first.keys() if k not in reserved]

    estimates: list[float] = []
    classified_runs: list[dict[str, Any]] = []
    band_counts: dict[str, int] = {}

    for idx, row in enumerate(runs):
        if estimate_key not in row or row[estimate_key] is None:
            raise ValueError(f"Run at index {idx} is missing numeric `{estimate_key}`.")
        est = float(row[estimate_key])
        ci_lo = float(row[ci_low_key]) if row.get(ci_low_key) is not None else None
        ci_hi = float(row[ci_high_key]) if row.get(ci_high_key) is not None else None
        status = _classify_band(est, ci_lo, ci_hi, t_min, t_max)
        band_counts[status] = band_counts.get(status, 0) + 1
        estimates.append(est)
        enriched = dict(row)
        enriched["_band_status"] = status
        classified_runs.append(enriched)

    sorted_est = sorted(estimates)
    n = len(sorted_est)
    mean_est = statistics.fmean(sorted_est)
    median_est = statistics.median(sorted_est)
    min_est = sorted_est[0]
    max_est = sorted_est[-1]
    q25 = sorted_est[max(0, int(round(0.25 * (n - 1))))]
    q75 = sorted_est[min(n - 1, int(round(0.75 * (n - 1))))]
    total_ss = sum((x - mean_est) ** 2 for x in sorted_est)
    sign_positive = sum(1 for x in sorted_est if x > 0)
    sign_negative = sum(1 for x in sorted_est if x < 0)
    sign_zero = n - sign_positive - sign_negative

    leverage_rows: list[dict[str, Any]] = []
    for axis in axis_keys:
        by_option: dict[str, list[float]] = {}
        for row, est in zip(classified_runs, estimates):
            opt = str(row.get(axis, "UNSPECIFIED"))
            by_option.setdefault(opt, []).append(est)

        if len(by_option) < 2:
            continue

        opt_means = {opt: statistics.fmean(vals) for opt, vals in by_option.items()}
        opt_counts = {opt: len(vals) for opt, vals in by_option.items()}
        min_opt = min(opt_means, key=lambda k: opt_means[k])
        max_opt = max(opt_means, key=lambda k: opt_means[k])
        max_spread = opt_means[max_opt] - opt_means[min_opt]

        between_ss = sum(
            len(vals) * ((opt_means[opt] - mean_est) ** 2)
            for opt, vals in by_option.items()
        )
        variance_share = (between_ss / total_ss) if total_ss > 1e-12 else 0.0

        flips_sign = (opt_means[max_opt] > 0 and opt_means[min_opt] < 0)

        leverage_rows.append(
            {
                "axis": axis,
                "options": opt_counts,
                "option_means": {k: round(v, 6) for k, v in opt_means.items()},
                "min_option": min_opt,
                "max_option": max_opt,
                "marginal_spread_delta": round(max_spread, 6),
                "abs_leverage": round(abs(max_spread), 6),
                "variance_share_r2": round(variance_share, 4),
                "flips_mean_sign": flips_sign,
            }
        )

    leverage_rows.sort(key=lambda r: (r["abs_leverage"], r["variance_share_r2"]), reverse=True)
    for rank, item in enumerate(leverage_rows, start=1):
        item["rank"] = rank

    band_shares = {k: round(v / n, 4) for k, v in sorted(band_counts.items())}

    return {
        "total_specifications": n,
        "distribution": {
            "mean": round(mean_est, 6),
            "median": round(median_est, 6),
            "min": round(min_est, 6),
            "max": round(max_est, 6),
            "total_range": round(max_est - min_est, 6),
            "q25": round(q25, 6),
            "q75": round(q75, 6),
            "iqr": round(q75 - q25, 6),
            "sign_split": {
                "positive": sign_positive,
                "negative": sign_negative,
                "zero": sign_zero,
            },
        },
        "threshold_band": {
            "t_min": t_min,
            "t_max": t_max,
            "counts": band_counts,
            "shares": band_shares,
        },
        "fork_leverage_ranking": leverage_rows,
    }


def generate_spec_grid(axes: dict[str, list[Any]], max_specs: int = 64) -> dict[str, Any]:
    """Generate a Cartesian or strided fractional specification grid from axis options."""
    if not axes:
        raise ValueError("Axes dictionary must contain at least one decision axis.")
    keys = list(axes.keys())
    value_lists = [axes[k] for k in keys]
    for k, vals in zip(keys, value_lists):
        if not isinstance(vals, list) or len(vals) < 2:
            raise ValueError(f"Axis `{k}` must provide a list of at least 2 options.")

    all_combos = list(itertools.product(*value_lists))
    full_count = len(all_combos)

    if full_count <= max_specs:
        selected = all_combos
        sampling = "full_cartesian"
    else:
        # Always include the two extremes (all-first and all-last) plus evenly strided interior points
        step = max(1, (full_count - 1) / (max_specs - 1))
        indices = sorted({0, full_count - 1} | {min(full_count - 1, int(round(i * step))) for i in range(max_specs)})
        selected = [all_combos[i] for i in indices[:max_specs]]
        sampling = f"fractional_strided({len(selected)}_of_{full_count})"

    specs = []
    for idx, combo in enumerate(selected, start=1):
        code = "".join(str(v)[0].upper() for v in combo)
        spec = {"spec_id": f"S{idx:02d}_{code}"}
        for k, v in zip(keys, combo):
            spec[k] = v
        specs.append(spec)

    return {
        "axes": axes,
        "full_cartesian_count": full_count,
        "returned_count": len(specs),
        "sampling_mode": sampling,
        "specifications": specs,
    }


# ---------------------------------------------------------------------------
# 2. `scan-defaults`: Surface Candidate Silent Defaults in Code/Configs
# ---------------------------------------------------------------------------

_DEFAULT_PATTERNS: list[tuple[str, str, re.Pattern[str]]] = [
    (
        "missingness_or_filter",
        "Row filtering / missingness drop (check if asymmetric across arms/slices)",
        re.compile(r"\b(dropna|fillna|filter|query|clip|trim|winsorize)\s*\("),
    ),
    (
        "weighting_or_aggregation",
        "Weighting or aggregation reducer (check unit-equal vs volume/duration weighted)",
        re.compile(r"\b(weights\s*=|sample_weight\s*=|average\s*\(|weighted|agg\s*\()"),
    ),
    (
        "estimator_or_loss",
        "Model / estimator / covariance / loss specification",
        re.compile(
            r"\b(OLS|WLS|Logit|Probit|PanelOLS|DifferenceInDifferences|ANCOVA|"
            r"cov_type\s*=|cluster|alpha\s*=|l1_ratio\s*=|regularization)\b"
        ),
    ),
    (
        "threshold_or_window",
        "Hardcoded threshold, quantile, window length, or radius parameter",
        re.compile(
            r"\b(threshold|cutoff|quantile|percentile|window|radius|feather|dilation|"
            r"cfg_scale|steps|min_score|max_length)\s*=\s*[-+]?\d+(?:\.\d+)?"
        ),
    ),
    (
        "stochastic_seed",
        "Random seed or stochastic sampling knob",
        re.compile(r"\b(random_state|seed|manual_seed|np\.random\.seed)\s*[=(]"),
    ),
]


def scan_file_for_defaults(path: pathlib.Path) -> list[dict[str, Any]]:
    """Scan a source or config file for candidate hardcoded judgment defaults."""
    text = path.read_text(encoding="utf-8", errors="replace")
    findings: list[dict[str, Any]] = []

    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("//"):
            continue
        for category, rationale, pattern in _DEFAULT_PATTERNS:
            match = pattern.search(line)
            if match:
                findings.append(
                    {
                        "file": str(path),
                        "line": lineno,
                        "category": category,
                        "matched_token": match.group(0).strip(),
                        "rationale": rationale,
                        "snippet": stripped[:140],
                    }
                )

    # If Python file, also inspect function signature default arguments
    if path.suffix == ".py":
        try:
            tree = ast.parse(text, filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    args = node.args
                    pos_names = [a.arg for a in args.args]
                    defaults = args.defaults
                    if defaults:
                        offset = len(pos_names) - len(defaults)
                        for arg_name, def_node in zip(pos_names[offset:], defaults):
                            if isinstance(def_node, ast.Constant) and isinstance(
                                def_node.value, (int, float, str, bool)
                            ):
                                if def_node.value is not None and arg_name not in {"self", "cls", "verbose", "debug"}:
                                    findings.append(
                                        {
                                            "file": str(path),
                                            "line": node.lineno,
                                            "category": "function_signature_default",
                                            "matched_token": f"{node.name}({arg_name}={def_node.value!r})",
                                            "rationale": "Function signature default parameter",
                                            "snippet": f"def {node.name}(..., {arg_name}={def_node.value!r})",
                                        }
                                    )
        except SyntaxError:
            pass

    return findings


# ---------------------------------------------------------------------------
# 3. `lint-neutrality`: Detect Asymmetric First-Person Advocacy in Matrix Prose
# ---------------------------------------------------------------------------

_ADVOCACY_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("first_person_lean", re.compile(r"\bI(?:\s+would|\'d)?\s+(?:lean\s+toward|prefer|recommend|advise|pick|choose|favor)\b", re.IGNORECASE)),
    ("my_preference", re.compile(r"\bmy\s+(?:preference|recommendation|preferred\s+specification|default\s+choice)\b", re.IGNORECASE)),
    ("sensitivity_demotion", re.compile(r"\bas\s+a\s+(?:secondary\s+)?(?:sensitivity\s+check|robustness\s+check|sanity\s+check)\b", re.IGNORECASE)),
    ("on_principle_bias", re.compile(r"\bon\s+principle,?\s+I\b", re.IGNORECASE)),
    ("obviously_superior", re.compile(r"\b(?:clearly|obviously|undeniably)\s+the\s+(?:better|superior|correct|right)\s+(?:choice|option|specification|model)\b", re.IGNORECASE)),
]


def lint_neutrality(text: str) -> dict[str, Any]:
    """Check drafted text for asymmetric advocacy phrases that violate `matrix` or `lock` neutrality."""
    violations: list[dict[str, Any]] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for rule_id, pattern in _ADVOCACY_PATTERNS:
            for match in pattern.finditer(line):
                violations.append(
                    {
                        "line": lineno,
                        "rule": rule_id,
                        "matched": match.group(0),
                        "context": line.strip()[:140],
                    }
                )
    return {
        "neutral": len(violations) == 0,
        "violation_count": len(violations),
        "violations": violations,
    }


# ---------------------------------------------------------------------------
# 4. Built-in Self-Test Suite (`--self-test`)
# ---------------------------------------------------------------------------

def run_self_test() -> int:
    # 1. Test `compute_sweep_leverage` on a synthetic 2^3 multiverse grid
    synthetic_runs = [
        {"d1_metric": "A_physical", "d2_model": "A_did", "d3_weight": "A_equal", "estimate": 4.8, "ci_low": 2.1, "ci_high": 7.5},
        {"d1_metric": "A_physical", "d2_model": "A_did", "d3_weight": "B_volume", "estimate": 4.2, "ci_low": 1.8, "ci_high": 6.6},
        {"d1_metric": "A_physical", "d2_model": "B_ancova", "d3_weight": "A_equal", "estimate": 1.1, "ci_low": -0.5, "ci_high": 2.7},
        {"d1_metric": "A_physical", "d2_model": "B_ancova", "d3_weight": "B_volume", "estimate": 0.7, "ci_low": -0.8, "ci_high": 2.2},
        {"d1_metric": "B_cost_norm", "d2_model": "A_did", "d3_weight": "A_equal", "estimate": 2.4, "ci_low": 0.3, "ci_high": 4.5},
        {"d1_metric": "B_cost_norm", "d2_model": "A_did", "d3_weight": "B_volume", "estimate": 1.8, "ci_low": -0.1, "ci_high": 3.7},
        {"d1_metric": "B_cost_norm", "d2_model": "B_ancova", "d3_weight": "A_equal", "estimate": -1.2, "ci_low": -2.8, "ci_high": 0.4},
        {"d1_metric": "B_cost_norm", "d2_model": "B_ancova", "d3_weight": "B_volume", "estimate": -1.6, "ci_low": -3.1, "ci_high": -0.1},
    ]
    res = compute_sweep_leverage(synthetic_runs, t_min=0.0, t_max=2.0)
    assert res["total_specifications"] == 8, f"Expected 8 specs, got {res['total_specifications']}"
    top_axis = res["fork_leverage_ranking"][0]
    assert top_axis["axis"] == "d2_model", f"Expected d2_model as highest leverage, got {top_axis['axis']}"
    assert math.isclose(top_axis["abs_leverage"], 3.55, rel_tol=1e-3), f"Unexpected leverage: {top_axis}"

    # 2. Test `generate_spec_grid`
    grid = generate_spec_grid({"d1": ["A", "B", "C"], "d2": ["narrow", "wide"]}, max_specs=10)
    assert grid["full_cartesian_count"] == 6
    assert grid["returned_count"] == 6

    # 3. Test `lint_neutrality`
    bad_text = "I lean toward Option B as the primary model, and we can run Option A as a sensitivity check."
    lint_bad = lint_neutrality(bad_text)
    assert not lint_bad["neutral"] and lint_bad["violation_count"] == 2
    good_text = "Option A assumes parallel trends in levels; Option B assumes selection on baseline observables."
    lint_good = lint_neutrality(good_text)
    assert lint_good["neutral"] and lint_good["violation_count"] == 0

    print(
        json.dumps(
            {
                "status": "ok",
                "tests_passed": [
                    "compute_sweep_leverage",
                    "generate_spec_grid",
                    "lint_neutrality",
                ],
                "sample_top_fork": top_axis,
            },
            indent=2,
        )
    )
    return 0


# ---------------------------------------------------------------------------
# 5. CLI Entrypoint
# ---------------------------------------------------------------------------

def _load_runs(path_str: str) -> list[dict[str, Any]]:
    path = pathlib.Path(path_str)
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            rows: list[dict[str, Any]] = []
            for r in reader:
                parsed: dict[str, Any] = {}
                for k, v in r.items():
                    if v is None or v == "":
                        parsed[k] = None
                    else:
                        try:
                            parsed[k] = float(v)
                        except ValueError:
                            parsed[k] = v
                rows.append(parsed)
            return rows
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "runs" in data:
        return list(data["runs"])
    if isinstance(data, list):
        return data
    raise ValueError("Input JSON must be a list of run objects or a dict with a `runs` list.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="spec_matrix.py",
        description="Deterministic specification grid, leverage decomposition, default scanner, and neutrality linter.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in verification self-test suite.")
    subparsers = parser.add_subparsers(dest="subcommand")

    # sweep
    p_sweep = subparsers.add_parser(
        "sweep",
        help="Compute marginal fork leverage across specification runs, or generate a specification grid.",
    )
    p_sweep.add_argument("--runs", type=str, help="Path to JSON or CSV file of specification runs.")
    p_sweep.add_argument(
        "--axes-json",
        type=str,
        help="JSON string or file path mapping axis names to option lists to generate a specification grid.",
    )
    p_sweep.add_argument("--estimate-key", type=str, default="estimate", help="Key for primary numeric estimate.")
    p_sweep.add_argument("--ci-low-key", type=str, default="ci_low", help="Key for lower confidence bound.")
    p_sweep.add_argument("--ci-high-key", type=str, default="ci_high", help="Key for upper confidence bound.")
    p_sweep.add_argument("--axes", type=str, nargs="*", help="Explicit list of decision axis column names.")
    p_sweep.add_argument("--t-min", type=float, default=None, help="Lower decision band threshold.")
    p_sweep.add_argument("--t-max", type=float, default=None, help="Upper decision band threshold.")
    p_sweep.add_argument("--max-specs", type=int, default=64, help="Max specifications when generating a grid.")

    # scan-defaults
    p_scan = subparsers.add_parser(
        "scan-defaults",
        help="Scan source or config files for candidate silent judgment defaults.",
    )
    p_scan.add_argument("paths", nargs="+", help="Files or directories to scan.")

    # lint-neutrality
    p_lint = subparsers.add_parser(
        "lint-neutrality",
        help="Check text or markdown file for asymmetric first-person advocacy or sensitivity-check demotion.",
    )
    p_lint.add_argument("--file", type=str, help="Path to markdown/text file (reads stdin if omitted).")
    p_lint.add_argument("--text", type=str, help="Inline text string to lint.")

    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    if args.subcommand == "sweep":
        if args.axes_json:
            p = pathlib.Path(args.axes_json)
            axes_data = json.loads(p.read_text(encoding="utf-8")) if p.exists() else json.loads(args.axes_json)
            out = generate_spec_grid(axes_data, max_specs=args.max_specs)
            print(json.dumps(out, indent=2))
            return 0
        if not args.runs:
            parser.error("`sweep` requires either `--runs <file.json|file.csv>` or `--axes-json <json>`.")
        runs = _load_runs(args.runs)
        out = compute_sweep_leverage(
            runs,
            estimate_key=args.estimate_key,
            ci_low_key=args.ci_low_key,
            ci_high_key=args.ci_high_key,
            axis_keys=args.axes,
            t_min=args.t_min,
            t_max=args.t_max,
        )
        print(json.dumps(out, indent=2))
        return 0

    if args.subcommand == "scan-defaults":
        all_findings: list[dict[str, Any]] = []
        allowed_exts = {".py", ".r", ".R", ".json", ".yaml", ".yml", ".toml", ".sh"}
        for raw_p in args.paths:
            target = pathlib.Path(raw_p)
            if target.is_dir():
                for child in sorted(target.rglob("*")):
                    if child.is_file() and child.suffix in allowed_exts:
                        all_findings.extend(scan_file_for_defaults(child))
            elif target.is_file():
                all_findings.extend(scan_file_for_defaults(target))
        print(
            json.dumps(
                {
                    "finding_count": len(all_findings),
                    "findings": all_findings,
                },
                indent=2,
            )
        )
        return 0

    if args.subcommand == "lint-neutrality":
        if args.text is not None:
            content = args.text
        elif args.file:
            content = pathlib.Path(args.file).read_text(encoding="utf-8")
        else:
            content = sys.stdin.read()
        result = lint_neutrality(content)
        print(json.dumps(result, indent=2))
        return 0 if result["neutral"] else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
