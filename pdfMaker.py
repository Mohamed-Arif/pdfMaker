# noinspection PyInterpreter
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os


# Compression function
def compress_and_convert(image_path, output_path, quality=85):
    try:
        img = Image.open(image_path)
    except FileNotFoundError:
        print(f"File not found: {image_path}")
        return None  # Return None if the file is not found
    except IOError:
        print(f"Cannot open file: {image_path}")
        return None  # Return None if there's an IOError

    img = img.convert("RGB")
    img.save(output_path, "JPEG", quality=quality, optimize=True)
    return output_path


# PDF conversion function
def images_to_pdf(source_folder, output_pdf):
    image_files = [f for f in os.listdir(source_folder) if f.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif'))]
    image_files.sort()

    c = canvas.Canvas(output_pdf, pagesize=letter)

    for image_file in image_files:
        compressed_image = os.path.join(source_folder, "compressed_" + image_file)
        compress_and_convert(os.path.join(source_folder, image_file), compressed_image)
        img = Image.open(compressed_image)

        max_width, max_height = letter
        img_width, img_height = img.size
        aspect_ratio = min(max_width / img_width, max_height / img_height)
        new_width = int(img_width * aspect_ratio)
        new_height = int(img_height * aspect_ratio)
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        c.drawImage(compressed_image, 0, 0, width=new_width, height=new_height)
        c.showPage()

    c.save()


# Example usage
source_folder = "C://Users//"
output_pdf = "output_optimized.pdf"
images_to_pdf(source_folder, output_pdf)
