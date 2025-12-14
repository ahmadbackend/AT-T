import requests
import pandas as pd
import brotli

from bs4 import BeautifulSoup as bs
import json
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
"""
address structure 
{
    "id": "",
    "addressLine1": "307 Avocet Dr",
    "geographicSubAddress": [],
    "postcode": "78610",
    "city": "Buda",
    "state": "TX",
    "customer_type": "Consumer"
}
"""

class Client:

    def __init__(self, csv_file):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0",
            "Accept": "*/*",
        })
        self.session_id = None
        self.trace_id = None
        self.auth_header = None
        self.addresses_file = pd.read_csv(csv_file)

    def address_constructor(self, addres):
        address = {"id": "", "addressLine1": addres["Address"], "geographicSubAddress": [], "postcode": str(addres["Zip"]),
                   "city": addres["City"], "state": addres["State"], "customer_type": "Consumer"}
        return address
    def build_all_addresses(self):
        addresses = []
        for _, row in self.addresses_file.iterrows():  # iterate over each row
            addr = self.address_constructor(row)
            addresses.append(addr)
        return addresses

    def initiate_cookies(self):
        url = "https://www.att.com/internet/"

        resp = self.session.get(url)
        resp.raise_for_status()

        return True

    def get_address_encoded(self, addres):
        url = "https://www.att.com/msapi/salesapi/wireless-sales-eapi/v2/address-validation"
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Client-Id": "2223",
            "Client-Secret": "43434",
            "Accept-Encoding":"gzip, deflate, br, zstd"
        })
        resp = self.session.post(url, json = addres)
        # print(resp.status_code)
        # print(resp.text[:500])  # print first 500 chars
        resp.raise_for_status()  # will raise if HTTP error
        data = resp.json()  # parse JSON

        valid_address = data.get("content", {}).get("validAddress", {})
        address_id = valid_address.get("id")
        #print(address_id)
        return address_id

    def get_fiber_value(self, valid_address):
        self.session.headers.update({
            "Accept": "application/json; charset=utf-8",
            "Accept-Encoding":"gzip, deflate, br"
        })

        url = f"https://www.att.com/msapi/idp-content-orchestration/v1/scms/sales/wbb/fiber?addressId={valid_address}&consumerType=CON"
        response= self.session.get(url)
        print(response.status_code)
        print("Content-Type:", response.headers.get("Content-Type"))
        print("Content-Encoding:", response.headers.get("Content-Encoding"))

        if response.status_code != 200:
            print("Request failed with status:", response.status_code)
            return None

        try:
            data = response.json()
            cms_feed = data.get("cms-feed", {})
            components = cms_feed.get("components", {})
            target = "Great news! AT&T Fiber® is available at"
            found, path = self.recursive_search(components, target)
            if found:
                print(f"Phrase found at path: {path}")
            else:
                print("Phrase not found")
            return data
        except json.JSONDecodeError as e:
            print("JSON decode failed:", e)
            return None

    def recursive_search(self, obj, target_phrase, current_path=None):
        """
        Recursively search for the target_phrase in 'text' values within a nested dict/list.
        Returns (True, path) if found, else (False, None).
        """
        if current_path is None:
            current_path = []

        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = current_path + [key]
                if key == 'text' and isinstance(value, str) and target_phrase in value:
                    return True, ' -> '.join(new_path)
                found, path = self.recursive_search(value, target_phrase, new_path)
                if found:
                    return True, path
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                new_path = current_path + [f'[{idx}]']
                found, path = self.recursive_search(item, target_phrase, new_path)
                if found:
                    return True, path
        return False, None
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    addresses_list = []
    scraper = Client('./Book1.csv')
    all_addresses = scraper.build_all_addresses()
    coo=scraper.initiate_cookies()
    if coo:
        for addres in all_addresses:
            resp = scraper.get_address_encoded(addres)
            scraper.get_fiber_value(resp)
            #print(resp)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
