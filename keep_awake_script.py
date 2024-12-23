from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Set up webdriver
print("Setting up webdriver...")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Navigate to your Streamlit app
url = "https://ch-burden.streamlit.app/"
print(f"Attempting to navigate to: {url}")
driver.get(url)

try:
    print("Waiting for page to load...")
    # Wait for a specific element to be present (adjust as needed)
    element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    print("Page is loaded. Title is: ", driver.title)
    print("Page source length: ", len(driver.page_source))
    
    # Add a small delay to ensure the page fully loads
    time.sleep(5)
    
    # Try to find some Streamlit-specific elements
    streamlit_elements = driver.find_elements(By.CLASS_NAME, "stApp")
    print(f"Found {len(streamlit_elements)} Streamlit elements")
    
except Exception as e:
    print("An error occurred:", str(e))
    print("Current URL:", driver.current_url)
    print("Page source:", driver.page_source[:500])  # Print first 500 chars of page source

finally:
    driver.quit()