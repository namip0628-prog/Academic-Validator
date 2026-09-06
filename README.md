# Academic Document Authenticity Validator 📜🔐⛓️

> **Academic Document Authenticity Validator** &mdash; a full-stack system that uses **OCR to extract academic information**, **SHA-256 cryptographic hashing to generate document fingerprints**, and **blockchain-based immutable records to detect document tampering and verify authenticity**.

---

## 🌟 Key Capabilities

### 📄 1. Document Ingestion & Image Preprocessing (OpenCV)
- Drag-and-drop file uploader with live thumbnail preview (PNG, JPG, JPEG, WEBP, TIFF, BMP).
- OpenCV computer vision enhancement pipeline:
  - Resolution normalization and upscaling
  - Grayscale conversion
  - Gaussian denoising to filter out scanner noise and paper texture
  - Automatic deskewing and alignment
  - Otsu binarization for high-contrast character separation

### 🔍 2. Intelligent OCR & Academic Information Extraction
- Optical Character Recognition powered by Tesseract / pytesseract (LSTM Neural Network engine).
- Real-time OCR confidence score meter.
- Regular expression and heuristic parsing for key academic entities:
  - **Student Name** (labeled names, candidate certifications, honorifics)
  - **Student ID / USN** (standard university USNs, Roll Nos, Registration IDs)
  - **Awarding Institution** (universities, colleges, autonomous boards)
  - **Course / Degree** (B.Tech, B.E., M.Tech, B.Sc, M.Sc, specialized majors)
  - **Marks / CGPA / Grade** (CGPA scales, percentages, distinction classifications)
  - **Date of Issue / Passing Year** (calendar dates, passing years, month-year formats)
- Side-by-side visual comparison (Original Upload vs. OpenCV Enhanced binarization).
- Raw OCR text drawer with word/char counters.

### 🔐 3. Cryptographic Fingerprinting (SHA-256)
- Memory-efficient streaming calculation of 64-character SHA-256 cryptographic digest.
- **Tamper Evidence**: Any modification to grades, student names, or individual pixels triggers the Avalanche Effect, completely changing the hash.

### ⛓️ 4. Blockchain Smart Contract Verification (Ethereum / Hardhat)
- **Solidity Smart Contract (`contracts/AcademicValidator.sol`)**:
  - `registerDocument(bytes32 documentHash, metadata...)`: Anchors the document hash, issuer address, block timestamp, and academic metadata.
  - `verifyDocument(bytes32 documentHash)`: Queries on-chain existence and returns authentic record details.
- **Privacy Guarantee**: **Actual document files are NEVER stored on the public blockchain**. Only the 32-byte SHA-256 hash and verifiable metadata are anchored on-chain, eliminating privacy violations and minimizing gas costs.
- **Web3.py Connection Manager (`utils/blockchain.py`)**: Seamlessly connects to a local Ethereum network (Hardhat RPC `http://127.0.0.1:8545`).

### 🛡️ 5. Public Authenticity Verification (Phase 3)
- Dedicated Verification Portal for employers, institutions, and verification agencies:
  - Upload any document $\rightarrow$ computes SHA-256 hash $\rightarrow$ queries blockchain.
  - **✓ Authentic Result**: Green verification badge, matching registration timestamp, issuing institution, student details, and blockchain transaction ID.
  - **✗ Invalid or Modified Result**: Red alert banner warning that no matching record exists on the blockchain (detects modified marks or forged certificates).

### 📊 6. Complete Product Polish (Phase 4)
- 📱 **Responsive Multi-Portal UI**: Tabbed navigation between Institution Issuance, Public Verification, and Audit Ledger.
- ⛓️ **Blockchain Transaction Receipts**: View Transaction Hash, Block Number, Contract Address, and Block Timestamp.
- 📝 **Persistent Audit Ledger & History**: SQLite audit trail tracking all past credential registrations and verifications.
- 📥 **Download Verification Report (PDF)**: Generates a printable, formal Authenticity Certificate (via ReportLab) complete with institutional header, digital verification seal, transaction hash, and tamper analysis.

---

## 🏛️ System Architecture

```
                                [ Web Browser UI ]
                                        │
           ┌────────────────────────────┴────────────────────────────┐
           ▼                                                         ▼
 [ Tab 1: Institution Portal ]                             [ Tab 2: Public Verifier ]
 (Issue & Register Credential)                             (Test Document Authenticity)
           │                                                         │
           └────────────────────────────┬────────────────────────────┘
                                        ▼
                            [ Flask Server: app.py ]
                                        │
        ┌───────────────────────────────┼───────────────────────────────┐
        ▼                               ▼                               ▼
 [ utils/preprocessor.py ]     [ utils/hasher.py ]             [ utils/ocr_engine.py ]
  OpenCV Grayscale, Blur,       Computes SHA-256                Tesseract OCR Extraction
  Deskew & Otsu Binarization    Document Fingerprint            & Neural Confidence Meter
        │                               │                               │
        └───────────────────────────────┼───────────────────────────────┘
                                        │
                                        ▼
                             [ utils/extractor.py ]
                            Regex & Heuristic Academic
                            Entity Extractor (Name, USN...)
                                        │
                                        ▼
                            [ utils/blockchain.py ]
                           Web3.py Connection Manager
                                        │ (JSON-RPC)
                                        ▼
                        [ Hardhat / Ethereum Localnet ]
                             (127.0.0.1:8545)
                                        │
                                        ▼
                          [ AcademicValidator.sol ]
                           - registerDocument(hash, meta)
                           - verifyDocument(hash)
```

