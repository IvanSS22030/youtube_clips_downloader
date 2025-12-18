import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def debug_cuevana(url):
    print(f"DEBUG(UC): Analyzing {url}")
    
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    # Block popups - UC might handle this differently, but let's try standard prefs
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.managed_default_content_settings.popups": 2,
        "profile.managed_default_content_settings.ads": 2,
    }
    options.add_experimental_option("prefs", prefs)

    # uc.Chrome auto-downloads the driver matching chrome version
    driver = uc.Chrome(options=options)
    
    try:
        driver.get(url)
        print("DEBUG: Initial Page loaded")
        time.sleep(10) # wait for CF
        
        print(f"DEBUG: Current URL: {driver.current_url}")
        print(f"DEBUG: Page Title: {driver.title}")

        # Check for buttons
        buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Latino') or contains(text(), 'Español') or contains(text(), 'Source')]")
        print(f"DEBUG: Found {len(buttons)} 'Latino/Español' elements")
        
        for b in buttons:
             if b.is_displayed():
                 print(f"   - Visible Button: {b.text[:30]}")
                 
             # Try clicking one
             if b.is_displayed():
                 print("Attempting click...")
                 b.click()
                 time.sleep(5)
                 # Look for iframes
                 iframes = driver.find_elements(By.TAG_NAME, "iframe")
                 print(f"Found {len(iframes)} iframes after click.")
                 for f in iframes:
                     print(f"  Frame Src: {f.get_attribute('src')}")
                 break

    except Exception as e:
        print(f"DEBUG: Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_cuevana("https://play.cuevana3cc.me/pelicula/zootopia/")
