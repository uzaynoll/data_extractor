from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import pandas as pd


chrome_driver_path = '/home/ujjwal/Downloads/chromedriver-linux64/chromedriver'
service = Service(chrome_driver_path)

# Initialize the WebDriver
driver = webdriver.Chrome(service=service)

# Open the URL
url = "https://foodmandu.com/Restaurant/Index?q=&k=restaurant&c=&cty=1&sortby=2"
driver.get(url)

# Wait for the page to load initially
time.sleep(3)

# Scroll to load all content
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    # Scroll down
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)  # Wait for new content to load

    # Check if we have reached the bottom
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Extract restaurant names and locations
restaurants = driver.find_elements(By.CSS_SELECTOR, ".title20.mt-2 > a.ng-binding")
locations = driver.find_elements(By.CSS_SELECTOR, ".icomoon.icon-location + .ng-binding")

# Collect data into a list
data = []
for name, location in zip(restaurants, locations):
    data.append({"Restaurant Name": name.text, "Location": location.text})

# Save to an Excel file using pandas
df = pd.DataFrame(data)
output_file = "restaurants.xlsx"
df.to_excel(output_file, index=False)

print(f"Data successfully saved to {output_file}")

# Close the browser
driver.quit()