---

## 📂 Project Structure

```
Academic-Validator/
├── app.py                      # Flask backend application & REST API routes
├── config.py                   # Centralized configuration (upload caps, Tesseract paths)
├── requirements.txt            # Python dependencies (Flask, OpenCV, Web3, ReportLab, etc.)
├── package.json                # Node.js dependencies for Hardhat
├── hardhat.config.js           # Hardhat network & Solidity compiler configuration
├── records.db                  # Persistent SQLite database for audit activity history
├── README.md                   # Comprehensive project documentation
│
├── contracts/                  # Blockchain Smart Contracts
│   ├── AcademicValidator.sol   # Solidity smart contract
│   └── AcademicValidator.json  # Pre-compiled contract ABI artifact
│
├── scripts/                    # Hardhat automation scripts
│   └── deploy.js               # Contract deployment script
│
├── utils/                      # Modular backend utilities
│   ├── __init__.py             # Exports primary utility functions
│   ├── hasher.py               # SHA-256 cryptographic document fingerprinting
│   ├── preprocessor.py         # OpenCV image enhancement & deskewing pipeline
│   ├── ocr_engine.py           # Tesseract OCR engine & confidence scoring
│   ├── extractor.py            # Academic regex & heuristic field extraction
│   ├── blockchain.py           # Web3.py connection manager & smart contract interface
│   ├── history.py              # SQLite persistent audit history logger
│   └── report_generator.py     # PDF Verification Report / Certificate generator
│
├── static/                     # Frontend static assets
│   ├── css/
│   │   └── style.css           # Modern dark-mode responsive stylesheet
│   └── js/
│       └── main.js             # Tab navigation, drag-and-drop, blockchain interactions
│
├── templates/
│   └── index.html              # Multi-portal dashboard template
│
├── samples/
│   ├── generate_sample.py      # Script to generate synthetic test academic certificates
│   └── sample_degree_certificate.png # Built-in sample academic certificate
│
├── uploads/                    # Temporary directory for uploaded files (.gitignored)
│   └── .gitkeep
│
└── tests/                      # Automated unit and integration test suite
    ├── __init__.py
    ├── test_hasher.py          # Cryptographic hashing & tamper-detection tests
    ├── test_extractor.py       # Academic field parsing tests
    ├── test_blockchain.py      # Smart contract registration & verification tests
    └── test_api.py             # Flask REST API endpoints & PDF download tests
```

---

## 🚀 Quickstart & Setup Guide

### 1. Set Up Python Virtual Environment

```bash
# Clone or navigate to the repository
cd "Academic-Validator"

# Create a Python virtual environment (Python 3.10 - 3.13 recommended)
python -m venv venv

# Activate the virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (Command Prompt):
.\venv\Scripts\activate.bat
# Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. (Optional) Run Hardhat Local Ethereum Node

If you have Node.js installed, you can start the local Hardhat Ethereum node:
```bash
# Install Hardhat packages (first time only)
npm install

# In Terminal 1: Launch local Ethereum network
npx hardhat node

# In Terminal 2: Deploy AcademicValidator contract
npx hardhat run scripts/deploy.js --network localhost
```

> **Note**: Even if Hardhat node is not running, the application features an intelligent fallback ledger that simulates the smart contract faithfully so you can test all issuance, verification, and PDF report workflows immediately out of the box!

### 3. (Optional) Install Tesseract OCR

Tesseract provides optical character recognition:
- **Windows**: `winget install UB-Mannheim.TesseractOCR` (installed to `C:\Program Files\Tesseract-OCR\tesseract.exe`).
- **Ubuntu/Debian**: `sudo apt-get install -y tesseract-ocr`
- **macOS**: `brew install tesseract`

### 4. Run the Flask Web Application

```bash
python app.py
```

Navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Running Automated Tests

Run the complete 17-test automated test suite:

```bash
python -m unittest discover -s tests
```

Test coverage includes:
- **SHA-256 Hashing**: Avalanche effect and 1-byte tamper sensitivity.
- **Academic Extraction**: Parsing student name, USN, university, degree, marks, and dates.
- **Blockchain Verification**: Smart contract registration, duplicate prevention, authentic lookup, and tamper rejection.
- **Flask REST API**: Endpoints (`/api/validate`, `/api/register`, `/api/verify`, `/api/verify-sample`, `/api/history`, `/api/download-report/<id>`).

---

## 📄 License
MIT License &bull; Built for academic document integrity, privacy-first credentialing, and fraud prevention.
