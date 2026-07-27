"""raip — Research Artifact Integrity Protocol CLI entry point."""

import argparse
import json
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="raip",
        description="Research Artifact Integrity Protocol v1.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  raip init\n"
            "  raip publish paper.md\n"
            "  raip verify paper.md\n"
            "  raip inspect paper.md\n"
            "  raip history paper.md\n"
            "  raip sign paper.md\n"
            "  raip revoke paper.md --reason 'error in methodology'\n"
            "  raip export paper.md --format bibtex\n"
        ),
    )
    parser.add_argument("--version", action="version", version="raip 1.0.0")

    sub = parser.add_subparsers(dest="command", metavar="<command>")
    sub.required = True

    # init
    sub.add_parser("init", help="Initialise RAIP in the current directory")

    # publish
    pub_p = sub.add_parser("publish", help="Publish a paper and generate its RAIP envelope")
    pub_p.add_argument("paper", metavar="PAPER", help="Path to the Markdown paper")
    pub_p.add_argument("--author", default="", help="Author identifier")

    # verify
    ver_p = sub.add_parser("verify", help="Verify the integrity of a published paper")
    ver_p.add_argument("paper", metavar="PAPER", help="Path to the Markdown paper")
    ver_p.add_argument("--json", action="store_true", dest="as_json", help="Output report as JSON")

    # inspect
    ins_p = sub.add_parser("inspect", help="Display the RAIP envelope for a paper")
    ins_p.add_argument("paper", metavar="PAPER", help="Path to the Markdown paper")

    # sign
    sgn_p = sub.add_parser("sign", help="Re-sign the RAIP envelope with the local key")
    sgn_p.add_argument("paper", metavar="PAPER", help="Path to the Markdown paper")

    # revoke
    rev_p = sub.add_parser("revoke", help="Append a REVOKED lifecycle event")
    rev_p.add_argument("paper", metavar="PAPER", help="Path to the Markdown paper")
    rev_p.add_argument("--reason", default="", help="Reason for revocation")

    # export
    exp_p = sub.add_parser("export", help="Export citation data for a paper")
    exp_p.add_argument("paper", metavar="PAPER", help="Path to the Markdown paper")
    exp_p.add_argument(
        "--format",
        choices=["bibtex", "ris", "csl"],
        default="bibtex",
        dest="fmt",
        help="Citation format (default: bibtex)",
    )

    # history
    hist_p = sub.add_parser("history", help="Show lifecycle event history")
    hist_p.add_argument("paper", metavar="PAPER", help="Path to the Markdown paper")

    args = parser.parse_args()

    try:
        if args.command == "init":
            _cmd_init()
        elif args.command == "publish":
            from raip.cli.publish import run
            run(args)
        elif args.command == "verify":
            _cmd_verify(args)
        elif args.command == "inspect":
            from raip.cli.inspect import run
            run(args)
        elif args.command == "sign":
            from raip.cli.sign import run
            run(args)
        elif args.command == "revoke":
            from raip.cli.revoke import run
            run(args)
        elif args.command == "export":
            _cmd_export(args)
        elif args.command == "history":
            _cmd_history(args)
    except KeyboardInterrupt:
        print("\nAborted.", file=sys.stderr)
        sys.exit(130)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Inline command implementations
# ---------------------------------------------------------------------------

