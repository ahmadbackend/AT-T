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

class client:

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
        #print(response.content[:500])  # look at first bytes
        content = response.content


        print("Content-Type:", response.headers.get("Content-Type"))
        print("Content-Encoding:", response.headers.get("Content-Encoding"))


        if response.headers.get("Content-Encoding") == "br":
            content = brotli.decompress(content)  # decompress Brotli
            cms_feed = content.get("cms-feed", {})
            components = cms_feed.get("components", {})
            print(components)
        try:
            data = json.loads(content.decode("utf-8"))


        except Exception as e:
            #print("JSON decode failed:", e)
            #print(content["cms-feed"]["components"])
            return None
        #print(data)
        return data


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    addresses_list = []
    scraper = client('./Book1.csv')
    all_addresses = scraper.build_all_addresses()
    coo=scraper.initiate_cookies()
    if coo:
        for addres in all_addresses:
            resp = scraper.get_address_encoded(addres)
            scraper.get_fiber_value(resp)
            #print(resp)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
