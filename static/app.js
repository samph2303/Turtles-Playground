const panel = document.querySelector("#result-panel");
const title = document.querySelector("#result-title");
const message = document.querySelector("#result-message");
const textResult = document.querySelector("#text-result");
const pixelInfo = document.querySelector("#pixel-info");
const pixelGrid = document.querySelector("#pixel-grid");
const downloadLink = document.querySelector("#download-result");

let activeDownloadUrl = null;

function clearOutput() {
  if (activeDownloadUrl) URL.revokeObjectURL(activeDownloadUrl);
  activeDownloadUrl = null;

  panel.hidden = true;
  textResult.hidden = true;
  pixelInfo.hidden = true;
  pixelGrid.hidden = true;
  downloadLink.hidden = true;

  textResult.textContent = "";
  pixelGrid.replaceChildren();
  downloadLink.removeAttribute("href");
}

document.querySelector("#clear-result").addEventListener("click", clearOutput);

document.querySelectorAll(".file-picker input").forEach(input => {
  input.addEventListener("change", () => {
    const label = input.closest(".file-picker").querySelector(".file-name");
    const files = Array.from(input.files);

    if (files.length === 0) {
      label.textContent = input.multiple ? "Choose image files" : "Choose file";
    } else if (files.length === 1) {
      label.textContent = files[0].name;
    } else {
      label.textContent = `${files.length} images selected`;
    }
  });
});

document.querySelectorAll(".tool-form").forEach(form => {
  form.addEventListener("submit", async event => {
    event.preventDefault();

    const fileInput = form.querySelector('input[type="file"]');
    const files = Array.from(fileInput.files);

    if (files.length === 0) return;

    const toolId = form.dataset.tool;
    const button = form.querySelector("button");
    const isImagePdf = toolId === "img2pdf";

    button.disabled = true;
    button.textContent = "Processing…";

    panel.hidden = false;
    title.textContent = form.closest(".tool-card").querySelector("h3").textContent;
    message.textContent = isImagePdf
      ? `Preparing ${files.length} image(s) for PDF conversion…`
      : `Working on ${files[0].name}…`;

    textResult.hidden = true;
    pixelInfo.hidden = true;
    pixelGrid.hidden = true;
    downloadLink.hidden = true;
    pixelGrid.replaceChildren();

    try {
      const formData = new FormData();

      if (isImagePdf) {
        files.forEach(file => formData.append("files", file));
      } else {
        formData.append("file", files[0]);
      }

      const response = await fetch(`/run/${toolId}`, {
        method: "POST",
        body: formData
      });

      const contentType = response.headers.get("content-type") || "";

      if (!contentType.includes("application/json")) {
        if (!response.ok) {
          throw new Error("The server could not complete the conversion.");
        }

        const blob = await response.blob();

        if (activeDownloadUrl) URL.revokeObjectURL(activeDownloadUrl);
        activeDownloadUrl = URL.createObjectURL(blob);

        downloadLink.href = activeDownloadUrl;

        if (toolId === "img2pdf") {
          downloadLink.download = "images.pdf";
        } else if (toolId === "bin2txt") {
          downloadLink.download = files[0].name.replace(/\.bin$/i, "") + ".txt";
        } else if (toolId === "bin2csv") {
          downloadLink.download = files[0].name.replace(/\.bin$/i, "") + ".csv";
        } else {
          downloadLink.download = files[0].name.replace(/\.txt$/i, "") + ".bin";
        }

        downloadLink.hidden = false;
        message.textContent = isImagePdf
          ? `PDF created from ${files.length} image(s). Select the download link below.`
          : "Conversion complete. Your original upload was not changed.";

        return;
      }

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || "Something went wrong.");
      }

      if (result.type === "text") {
        textResult.textContent = result.text;
        textResult.hidden = false;
        message.textContent = `${result.count.toLocaleString()} bits.`;
      } else if (result.type === "rgb") {
        pixelInfo.textContent = `${result.count.toLocaleString()} RGB pixels`;
        pixelInfo.hidden = false;

        // Limit the preview so large uploads do not freeze the browser.
        const pixels = result.pixels.slice(0, 10000);
        const fragment = document.createDocumentFragment();

        for (const [r, g, b] of pixels) {
          const pixel = document.createElement("div");
          pixel.className = "pixel";
          pixel.style.backgroundColor = `rgb(${r}, ${g}, ${b})`;
          pixel.title = `RGB(${r}, ${g}, ${b})`;
          fragment.appendChild(pixel);
        }

        pixelGrid.appendChild(fragment);
        pixelGrid.hidden = false;

        message.textContent = result.count > pixels.length
          ? `Showing the first ${pixels.length.toLocaleString()} pixels to keep the browser responsive.`
          : "RGB preview generated.";
      }
    } catch (error) {
      message.textContent = error.message;
    } finally {
      button.disabled = false;
      button.innerHTML = 'Run tool <span>↗</span>';
    }
  });
});