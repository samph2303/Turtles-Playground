import argparse
from pathlib import Path

from PIL import Image, UnidentifiedImageError


def convert_images(image_paths: list[Path], output_path: Path) -> None:
	if output_path.resolve() in {path.resolve() for path in image_paths}:
		raise ValueError("The output PDF must not overwrite an input image.")

	pages: list[Image.Image] = []
	try:
		for image_path in image_paths:
			try:
				with Image.open(image_path) as image:
					rgba_image = image.convert("RGBA")
					page = Image.new("RGB", rgba_image.size, "white")
					page.paste(rgba_image, mask=rgba_image.getchannel("A"))
					pages.append(page)
			except (OSError, UnidentifiedImageError) as error:
				raise ValueError(f"Could not read image '{image_path}': {error}") from error

		if not pages:
			raise ValueError("Provide at least one image.")

		pages[0].save(
			output_path,
			format="PDF",
			save_all=True,
			append_images=pages[1:],
		)
	finally:
		for page in pages:
			page.close()


def main() -> None:
	parser = argparse.ArgumentParser(
		description="Combine multiple images into one PDF file."
	)
	parser.add_argument(
		"images",
		type=Path,
		nargs="+",
		help="Image files to add, in PDF page order",
	)
	parser.add_argument(
		"-o",
		"--output",
		type=Path,
		default=Path("output.pdf"),
		help="Output PDF path (default: output.pdf)",
	)
	args = parser.parse_args()

	try:
		convert_images(args.images, args.output)
	except (OSError, ValueError) as error:
		parser.error(str(error))

	print(f"Created {args.output}")


if __name__ == "__main__":
	main()
