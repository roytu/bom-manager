
import logging
import requests
from bs4 import BeautifulSoup
from creds import *

#try:
#    import http.client as http_client
#except ImportError:
#    # Python 2
#    import httplib as http_client
#http_client.HTTPConnection.debuglevel = 1
#
## You must initialize logging, otherwise you'll not see debug output.
#logging.basicConfig()
#logging.getLogger().setLevel(logging.DEBUG)
#requests_log = logging.getLogger("requests.packages.urllib3")
#requests_log.setLevel(logging.DEBUG)
#requests_log.propagate = True

ROOT_URL = "https://www.mammothelectronics.com"

try:
    input = raw_input
except NameError:
    pass

def ellipses(s, max_size=30):
    if len(s) < max_size:
        return s
    else:
        left = int(max_size / 2) - 3

        res = s[:left]
        res += ".."
        res += s[-(max_size - len(res)):]
        
        return res

def pprint_cart(cart):
    for elem in cart:
        name = ellipses(elem["name"], 30)
        quantity = elem["quantity"]
        unit_price = elem["unit_price"]
        total_price = elem["total_price"]
        url = ellipses(elem["url"], 30)
        
        print("{0} | {1} | {2} | {3} | {4}".format(name, quantity, unit_price, total_price, url))

def get_cart():
    # Get cart
    url = "/".join([ROOT_URL, "cart"])
    resp = requests.get(url, cookies={"cart": CART_ID})

    # Parse HTML
    bs = BeautifulSoup(resp.text.encode("ascii", "ignore"), "html.parser")
    try:
        table = bs.find_all("table")[0]
    except IndexError:
        return []  # Empty cart?
    trs = table.find_all("tr")[1:]  # Skip header row

    # Construct cart list
    cart = []
    for tr in trs:
        name = tr.find("div", {"class": "cart-title"}).get_text()
        name = name.lstrip().rstrip()
        bads = ["<b>", "</b>", "<i>", "</i>", "<br>"]
        for bad in bads:
            name = name.replace(bad, "")
        quantity = int(tr.find("input", {"class": "cart-qty"})["value"])
        url = tr.find("a")["href"]
        url = ROOT_URL + url

        unit_price = tr.find("span", {"class": "saso-cart-item-price"}).get_text()
        unit_price = float(unit_price.lstrip().rstrip().replace("$", ""))

        total_price = tr.find("span", {"class": "saso-cart-item-line-price"}).get_text()
        total_price = float(total_price.lstrip().rstrip().replace("$", ""))

        #print("Adding to cart:")
        #print("\tName: {0}".format(name))
        #print("\tQty: {0}".format(quantity))
        #print("\tUnit Price: {0}".format(unit_price))
        #print("\tTotal Price: {0}".format(total_price))
        #print("\tURL: {0}".format(url))
        #print("")

        elem = {
                "name": name,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_price": total_price,
                "url": url
                }
        cart.append(elem)

    return cart

def clear_cart():
    cart = get_cart()

    while len(cart) > 0:
        print("Clearing cart...")
        cart = get_cart()
        url = "/".join([ROOT_URL, "cart", "change"])

        for line in range(len(cart)):
            line += 1  # Starts counting from 1 on the site
            params = {
                    "line": line,
                    "quantity": 0
                    }
            resp = requests.get(url, cookies={"cart": CART_ID}, params=params)

def save_cart_to_bom(cart, csv_fname):
    text = ""
    for elem in cart:
        name = elem["name"]
        quantity = str(elem["quantity"])
        unit_price = str(elem["unit_price"])
        total_price = str(elem["total_price"])
        url = elem["url"]

        row = "|".join([name, quantity, unit_price, total_price, url])
        text += row
        text += "\n"

    with open(csv_fname, "w") as f:
        f.write(text)

def load_cart_from_bom(csv_fname):
    with open(csv_fname, "r") as f:
        lines = f.readlines()

    for line in lines:
        name, quantity, unit_price, total_price, url = line.split("|")

        id_ = get_id_from_url(url)
        add_item_to_cart(id_, quantity)

def add_item_to_cart(id_, quantity):
    # Get cart
    print("Adding {0} (quantity {1})".format(id_, quantity))
    url = "/".join([ROOT_URL, "cart", "add"])
    cookie = {
            "cart": CART_ID,
            }
    params = {
            "id": (None, id_),
            "quantity": (None, quantity),
            "button": (None, "Add to Cart")
            }
    resp = requests.post(url, cookies=cookie, files=params)

def get_id_from_url(url):
    # Just parse the URL for now
    id_ = url.split("variant=")[1].rstrip()
    return id_

def process_cmd():
    input_str = input("> ")
    args = input_str.split()
    cmd, args = args[0], args[1:]

    if cmd == "cart":
        cart = get_cart()
        pprint_cart(cart)
    elif cmd == "load":
        load_cart_from_bom(args[0])
    elif cmd == "save":
        cart = get_cart()
        save_cart_to_bom(cart, args[0])
    elif cmd == "clear":
        clear_cart()

if __name__ == "__main__":
    # Save current cart
    #cart = get_cart()
    #save_cart_to_bom(cart, "test.csv")

    # Clear cart
    #clear_cart()

    # Load BOM
    #clear_cart()
    #load_cart_from_bom("test.csv")

    #login()
    try:
        while True:
            process_cmd()
    except KeyboardInterrupt:
        pass
    #logout()
