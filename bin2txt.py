import argparse
from pathlib import Path


def convert_binary_to_text(input_path: Path, output_path: Path) -> int:
	if not input_path.is_file():
		raise FileNotFoundError(f"Input file not found: {input_path}")
	if input_path.resolve() == output_path.resolve():
		raise ValueError("Input and output filenames must be different.")

	total_bits = 0
	with input_path.open("rb") as binary_file, output_path.open(
		"w", encoding="ascii", newline=""
	) as text_file:
		while chunk := binary_file.read(64 * 1024):
			bit_text = "".join(f"{byte:08b}" for byte in chunk)
			text_file.write(bit_text)
			total_bits += len(bit_text)

	return total_bits


def main() -> None:
	parser = argparse.ArgumentParser(
		description="Write every bit from a binary file as 0s and 1s in a text file."
	)
	parser.add_argument("input_file", type=Path, help="input .bin file")
	parser.add_argument(
		"output_file",
		type=Path,
		nargs="?",
		help="output .txt file (defaults to the input filename with a .txt extension)",
	)
	args = parser.parse_args()
	output_path = args.output_file or args.input_file.with_suffix(".txt")

	try:
		total_bits = convert_binary_to_text(args.input_file, output_path)
	except (FileNotFoundError, OSError, ValueError) as error:
		parser.error(str(error))

	print(f"Wrote {total_bits} bits to {output_path}")


if __name__ == "__main__":
	main()
