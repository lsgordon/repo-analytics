#!/usr/bin/env python3
"""
Workflow: fetch Python code corpus from the web → keep in RAM → tokenize →
count keyword, built-in, and dunder method frequencies for analytics.
Language reference frozen at Python 3.12 (see py312_language.py).
Supports single URL, in-memory source, or full python/cpython repo (all .py files).
"""

import io
import json
import re
import shutil
import subprocess
import tempfile
import tokenize
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Optional

from py312_language import PY312_BUILTINS, PY312_KEYWORDS, PY312_SPECIAL_METHODS


def fetch_corpus_into_ram(url: str) -> str:
    """Fetch raw text from URL into memory (RAM); return as string."""
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def tokenize_source(source: str) -> list[tuple[str, str]]:
    """
    Tokenize Python source (in RAM). Returns list of (kind, string) where
    kind is 'keyword' or 'name'. Uses Python 3.12 keyword set.
    """
    tokens = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(source).readline):
            if tok.type != tokenize.NAME:
                continue
            if tok.string in PY312_KEYWORDS:
                tokens.append(("keyword", tok.string))
            else:
                tokens.append(("name", tok.string))
    except tokenize.TokenError:
        pass
    return tokens


def count_keywords_builtins_dunder(
    tokens: list[tuple[str, str]],
) -> tuple[Counter, Counter, Counter]:
    """
    Count keyword, built-in, and dunder method frequency from token list.
    Uses Python 3.12 frozen language reference.
    """
    keyword_counts: Counter = Counter()
    builtin_counts: Counter = Counter()
    dunder_counts: Counter = Counter()
    for kind, s in tokens:
        if kind == "keyword":
            keyword_counts[s] += 1
        elif kind == "name":
            if s in PY312_BUILTINS:
                builtin_counts[s] += 1
            if s in PY312_SPECIAL_METHODS:
                dunder_counts[s] += 1
    return keyword_counts, builtin_counts, dunder_counts


def run_workflow(
    corpus_url: Optional[str] = None,
    in_memory_source: Optional[str] = None,
) -> dict:
    """
    Run full workflow: load corpus (URL or in-memory), tokenize, count.
    Returns dict with keyword_freq, builtin_freq, and metadata for analytics.
    """
    if in_memory_source is not None:
        source = in_memory_source
        source_note = "in_memory"
    elif corpus_url:
        source = fetch_corpus_into_ram(corpus_url)
        source_note = corpus_url
    else:
        raise ValueError("Provide either corpus_url or in_memory_source")

    tokens = tokenize_source(source)
    keyword_freq, builtin_freq, dunder_freq = count_keywords_builtins_dunder(tokens)

    return {
        "meta": {
            "source": source_note,
            "language_reference": "Python 3.12 (frozen)",
            "total_tokens_analyzed": len(tokens),
            "total_keyword_occurrences": sum(keyword_freq.values()),
            "total_builtin_occurrences": sum(builtin_freq.values()),
            "total_dunder_occurrences": sum(dunder_freq.values()),
        },
        "keyword_freq": dict(keyword_freq.most_common()),
        "builtin_freq": dict(builtin_freq.most_common()),
        "dunder_freq": dict(dunder_freq.most_common()),
    }


def save_analytics(result: dict, path: str = "keyword_analytics.json") -> None:
    """Persist analytics result to JSON for later use."""
    with open(path, "w") as f:
        json.dump(result, f, indent=2)


def _run_workflow_directory(repo_root: Path, source_label: str) -> dict:
    """
    Walk all .py files under repo_root, tokenize, aggregate keyword/builtin/dunder.
    Shared by run_workflow_cpython and run_workflow_repo.
    """
    keyword_totals: Counter = Counter()
    builtin_totals: Counter = Counter()
    dunder_totals: Counter = Counter()
    total_tokens = 0
    files_processed = 0
    total_bytes = 0

    py_files = sorted(repo_root.rglob("*.py"))
    for path in py_files:
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        total_bytes += len(source.encode("utf-8", errors="replace"))
        tokens = tokenize_source(source)
        kw, blt, dnd = count_keywords_builtins_dunder(tokens)
        keyword_totals.update(kw)
        builtin_totals.update(blt)
        dunder_totals.update(dnd)
        total_tokens += len(tokens)
        files_processed += 1

    return {
        "meta": {
            "source": source_label,
            "language_reference": "Python 3.12 (frozen)",
            "files_processed": files_processed,
            "total_tokens_analyzed": total_tokens,
            "total_keyword_occurrences": sum(keyword_totals.values()),
            "total_builtin_occurrences": sum(builtin_totals.values()),
            "total_dunder_occurrences": sum(dunder_totals.values()),
            "total_bytes": total_bytes,
        },
        "keyword_freq": dict(keyword_totals.most_common()),
        "builtin_freq": dict(builtin_totals.most_common()),
        "dunder_freq": dict(dunder_totals.most_common()),
    }


