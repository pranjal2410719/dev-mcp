#!/usr/bin/env python3
"""
Comprehensive Link & Markdown Integrity Verifier for dev-mcp.

Checks all 11 Markdown files:
1. Zero `file:///` URLs anywhere in repo
2. Zero `/home/dev` paths in markdown documentation
3. 100% of internal relative links resolve to existing files on disk
4. All heading anchor links match actual heading slugs (GitHub slug algorithm + HTML id/name anchors)
"""
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

REPO_ROOT = Path("/home/dev/Desktop/projects/mcp/dev-mcp").resolve()

DOC_FILES = [
    "README.md",
    "CONTRIBUTING.md",
    "docs/architecture-v2.md",
    "docs/security.md",
    "docs/workspaces.md",
    "docs/user_manual.md",
    "docs/antigravity.md",
    "docs/architecture-eraser.md",
    "docs/open-design.md",
    "docs/release-notes-v2.0.0.md",
    "docs/releases/v2.0.0-summary.md",
]

def github_slug(text: str) -> str:
    """Generate GitHub-compatible slug from heading text."""
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Remove Markdown inline formatting: code ticks, bold/italic asterisks, underscores, strikethrough
    text = text.replace("`", "")
    text = re.sub(r"[*_~]", "", text)
    # Lowercase
    slug = text.strip().lower()
    # Remove punctuation: keep letters, numbers, spaces, hyphens
    slug = re.sub(r"[^\w\s-]", "", slug)
    # Replace spaces with hyphens
    slug = re.sub(r"\s+", "-", slug)
    return slug

def parse_markdown_document(doc_path: Path):
    """
    Parses a markdown document and extracts:
    - headings and slugs
    - explicit HTML anchors (<a id=...> / <a name=...>)
    - custom anchor extensions ({#my-anchor})
    - all links (inline [text](url) and reference [id]: url)
    """
    content = doc_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    slugs = set()
    explicit_anchors = set()
    slug_counts = {}

    # Check explicit HTML anchors: <a id="..." or <a name="...">
    for m in re.finditer(r'<a\s+[^>]*(?:id|name)=["\']([^"\']+)["\']', content, re.IGNORECASE):
        explicit_anchors.add(m.group(1))

    for line_num, line in enumerate(lines, 1):
        m = re.match(r'^(#{1,6})\s+(.+)$', line)
        if m:
            heading_text = m.group(2).strip()
            # Check for custom header IDs {#id}
            custom = re.search(r'\{#([^}]+)\}', heading_text)
            if custom:
                explicit_anchors.add(custom.group(1))
                heading_text = heading_text[:custom.start()].strip()
            
            base_slug = github_slug(heading_text)
            if not base_slug:
                continue
            if base_slug in slug_counts:
                slug_counts[base_slug] += 1
                unique_slug = f"{base_slug}-{slug_counts[base_slug]}"
            else:
                slug_counts[base_slug] = 0
                unique_slug = base_slug
            slugs.add(unique_slug)

    all_anchors = slugs | explicit_anchors

    # Extract all markdown links
    # Pattern handles [text](url) where url may have spaces before titles or balanced parens
    # Also ignore image links if needed or check image files as well
    links = []

    # Inline links: [text](target)
    for m in re.finditer(r'!?\[([^\]]*)\]\(([^)]+)\)', content):
        raw_target = m.group(2).strip()
        link_text = m.group(1)
        # Handle title in quotes e.g. [text](url "title")
        parts = raw_target.split(None, 1)
        target = parts[0] if parts else raw_target
        target = target.strip('<>')
        # find line number
        char_idx = m.start()
        line_no = content[:char_idx].count('\n') + 1
        links.append((line_no, link_text, target))

    # Reference links: [id]: target
    for m in re.finditer(r'^\s*\[([^\]]+)\]:\s*(\S+)', content, re.MULTILINE):
        raw_target = m.group(2).strip()
        link_text = m.group(1)
        target = raw_target.strip('<>')
        line_no = content[:m.start()].count('\n') + 1
        links.append((line_no, link_text, target))

    return all_anchors, links

