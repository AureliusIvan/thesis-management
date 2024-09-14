# Copyright (c) 2024, Aurelius Ivan Wijaya and contributors
# For license information, please see license.txt

import frappe
import ed25519
import fitz  # PyMuPDF
from frappe.model.document import Document
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from PIL import Image
import os
import pikepdf


class DocumentSubmission(Document):

    def validate(self):
        """
        Validate Document Submission
        """
        pass

    def on_submit(self):
        """
        On Submit Document Submission.
        Get thesis from "thesis" field and copy it to "signed_thesis" field
        """
        # Get the file URL from the "thesis" field
        thesis_file_url = self.thesis
        base_file_name = os.path.basename(thesis_file_url)

        # Check if the file is stored in the private or public folder
        if thesis_file_url.startswith("/private/files"):
            thesis_pdf_path = frappe.get_site_path(thesis_file_url.strip("/"))
        elif thesis_file_url.startswith("/files"):
            thesis_pdf_path = frappe.get_site_path("public", thesis_file_url.strip("/files"))

        # Get the file URL from signature field om child table document_submission_item
        # TODO: multiple signature support
        lecturer = self.get("document_submission_item")[0].lecturer
        signature_file_url = frappe.get_value("Lecturer", lecturer, "signature")

        # Check if the file is stored in the private or public folder
        if signature_file_url.startswith("/private/files"):
            signature_image_path = frappe.get_site_path(signature_file_url.strip("/"))
        elif signature_file_url.startswith("/files"):
            signature_image_path = frappe.get_site_path("public", signature_file_url.strip("/files"))

        # embed_xml
        # Create the XML metadata to be embedded in the PDF
        xml_output_filename = f"{base_file_name}-{self.name}-{self.student}-xml.pdf"
        xml_data = """
        <?xml version="1.0" encoding="UTF-8"?>
            <metadata>
                <title>Embedded XML Example</title>
                <author>Aurel</author>
                <description>This XML data is embedded into the PDF as metadata.</description>
            </metadata>
        """
        embed_xml(
            thesis_pdf_path,
            xml_output_filename,
            xml_data
        )

        # Coordinates to place the signature on the PDF (example coordinates)
        x, y = 390, 250

        # Sign the PDF by overlaying the signature image and saving the result
        signed_pdf_path = f"{os.path.basename(thesis_pdf_path)}-{self.name}-{self.student}-signed.pdf"
        signed_thesis_pdf_path = insert_image_on_page(
            xml_output_filename,
            signature_image_path,
            signed_pdf_path,
            page_number=0, x=x, y=y
        )

        # Update the signed_thesis field with the signed PDF file path (relative path to private files)
        self.signed_thesis = signed_thesis_pdf_path
        self.save()


def create_image_overlay(image_path, page_width, page_height, x, y):
    """
    Create a transparent PDF with an image (e.g., signature) at the specified position.
    """
    img_pdf = BytesIO()

    # Use reportlab to create a transparent canvas for the image
    can = canvas.Canvas(img_pdf, pagesize=(page_width, page_height))

    # Load the signature or image from the path
    img = Image.open(image_path)
    img_width, img_height = img.size

    # Draw the image at the specified position (x, y) with given width and height
    can.drawImage(image_path, x, y, width=100, height=100)

    can.showPage()
    can.save()

    img_pdf.seek(0)
    return img_pdf


def insert_image_on_page(
        input_pdf_path,
        image_path,
        output_filename,
        page_number=0,
        x=0,
        y=0):
    """
    Insert an image (e.g., signature) onto a specified page of a PDF and save it to the private directory.

    :param input_pdf_path: The path to the input PDF (thesis or document)
    :param image_path: The path to the image (e.g., signature image) to be added
    :param output_filename: The desired output filename (e.g., "signed_thesis.pdf")
    :param page_number: The page on which to overlay the image (default: 0, first page)
    :param x: The x-coordinate where the image will be placed
    :param y: The y-coordinate where the image will be placed
    :return: The path to the saved PDF file in the private directory
    """
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    # Get the dimensions of the page where the image will be placed
    page = reader.pages[page_number]
    page_width = page.mediabox.width
    page_height = page.mediabox.height

    # Create the image overlay PDF (signature)
    image_overlay_pdf = create_image_overlay(
        image_path,
        page_width,
        page_height,
        x,
        y
    )

    image_overlay_reader = PdfReader(image_overlay_pdf)

    # Merge the image with the existing page
    page.merge_page(image_overlay_reader.pages[0])

    # Add all pages to the writer (including the modified one)
    for p in reader.pages:
        writer.add_page(p)

    # Save the modified PDF to the Frappe private directory
    output_pdf_path = frappe.get_site_path("public", "files", output_filename)

    with open(output_pdf_path, "wb") as output_file:
        writer.write(output_file)

    relative_path = f"/files/{output_filename}"
    return relative_path


def embed_xml(input_pdf_path, output_pdf_path, xml_metadata):
    """
    Embed XML Signature in PDF
    """
    # Load the input PDF using PyPDF2
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    # Add all pages from the original PDF
    for page_num in range(len(reader.pages)):
        writer.add_page(reader.pages[page_num])

    # Create an output stream for writing the PDF
    with open(output_pdf_path, "wb") as output_pdf_file:
        writer.write(output_pdf_file)

    # Add custom XML metadata using pikepdf, allowing overwriting of the input file
    with pikepdf.open(output_pdf_path, allow_overwriting_input=True) as pdf:
        # Insert XML metadata into the document info
        pdf.docinfo['/XMLMetadata'] = xml_metadata
        pdf.save(output_pdf_path)

    # Save the file to Frappe as a File document
    with open(output_pdf_path, "rb") as pdf_file:
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": output_pdf_path.split("/")[-1],  # Extract filename
            "is_private": 1,  # Set to 0 for public files
            "content": pdf_file.read()  # Read the PDF content and upload it
        })
        file_doc.insert()  # Insert the file record into the database
        frappe.db.commit()  # Commit the transaction to save the file

    return file_doc.name  # Return the name or ID of the saved file



@frappe.whitelist()
def approve(docname):
    """
    Approve Document Submission
    """
    doc: Document = frappe.get_doc("Document Submission", docname)
    doc.status = "Approved"
    doc.save()
    frappe.msgprint("Document Submission Approved")


@frappe.whitelist()
def reject(docname):
    """
    Reject Document Submission
    """
    doc: Document = frappe.get_doc("Document Submission", docname)
    doc.status = "Rejected"
    doc.save()
    frappe.msgprint("Document Submission Rejected")


