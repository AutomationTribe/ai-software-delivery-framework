#!/usr/bin/env python3
"""Validate the framework repository (default) or an adopting project (--project PATH).

Standard library only. Exit code 0 = all checks passed, 1 = at least one failed.
Checks structure and consistency; it does NOT prove agents behave correctly (see docs/VALIDATION.md).
"""
import argparse, json, re, sys
from pathlib import Path

EXPECTED_AGENTS = ["design", "database-architect", "backend", "backend-reviewer", "frontend",
                   "frontend-reviewer", "reviewer", "qa", "security", "devops"]
READ_ONLY_AGENTS = ["database-architect", "backend-reviewer", "frontend-reviewer", "reviewer", "security"]
WRITE_TOOLS = {"Write", "Edit", "NotebookEdit", "MultiEdit"}
# Installed-path -> repository-path mapping for references made by agents.
REPO_MAP = {"docs/framework/POLICY.md": "docs/POLICY.md",
            "docs/framework/VERSIONING.md": "docs/VERSIONING.md",
            "docs/framework/PROJECT_PROFILE.md": "templates/PROJECT_PROFILE.md.template",
            "docs/framework/ADOPTION_RECORD.md": "templates/ADOPTION_RECORD.md.template",
            "docs/framework/FRAMEWORK_VERSION": "VERSION"}
# Project-specific terms that must not appear in the generic framework. Built from fragments so this
# file does not itself contain them.
BANNED = ["".join(p) for p in [("Test", "Flow"), ("test", "flow"), ("Int", "ello"), ("Pay", "stack"),
                               ("Ne", "on"), ("Ren", "der"), ("PS", "A"), ("Stitch ", "project"),
                               ("Auto", "mationTribe-internal")]]
BANNED_WORD = {"".join(("Ne", "on")), "".join(("Ren", "der")), "".join(("PS", "A"))}
SECRET_PATTERNS = [r"sk-[A-Za-z0-9]{20,}", r"ghp_[A-Za-z0-9]{20,}", r"github_pat_[A-Za-z0-9_]{20,}",
                   r"AKIA[0-9A-Z]{16}", r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
                   r"xox[baprs]-[A-Za-z0-9-]{10,}", r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}",
                   r"/Users/[A-Za-z0-9_.-]+", r"postgres(ql)?://[^\s]+:[^\s]+@"]
ALLOWED_URLS = ("https://github.com/AutomationTribe/ai-software-delivery-framework", "https://claude.com/claude-code", "https://semver.org/", "https://keepachangelog.com/")

fails, passes = [], []
def ok(msg): passes.append(msg)
def bad(msg): fails.append(msg)
def check(cond, good, problem):
    ok(good) if cond else bad(problem)

def parse_frontmatter(text):
    """Parse the deliberately restricted, single-line YAML scalar frontmatter schema.

    The framework's agent metadata uses only scalar key/value pairs. Reject YAML
    constructs outside that subset rather than silently accepting invalid YAML.
    No external YAML dependency is needed.
    """
    m = re.match(r"^---\\r?\\n(.*?)\\r?\\n---(?:\\r?\\n|$)", text, re.S)
    if not m:
        raise ValueError("missing or unterminated YAML frontmatter")
    out = {}
    for line_no, line in enumerate(m.group(1).splitlines(), 2):
        if not line.strip() or line.startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_-]*):[ \\t]+(.+)", line)
        if not match:
            raise ValueError(f"line {line_no}: expected unindented key: scalar")
        key, value = match.groups()
        if key in out:
            raise ValueError(f"line {line_no}: duplicate key {key!r}")
        value = value.strip()
        if value.startswith('"'):
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError(f"line {line_no}: invalid double-quoted scalar: {exc}") from exc
            if not isinstance(parsed, str):
                raise ValueError(f"line {line_no}: expected string scalar")
            value = parsed
        elif value.startswith("'"):
            if not re.fullmatch(r"'(?:[^']|'')*'", value):
                raise ValueError(f"line {line_no}: invalid single-quoted scalar")
            value = value[1:-1].replace("''", "'")
        else:
            # YAML plain scalars cannot contain a colon followed by whitespace,
            # or a whitespace-prefixed comment marker. This catches the v1.1.0
            # devops description that the old split(':', 1) parser accepted.
            if re.search(r":(?=\\s|$)|\\s#", value):
                raise ValueError(f"line {line_no}: invalid unquoted YAML scalar")
            if value[0] in "{}[]&*!|>%@`":
                raise ValueError(f"line {line_no}: unsupported YAML scalar syntax")
        out[key] = value
    return out

