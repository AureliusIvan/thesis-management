# Copyright (c) 2024, Aurelius Ivan Wijaya and contributors
# For license information, please see license.txt

import frappe
import ed25519
from frappe.model.document import Document


class DocumentSubmission(Document):
    def validate(self):
        """
        Validate Document Submission
        """
        pass

    def on_submit(self):
        """
        On Submit Document Submission
        """
        pass

    def on_cancel(self):
        """
        On Cancel Document Submission
        """
        pass

    def sign(self):
        """
        Sign Document Submission
        """
        pass

    def verify(self):
        """
        Verify Document Submission
        """
        pass


@frappe.whitelist()
def approve_document_submission(docname):
    """
    Approve Document Submission
    """
    doc: Document = frappe.get_doc("Document Submission", docname)
    doc.status = "Approved"
    doc.save()
    frappe.msgprint("Document Submission Approved")
