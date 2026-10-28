(() => {
  const canvas = document.getElementById("digit-canvas");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  const predictButton = document.getElementById("digit-predict");
  const clearButton = document.getElementById("digit-clear");
  const eraseButton = document.getElementById("digit-erase");
  const status = document.getElementById("digit-status");
  const prediction = document.getElementById("digit-prediction");
  const confidence = document.getElementById("digit-confidence");
  const probabilities = document.getElementById("digit-probabilities");
  const saveCorrectionButton = document.getElementById("digit-save-correction");
  const correctionCount = document.getElementById("digit-correction-count");
  const digitLabels = document.getElementById("digit-labels");

  let lastPixels = null;
  let selectedLabel = null;
  let drawing = false;
  let erasing = false;
  let hasDrawing = false;

  ctx.fillStyle = "#000";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.lineWidth = 16;
  ctx.strokeStyle = "#fff";

  function position(event) {
    const rect = canvas.getBoundingClientRect();
    return {
      x: (event.clientX - rect.left) * canvas.width / rect.width,
      y: (event.clientY - rect.top) * canvas.height / rect.height,
    };
  }

  function startDrawing(event) {
    event.preventDefault();
    drawing = true;
    hasDrawing = true;
    canvas.setPointerCapture(event.pointerId);

    const point = position(event);
    ctx.beginPath();
    ctx.moveTo(point.x, point.y);
    ctx.lineTo(point.x + 0.1, point.y + 0.1);
    ctx.stroke();
  }

  function draw(event) {
    if (!drawing) return;
    event.preventDefault();

    const point = position(event);
    ctx.strokeStyle = erasing ? "#000" : "#fff";
    ctx.lineTo(point.x, point.y);
    ctx.stroke();
  }

  function stopDrawing() {
    drawing = false;
    ctx.beginPath();
  }

  canvas.addEventListener("pointerdown", startDrawing);
  canvas.addEventListener("pointermove", draw);
  canvas.addEventListener("pointerup", stopDrawing);
  canvas.addEventListener("pointercancel", stopDrawing);
  canvas.addEventListener("lostpointercapture", stopDrawing);

  clearButton.addEventListener("click", () => {
    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.beginPath();

    hasDrawing = false;
    prediction.textContent = "?";
    confidence.textContent = "Your prediction will appear here.";
    probabilities.replaceChildren();
    status.textContent = "Grid cleared. Draw a digit to get started.";
  });

  eraseButton.addEventListener("click", () => {
    erasing = !erasing;
    eraseButton.textContent = `Eraser: ${erasing ? "on" : "off"}`;
  });

  predictButton.addEventListener("click", async () => {
    if (!hasDrawing) {
      status.textContent = "Draw a digit first.";
      return;
    }

    predictButton.disabled = true;
    status.textContent = "Recognising…";

    try {
      
      const smallCanvas = document.createElement("canvas");
      smallCanvas.width = 28;
      smallCanvas.height = 28;

      const smallCtx = smallCanvas.getContext("2d");

      // Start with a black 28×28 image.
      smallCtx.fillStyle = "#000";
      smallCtx.fillRect(0, 0, 28, 28);

      // Find the bounding box of the drawn digit.
      const source = ctx.getImageData(0, 0, canvas.width, canvas.height);

      let minX = canvas.width;
      let minY = canvas.height;
      let maxX = -1;
      let maxY = -1;

      for (let y = 0; y < canvas.height; y++) {
        for (let x = 0; x < canvas.width; x++) {
          const index = (y * canvas.width + x) * 4;

          if (source.data[index] > 20) {
            minX = Math.min(minX, x);
            minY = Math.min(minY, y);
            maxX = Math.max(maxX, x);
            maxY = Math.max(maxY, y);
          }
        }
      }

      if (maxX < 0) {
        status.textContent = "Draw a digit first.";
        predictButton.disabled = false;
        return;
      }

      // Crop the digit and fit it inside a 20×20 area.
      const width = maxX - minX + 1;
      const height = maxY - minY + 1;
      const scale = 20 / Math.max(width, height);
      const targetWidth = width * scale;
      const targetHeight = height * scale;

      // Centre the digit on the 28×28 image.
      const offsetX = (28 - targetWidth) / 2;
      const offsetY = (28 - targetHeight) / 2;

      smallCtx.imageSmoothingEnabled = true;
      smallCtx.imageSmoothingQuality = "high";

      smallCtx.drawImage(
        canvas,
        minX, minY, width, height,
        offsetX, offsetY, targetWidth, targetHeight
      );

      const rgba = smallCtx.getImageData(0, 0, 28, 28).data;
      const pixels = [];


      for (let i = 0; i < rgba.length; i += 4) {
        pixels.push(rgba[i] / 255);
      }

      lastPixels = pixels;
      selectedLabel = null;
      saveCorrectionButton.disabled = false;

      digitLabels.querySelectorAll("button").forEach((button) => {
        button.classList.remove("selected");
      });

      const response = await fetch("/api/digit-recogniser/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pixels }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || "Prediction failed.");
      }

      prediction.textContent = result.prediction;
      confidence.textContent = `Model confidence: ${result.confidence.toFixed(2)}%`;
      status.textContent = "Prediction complete.";

      probabilities.replaceChildren();

      result.probabilities.forEach((value, digit) => {
        const row = document.createElement("div");
        row.className = "digit-probability";

        const label = document.createElement("span");
        label.textContent = digit;

        const bar = document.createElement("div");
        bar.className = "digit-bar";

        const fill = document.createElement("div");
        fill.className = "digit-bar-fill";
        fill.style.width = `${value}%`;
        bar.appendChild(fill);

        const percent = document.createElement("span");
        percent.textContent = `${value.toFixed(1)}%`;

        row.append(label, bar, percent);
        probabilities.appendChild(row);
      });
    } catch (error) {
      status.textContent = error.message || "Something went wrong.";
    } finally {
      predictButton.disabled = false;
    }
  });


async function refreshCorrectionCount() {
  try {
    const response = await fetch("/api/digit-recogniser/corrections");
    const result = await response.json();

    if (!response.ok) throw new Error("Could not load saved examples.");

    correctionCount.textContent = `Saved corrections: ${result.count}`;
  } catch {
    correctionCount.textContent = "Could not load saved examples.";
  }
}

digitLabels.querySelectorAll("button").forEach((button) => {
  button.addEventListener("click", () => {
    selectedLabel = Number(button.dataset.digit);

    digitLabels.querySelectorAll("button").forEach((item) => {
      item.classList.toggle("selected", item === button);
    });
  });
});

saveCorrectionButton.addEventListener("click", async () => {
  if (!lastPixels) {
    status.textContent = "Recognise a digit before saving a correction.";
    return;
  }

  if (selectedLabel === null) {
    status.textContent = "Select the correct digit first.";
    return;
  }

  saveCorrectionButton.disabled = true;
  status.textContent = "Saving correction…";

  try {
    const response = await fetch("/api/digit-recogniser/correct", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        pixels: lastPixels,
        label: selectedLabel,
      }),
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || "Could not save correction.");
    }

    status.textContent = `Correction saved as ${selectedLabel}.`;
    correctionCount.textContent = `Saved corrections: ${result.count}`;
    lastPixels = null;
    selectedLabel = null;

    digitLabels.querySelectorAll("button").forEach((button) => {
      button.classList.remove("selected");
    });
  } catch (error) {
    status.textContent = error.message || "Could not save correction.";
  } finally {
    saveCorrectionButton.disabled = false;
  }
});

refreshCorrectionCount();


})();
