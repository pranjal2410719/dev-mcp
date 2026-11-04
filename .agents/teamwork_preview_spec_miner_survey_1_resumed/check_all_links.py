import re
import os
from pathlib import Path

project_root = Path("/home/dev/Desktop/projects/mcp/dev-mcp")

doc_files = [
    "README.md",
    "CONTRIBUTING.md",
    "docs/architecture-v2.md",
    "docs/architecture-eraser.md",
    "docs/security.md",
    "docs/workspaces.md",
    "docs/user_manual.md",
    "docs/antigravity.md",
    "docs/open-design.md",
    "docs/release-notes-v2.0.0.md",
    "docs/releases/v2.0.0-summary.md",
]

# GitHub Markdown slug generator
def github_slug(heading_text):
    # Remove emojis and non-alphanumeric/spaces/hyphens
    clean = re.sub(r'[^\w\s-]', '', heading_text.lower()).strip()
    return re.sub(r'[-\s]+', '-', clean)

headings_map = {}
for df in doc_files:
    fp = project_root / df
    text = fp.read_text(encoding="utf-8")
    slugs = set()
    for line in text.splitlines():
        if line.startswith("#"):
            h = line.lstrip("#").strip()
            slugs.add(github_slug(h))
            # Also without emoji manually in case
            no_emoji = re.sub(r'[^\x00-\x7F]+', '', h).strip()
            slugs.add(github_slug(no_emoji))
    headings_map[df] = slugs

link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

findings = []

for df in doc_files:
    fp = project_root / df
    text = fp.read_text(encoding="utf-8")
    for match in link_pattern.finditer(text):
        label = match.group(1)
        raw_url = match.group(2).strip()
        
        # Check for file:// protocol
        if raw_url.startswith("file:///"):
            # extract path
            local_path = raw_url.replace("file://", "")
            # check if exists locally
            exists = os.path.exists(local_path)
            # calculate correct relative link
            target_rel = os.path.relpath(local_path, fp.parent)
            findings.append({
                "file": df,
                "label": label,
                "target": raw_url,
                "issue": "ABSOLUTE_FILE_URI",
                "detail": f"Uses local machine file URI. Exists locally: {exists}. Recommended relative path: '{target_rel}'"
            })
            continue

        if raw_url.startswith("http://") or raw_url.startswith("https://") or raw_url.startswith("mailto:"):
            continue

        # Relative or anchor link
        if "#" in raw_url:
            path_part, anchor = raw_url.split("#", 1)
        else:
            path_part, anchor = raw_url, None

        if path_part == "":
            target_file = df
        else:
            target_abs = (fp.parent / path_part).resolve()
            try:
                target_file = str(target_abs.relative_to(project_root))
            except ValueError:
                target_file = str(target_abs)
            
            if not target_abs.exists():
                findings.append({
                    "file": df,
                    "label": label,
                    "target": raw_url,
                    "issue": "BROKEN_FILE_PATH",
                    "detail": f"Target file does not exist: {target_abs}"
                })
                continue

        if anchor:
            if target_file in headings_map:
                if anchor not in headings_map[target_file]:
                    findings.append({
                        "file": df,
                        "label": label,
                        "target": raw_url,
                        "issue": "BROKEN_ANCHOR",
                        "detail": f"Anchor '#{anchor}' not found in {target_file}"
                    })

print(f"Total issues found: {len(findings)}")
for f in findings:
    print(f"[{f['file']}] '{f['label']}' -> {f['target']} ({f['issue']}): {f['detail']}")

