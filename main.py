import pypdf
import os
from PIL import Image
from fpdf import FPDF
import markdown2
import pdfkit
from markdown_pdf import MarkdownPdf, Section
from io import BytesIO # Import BytesIO to handle uploaded file objects in memory

# --- Configuration and Helpers ---

def get_file_extension(file_path: str) -> str:
    """Extracts the file extension from a given path."""
    return os.path.splitext(file_path)[1].lstrip('.').lower()

def process_image(input_file_bytes: bytes, user_name: str, temp_dir: str) -> tuple[bytes | None, str]:
    """Handles image file processing (JPG/PNG)."""
    temp_save_path = os.path.join(temp_dir, "out_image.pdf")
    try:
        # Use BytesIO to simulate opening the uploaded file in memory
        img_stream = BytesIO(input_file_bytes)
        with Image.open(img_stream) as img:
            img_rgb = img.convert("RGB")
            # Save directly to a temporary path for PIL/PDF writing compatibility
            temp_path = os.path.join(temp_dir, "temp_image.pdf")
            img_rgb.save(temp_path, "PDF")

        # Read the generated PDF bytes
        with open(temp_path, "rb") as pdf_file:
            read_file = BytesIO(pdf_file.read())
            out_file = pypdf.PdfWriter(clone_from=read_file)
            out_file.encrypt(f"{user_name[:4]}")
            final_pdf_bytes = BytesIO()
            out_file.write(final_pdf_bytes)
            final_pdf_bytes.seek(0)

        # Cleanup
        os.remove(temp_path)
        return final_pdf_bytes.getvalue(), "Image PDF"
    except Exception as e:
        print(f"Error processing image: {e}")
        return None, ""


def process_text(input_file_bytes: bytes, user_name: str, temp_dir: str) -> tuple[bytes | None, str]:
    """Handles plain text file processing."""
    temp_save_path = os.path.join(temp_dir, "out_text.pdf")
    try:
        # Use BytesIO to read the uploaded content as text
        text_content = input_file_bytes.decode("utf-8")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Process line by line from the decoded string
        for line in text_content.splitlines():
            if line: # Avoid adding empty lines if they result from splitting
                pdf.cell(text=line, ln=True, align="L")
        
        pdf.output(temp_save_path)

        # Read the generated PDF bytes
        with open(temp_save_path, "rb") as pdf_file:
            # Wrap the raw bytes in BytesIO so pypdf can 'seek' through it
            read_file = BytesIO(pdf_file.read())  
            out_file = pypdf.PdfWriter(clone_from=read_file)
            out_file.encrypt(f"{user_name[:4]}")
            final_pdf_bytes = BytesIO()
            out_file.write(final_pdf_bytes)
            final_pdf_bytes.seek(0)

        # Cleanup
        os.remove(temp_save_path)
        return final_pdf_bytes.getvalue(), "Text PDF"
    except Exception as e:
        print(f"Error processing text: {e}")
        return None, ""


def process_pdf(input_file_bytes: bytes, user_name: str, temp_dir: str) -> tuple[bytes | None, str]:
    """Handles PDF file processing."""
    temp_save_path = os.path.join(temp_dir, "out_pdf.pdf")
    try:
        # Use BytesIO to read the uploaded content as binary data
        read_file = BytesIO(input_file_bytes)
        out_file = pypdf.PdfWriter(clone_from=read_file)
        out_file.encrypt(f"{user_name[:4]}")

        final_pdf_bytes = BytesIO()
        out_file.write(final_pdf_bytes)
        final_pdf_bytes.seek(0)
        return final_pdf_bytes.getvalue(), "Encrypted PDF"
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return None, ""


def process_markdown(input_file_bytes: bytes, user_name: str, temp_dir: str) -> tuple[bytes | None, str]:
    """Handles Markdown file processing."""
    temp_save_path = os.path.join(temp_dir, "out_md.pdf")
    try:
        markdown_content = input_file_bytes.decode("utf-8")
        
        pdf = MarkdownPdf(toc_level=2)
        # Assuming the entire content is one section for simplicity in this refactor
        pdf.add_section(Section(markdown_content)) 
        pdf.save(temp_save_path)

        # Read the generated PDF bytes
        with open(temp_save_path, "rb") as pdf_file:
            read_file = BytesIO(pdf_file.read())
            out_file = pypdf.PdfWriter(clone_from=read_file)
            out_file.encrypt(f"{user_name[:4]}")

        final_pdf_bytes = BytesIO()
        out_file.write(final_pdf_bytes)
        final_pdf_bytes.seek(0)
        
        # Cleanup
        os.remove(temp_save_path)
        return final_pdf_bytes.getvalue(), "Encrypted Markdown PDF"
    except Exception as e:
        print(f"Error processing markdown: {e}")
        return None, ""


def process_file(uploaded_file, user_name: str):
    """
    Main orchestration function to process the uploaded file based on its type.

    Args:
        uploaded_file: The Streamlit UploadedFile object.
        user_name: The name of the user for encryption/naming.

    Returns:
        A tuple containing (bytes_content, result_message) or (None, error_message).
    """
    if uploaded_file is None:
        return None, "No file was uploaded."

    user_name = user_name.upper()
    # 1. Setup temporary environment
    temp_dir = os.path.join("temp_processing", f"{user_name}")
    os.makedirs(temp_dir, exist_ok=True)
    
    file_extension = get_file_extension(uploaded_file.name)
    input_bytes = uploaded_file.read() # Read content once

    # 2. Determine processing path
    if file_extension in ["jpg", "png"]:
        result_bytes, message = process_image(input_bytes, user_name, temp_dir)
    elif file_extension == "txt":
        result_bytes, message = process_text(input_bytes, user_name, temp_dir)
    elif file_extension == "pdf":
        result_bytes, message = process_pdf(input_bytes, user_name, temp_dir)
    elif file_extension == "md":
        result_bytes, message = process_markdown(input_bytes, user_name, temp_dir)
    elif file_extension == "doc":
        # Placeholder for DOC handling (requires external library/conversion)
        message = "DOC format is not yet supported in this refactored backend."
        result_bytes = None
    else:
        message = f"Unsupported file type: .{file_extension}"
        result_bytes = None

    # 3. Cleanup and return
    try:
        # Clean up the temporary directory structure after processing
        import shutil
        shutil.rmtree(temp_dir)
    except OSError as e:
        print(f"Error during cleanup of {temp_dir}: {e}")

    return result_bytes, message

if __name__ == '__main__':
    # Example usage placeholder for local testing (requires manual setup of inputs)
    print("--- Backend Logic Refactored ---")
    print("The file processing logic is now encapsulated in the 'process_file' function.")
    print("This function accepts uploaded files, user name, and date as arguments.")