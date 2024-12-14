import requests
from bs4 import BeautifulSoup
import csv
import time

# Initialize the data structure to store the scraped data
products = []

# Initialize the list of discovered URLs with the first page to visit
urls = ["https://www.scrapingcourse.com/ecommerce/"]

# Set of visited URLs to prevent revisiting the same pages
visited_urls = set()

# Crawl until all pages have been visited
while urls:
    current_url = urls.pop()  # Get the page to visit from the list
    
    # Skip if the URL has already been visited
    if current_url in visited_urls:
        continue
    
    visited_urls.add(current_url)  # Mark the current URL as visited
    
    # Crawling logic with error handling
    try:
        response = requests.get(current_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find all links on the page
        link_elements = soup.select("a[href]")
        for link_element in link_elements:
            url = link_element["href"]
            # Only add internal URLs to the queue
            if url.startswith("https://www.scrapingcourse.com/ecommerce/") and url not in visited_urls:
                urls.append(url)

        # If current_url is a product page, scrape product details
        if soup.select_one(".product_title") and soup.select_one(".wp-post-image"):
            product = {}
            product["url"] = current_url
            product["image"] = soup.select_one(".wp-post-image")["src"]
            product["name"] = soup.select_one(".product_title").get_text(strip=True)
            product["price"] = soup.select_one(".price").get_text(strip=True) if soup.select_one(".price") else "N/A"

            products.append(product)
    
    except requests.RequestException as e:
        print(f"Error fetching {current_url}: {e}")
    except Exception as e:
        print(f"Error parsing {current_url}: {e}")
    
    # To prevent hitting the server too quickly
    time.sleep(1)

# Initialize the CSV output file using DictWriter for structured writing
with open('products.csv', 'w', newline='', encoding='utf-8') as csv_file:
    fieldnames = ['url', 'image', 'name', 'price']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()  # Write the header row

    # Write product data to CSV
    for product in products:
        writer.writerow(product)

print(f"Scraping complete! {len(products)} products found and saved to products.csv.")
