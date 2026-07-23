# Amazon Logic Transformer

Amazon Logic Transformer is a specialized, production-ready web application designed to normalize, transform, and map Amazon Seller Central reports (B2B and B2C) into a format strictly compatible with Logic ERP systems.

## Features
- **Universal Transformation Engine:** Automatically detects input formats and uses a unified schema.
- **Configurable Plugin Architecture:** Rules for filtering, formatting, trimming, and mapping are isolated in extensible plugins.
- **Rule Engine:** Easily edit `rules.json` to configure invoice prefixes, location constraints, and transaction types without changing code.
- **Real-Time Dry Run:** Preview transformation results (removed rows, missing fields) directly in the UI before generating the final Excel file.

## Tech Stack
- **Backend:** Python 3, FastAPI, Pandas
- **Frontend:** React, Vite, Vanilla CSS

---

## 🚀 Setup & Installation (Production)

### Prerequisites
- Node.js (v18+)
- Python (v3.9+)
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/Monu123a/Halte_data_transformation.git
cd Halte_data_transformation
```

### 2. Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate
   
   # On Windows
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the backend production server using Uvicorn:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

### 3. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install Node modules:
   ```bash
   npm install
   ```
3. Build the frontend for production:
   ```bash
   npm run build
   ```
4. Serve the production build:
   - You can use any static server (like Nginx, Apache, or `serve`).
   - Using `serve`:
     ```bash
     npm install -g serve
     serve -s dist -l 5173
     ```
   *(Note: For local development, you can simply run `npm run dev`)*

---

## 📁 Directory Structure
```
amazon_logic_transformer/
├── backend/
│   ├── app/                # FastAPI application
│   │   ├── api/            # API routing
│   │   ├── engines/        # Core transformation engines
│   │   └── plugins/        # Transformation rule plugins
│   ├── config/             # rules.json and schema mappings
│   ├── lookups/            # Excel files for Account Codes & GST mappings
│   ├── logs/               # Manifests & execution audits
│   └── outputs/            # Final generated Logic ERP Excel files
└── frontend/
    ├── src/
    │   ├── components/     # React UI Components
    │   └── App.jsx         # Main React application
    └── public/
```

## ⚙️ Configuration
The rules governing the transformation can be edited in `backend/config/rules.json`.
- **TransactionFilter**: Whitelists transaction types (e.g., `Shipment`).
- **InvoiceFilter**: Restricts prefixes (e.g., `VSHB`).
- **LocationFilter**: Whitelists states (e.g., `Chandigarh`).
- **AccountCodeMapper**: Connects internal GST codes to Logic ERP Account Codes.

## 🤝 Support
For any questions regarding the transformation logic or adding new plugins, consult the `backend/app/plugins/` directory to create a new `BasePlugin`.
