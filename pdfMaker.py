import os
import logging
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from PIL import Image
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_QUALITY = 85
SUPPORTED_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff")


class PDFGenerator:
    def __init__(
            self,
            source_folder: str,
            output_pdf: str,
            page_size: Tuple[float, float] = letter,
            image_quality: int = DEFAULT_QUALITY,
            max_workers: int = 4,
            dpi: int = 300,
    ):
        self.source_folder = Path(source_folder)
        self.output_pdf = Path(output_pdf)
        self.page_size = page_size
        self.quality = image_quality
        self.max_workers = max_workers
        self.dpi = dpi

    def validate_inputs(self) -> None:
        """Ensure source folder exists and output directory is writable."""
        if not self.source_folder.exists():
            raise FileNotFoundError(f"Source folder not found: {self.source_folder}")
        if not self.source_folder.is_dir():
            raise NotADirectoryError(f"Not a directory: {self.source_folder}")

        output_dir = self.output_pdf.parent
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
        if not os.access(output_dir, os.W_OK):
            raise PermissionError(f"Cannot write to: {output_dir}")

    def get_sorted_images(self) -> List[Path]:
        """Return supported images sorted by name."""
        images = [
            f for f in self.source_folder.iterdir()
            if f.suffix.lower() in SUPPORTED_EXTENSIONS
        ]
        return sorted(images, key=lambda x: x.name.lower())

    def process_image(self, image_path: Path) -> Optional[Tuple[ImageReader, Path]]:
        """Resize, compress, and convert image to PDF-compatible format."""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary (e.g., PNG transparency)
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # Calculate scaling while maintaining aspect ratio
                width, height = img.size
                max_width, max_height = self.page_size
                scale = min(max_width / width, max_height / height)
                new_size = (int(width * scale), int(height * scale))

                # High-quality downscaling
                img = img.resize(new_size, Image.Resampling.LANCZOS)

                # Save as temporary JPEG
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                    img.save(tmp.name, "JPEG", quality=self.quality, optimize=True)
                    return ImageReader(tmp.name), Path(tmp.name)

        except Exception as e:
            logger.error(f"Failed to process {image_path.name}: {str(e)}")
            return None

    def generate_pdf(self) -> None:
        """Convert images to a single PDF file."""
        self.validate_inputs()
        images = self.get_sorted_images()

        if not images:
            logger.warning("No supported images found in the source folder!")
            return

        logger.info(f"Processing {len(images)} images into {self.output_pdf}...")

        c = canvas.Canvas(str(self.output_pdf), pagesize=self.page_size)
        temp_files = []

        try:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(self.process_image, img): img
                    for img in images
                }

                for future in as_completed(futures):
                    img_path = futures[future]
                    try:
                        result = future.result()
                        if result is None:
                            continue  # Skip failed images

                        img_reader, tmp_path = result
                        temp_files.append(tmp_path)

                        # Draw image on PDF
                        c.drawImage(
                            img_reader,
                            0, 0,
                            width=self.page_size[0],
                            height=self.page_size[1],
                            preserveAspectRatio=True,
                            mask="auto",
                        )
                        c.showPage()
                        logger.info(f"Added: {img_path.name}")

                    except Exception as e:
                        logger.error(f"Error adding {img_path.name}: {str(e)}")

            c.save()
            logger.info(f"PDF successfully generated: {self.output_pdf}")

        finally:
            # Clean up temporary files
            for tmp in temp_files:
                try:
                    tmp.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete {tmp}: {str(e)}")


if __name__ == "__main__":
    # Example Usage
    generator = PDFGenerator(
        source_folder="C:/Users/Arif1/Pictures/New Folder",
        output_pdf="output.pdf",
        page_size=A4,  # or letter
        image_quality=90,  # Higher quality
        max_workers=6,  # More threads for faster processing
        dpi=300,  # High DPI for print-ready PDFs
    )
    generator.generate_pdf()