def agent_checks(agent_dir, label, strict_set):
    files = sorted(agent_dir.glob("*.md"))
    names = [f.stem for f in files]
    if strict_set:
        check(sorted(names) == sorted(EXPECTED_AGENTS), f"{label}: all {len(EXPECTED_AGENTS)} framework agents present",
              f"{label}: agent set mismatch; missing={sorted(set(EXPECTED_AGENTS)-set(names))} extra={sorted(set(names)-set(EXPECTED_AGENTS))}")
    for f in files:
        try:
            fm = parse_frontmatter(f.read_text())
        except ValueError as exc:
            bad(f"{f.name}: invalid frontmatter: {exc}")
            continue
        for key in ("name", "description", "tools", "model"):
            check(bool(fm.get(key)), f"{f.name}: has {key}", f"{f.name}: missing/empty frontmatter '{key}'")
        check(fm.get("name") == f.stem, f"{f.name}: name matches filename", f"{f.name}: name '{fm.get('name')}' != filename")
        tools = {t.strip() for t in fm.get("tools", "").split(",") if t.strip()}
        if f.stem in READ_ONLY_AGENTS:
            check(not (tools & WRITE_TOOLS), f"{f.name}: read-only reviewer has no write tools",
                  f"{f.name}: reviewer has write tools {sorted(tools & WRITE_TOOLS)}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", help="validate an adopting project instead of the framework repo")
    args = ap.parse_args()

    if args.project:
        root = Path(args.project).resolve()
        agent_checks(root / ".claude" / "agents", "project agents", strict_set=False)
        for rel in ("docs/framework/POLICY.md", "docs/framework/VERSIONING.md", "docs/framework/FRAMEWORK_VERSION",
                    "docs/framework/PROJECT_PROFILE.md", "docs/framework/ADOPTION_RECORD.md"):
            check((root / rel).exists(), f"{rel} present", f"{rel} missing")
        for f in (root / ".claude" / "agents").glob("*.md"):
            for ref in re.findall(r"docs/framework/[A-Za-z_./-]+\.md", f.read_text()):
                check((root / ref.rstrip(".")).exists(), f"{f.name}: {ref} resolves", f"{f.name}: {ref} does not resolve")
        prof = root / "docs/framework/PROJECT_PROFILE.md"
        if prof.exists():
            check("{{" not in prof.read_text(), "project profile has no unfilled placeholders",
                  "project profile still contains {{placeholders}} (fill in or mark pending)")
    else:
        root = Path(__file__).resolve().parent.parent
        agent_checks(root / "agents", "agents", strict_set=True)
        # references
        for f in (root / "agents").glob("*.md"):
            for ref in set(re.findall(r"docs/framework/[A-Za-z_./-]*[A-Za-z_]", f.read_text())):
                target = REPO_MAP.get(ref)
                check(target is not None and (root / target).exists(), f"{f.name}: {ref} resolves",
                      f"{f.name}: reference {ref} has no repository target")
        # workflow + registry
        policy = (root / "docs/POLICY.md").read_text()
        for n in range(1, 21):
            check(re.search(rf"^\s*{n}\.\s", policy, re.M) is not None, f"POLICY step {n} present", f"POLICY step {n} missing")
        for a in EXPECTED_AGENTS:
            check(f"`{a}`" in policy, f"POLICY registry mentions {a}", f"POLICY does not mention agent {a}")
        # version consistency
        v = (root / "VERSION").read_text().strip()
        cl = re.search(r"^## \[([0-9.]+)\]", (root / "CHANGELOG.md").read_text(), re.M)
        check(cl and cl.group(1) == v, f"CHANGELOG top entry == VERSION ({v})", "CHANGELOG top entry != VERSION")
        check(f"Framework version: {v}" in policy, "POLICY header version matches", "POLICY header version != VERSION")
        check(f"Current version: {v}" in (root / "docs/VERSIONING.md").read_text(), "VERSIONING current version matches", "VERSIONING current version != VERSION")
        # templates
        for t in ("CLAUDE.md.template", "PROJECT_PROFILE.md.template", "ADOPTION_RECORD.md.template", "PROJECT_STATUS.md.template",
                  "coding-standards.md.template", "technical-debt.md.template", "adr-template.md", "claude-settings.stop-hook.example.json"):
            check((root / "templates" / t).exists(), f"template {t} present", f"template {t} missing")
        try:
            json.loads((root / "templates/claude-settings.stop-hook.example.json").read_text()); ok("hook example is valid JSON")
        except Exception as e:
            bad(f"hook example invalid JSON: {e}")
        for p in ("adopt-existing-project.md", "bootstrap-new-project.md", "upgrade-framework.md"):
            check((root / "prompts" / p).exists(), f"prompt {p} present", f"prompt {p} missing")
        # markdown relative links
        for md in root.rglob("*.md"):
            if ".git" in md.parts: continue
            for target in re.findall(r"\]\(([^)#\s]+)\)", md.read_text()):
                if target.startswith(("http", "mailto:")): continue
                check((md.parent / target).exists(), f"{md.relative_to(root)}: link {target} ok", f"{md.relative_to(root)}: broken link {target}")
        # content hygiene
        me = Path(__file__).resolve()
        for f in root.rglob("*"):
            if not f.is_file() or ".git" in f.parts or f == me: continue
            try: text = f.read_text()
            except UnicodeDecodeError: continue
            rel = f.relative_to(root)
            for term in BANNED:
                hit = re.search(rf"\b{re.escape(term)}\b", text) if term in BANNED_WORD else (term in text)
                if hit: bad(f"{rel}: contains project-specific term '{term}'")
            for pat in SECRET_PATTERNS:
                for m in re.finditer(pat, text):
                    if m.group(0).startswith("noreply@"): continue
                    bad(f"{rel}: matches secret/path pattern {pat!r}: {m.group(0)[:40]}")
            for url in re.findall(r"https?://[^\s)>\"']+", text):
                if not url.startswith(ALLOWED_URLS): bad(f"{rel}: unexpected URL {url}")
        ok("content hygiene scan completed")

    for m in passes: print("PASS", m)
    for m in fails: print("FAIL", m)
    print(f"\n{len(passes)} passed, {len(fails)} failed")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
