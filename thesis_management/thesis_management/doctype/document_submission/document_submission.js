// Copyright (c) 2024, Aurelius Ivan Wijaya and contributors
// For license information, please see license.txt


frappe.ui.form.on('Document Submission', {

  refresh: function (frm) {
    // add custom button
    if (frm.doc.docstatus === 1) {
      frm.add_custom_button('Approve', () => {
        frappe.msgprint('Approved');
        // TODO: add approval logic from backend
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
            console.log(values);
            dialog.hide();
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