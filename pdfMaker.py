# noinspection PyInterpreter
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
import os
import concurrent.futures


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
def images_to_pdf(source_folder, output_pdf, page_size=letter, max_workers=4):
    image_files = [f for f in os.listdir(source_folder) if f.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif'))]
    image_files.sort()

    c = canvas.Canvas(output_pdf, pagesize=page_size)
    max_width, max_height = page_size

    # Using ThreadPoolExecutor for concurrency
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for image_file in image_files:
            compressed_image = os.path.join(source_folder, "compressed_" + image_file)
            future = executor.submit(compress_and_convert, os.path.join(source_folder, image_file), compressed_image)
            futures.append((future, compressed_image))

        for future, compressed_image_path in futures:
            result = future.result()
            if result is None:
                continue  # Skip this image if it couldn't be processed

            img = Image.open(compressed_image_path)
            img_width, img_height = img.size
            aspect_ratio = min(max_width / img_width, max_height / img_height)
            new_width = int(img_width * aspect_ratio)
            new_height = int(img_height * aspect_ratio)
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            c.drawImage(compressed_image_path, 0, 0, width=new_width, height=new_height)
            c.showPage()

            # Cleanup: Delete the compressed image after it has been added to the PDF
            try:
                os.remove(compressed_image_path)
                print(f"Deleted temporary file: {compressed_image_path}")
            except Exception as e:
                print(f"Error deleting file {compressed_image_path}: {e}")

    c.save()


# Example usage
source_folder = "C://Users//Arif1//Pictures//Camera Roll"
output_pdf = "output_file.pdf"
images_to_pdf(source_folder, output_pdf, page_size=letter, max_workers=4)  # or use page_size=A4
