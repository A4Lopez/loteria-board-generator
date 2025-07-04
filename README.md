# Lotería Board Generator

A Python application for creating customizable Lotería (Mexican Bingo) boards with image editing and PDF export functionality.

This was built as a free and easy-to-use alternative to online generators — most are either paywalled, clunky, or missing key features. This tool is meant to be simple, flexible, and completely open for anyone to use or build on.

---

## Features

- Customizable Cards: Edit card names and images with zoom and pan functionality
- Image Editor: Built-in image editor with zoom (0.1x to 3.0x) and drag-to-pan
- PDF Export: Generate professional PDF boards with configurable layouts
- Cards List: Optional cut-out cards pages for reference
- Random Board Generation: Each board uses unique random card combinations
- Text Wrapping: Automatic text wrapping for long card names
- Configurable Layout: Fine-tune spacing, positioning, and sizing

---

## Requirements

- Python 3.6+
- tkinter (usually included with Python)
- Pillow
- reportlab

---

## Installation

1. Clone the repository:
   git clone https://github.com/A4Lopez/loteria-board-generator.git
   cd loteria-board-generator

2. Install dependencies:
   pip install -r requirements.txt

3. Run the application:
   python loteria.py

---

## Usage

- Edit Cards: Click on card names or images to edit them
- Image Editing: Use the zoom slider and drag to pan within images
- Generate Boards: Set the number of boards and click "Export PDF"
- Cards List: Toggle "Include Cards List" to add reference pages

---

## Configuration

The application includes extensive configuration options at the top of the file:

- Main Screen: Card sizes, grid layout, fonts
- PDF Board Pages: Card dimensions, spacing, text positioning
- Cards List Pages: Separate configuration for reference pages
- Text Positioning: Fine control over text placement and spacing

---

## Building an Executable

To generate a standalone .exe (Windows only):

   pip install pyinstaller
   pyinstaller --onefile --windowed --icon=favicon.ico loteria.py

The executable will be created in the /dist folder.

---

## Download Executable

You can download the prebuilt .exe from the Releases tab on GitHub.

---

## Contributing

Contributions are welcome!  
Feel free to submit bug fixes, enhancements, or feature suggestions via Pull Requests or Issues.

---

## License

This project is open source and available under the MIT License.

---

## README Note

This README was written with help from ChatGPT as a test of how well it can document Python projects. Verdict: Honestly not even bad.
