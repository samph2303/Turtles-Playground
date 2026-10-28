# Turtle's Playground

A local web-based toolbox built with Python and Flask, featuring file converters, an RGB visualiser, and a handwritten digit recogniser powered by a PyTorch neural network.

Everything runs locally on your computer through your web browser.

## Features

- **File converters** — tools for converting between supported file formats.
- **RGB visualiser** — explore image pixel data and RGB colour values.
- **Digit recogniser** — draw a digit and let a trained neural network predict what it is.
- **Correction collection** — save correctly labelled drawings to build a dataset for future model training.
- **Local storage** — saved digit corrections remain on your machine.

## Requirements

- Python 3.12 or newer, provided your installed PyTorch version supports it.
- Git
- An internet connection for the initial dependency installation.

The digit recogniser runs on the CPU, so a dedicated graphics card is not required.

## Installation

### Linux

These instructions work on most Linux distributions, including Fedora and Ubuntu.

**1. Install Git and Python**

Fedora:

```bash
sudo dnf install git python3 python3-pip
```

Ubuntu:

```bash
sudo apt update
sudo apt install git python3 python3-venv python3-pip
```

**2. Clone the repository**

```bash
git clone https://github.com/samph2303/rgb-webapp.git
cd rgb-webapp
```

**3. Create a virtual environment**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**4. Install dependencies**

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**5. Start the application**

```bash
python -m flask --app app run
```

### Windows

**1. Install Python and Git**

- Install Python from [python.org](https://www.python.org/downloads/).
- Install Git from [git-scm.com](https://git-scm.com/downloads).

During Python installation, enable **Add Python to PATH** if that option is available.

**2. Clone the repository**

Open PowerShell and run:

```powershell
git clone https://github.com/samph2303/rgb-webapp.git
cd rgb-webapp
```

**3. Create a virtual environment**

```powershell
py -3 -m venv .venv
```

**4. Activate the environment**

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, you can use the virtual environment's Python directly instead:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If activation worked, install the dependencies with:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**5. Start the application**

```powershell
python -m flask --app app run
```

If the application starts successfully, the terminal will display a local address.

## Using the application

Open your browser and visit:

**http://127.0.0.1:5000**

Keep the terminal running while you use the application. To stop the server, press `Ctrl+C`.

## Digit recogniser

The digit recogniser uses a neural network trained on the MNIST handwritten digit dataset.

1. Open the Digit Recogniser page.
2. Draw a digit on the canvas.
3. Select **Recognise digit** to see the prediction and class probabilities.
4. If you want to save the example, select its correct label and save the correction — even if the prediction was already correct.

Saved corrections are stored in a local SQLite database. They are collected for possible future training and **do not automatically change the model**.

The pre-trained model is included in the repository, so you do not need to train it before running the application.

## Training the model

The repository includes `train_digit_model.py` for training the digit recognition model.

Training requires PyTorch and torchvision, and downloading MNIST may require an internet connection. Training a new model is separate from collecting corrections in the web application.

## Project structure

```text
rgb-webapp/
├── app.py
├── train_digit_model.py
├── models/
│   └── digit_model_28.pth
├── static/
│   ├── style.css
│   ├── app.js
│   └── digit-recogniser.js
├── templates/
│   └── index.html
├── requirements.txt
└── .gitignore
```

The application may create `digit_corrections.db` locally when the digit correction feature is first used.

## Notes

- Keep the virtual environment active when running the application, or invoke its Python executable directly.
- Do not commit your local correction database or virtual environment to Git.
- The Flask development server is intended for local use, not as a production deployment.

## License

See the repository for licensing information.
