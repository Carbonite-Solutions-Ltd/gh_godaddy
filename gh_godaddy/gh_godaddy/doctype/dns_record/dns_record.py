# Copyright (c) 2024, Carbonite Solutions Ltd and contributors
# For license information, please see license.txt

import json
import frappe
from frappe.model.document import Document
import requests

def get_godaddy_api_headers():
    api_key = frappe.db.get_single_value('Credentials', 'api_key')
    api_secret = frappe.db.get_single_value('Credentials', 'api_secret')
    return {
        "Authorization": f"sso-key {api_key}:{api_secret}"
    }

def get_godaddy_dns_records(domain):
    url = f"https://api.godaddy.com/v1/domains/{domain}/records"
    headers = get_godaddy_api_headers()
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch DNS records: {response.text}")

@frappe.whitelist()
def delete_dns_record(name, record_type):
    domain = frappe.db.get_single_value('Credentials', 'domain')
    if not name or not record_type:
        frappe.throw("Record name or type not specified")

    url = f"https://api.godaddy.com/v1/domains/{domain}/records/{record_type}/{name}"
    headers = get_godaddy_api_headers()

    response = requests.delete(url, headers=headers)
    if response.status_code in [200, 204]:
        return "DNS Record deleted successfully"
    else:
        frappe.throw(f"Failed to delete DNS record: {response.text}")
        
# Inside dns_record.py or equivalent file

@frappe.whitelist()
def update_dns_record(docname, details):
    details = json.loads(details)  # Parse the JSON string into a dictionary
    domain = frappe.db.get_single_value('Credentials', 'domain')
    headers = get_godaddy_api_headers()

    # Construct the payload with new details
    payload = [{
        "data": details['data'],
        "ttl": details['ttl']
    }]

    # Use PUT method to update the specific record
    url = f"https://api.godaddy.com/v1/domains/{domain}/records/{details['type']}/{details['name']}"
    response = requests.put(url, headers=headers, json=payload)

    if response.status_code not in [200, 201, 204]:
        frappe.throw(f"Failed to update DNS record: {response.text}")

    return 'DNS Record Updated Successfully'

        



class DNSRecord(Document):
    @staticmethod
    def get_list(args):
        domain = frappe.db.get_single_value('Credentials', 'domain')
        dns_records = get_godaddy_dns_records(domain)
        return DNSRecord.format_records_for_list_view(dns_records)

    @staticmethod
    def format_records_for_list_view(records):
        formatted_records = []
        for record in records:
            formatted_record = {
                'data': record.get('data'),
                'name': record.get('name'),
                'ttl': record.get('ttl'),
                'type': record.get('type'),
                'id': record.get('name'),
            }
            formatted_records.append(formatted_record)
        return formatted_records
    
    
    def load_from_db(self):
        domain = frappe.db.get_single_value('Credentials', 'domain')
        records = get_godaddy_dns_records(domain)

        record_data = next((r for r in records if r.get('name') == self.name), None)
        if not record_data:
            frappe.throw("DNS Record not found", frappe.DoesNotExistError)

        # Map the API data to the document fields
        data = {
            "name": record_data.get('name'),
            "data": record_data.get('data'),
            "type": record_data.get('type'),
            "ttl": record_data.get('ttl'),
            "id": record_data.get('name'),
            # Include other fields as necessary
        }

        # Initialize the Document object with the fetched data
        super(Document, self).__init__(frappe._dict(data))
        
    
    def db_insert(self, *args, **kwargs):
        domain = frappe.db.get_single_value('Credentials', 'domain')

        url = f"https://api.godaddy.com/v1/domains/{domain}/records"
        headers = get_godaddy_api_headers()
        payload = [{
            "type": self.type,
            "name": self.name,
            "data": self.data,
            "ttl": self.ttl
        }]

        response = requests.patch(url, headers=headers, json=payload)
        if response.status_code not in [200, 201, 204]:
            response_data = json.loads(response.text)
            if response_data.get("code") == "DUPLICATE_RECORD":
                frappe.throw("A DNS record with the same name and type already exists.")
            else:
                frappe.throw(f"Failed to create DNS record: {response.text}")
        
    
    def db_update(self):
        domain = frappe.db.get_single_value('Credentials', 'domain')

        url = f"https://api.godaddy.com/v1/domains/{domain}/records/{self.type}/{self.name}"
        headers = get_godaddy_api_headers()
        payload = [{
            "data": self.data,
            "ttl": self.ttl
        }]

        response = requests.put(url, headers=headers, json=payload)
        if response.status_code not in [200, 201, 204]:
            response_data = json.loads(response.text)
            if response_data.get("code") == "DUPLICATE_RECORD":
                frappe.throw("A DNS record with the same name and type already exists.")
            else:
                frappe.throw(f"Failed to update DNS record: {response.text}")
		

        


    @staticmethod
    def get_count(args):
        pass

    @staticmethod
    def get_stats(args):
        pass
    
    

