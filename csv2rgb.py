import argparse
import csv
from pathlib import Path

from rich.console import Console

console = Console()
CHANNELS = ("red", "green", "blue")


def render_csv(input_path: Path) -> int:
	pixel_count = 0

	with input_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
		reader = csv.DictReader(csv_file)
		if reader.fieldnames is None:
			raise ValueError("CSV file is empty or has no header row.")

		headers = [header.strip().casefold() for header in reader.fieldnames]
		if len(headers) != 3 or set(headers) != set(CHANNELS):
			raise ValueError("CSV must have exactly three columns: Red, Green, Blue.")
		if len(set(headers)) != len(headers):
			raise ValueError("CSV column names must be unique.")

		column_names = {
			header.strip().casefold(): header for header in reader.fieldnames
		}
		for row in reader:
			if None in row:
				raise ValueError(f"Too many values on CSV line {reader.line_num}.")

			try:
				channel_bits = tuple(
					row[column_names[channel]].strip() for channel in CHANNELS
				)
			except (AttributeError, TypeError) as error:
				raise ValueError(
					f"Invalid RGB value on CSV line {reader.line_num}; "
					"each channel must be an 8-bit binary value."
				) from error

			if any(
				len(bits) != 8 or any(bit not in "01" for bit in bits)
				for bits in channel_bits
			):
				raise ValueError(
					f"Invalid RGB value on CSV line {reader.line_num}; "
					"each channel must contain exactly 8 bits (0 or 1)."
				)

			red, green, blue = (int(bits, 2) for bits in channel_bits)

			pixel_count += 1
			console.print(
				"██", style=f"rgb({red},{green},{blue})", end=""
			)
			if pixel_count % 20 == 0:
				console.print()

	if pixel_count % 20 != 0:
		console.print()
	return pixel_count


def main() -> None:
	parser = argparse.ArgumentParser(
		description="Render each Red, Green, Blue CSV row as one colored pixel."
	)
	parser.add_argument("input_file", type=Path, help="CSV file containing RGB rows")
	args = parser.parse_args()

	try:
		pixel_count = render_csv(args.input_file)
	except (csv.Error, OSError, ValueError) as error:
		parser.error(str(error))

	console.print(f"Pixels: {pixel_count}")


if __name__ == "__main__":
	main()
