import pypdf
import os
from PIL import Image
from fpdf import FPDF
import markdown2
import pdfkit
from markdown_pdf import MarkdownPdf, Section

root = os.path.curdir() # Set as dummy rn

# Set input variables
user_name = ""
date = ""  # Optional

path = os.path.join(root, f"{user_name}_{date}") # Set as sample, needs editing based on client storage format

extension_map = {
    "jpg" : "image",
    "png" : "image",
    "txt" : "text",
    "pdf" : "pdf",
    "doc" : "doc",
    "md" : "markdown",
}

file_type = path.split(".")[1]


temp_save_path = root + "/out_file.pdf"


# Handle images
if extension_map[file_type] == "image":
    with Image.open(path) as img:
        img_rgb = img.convert("RGB")
        img_rgb.save(temp_save_path, "PDF")
    with open(temp_save_path, "r") as pdf_file:
        read_file = pdf_file.read()  
        out_file = pypdf.PdfWriter(clone_from=read_file)
        out_file.encrypt(f"{user_name[:4]}")
    # Return the out_file to user and remove the temp_file and out_file
    if os.path.exists(temp_save_path):
        os.remove(temp_save_path)

# Handle text
if extension_map[file_type] == "text":
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            pdf.cell(text=line, ln=True, align = "L")
    pdf.output(temp_save_path)


    with open(temp_save_path, "r") as pdf_file:
        read_file = pdf_file.read()  
        out_file = pypdf.PdfWriter(clone_from=read_file)
        out_file.encrypt(f"{user_name[:4]}")
    if os.path.exists(temp_save_path):
        os.remove(temp_save_path)



# Handle pdf
if extension_map[file_type] == "pdf":
    with open(path, "r") as pdf_file:
        read_file = pdf_file.read()  
        out_file = pypdf.PdfWriter(clone_from=read_file)
        out_file.encrypt(f"{user_name[:4]}")


# Handle doc
if extension_map[file_type] == "doc":
    pass


# Handle markdown
if extension_map[file_type] == "markdown":
    pdf = MarkdownPdf(toc_level=2)
    with open(path, "r", encoding="utf-8") as file:
        markdown_content = file.read()
    pdf.add_section(Section(markdown_content))
    pdf.save(temp_save_path)

    with open(temp_save_path, "r") as pdf_file:
        read_file = pdf_file.read()  
        out_file = pypdf.PdfWriter(clone_from=read_file)
        out_file.encrypt(f"{user_name[:4]}")
    
    if os.path.exists(temp_save_path):
        os.remove(temp_save_path)



# with open(path, "r") as file:
#     read_file = file.read()
#     out_file = pypdf.PdfWriter(clone_from=read_file)
#     out_file.encrypt(f"{user_name[:4]}")  # Final version should have numbers too

# out_file is the final output to be sent