def run_audit():
    print("=" * 80)
    print("DEV-MCP COMPREHENSIVE LINK & MARKDOWN INTEGRITY AUDIT")
    print("=" * 80)

    # 1. Global file:/// check
    print("\n[CHECK 1] Verifying ZERO file:/// URLs in repository (excluding git/venv/agents)...")
    file_url_errors = []
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", ".venv", ".agents", "__pycache__", "dev_mcp.egg-info")]
        for f in files:
            p = Path(root) / f
            try:
                text = p.read_text(encoding="utf-8")
                for lno, line in enumerate(text.splitlines(), 1):
                    if "file:///" in line:
                        file_url_errors.append((p.relative_to(REPO_ROOT), lno, line.strip()))
            except Exception:
                pass

    if file_url_errors:
        print(f"❌ FAILED: Found {len(file_url_errors)} file:/// occurrences:")
        for file, lno, line in file_url_errors:
            print(f"   {file}:{lno} -> {line}")
    else:
        print("✅ PASSED: Exactly 0 file:/// URLs found in repository.")

    # 2. Hardcoded /home/dev check in docs
    print("\n[CHECK 2] Verifying ZERO hardcoded /home/dev paths in documentation...")
    home_dev_errors = []
    for rel_doc in DOC_FILES:
        doc_path = REPO_ROOT / rel_doc
        if not doc_path.exists():
            print(f"❌ FAILED: File {rel_doc} does not exist!")
            continue
        text = doc_path.read_text(encoding="utf-8")
        for lno, line in enumerate(text.splitlines(), 1):
            if "/home/dev" in line:
                home_dev_errors.append((rel_doc, lno, line.strip()))

    if home_dev_errors:
        print(f"❌ FAILED: Found {len(home_dev_errors)} /home/dev references in documentation:")
        for file, lno, line in home_dev_errors:
            print(f"   {file}:{lno} -> {line}")
    else:
        print("✅ PASSED: Exactly 0 hardcoded /home/dev paths found in all 11 documentation files.")

    # 3. Relative links & anchors in all 11 markdown files
    print("\n[CHECK 3] Verifying relative Markdown links and heading anchors...")
    total_internal_links = 0
    total_external_links = 0
    broken_file_links = []
    broken_anchor_links = []

    # Pre-parse all docs
    parsed_docs = {}
    for rel_doc in DOC_FILES:
        doc_path = REPO_ROOT / rel_doc
        if doc_path.exists():
            anchors, links = parse_markdown_document(doc_path)
            parsed_docs[rel_doc] = {
                "path": doc_path,
                "anchors": anchors,
                "links": links
            }

    for rel_doc, doc_data in parsed_docs.items():
        doc_path = doc_data["path"]
        doc_dir = doc_path.parent
        anchors = doc_data["anchors"]
        links = doc_data["links"]

        print(f"\nAuditing {rel_doc} ({len(links)} links, {len(anchors)} headings/anchors):")

        for line_no, link_text, target in links:
            # Check if external
            if target.startswith(("http://", "https://", "mailto:", "ftp://", "tel:")):
                total_external_links += 1
                continue

            total_internal_links += 1

            if target.startswith("#"):
                # Same-page anchor
                anchor = unquote(target[1:])
                if anchor in anchors:
                    print(f"  ✓ L{line_no}: [{link_text}]({target}) -> local anchor found")
                else:
                    print(f"  ✗ L{line_no}: [{link_text}]({target}) -> ANCHOR NOT FOUND")
                    broken_anchor_links.append((rel_doc, line_no, link_text, target, f"Anchor '{anchor}' not in {rel_doc}"))
            else:
                # File link, possibly with anchor
                if "#" in target:
                    target_file_rel, target_anchor = target.split("#", 1)
                    target_anchor = unquote(target_anchor)
                else:
                    target_file_rel, target_anchor = target, None

                # Clean up target path
                target_file_rel = unquote(target_file_rel)
                target_path = (doc_dir / target_file_rel).resolve()

                if not target_path.exists():
                    print(f"  ✗ L{line_no}: [{link_text}]({target}) -> TARGET FILE NOT FOUND: {target_path}")
                    broken_file_links.append((rel_doc, line_no, link_text, target, f"File {target_path} does not exist"))
                else:
                    # Target exists!
                    if target_anchor:
                        # Check anchor in target file if markdown
                        rel_target_str = str(target_path.relative_to(REPO_ROOT))
                        if rel_target_str in parsed_docs:
                            target_doc_anchors = parsed_docs[rel_target_str]["anchors"]
                        elif target_path.suffix == ".md":
                            target_doc_anchors, _ = parse_markdown_document(target_path)
                        else:
                            target_doc_anchors = None

                        if target_doc_anchors is not None:
                            if target_anchor in target_doc_anchors:
                                print(f"  ✓ L{line_no}: [{link_text}]({target}) -> target file & anchor #{target_anchor} verified")
                            else:
                                print(f"  ✗ L{line_no}: [{link_text}]({target}) -> TARGET ANCHOR NOT FOUND: #{target_anchor}")
                                broken_anchor_links.append((rel_doc, line_no, link_text, target, f"Anchor '{target_anchor}' not in {rel_target_str}"))
                        else:
                            print(f"  ✓ L{line_no}: [{link_text}]({target}) -> target file verified")
                    else:
                        print(f"  ✓ L{line_no}: [{link_text}]({target}) -> target file verified")

    print("\n" + "=" * 80)
    print("AUDIT SUMMARY:")
    print(f"  Total markdown documents checked: {len(DOC_FILES)}")
    print(f"  Total external links: {total_external_links}")
    print(f"  Total internal relative links: {total_internal_links}")
    print(f"  Broken file links: {len(broken_file_links)}")
    print(f"  Broken anchor links: {len(broken_anchor_links)}")
    print(f"  file:/// violations: {len(file_url_errors)}")
    print(f"  /home/dev path violations: {len(home_dev_errors)}")
    print("=" * 80)

    success = (len(broken_file_links) == 0 and
               len(broken_anchor_links) == 0 and
               len(file_url_errors) == 0 and
               len(home_dev_errors) == 0)

    if success:
        print("\n🎉 ALL INTEGRITY CHECKS PASSED PERFECTLY (100% COMPLIANT)!\n")
        return 0
    else:
        print("\n❌ INTEGRITY CHECKS FAILED. Please review the errors above.\n")
        return 1

if __name__ == "__main__":
    sys.exit(run_audit())
