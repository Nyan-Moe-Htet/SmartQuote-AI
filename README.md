# SmartQuote AI

## Overview
SmartQuote AI is an AI-powered quotation analysis tool designed to help users review supplier quotations, compare prices, and make more informed purchasing decisions.

## Features
- AI-powered quotation analysis using GLM-5.3 through RunPod.
- Supplier quotation review and information extraction.
- Quotation comparison to support purchasing decisions.
- Purchase workflow support.

## Technology Stack
- **Programming Language:** Python
- **AI Model:** GLM-5.3
- **AI API Provider:** RunPod
- **Application:** Python-based SmartQuote AI application

## Setup Instructions

### 1. Clone the repository
```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd YOUR_REPOSITORY_FOLDER
```

### 2. Install dependencies
Install the dependencies listed in `requirements.txt` using your Python environment.

```bash
pip install -r requirements.txt
```

If your environment uses a managed Python setup, use the appropriate virtual environment or package manager.

### 3. Configure the API key
Set the `RUNPOD_API_KEY` environment variable using your environment's secret manager. Do not put API keys directly in the source code or commit them to GitHub.

### 4. Run the application
Run the application using the project's configured entry point. For example:

```bash
python app.py
```

## Security
API credentials should be stored securely as environment variables or platform secrets. Never commit secret keys to version control.

## Project Purpose
SmartQuote AI aims to simplify supplier quotation review and comparison through AI-assisted analysis.
