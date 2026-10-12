
from pathlib import Path

# Ask for filenames
input_name = input("Enter the input filename (e.g. bits.txt): ").strip()
output_name = input("Enter the output filename (e.g. image.bin): ").strip()

input_path = Path(input_name)
output_path = Path(output_name)

# Check that the input file exists
if not input_path.is_file():
    raise FileNotFoundError(f"Input file not found: {input_name}")

# Prevent accidentally overwriting the input file
if input_path.resolve() == output_path.resolve():
    raise ValueError("Input and output filenames must be different.")

# Read the bits from the input file
text = input_path.read_text()
bits = "".join(text.split())

# Validate the input
if not bits or any(bit not in "01" for bit in bits):
    raise ValueError("Input file must contain only 0s and 1s.")

if len(bits) % 8 != 0:
    raise ValueError(
        f"You have {len(bits)} bits. "
        "The total must be divisible by 8."
    )

# Pack every 8 bits into one byte
data = bytes(
    int(bits[i:i + 8], 2)
    for i in range(0, len(bits), 8)
)

# Create the binary file
output_path.write_bytes(data)

print(f"\nBits: {len(bits)}")
print(f"Bytes: {len(data)}")
print(f"Created: {output_path}")

# Delete the original file after successful conversion
input_path.unlink()
print(f"Deleted: {input_path}")