def _cmd_init() -> None:
    """Create .raip/ with a fresh Ed25519 keypair."""
    from raip.core.signatures import generate_keypair, private_key_to_pem, public_key_to_pem, public_key_to_b64

    raip_dir = Path(".raip")
    if raip_dir.exists():
        print("RAIP already initialised in this directory.")
        return

    raip_dir.mkdir(mode=0o700)

    private_key, public_key = generate_keypair()
    priv_pem = private_key_to_pem(private_key)
    pub_pem = public_key_to_pem(public_key)

    (raip_dir / "private.pem").write_bytes(priv_pem)
    (raip_dir / "private.pem").chmod(0o600)
    (raip_dir / "public.pem").write_bytes(pub_pem)

    config = {
        "raip_version": "1.0",
        "sign_algorithm": "Ed25519",
        "public_key_b64": public_key_to_b64(public_key),
    }
    (raip_dir / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    print("Initialised RAIP in .raip/")
    print(f"  Private key: .raip/private.pem  (keep secret — never commit)")
    print(f"  Public key:  .raip/public.pem")
    print(f"  Public key (b64): {public_key_to_b64(public_key)}")
    print()
    print("Add .raip/private.pem to .gitignore (it is already excluded by *.pem).")


def _cmd_verify(args) -> None:
    from raip.cli.verify import run
    if getattr(args, "as_json", False):
        from raip.core.verifier import verify_paper
        paper_path = Path(args.paper).resolve()
        report = verify_paper(paper_path)
        print(report.to_json())
        if not report.overall:
            sys.exit(1)
    else:
        run(args)


def _cmd_export(args) -> None:
    """Export citation data from paper frontmatter."""
    import re
    import yaml

    paper_path = Path(args.paper).resolve()
    if not paper_path.exists():
        print(f"error: file not found: {paper_path}", file=sys.stderr)
        sys.exit(1)

    text = paper_path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    fm: dict = yaml.safe_load(match.group(1)) if match else {}

    title = fm.get("title", "Untitled")
    authors = fm.get("authors", [])
    date = str(fm.get("date", ""))
    year = date[:4] if date else "9999"
    doi = fm.get("doi", "")
    abstract = fm.get("abstract", "")
    keywords = fm.get("keywords", fm.get("tags", []))
    key = _make_cite_key(authors, year, title)

    if args.fmt == "bibtex":
        print(_to_bibtex(key, title, authors, year, doi, abstract, keywords))
    elif args.fmt == "ris":
        print(_to_ris(title, authors, year, doi, abstract, keywords))
    elif args.fmt == "csl":
        print(_to_csl(key, title, authors, year, doi, abstract, keywords))


def _make_cite_key(authors: list, year: str, title: str) -> str:
    first = ""
    if authors:
        a = authors[0]
        name = a.get("name", a) if isinstance(a, dict) else str(a)
        first = name.split()[-1].lower() if name else ""
    slug = title.lower().split()[:2]
    slug_str = "".join(w for w in slug if w.isalpha())
    return f"{first}{year}{slug_str}"


def _to_bibtex(key, title, authors, year, doi, abstract, keywords) -> str:
    author_str = " and ".join(
        (a.get("name", "") if isinstance(a, dict) else str(a)) for a in authors
    )
    lines = [
        f"@article{{{key},",
        f"  title   = {{{title}}},",
        f"  author  = {{{author_str}}},",
        f"  year    = {{{year}}},",
    ]
    if doi:
        lines.append(f"  doi     = {{{doi}}},")
    if abstract:
        lines.append(f"  abstract = {{{abstract}}},")
    if keywords:
        lines.append(f"  keywords = {{{', '.join(str(k) for k in keywords)}}},")
    lines.append("}")
    return "\n".join(lines)


def _to_ris(title, authors, year, doi, abstract, keywords) -> str:
    lines = ["TY  - JOUR", f"TI  - {title}", f"PY  - {year}"]
    for a in authors:
        name = a.get("name", a) if isinstance(a, dict) else str(a)
        lines.append(f"AU  - {name}")
    if doi:
        lines.append(f"DO  - {doi}")
    if abstract:
        lines.append(f"AB  - {abstract}")
    for kw in keywords:
        lines.append(f"KW  - {kw}")
    lines.append("ER  -")
    return "\n".join(lines)


def _to_csl(key, title, authors, year, doi, abstract, keywords) -> str:
    author_list = []
    for a in authors:
        if isinstance(a, dict):
            name = a.get("name", "")
            parts = name.rsplit(" ", 1)
            author_list.append(
                {"family": parts[-1], "given": parts[0] if len(parts) > 1 else ""}
            )
        else:
            author_list.append({"literal": str(a)})

    csl = {
        "id": key,
        "type": "article-journal",
        "title": title,
        "author": author_list,
        "issued": {"date-parts": [[int(year)] if year.isdigit() else [9999]]},
    }
    if doi:
        csl["DOI"] = doi
    if abstract:
        csl["abstract"] = abstract
    if keywords:
        csl["keyword"] = ", ".join(str(k) for k in keywords)
    return json.dumps(csl, indent=2, ensure_ascii=False)


def _cmd_history(args) -> None:
    paper_path = Path(args.paper).resolve()
    envelope_path = paper_path.with_name(paper_path.stem + ".raip.json")
    if not envelope_path.exists():
        print(f"error: envelope not found: {envelope_path}", file=sys.stderr)
        sys.exit(1)

    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    events = envelope.get("events", [])
    print(f"Lifecycle history for {paper_path.name}  ({len(events)} event(s))\n")
    for i, ev in enumerate(events, 1):
        meta = ev.get("metadata", {})
        print(f"  [{i}] {ev['type']}")
        print(f"       timestamp : {ev['timestamp']}")
        print(f"       actor     : {ev['actor']}")
        if meta:
            for k, v in meta.items():
                print(f"       {k:10s}: {v}")
        print()


if __name__ == "__main__":
    main()
