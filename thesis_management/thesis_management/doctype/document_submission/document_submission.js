// Copyright (c) 2024, Aurelius Ivan Wijaya and contributors
// For license information, please see license.txt

frappe.listview_settings['Document Submission'] = {
  get_indicator(doc) {
    // customize indicator color
    if (doc.status == "Approved") {
      return [__("Approved"), "green", "status,=,Approved"];
    } else if (doc.status == "Rejected") {
      return [__("Rejected"), "red", "status,=,Rejected"];
    } else {
      return [__("Pending"), "orange", "status,=,Pending"];
    }
  },
}


frappe.ui.form.on('Document Submission', {
  refresh: function (frm) {
    // add custom button
    if (frm.doc.docstatus === 1) {
      frm.add_custom_button('Approve', () => {
        frappe.call({
          method: 'thesis_management.thesis_management.doctype.document_submission.document_submission.approve',
          args: {
            docname: frm.doc.name
          },
          callback: function (r) {
            frappe.msgprint('Approved');
            frm.reload_doc();
          }
        });
      }).addClass("btn-primary");

      frm.add_custom_button('Reject', () => {
        let dialog = new frappe.ui.Dialog({
          title: 'Enter details',
          fields: [
            {
              label: 'Subject',
              fieldname: 'subject',
              fieldtype: 'Data',
              reqd: 1
            },
            {
              label: 'Description',
              fieldname: 'description',
              fieldtype: 'Text',
              reqd: 1
            },
            {
              label: 'Attachment',
              fieldname: 'attachment',
              fieldtype: 'Attach'
            }
          ],
          size: 'small', // small, large, extra-large
          primary_action_label: 'Submit',
          primary_action(values) {
            dialog.hide();
            // trigger reject method
            frappe.call({
              method: 'thesis_management.thesis_management.doctype.document_submission.document_submission.reject',
              args: {
                docname: frm.doc.name,
                subject: values.subject,
                description: values.description,
                attachment: values.attachment
              },
              callback: function (r) {
                frappe.msgprint('Rejected');
                frm.reload_doc();
              }
            });
          }
        });
        dialog.show();
      }).addClass("btn-danger");
    }

    // auto set posting date
    if (frm.is_new()) {
      frm.set_value('posting_datetime', frappe.datetime.now_date());
    }
  }

});