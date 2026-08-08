"""
termdash — a live CPU/memory/process dashboard, pinky winky edition v2 💗
"""

import time
import datetime
import psutil
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

# --- pinky winky palette, low -> high load ---
BABY_PINK = "#FFD1E3"
HOT_PINK = "#FF69B4"
DEEP_RED = "#FF2D6F"
MAGENTA = "#C71585"
DEEP_PLUM = "#8B006D"

BAR_WIDTH = 34
BLOCK = "█"
EMPTY = "░"

START_TIME = time.time()


def color_for(percent: float) -> str:
    if percent < 40:
        return BABY_PINK
    elif percent < 75:
        return HOT_PINK
    return DEEP_RED


def make_bar(label: str, percent: float) -> Text:
    filled = int(BAR_WIDTH * percent / 100)
    color = color_for(percent)
    bar_str = BLOCK * filled + EMPTY * (BAR_WIDTH - filled)

    line = Text()
    line.append(f"{label:<8}", style=f"bold {BABY_PINK}")
    line.append(bar_str, style=color)
    line.append(f"  {percent:5.1f}%", style=f"bold {color}")
    return line


def make_process_table() -> Table:
    table = Table(
        show_header=True,
        header_style=f"bold {MAGENTA}",
        border_style=MAGENTA,
        box=None,
        padding=(0, 1),
    )
    table.add_column("PID", style=BABY_PINK, width=7)
    table.add_column("Process", style="white")
    table.add_column("CPU%", justify="right", width=7)
    table.add_column("Mem%", justify="right", width=7)

    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    procs.sort(key=lambda p: p["cpu_percent"] or 0, reverse=True)

    for p in procs[:5]:
        cpu = p["cpu_percent"] or 0
        mem = p["memory_percent"] or 0
        table.add_row(
            str(p["pid"]),
            (p["name"] or "?")[:20],
            Text(f"{cpu:.1f}", style=color_for(cpu)),
            Text(f"{mem:.1f}", style=color_for(mem)),
        )
    return table


def render() -> Panel:
    cpu = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()
    uptime = str(datetime.timedelta(seconds=int(time.time() - START_TIME)))

    body = Table.grid(padding=(0, 0, 1, 0))
    body.add_row(make_bar("CPU", cpu))
    body.add_row(make_bar("Memory", mem.percent))
    body.add_row(Text(""))
    body.add_row(Text("top processes", style=f"italic {BABY_PINK}"))
    body.add_row(make_process_table())

    return Panel(
        body,
        title=f"[bold {HOT_PINK}]✨ t e r m d a s h ✨[/]",
        subtitle=f"[{DEEP_PLUM}]uptime {uptime}[/]",
        border_style=MAGENTA,
        padding=(1, 2),
    )


if __name__ == "__main__":
    # prime cpu_percent so first reading isn't 0.0
    psutil.cpu_percent(interval=None)
    for p in psutil.process_iter():
        try:
            p.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    with Live(render(), console=console, refresh_per_second=1) as live:
        try:
            while True:
                time.sleep(1)
                live.update(render())
        except KeyboardInterrupt:
            console.print(f"\n[{DEEP_PLUM}]bye bye 💗[/]")
