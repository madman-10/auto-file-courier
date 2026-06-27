import pypdf
import os
from PIL import Image

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

# Handle text
if extension_map[file_type] == "text":
    pass


# Handle pdf
if extension_map[file_type] == "pdf":
    pass


# Handle doc
if extension_map[file_type] == "doc":
    pass


# Handle markdown
if extension_map[file_type] == "markdown":
    pass


# with open(path, "r") as file:
#     read_file = file.read()
#     out_file = pypdf.PdfWriter(clone_from=read_file)
#     out_file.encrypt(f"{user_name[:4]}")  # Final version should have numbers too

# out_file is the final output to be sent