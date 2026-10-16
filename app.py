

from pathlib import Path
from tempfile import TemporaryDirectory
import csv
import io
import subprocess
import sys

from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

SCRIPTS_DIR = Path(__file__).resolve().parent
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024  # 32 MB upload limit

TOOLS = [
    {
        "id": "datadump",
	    "category": "rgb",
        "name": "BIN → RGB Pixels",
        "description": "Visualise a binary file as RGB pixels.",
        "accept": ".bin",
    },
    {
        "id": "txt2bin",
	    "category": "converter",
        "name": "TXT → BIN",
        "description": "Convert a text file of binary bits into a binary file.",
        "accept": ".txt",
    },
    {
        "id": "bin2txt",
	    "category": "converter",
        "name": "BIN → TXT",
        "description": "Convert each byte into eight text bits.",
        "accept": ".bin",
    },
    {
        "id": "bin2bits",
	    "category": "converter",
        "name": "BIN → Bits",
        "description": "Display the binary contents of a file.",
        "accept": ".bin",
    },
    {
        "id": "csv2rgb",
	    "category": "rgb",
        "name": "CSV → RGB Pixels",
        "description": "Visualise RGB values from a CSV file.",
        "accept": ".csv",
    },
    {
        "id": "bin2csv",
	    "category": "converter",
        "name": "BIN → CSV",
        "description": "Convert every three bytes into an RGB CSV row.",
        "accept": ".bin",
    },
    {
        "id": "img2pdf",
        "category": "converter",
        "name": "Images → PDF",
        "description": "Combine multiple images into one multi-page PDF.",
        "accept": ".png,.jpg,.jpeg,.webp,.bmp,.gif,.tif,.tiff",
        "multiple": True,
    },
]


def rgb_from_binary(data):
    if not data:
        raise ValueError("The uploaded file is empty.")

    if len(data) % 3 != 0:
        raise ValueError(
            "The file size must be divisible by 3 bytes "
            "to form complete RGB pixels."
        )

    return [
        (data[i], data[i + 1], data[i + 2])
        for i in range(0, len(data), 3)
    ]


def rgb_from_csv(data):
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError("The CSV file must be UTF-8 text.")

    reader = csv.DictReader(io.StringIO(text))

    if not reader.fieldnames:
        raise ValueError("The CSV file has no header row.")

    headers = {h.strip().lower(): h for h in reader.fieldnames if h}
    if not all(k in headers for k in ("red", "green", "blue")):
        raise ValueError("CSV headers must contain Red, Green and Blue.")

    pixels = []

    for row_number, row in enumerate(reader, start=2):
        channels = []

        for name in ("red", "green", "blue"):
            bits = (row.get(headers[name]) or "").strip()

            if len(bits) != 8 or any(bit not in "01" for bit in bits):
                raise ValueError(
                    f"Row {row_number}: {name} must be exactly 8 binary bits."
                )

            channels.append(int(bits, 2))

        pixels.append(tuple(channels))

    if not pixels:
        raise ValueError("The CSV contains no pixel rows.")

    return pixels


@app.get("/")
def index():
    return render_template("index.html", tools=TOOLS)


@app.post("/run/<tool_id>")
def run_tool(tool_id):
    tool = next((item for item in TOOLS if item["id"] == tool_id), None)

    if tool is None:
        return jsonify(error="Unknown tool."), 404

    if tool_id == "img2pdf":
        uploads = [
            item for item in request.files.getlist("files")
            if item and item.filename
        ]

        if not uploads:
            return jsonify(error="Choose one or more images first."), 400

        try:
            with TemporaryDirectory(prefix="toolbox-") as temp:
                temp_dir = Path(temp)
                image_paths = []

                for index, image_upload in enumerate(uploads, start=1):
                    image_filename = secure_filename(image_upload.filename)

                    if not image_filename:
                        raise ValueError("One of the image filenames is invalid.")

                    image_path = temp_dir / f"{index:03d}_{image_filename}"
                    image_path.write_bytes(image_upload.read())
                    image_paths.append(image_path)

                output_path = temp_dir / "images.pdf"

                result = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPTS_DIR / "img2pdf.py"),
                        *[str(path) for path in image_paths],
                        "--output",
                        str(output_path),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                if result.returncode != 0 or not output_path.exists():
                    error = result.stderr.strip() or result.stdout.strip()
                    raise ValueError(error or "Image to PDF conversion failed.")

                return send_file(
                    io.BytesIO(output_path.read_bytes()),
                    as_attachment=True,
                    download_name="images.pdf",
                    mimetype="application/pdf",
                )

        except subprocess.TimeoutExpired:
            return jsonify(
                error="The image conversion took too long to finish."
            ), 408
        except (ValueError, OSError) as exc:
            return jsonify(error=str(exc)), 400

    upload = request.files.get("file")
    if not upload or not upload.filename:
        return jsonify(error="Choose a file first."), 400

    filename = secure_filename(upload.filename)
    if not filename:
        return jsonify(error="Invalid filename."), 400

    data = upload.read()

    try:
        if tool_id == "datadump":
            pixels = rgb_from_binary(data)
            return jsonify(type="rgb", pixels=pixels, count=len(pixels))

        if tool_id == "csv2rgb":
            pixels = rgb_from_csv(data)
            return jsonify(type="rgb", pixels=pixels, count=len(pixels))

        with TemporaryDirectory(prefix="toolbox-") as temp:
            temp_dir = Path(temp)
            input_path = temp_dir / filename
            input_path.write_bytes(data)

            if tool_id == "bin2bits":
                bits = "".join(f"{byte:08b}" for byte in data)
                return jsonify(type="text", text=bits, count=len(bits))

            if tool_id == "txt2bin":
                # Run the existing interactive script against a temporary copy.
                # Its input-deletion behaviour cannot delete the user's original.
                output_path = temp_dir / "converted.bin"
                result = subprocess.run(
                    [sys.executable, str(SCRIPTS_DIR / "txt2bin.py")],
                    input=f"{input_path.name}\n{output_path.name}\n",
                    text=True,
                    capture_output=True,
                    cwd=temp_dir,
                    timeout=30,
                )
                if result.returncode != 0 or not output_path.exists():
                    message = result.stderr.strip() or result.stdout.strip()
                    raise ValueError(message or "TXT to BIN conversion failed.")
                return send_file(
                    output_path,
                    as_attachment=True,
                    download_name=Path(filename).stem + ".bin",
                    mimetype="application/octet-stream",
                )

            script_map = {
                "bin2txt": "bin2txt.py",
                "bin2csv": "bin2csv.py",
            }

            script = SCRIPTS_DIR / script_map[tool_id]
            output_ext = ".txt" if tool_id == "bin2txt" else ".csv"
            output_path = temp_dir / (Path(filename).stem + output_ext)

            result = subprocess.run(
                [sys.executable, str(script), str(input_path), str(output_path)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0 or not output_path.exists():
                message = result.stderr.strip() or result.stdout.strip()
                raise ValueError(message or "Conversion failed.")

            mimetype = "text/plain" if output_ext == ".txt" else "text/csv"
            return send_file(
                output_path,
                as_attachment=True,
                download_name=output_path.name,
                mimetype=mimetype,
            )

    except subprocess.TimeoutExpired:
        return jsonify(error="The script took too long to finish."), 408
    except (ValueError, OSError) as exc:
        return jsonify(error=str(exc)), 400


@app.errorhandler(413)
def too_large(_error):
    return jsonify(error="File too large. Maximum upload size is 32 MB."), 413


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
