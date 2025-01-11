# CUFE Document Download and Classification System

This repository provides a system for classifying and processing Colombian Electronic Invoice (CUFE) documents. It consists of two main components:

1. **Backend Script** (`backend.py`): Handles the core functionality, including CUFE extraction, PDF classification based on payment type, and file relocation.
2. **Graphical User Interface (GUI)** (`gui.py`): A user-friendly interface for selecting files and directories, and triggering the classification process.

---

## Features

### Backend (`backend.py`)
- **CUFE Extraction**: Reads Excel files to extract CUFE codes associated with electronic invoices.
- **PDF Analysis**: Scans PDF files to determine the payment type ("Contado" or "Crédito").
- **File Classification and Relocation**: Organizes PDFs into subdirectories based on payment type.
- **Integration with Selenium**: Automates the download of PDFs from the DIAN website.

### GUI (`gui.py`)
- **File Selection**: Allows users to select an Excel file containing CUFE codes.
- **Directory Selection**: Enables users to choose a target folder for saving and organizing classified files.
- **Threaded Processing**: Runs classification tasks in the background to ensure the GUI remains responsive.
- **Error Handling**: Provides user feedback through warnings and error messages.

---

## Installation

### Prerequisites
- **Python 3.8 or higher**
- Required Python packages:
  - `seleniumbase`
  - `pandas`
  - `pdfplumber`
  - `tkinter` (built into Python standard library)

### Installation Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/nico323vera/CUFE-File-Downloader.git
   cd CUFE-File-Downloader
