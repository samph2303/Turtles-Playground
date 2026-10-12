import argparse
import csv
from pathlib import Path


def convert_binary_to_csv(input_path: Path, output_path: Path) -> int:
	if not input_path.is_file():
		raise FileNotFoundError(f"Input file not found: {input_path}")
	if input_path.resolve() == output_path.resolve():
		raise ValueError("Input and output filenames must be different.")
	if input_path.stat().st_size % 3 != 0:
		raise ValueError("Input file size must be divisible by 3 bytes for complete RGB pixels.")

	pixel_count = 0
	chunk_size = 64 * 1024 - (64 * 1024) % 3
	with input_path.open("rb") as binary_file, output_path.open(
		"w", encoding="utf-8", newline=""
	) as csv_file:
		writer = csv.writer(csv_file, lineterminator="\n")
		writer.writerow(("Red", "Green", "Blue"))

		while chunk := binary_file.read(chunk_size):
			for offset in range(0, len(chunk), 3):
				writer.writerow(
					f"{byte:08b}" for byte in chunk[offset:offset + 3]
				)
				pixel_count += 1

	return pixel_count


def main() -> None:
	parser = argparse.ArgumentParser(
		description="Convert each 3 bytes in a binary file into one RGB CSV row."
	)
	parser.add_argument("input_file", type=Path, help="input .bin file")
	parser.add_argument(
		"output_file",
		type=Path,
		nargs="?",
		help="output .csv file (defaults to the input filename with a .csv extension)",
	)
	args = parser.parse_args()
	output_path = args.output_file or args.input_file.with_suffix(".csv")

	try:
		pixel_count = convert_binary_to_csv(args.input_file, output_path)
	except (FileNotFoundError, OSError, ValueError) as error:
		parser.error(str(error))

	print(f"Wrote {pixel_count} RGB pixels to {output_path}")


if __name__ == "__main__":
	main()
