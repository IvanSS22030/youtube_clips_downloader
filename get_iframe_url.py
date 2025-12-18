import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def get_url():
    url = "https://play.cuevana3cc.me/pelicula/zootopia/"
    print(f"Analyzing {url}")
    
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.managed_default_content_settings.popups": 2,
        "profile.managed_default_content_settings.ads": 2,
    }
    options.add_experimental_option("prefs", prefs)

    driver = uc.Chrome(options=options)
    
    try:
        driver.get(url)
        time.sleep(5)
        
        # Click Strategy
        buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Latino') or contains(text(), 'Español') or contains(text(), 'Source')]")
        visible_buttons = [b for b in buttons if b.is_displayed()]
        
        if visible_buttons:
            btn = visible_buttons[0]
            print(f"Clicking {btn.text}")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
            time.sleep(1)
            try:
                btn.click()
            except:
                driver.execute_script("arguments[0].click();", btn)
            
            time.sleep(3)
            # Double click check
            if not driver.find_elements(By.TAG_NAME, "iframe"):
                print("Clicking again...")
                try:
                    btn.click()
                except:
                    driver.execute_script("arguments[0].click();", btn)
                time.sleep(3)

        # Extract
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        with open("found_url.txt", "w") as f:
            for frame in iframes:
                src = frame.get_attribute("src")
                print(f"Found: {src}")
                if src:
                    f.write(src + "\n")
                    
    finally:
        driver.quit()

if __name__ == "__main__":
    get_url()
