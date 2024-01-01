// Copyright (c) 2024, Carbonite Solutions Ltd and contributors
// For license information, please see license.txt


frappe.ui.form.on("DNS Record", {
    refresh(frm) {
        // Delete Record button
        frm.add_custom_button(__("Delete Record"), function() {
            frappe
                .xcall('gh_godaddy.gh_godaddy.doctype.dns_record.dns_record.delete_dns_record', {
                    name: frm.doc.name,
                    record_type: frm.doc.type // Ensure this is the correct field name
                })
                .then((message) => {
                    frappe.msgprint(message, () => {
                        // Redirect to the list view after the message is closed
                        frappe.set_route("List", "DNS Record");
                    });
                })
                .fail((error) => {
                    frappe.show_alert({ message: error.message, indicator: 'red' }); // Show error alert
                });
        }, "Actions");

        // Update Record button
        frm.add_custom_button(__("Update Record"), function() {
            const dialog = new frappe.ui.Dialog({
                title: 'Update DNS Record',
                fields: [
                    {label: 'Type', fieldname: 'type', fieldtype: 'Select', options: ['A', 'CNAME', 'MX', 'TXT', 'SRV', 'NS'], reqd: 1, default: frm.doc.type},
                    {label: 'Name', fieldname: 'name', fieldtype: 'Data', reqd: 1, default: frm.doc.name},
                    {label: 'Data', fieldname: 'data', fieldtype: 'Data', reqd: 1, default: frm.doc.data},
                    {label: 'TTL', fieldname: 'ttl', fieldtype: 'Int', reqd: 1, default: frm.doc.ttl}
                ],
                primary_action_label: 'Update',
                primary_action(values) {
                    frappe.call({
                        method: 'gh_godaddy.gh_godaddy.doctype.dns_record.dns_record.update_dns_record',
                        args: {
                            docname: frm.doc.name,
                            details: values
                        },
                        callback: function(r) {
                            if (!r.exc) {
                                dialog.hide();
                                frappe.show_alert({message: 'DNS Record Updated Successfully', indicator: 'green'}, 5);
                                setTimeout(function() {
                                    frm.reload_doc();  // Reload the document after the message disappears
                                }, 1000); // 5 seconds delay
                            }
                        },
                        error: function(err) {
                            frappe.msgprint(err.message);
                        }
                    });
                }
            });
            dialog.show();
        }, "Actions");
    }
});





