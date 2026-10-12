import sys
from pathlib import Path
from rich.console import Console

console = Console()


def rgbconv(rbits, gbits, bbits):
    return (int(rbits, 2), int(gbits, 2), int(bbits, 2))


if len(sys.argv) > 1:
    path = Path(sys.argv[1])
    rawbits = "".join(f"{byte:08b}" for byte in path.read_bytes())
else:
    console.print("[yellow]input raw binary: (paste one line or many lines, then press Ctrl+D to finish)[/yellow]")
    console.print("[yellow]Note: a single terminal line is limited by your shell, so very large dumps should be split across lines or use a .bin file.[/yellow]")

    if sys.stdin.isatty():
        rawbits = ""
        while True:
            try:
                line = sys.stdin.readline()
            except KeyboardInterrupt:
                break
            if not line:
                break
            rawbits += "".join(ch for ch in line if ch in "01")
    else:
        rawbits = "".join(ch for ch in sys.stdin.read() if ch in "01")

if not rawbits:
    console.print("[bold red]No binary data entered.[/bold red]")
    raise SystemExit

remainder = len(rawbits) % 24
if remainder != 0:
    missing = 24 - remainder
    console.print(f"[bold red]Invalid length: {len(rawbits)} bits. Needs to be a multiple of 24.[/bold red]")
    console.print(f"[bold red]Off by {remainder} bits; add {missing} more bit(s) or remove {remainder} bit(s).[/bold red]")
    raise SystemExit

pixels = []

for i in range(0, len(rawbits), 24):
    chunk = rawbits[i:i + 24]
    r = chunk[:8]
    g = chunk[8:16]
    b = chunk[16:24]

    rr, gg, bb = rgbconv(r, g, b)
    pixels.append(f"rgb({rr},{gg},{bb})")

for index, color in enumerate(pixels, start=1):
    console.print("██", style=color, end="")
    if index % 20 == 0:
        console.print()

if len(pixels) % 20 != 0:
    console.print()

