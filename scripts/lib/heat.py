"""Heatmap geometry shared by the website (inline SVG) and the README card."""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


@dataclass
class Cell:
    date: str
    count: int
    level: int
    col: int
    row: int


def levels_for(counts: list[int]) -> tuple[int, int, int]:
    """Quartile thresholds over non-zero days so sparse profiles still show contrast."""
    nz = sorted(c for c in counts if c > 0)
    if not nz:
        return (1, 2, 3)

    def q(p: float) -> int:
        return nz[min(len(nz) - 1, int(p * (len(nz) - 1) + 0.5))]

    return (q(0.25), q(0.5), q(0.75))


def level(count: int, th: tuple[int, int, int]) -> int:
    if count <= 0:
        return 0
    if count <= th[0]:
        return 1
    if count <= th[1]:
        return 2
    if count <= th[2]:
        return 3
    return 4


def build(days: list[dict]) -> tuple[list[Cell], int, list[tuple[int, str]]]:
    """Return (cells, column_count, month_labels[(col, 'Sep')])."""
    if not days:
        return [], 0, []
    th = levels_for([d["count"] for d in days])
    first = dt.date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # Sunday-first rows, like GitHub
    cells: list[Cell] = []
    for i, d in enumerate(days):
        idx = i + offset
        cells.append(Cell(d["date"], d["count"], level(d["count"], th), idx // 7, idx % 7))
    cols = cells[-1].col + 1

    labels: list[tuple[int, str]] = []
    last_month = -1
    seen_cols: set[int] = set()
    for c in cells:
        if c.col in seen_cols:
            continue
        seen_cols.add(c.col)
        month = int(c.date[5:7])
        if month != last_month:
            labels.append((c.col, MONTHS[month - 1]))
            last_month = month
    # drop a first label that would collide with the next one
    if len(labels) > 1 and labels[1][0] - labels[0][0] < 3:
        labels.pop(0)
    return cells, cols, labels


def tip(cell: Cell) -> str:
    y, m, d = cell.date.split("-")
    noun = "contribution" if cell.count == 1 else "contributions"
    n = "No contributions" if cell.count == 0 else f"{cell.count} {noun}"
    return f"{n} on {d}.{m}.{y}"