def _normalize_repo_url(repo_input: str) -> str:
    """Convert 'user/repo' or 'https://github.com/user/repo' to clone URL."""
    s = repo_input.strip()
    if re.match(r"^[\w.-]+/[\w.-]+$", s):
        return f"https://github.com/{s}.git"
    if "github.com" in s and not s.endswith(".git"):
        return s if s.endswith("/") else s + ".git"
    return s


def clone_repo(repo_url: str, target_dir: Path, timeout_seconds: int = 120) -> Path:
    """
    Clone repo (shallow) into target_dir. Returns path to repo root.
    target_dir must exist; clone creates target_dir / repo_name.
    """
    url = _normalize_repo_url(repo_url)
    # repo name from URL, e.g. https://github.com/django/django.git -> django
    name = url.rstrip("/").split("/")[-1].replace(".git", "") or "repo"
    repo_path = target_dir / name
    if repo_path.exists():
        shutil.rmtree(repo_path)
    subprocess.run(
        ["git", "clone", "--depth", "1", url, str(repo_path)],
        check=True,
        capture_output=True,
        timeout=timeout_seconds,
    )
    return repo_path


def run_workflow_repo(repo_url: str, timeout_seconds: int = 120, max_files: int = 50_000) -> dict:
    """
    Clone repo to a temp dir, run analytics on all .py files, return result and cleanup.
    Raises ValueError if repo has no .py files or clone fails.
    """
    with tempfile.TemporaryDirectory(prefix="keyword_analytics_") as tmp:
        work = Path(tmp)
        clone_repo(repo_url, work, timeout_seconds=timeout_seconds)
        # Clone puts repo in work/repo_name; find single top-level dir
        children = [p for p in work.iterdir() if p.is_dir()]
        if not children:
            raise ValueError("Clone produced no directory")
        repo_root = children[0]
        py_count = len(list(repo_root.rglob("*.py")))
        if py_count == 0:
            raise ValueError("Repository contains no .py files")
        if py_count > max_files:
            raise ValueError(f"Repository has {py_count} .py files; max allowed is {max_files}")
        result = _run_workflow_directory(repo_root, repo_url)
        result["meta"]["repo_url"] = repo_url
        return result


def ensure_cpython_repo(target_dir: Path, clone_url: str = "https://github.com/python/cpython.git") -> Path:
    """
    Clone python/cpython (shallow) into target_dir if it doesn't exist or is empty.
    Returns path to repo root (target_dir / "cpython").
    """
    repo_root = target_dir / "cpython"
    if repo_root.exists() and (repo_root / "Lib").exists():
        return repo_root
    target_dir.mkdir(parents=True, exist_ok=True)
    if repo_root.exists():
        shutil.rmtree(repo_root)
    subprocess.run(
        ["git", "clone", "--depth", "1", "--branch", "main", clone_url, str(repo_root)],
        check=True,
        capture_output=True,
    )
    return repo_root


def run_workflow_cpython(cpython_root: Path) -> dict:
    """
    Run analytics on all .py files under cpython_root. Uses Python 3.12 frozen reference.
    """
    result = _run_workflow_directory(cpython_root, "python/cpython (full repo)")
    result["meta"]["cpython_root"] = str(cpython_root)
    return result


# Default corpus: small, real Python module from CPython stdlib
DEFAULT_CORPUS_URL = (
    "https://raw.githubusercontent.com/python/cpython/main/Lib/collections/__init__.py"
)

# Where to clone cpython (same directory as this script)
CPYTHON_CLONE_DIR = Path(__file__).resolve().parent


def main() -> None:
    print("Using full python/cpython source + stdlib...")
    repo = ensure_cpython_repo(CPYTHON_CLONE_DIR)
    result = run_workflow_cpython(repo)
    meta = result["meta"]
    print(f"Language reference: {meta['language_reference']}")
    print(f"Files processed: {meta['files_processed']}")
    print(f"Tokens analyzed: {meta['total_tokens_analyzed']}")
    print(f"Keyword occurrences: {meta['total_keyword_occurrences']}")
    print(f"Built-in occurrences: {meta['total_builtin_occurrences']}")
    print(f"Dunder occurrences: {meta['total_dunder_occurrences']}")
    print(f"Total bytes: {meta['total_bytes']}")
    out_path = "keyword_analytics.json"
    save_analytics(result, out_path)
    print(f"Analytics saved to {out_path}")
    print("\nTop keywords:", list(result["keyword_freq"].items())[:15])
    print("Top built-ins:", list(result["builtin_freq"].items())[:15])
    print("Top dunder:", list(result["dunder_freq"].items())[:15])


if __name__ == "__main__":
    main()
