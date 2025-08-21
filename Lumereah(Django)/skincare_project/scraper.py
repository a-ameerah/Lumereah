"""from bs4 import BeautifulSoup
import requests

url = "https://www.jumia.com.ng/facial-skin-care-d/"
headers = {
        "User-Agent": "MiraBot/1.0 (+mailto:ameerah.adisa64@gmail.com)"
    }
page_to_scrape = requests.get(url, headers=headers)

if page_to_scrape.status_code == 200:
 
    soup = BeautifulSoup(page_to_scrape.text, "html.parser")
    product_names = soup.find_all(attrs={"class": "name"})
    prices = soup.find_all(attrs={"class": "prc"})
    for name, price in zip(product_names, prices):
        print(f"Product: {name.text.strip()} | Price: {price.text.strip()}")

else:
    print(f"Failed to retrieve page. Status code: {page_to_scrape.status_code}")"""


"""url = "https://quotes.toscrape.com/"
headers = {
        "User-Agent": "MiraBot/1.0 (+mailto:ameerah.adisa64@gmail.com)"
    }
page_to_scrape = requests.get(url, headers=headers)


 
soup = BeautifulSoup(page_to_scrape.text, "html.parser")

product_names = soup.find_all("span", attrs={"class": "text"})
prices = soup.find_all("small", attrs={"class": "author"})
for name, price in zip(product_names, prices):
    print(f"Product: {name.text.strip()} | Price: {price.text.strip()}")



url = "https://quotes.toscrape.com/"
headers = {
    "User-Agent": "MiraBot/1.0 (+mailto:ameerah.adisa64@gmail.com)"
}

print("Request finished.")
response = requests.get(url, headers=headers, timeout=10)
print("Request finished.")


print(f"Status code: {response.status_code}")
print(response.text[:500])  # Preview of HTML

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    quotes = soup.find_all("span", class_="text")
    authors = soup.find_all("small", class_="author")

    for quote, author in zip(quotes, authors):
        print(f"Quote: {quote.text.strip()} | Author: {author.text.strip()}")
else:
    print(f"Failed to retrieve page. Status code: {response.status_code}")

"""
