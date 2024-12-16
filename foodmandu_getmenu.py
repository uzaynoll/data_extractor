from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time

chrome_driver_path = '/home/ujjwal/Downloads/chromedriver-linux64/chromedriver'
service = Service(chrome_driver_path)

# Initialize the WebDriver
driver = webdriver.Chrome(service=service)

# menu_items = driver.find_elements(By.CSS_SELECTOR, "span.mr-2.ng-binding")  # Replace with actual selector
# prices = driver.find_elements(By.XPATH,'//div[@class = "menu__price"]/span[@class = "ng-binding"]')  # Replace with actual selector

# Navigate to the Foodmandu restaurant listing page
url = "https://foodmandu.com/Restaurant/Index?q=&k=restaurant&c=&cty=1&sortby=2"
driver.get(url)
time.sleep(5)  # Allow the page to load

# List to store restaurant links
restaurant_links = []
# Set to track processed restaurant links
processed_links = set()


# Function to scroll and load more restaurants
def scroll_to_load_more():
    scroll_attempts = 0
    while True:
        last_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait for new content to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height or scroll_attempts > 10:
            break
        scroll_attempts += 1


# Collect restaurant links
while True:
    restaurant_elements = driver.find_elements(By.CSS_SELECTOR, ".title20.mt-2 > a.ng-binding")
    if not restaurant_elements:
        print("No more restaurant links found.")
        break
    for restaurant_element in restaurant_elements:
        restaurant_name = restaurant_element.text.strip()
        restaurant_link = restaurant_element.get_attribute("href")
        if restaurant_link not in processed_links:
            processed_links.add(restaurant_link)
            restaurant_links.append((restaurant_name, restaurant_link))
    print(f"Collected {len(restaurant_links)} restaurant links so far.")
    scroll_to_load_more()  # Scroll to load more restaurants

    # Break the loop if we've already collected all the restaurant links
    if len(restaurant_links) >= 835:
        print("Reached the limit of restaurant links.")
        break

# Chunk restaurant links
chunk_size = 200
chunks = [restaurant_links[i:i + chunk_size] for i in range(0, len(restaurant_links), chunk_size)]
print(f"Total number of restaurants: {len(restaurant_links)}. Number of chunks: {len(chunks)}")

# Process each chunk
processed_restaurants = set()
for chunk_index, chunk in enumerate(chunks):
    chunk_restaurant_data = {}
    print(f"Processing chunk {chunk_index + 1}/{len(chunks)} with {len(chunk)} restaurants.")
    for restaurant_name, restaurant_link in chunk:
        if restaurant_name in processed_restaurants:
            print(f"Skipping already processed restaurant: {restaurant_name}")
            continue
        processed_restaurants.add(restaurant_name)

        try:
            print(f"Visiting restaurant link: {restaurant_link}")
            driver.get(restaurant_link)
            time.sleep(5)  # Ensure the page is fully loaded

            # Ensure menu items are fully loaded
            scroll_to_load_more()

            # Extract menu items
            menu_items = driver.find_elements(By.CSS_SELECTOR, "span.mr-2.ng-binding")  # Replace with actual selector
            prices = driver.find_elements(By.XPATH,'//div[@class = "menu__price"]/span[@class = "ng-binding"]')  # Replace with actual selector

            if len(menu_items) != len(prices):
                print(f"Skipping {restaurant_name}: Menu items and prices mismatch.")
                continue

            restaurant_data = [
                {
                    "restaurant_name": restaurant_name,
                    "food_item": item.text.strip(),
                    "price": price.text.strip(),
                }
                for item, price in zip(menu_items, prices)
            ]
            chunk_restaurant_data[restaurant_name] = restaurant_data
            print(f"Extracted {len(restaurant_data)} menu items from {restaurant_name}.")

        except Exception as e:
            print(f"Error processing {restaurant_name}: {e}")

    # Save each chunk of data to a separate Excel file
    df = pd.DataFrame([entry for sublist in chunk_restaurant_data.values() for entry in sublist])
    df.to_excel(f"foodmandu_menus_{chunk_index + 1}.xlsx", index=False, sheet_name=f"Chunk_{chunk_index + 1}")
    print(f"Chunk {chunk_index + 1} data saved to foodmandu_menus_{chunk_index + 1}.xlsx")

# Close the WebDriver
driver.quit()
print("Data extraction complete. All chunks saved successfully.")