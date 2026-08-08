"""
termdash — a live CPU/memory dashboard, pinky winky edition 💗
"""

import time
import psutil
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.table import Table

console = Console()

# --- pinky winky palette ---
HOT_PINK = "#FF69B4"
BABY_PINK = "#FFD1E3"
MAGENTA = "#C71585"
DEEP_PLUM = "#8B006D"


def make_bar(label: str, percent: float) -> Table:
    bar = ProgressBar(total=100, completed=percent, width=30,
                       complete_style=HOT_PINK, finished_style=MAGENTA)
    row = Table.grid(padding=(0, 1))
    row.add_column(justify="left", width=10)
    row.add_column()
    row.add_column(justify="right", width=6)
    row.add_row(f"[{BABY_PINK}]{label}[/]", bar, f"[{HOT_PINK}]{percent:5.1f}%[/]")
    return row


def render() -> Panel:
    cpu = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()

    body = Table.grid(padding=(0, 0, 1, 0))
    body.add_row(make_bar("CPU", cpu))
    body.add_row(make_bar("Memory", mem.percent))

    return Panel(
        body,
        title=f"[bold {HOT_PINK}]✨ termdash ✨[/]",
        border_style=MAGENTA,
        padding=(1, 2),
    )


if __name__ == "__main__":
    with Live(render(), console=console, refresh_per_second=2) as live:
        try:
            while True:
                time.sleep(0.5)
                live.update(render())
        except KeyboardInterrupt:
            console.print(f"\n[{DEEP_PLUM}]bye bye 💗[/]")
