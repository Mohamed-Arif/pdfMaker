# Image to PDF Converter

This script converts images from a specified folder into a single PDF file. It supports multiple image formats and allows for customization of various settings such as image quality, page size, thread count, and more.

## Features

- **Image Formats Supported**: PNG, JPG, JPEG, BMP, GIF, TIFF
- **Customizable PDF Settings**:
  - Page size (A4, Letter, etc.)
  - Image quality (JPEG compression)
  - Maximum number of threads for concurrent processing
  - DPI (dots per inch) for print-quality PDFs
- **Error Handling**: Logs any issues during image processing or file handling.
- **Temporary File Cleanup**: Automatically deletes temporary files created during the conversion.

## Installation

To run this script, you need to have Python 3.6+ installed, along with the following dependencies:

```bash
pip install pillow reportlab
```

## Usage

1. Clone the repository:

```bash
git clone https://github.com/your-username/image-to-pdf.git
cd image-to-pdf
```
2. Update the source_folder and output_pdf paths in the script or pass them as arguments.
3. Run the script:
```bash
python pdf_generator.py
```
## Example Usage
```python
from pdf_generator import PDFGenerator
from reportlab.lib.pagesizes import A4

generator = PDFGenerator(
    source_folder="path/to/your/images",
    output_pdf="output.pdf",
    page_size=A4,  # or letter
    image_quality=90,  # JPEG compression quality
    max_workers=4,     # Number of concurrent threads for processing
    dpi=300,           # DPI for high-quality print-ready PDFs
)
generator.generate_pdf()
```
## Logging
The script uses Python’s built-in logging module to log progress and errors. Logs are displayed in the console and can be configured to log to a file for persistent records.

## Concurrency
The script uses threading (via ThreadPoolExecutor) to process images concurrently, speeding up the conversion process when handling a large number of images.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
