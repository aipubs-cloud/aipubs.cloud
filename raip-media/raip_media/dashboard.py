"""raip_media.dashboard

Console TUI dashboard built with ``rich``.

Two modes:
  run_pipeline_dashboard(stages, runner_fn)
    — Live animated dashboard while a pipeline runs.

  show_bundle_dashboard(bundle_dir)
    — Static view of a completed bundle (manifest + provenance).
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional

from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
)
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

console = Console()

# ---------------------------------------------------------------------------
# Stage definitions
# ---------------------------------------------------------------------------

PIPELINE_STAGES: list[str] = [
    "Integrity Check",
    "Audio Extraction",
    "Transcription",
    "Keyword Extraction",
    "Provenance Generation",
    "Signature",
    "Archive",
]

_STATUS_DONE = "[green]✓[/green]"
_STATUS_ACTIVE = "[bold cyan]►[/bold cyan]"
_STATUS_PENDING = "[dim]□[/dim]"
_STATUS_FAIL = "[red]✗[/red]"


@dataclass
class StageState:
    name: str
    status: str = "pending"   # pending | active | done | fail
    detail: str = ""


# ---------------------------------------------------------------------------
# Pipeline dashboard (live)
# ---------------------------------------------------------------------------

def run_pipeline_dashboard(
    bundle_name: str,
    stages: List[str],
    runner: Callable[[str, "PipelineCallback"], None],
) -> None:
    """Show a live dashboard while *runner* executes the pipeline.

    *runner* receives the *bundle_name* and a :class:`PipelineCallback` that
    it should call to advance the dashboard.
    """
    state = [StageState(name=s) for s in stages]
    progress = _make_progress()
    task_id = progress.add_task("Pipeline", total=len(stages))

    cb = PipelineCallback(state, progress, task_id)

    with Live(
        _render(bundle_name, state, progress, None),
        console=console,
        refresh_per_second=8,
        vertical_overflow="visible",
    ) as live:
        cb._live = live
        cb._bundle_name = bundle_name
        runner(bundle_name, cb)
        # Final render
        live.update(_render(bundle_name, state, progress, cb._summary))

    if cb._failed:
        console.print(f"\n[bold red]Pipeline FAILED.[/bold red]")
    else:
        console.print(f"\n[bold green]Pipeline completed.[/bold green]")


class PipelineCallback:
    """Passed to the pipeline runner to update dashboard state."""

    def __init__(
        self,
        state: List[StageState],
        progress: Progress,
        task_id: TaskID,
    ) -> None:
        self._state = state
        self._progress = progress
        self._task_id = task_id
        self._live: Optional[Live] = None
        self._bundle_name: str = ""
        self._summary: Optional[Dict] = None
        self._failed = False

    def start_stage(self, name: str) -> None:
        for s in self._state:
            if s.name == name:
                s.status = "active"
            elif s.status == "active":
                s.status = "done"
        self._refresh()

    def complete_stage(self, name: str, detail: str = "") -> None:
        for s in self._state:
            if s.name == name:
                s.status = "done"
                s.detail = detail
        self._progress.advance(self._task_id, 1)
        self._refresh()

    def fail_stage(self, name: str, detail: str = "") -> None:
        for s in self._state:
            if s.name == name:
                s.status = "fail"
                s.detail = detail
        self._failed = True
        self._refresh()

    def set_summary(self, summary: Dict) -> None:
        self._summary = summary
        self._refresh()

    def _refresh(self) -> None:
        if self._live:
            self._live.update(
                _render(self._bundle_name, self._state, self._progress, self._summary)
            )


# ---------------------------------------------------------------------------
# Bundle (static) dashboard
# ---------------------------------------------------------------------------

def show_bundle_dashboard(bundle_dir: Path) -> None:
    """Display a static overview of a completed bundle."""
    manifest_path = bundle_dir / "manifest.json"
    prov_path = bundle_dir / "provenance.raip.json"

    manifest: Dict = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    prov: Dict = {}
    if prov_path.exists():
        prov = json.loads(prov_path.read_text(encoding="utf-8"))

    console.rule(f"[bold cyan]RAIP Media Bundle — {bundle_dir.name}[/bold cyan]")
    console.print()
    console.print(_make_meta_panel(manifest))
    console.print()
    console.print(_make_artifacts_table(manifest))
    console.print()
    console.print(_make_provenance_panel(prov))
    console.print()


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

def _make_progress() -> Progress:
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=30),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        transient=False,
    )


def _render(
    bundle_name: str,
    state: List[StageState],
    progress: Progress,
    summary: Optional[Dict],
) -> Panel:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=3),
    )
    layout["body"].split_row(
        Layout(name="stages", ratio=1),
        Layout(name="right", ratio=2),
    )
    layout["right"].split_column(
        Layout(name="progress_area", size=5),
        Layout(name="artifacts", ratio=1),
    )

    # Header
    layout["header"].update(
        Panel(
            Text(
                f"  RAIP MEDIA INTELLIGENCE SUITE  —  {bundle_name}",
                justify="center",
                style="bold white on blue",
            ),
            box=box.HEAVY,
            border_style="blue",
        )
    )

    # Stage list
    stage_lines: list[Text] = []
    for s in state:
        if s.status == "done":
            icon = _STATUS_DONE
        elif s.status == "active":
            icon = _STATUS_ACTIVE
        elif s.status == "fail":
            icon = _STATUS_FAIL
        else:
            icon = _STATUS_PENDING
        line = Text.assemble(f"  {icon} ", (s.name, ""))
        if s.detail:
            line.append(f"  {s.detail}", style="dim")
        stage_lines.append(line)

    stage_content = "\n".join(str(l) for l in stage_lines)
    layout["stages"].update(
        Panel(stage_content, title="[bold]Stages[/bold]", border_style="cyan", padding=(1, 1))
    )

    # Progress bar
    layout["progress_area"].update(Panel(progress, title="[bold]Progress[/bold]", border_style="green"))

    # Artifacts table (summary if available)
    if summary:
        art_table = _make_artifacts_table(summary)
    else:
        art_table = Table(box=box.SIMPLE, show_header=False)
        art_table.add_row("[dim]Awaiting artifacts...[/dim]")
    layout["artifacts"].update(Panel(art_table, title="[bold]Artifacts[/bold]", border_style="magenta"))

    # Footer
    done = sum(1 for s in state if s.status == "done")
    total = len(state)
    pct = int(done / total * 100) if total else 0
    footer_text = Text.assemble(
        "  Stages: ",
        (f"{done}/{total}", "bold green"),
        f"  ({pct}%)   ",
    )
    layout["footer"].update(
        Panel(footer_text, border_style="dim")
    )

    return Panel(layout, box=box.HEAVY, border_style="blue", padding=0)


def _make_meta_panel(manifest: Dict) -> Panel:
    t = Table(box=None, show_header=False, padding=(0, 2))
    t.add_column(style="dim")
    t.add_column()
    t.add_row("Bundle ID", manifest.get("bundle_id", "—"))
    t.add_row("Generated at", manifest.get("generated_at", "—"))
    t.add_row("Generator", f"{manifest.get('generator', '—')} {manifest.get('generator_version', '')}")
    t.add_row("Artifacts", str(len(manifest.get("artifacts", []))))
    return Panel(t, title="[bold cyan]Bundle Metadata[/bold cyan]", border_style="cyan")


def _make_artifacts_table(manifest: Dict) -> Table:
    t = Table(
        title=None,
        box=box.SIMPLE_HEAD,
        show_header=True,
        header_style="bold magenta",
        padding=(0, 1),
    )
    t.add_column("ID", style="cyan", no_wrap=True)
    t.add_column("Type")
    t.add_column("ACF (prefix)", style="dim", no_wrap=True)
    t.add_column("Parent ACF (prefix)", style="dim")
    t.add_column("Path")

    for a in manifest.get("artifacts", []):
        acf = (a.get("acf") or "")
        parent_acf = (a.get("parent_acf") or "—")
        acf_short = acf[:19] + "..." if len(acf) > 19 else acf
        parent_short = parent_acf[:19] + "..." if len(parent_acf) > 19 else parent_acf
        t.add_row(
            a.get("id", "—"),
            a.get("type", "—"),
            acf_short,
            parent_short,
            Path(a.get("path", "")).name,
        )
    return t


def _make_provenance_panel(prov: Dict) -> Panel:
    if not prov:
        return Panel("[dim]No provenance found.[/dim]", title="[bold]Provenance[/bold]")

    artifact = prov.get("artifact", {})
    lifecycle = prov.get("lifecycle", {})
    attestation = prov.get("attestation", {})

    t = Table(box=None, show_header=False, padding=(0, 2))
    t.add_column(style="dim")
    t.add_column()
    t.add_row("Manifest ACF", artifact.get("acf", "—"))
    t.add_row("ALC hash", lifecycle.get("current_hash", "—"))
    t.add_row("Events", str(len(lifecycle.get("events", []))))
    t.add_row("Algorithm", attestation.get("algorithm", "—"))
    sig = attestation.get("signature", "")
    t.add_row("Signature", (sig[:32] + "...") if len(sig) > 32 else sig)

    return Panel(t, title="[bold green]RAIP Provenance[/bold green]", border_style="green")
