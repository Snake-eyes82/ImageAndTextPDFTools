# Image and Text PDF Tools

A versatile Python application with a Tkinter GUI for handling various PDF and text conversion tasks. This suite allows you to convert images into searchable PDF documents, extract text from existing PDFs, and transform plain text files into new PDF documents.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

This application provides three core functionalities accessible through a user-friendly graphical interface:

1.  **Image to Searchable PDF Converter:**
    * Converts one or more image files (JPG, PNG, TIFF, BMP, GIF) into a single PDF document.
    * Utilizes OCR (Optical Character Recognition) powered by Tesseract to make the text in the generated PDF selectable and searchable.
    * Supports merging multiple image-based pages into one PDF.

2.  **Searchable PDF to Plain Text Converter:**
    * Extracts all selectable text content from a given PDF document.
    * Saves the extracted text into a plain `.txt` file, preserving the textual content without formatting or images. Ideal for text analysis or content reuse.

3.  **Plain Text File to PDF Converter:**
    * Takes a plain `.txt` file and converts its content into a new, well-formatted PDF document.
    * Useful for creating clean PDF versions of text-only documents, code snippets, or notes.

## Prerequisites

Before running this application, ensure you have the following installed:

* **Python 3.7+:** Download from [python.org](https://www.python.org/downloads/).
* **Tesseract OCR Engine:** The core OCR engine required for the "Image to Searchable PDF" functionality.
    * **Windows:** Download the installer from the [Tesseract GitHub Wiki](https://tesseract-ocr.github.io/tessdoc/Downloads.html). During installation, make sure to check the option to "Add to PATH."
    * **macOS (using Homebrew):** `brew install tesseract`
    * **Linux (Debian/Ubuntu):** `sudo apt-get install tesseract-ocr`

## Installation

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/YourUsername/ImageAndTextPDFTools.git](https://github.com/YourUsername/ImageAndTextPDFTools.git)
    cd ImageAndTextPDFTools
    ```
    (Replace `YourUsername` with your actual GitHub username)

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    ```

3.  **Activate the Virtual Environment:**
    * **Windows (PowerShell):**
        ```bash
        .\venv\Scripts\Activate
        ```
    * **Windows (Command Prompt):**
        ```bash
        venv\Scripts\activate.bat
        ```
    * **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

4.  **Install Python Dependencies:**
    ```bash
    pip install Pillow PyPDF2 fpdf pytesseract
    ```

5.  **Configure Tesseract Path (if not in system PATH):**
    If you did not add Tesseract to your system's PATH during its installation, you need to explicitly tell `pytesseract` where to find `tesseract.exe`.
    * Open `unified_converter.py`.
    * Locate the line (around line 12-14) that looks like:
        ```python
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        ```
    * Uncomment this line (remove the `#`) and change the path `C:\Program Files\Tesseract-OCR\tesseract.exe` to the actual location where `tesseract.exe` is installed on your system. Save the file.

## Usage

1.  **Run the Application:**
    Ensure your virtual environment is active, then execute:
    ```bash
    python unified_converter.py
    ```

2.  **Navigate the Interface:**
    The application will open a single window with a navigation bar at the top. Click on the respective buttons to switch between the three conversion tools:
    * **Image to Searchable PDF**
    * **Searchable PDF to Text**
    * **Text File to PDF**

3.  **Follow On-Screen Instructions:**
    Each section provides buttons to select input files and initiate the conversion process, with status updates displayed at the bottom.

## Project Structure

ImageAndTextPDFTools/
├── unified_converter.py       # Main application file containing all GUI and logic
├── README.md                  # This file
├── venv/                      # Python virtual environment (created upon setup)
└── ...                        # Other project files/data (e.g., sample images/PDFs)