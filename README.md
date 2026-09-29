
# 🌿 Parsely Studio

**Herbarium Specimen Digitization Platform**

Parsely Core + Studio help herbaria, museums, and researchers digitize large volumes of specimen labels with the latest AI models in a clean, intuitive workflow. Parsely Core is the name of the underlying code and Parsely Studio is the name of the web application.

🔗 **Parsely Studio version 1.0.0: [parselystudio.com](https://parselystudio.com)**

> For local use, see the [Getting Started](#-getting-started) section below.
>
> Protocol for reporting the use of Parsely Studio in specimen digitization: "Parsely Studio (version 1.0.0) and its underlying technology (Google Gemini Pro 2.5 and Google Cloud Vision) was used to transcribe this specimen."

<img width="468" height="48" alt="image" src="https://github.com/user-attachments/assets/87376d6b-4874-450a-8672-aef40ed1b976" />


## ✨ What it does

Given a set of specimen label images, Parsely can:

- **Preprocess images** — crop, deskew, and auto-rotate to prepare for AI extraction.  
- **Run OCR** — call Google Vision OCR (or other engines) to extract text from images.  
- **Extract structured data** — send OCR + images to an LLM via OpenRouter (currently Gemini 2.5 Pro) to parse into specimen fields (e.g., catalog number, taxon, collector) according to Darwin Core schema.
- **Edit + review** — provide a simple web UI for curators to view images, edit predictions, and export results to CSV.  

## 🚀 Getting Started

### 1. Prerequisites

Make sure the following are installed on your system:

- **Python 3.11**
- **Node.js 20** and `npm`
- System packages required by OpenCV and HEIF support. On Debian/Ubuntu:

  ```bash
  sudo apt-get install -y libgl1 libglib2.0-0 libheif1 libde265-0
  ```

If you don’t have Poetry yet:

```bash
pip3 install poetry
```

### 2. Clone and install

```bash
git clone https://github.com/<your-user>/herbarium-processor.git
cd herbarium-processor
poetry install
cd src/herbarium_processor/web/frontend
npm ci
cd -
```

### 3. Configure environment

Create a `.env` file in the project root with:

```bash
OPENROUTER_API_KEY=your_openrouter_key_here
GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
```

Optional: install pre-commit hooks (we use this to strip notebook metadata):

```bash
poetry run pre-commit install
```

## 🖥️ Usage

### Option A: Web App

1. Start the server:
     ```bash
     poetry run dev
     ```
2. Open the frontend at [http://localhost:5173/](http://localhost:5173/)
3. The API server runs at [http://localhost:8000/](http://localhost:8000/)
4. Upload images → edit predictions → finalize CSV.
5. Processed files are stored in `/tmp`.

### Option B: Notebook

1. Open [`notebooks/herbarium_processor.ipynb`](notebooks/herbarium_processor.ipynb).
2. Point it to a directory of images (`img/bucket`).

## 📜 License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.
See [LICENSE](LICENSE) for details.
See [NOTICE](NOTICE) and [COPYRIGHT](COPYRIGHT) for attribution and trademark information.
