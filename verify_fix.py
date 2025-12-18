import undetected_chromedriver as uc
import time

def verify_fix():
    url = "https://play.cuevana3cc.me/pelicula/zootopia/"
    print(f"Testing blocking on {url}")
    
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    # Strict preferences
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.managed_default_content_settings.popups": 2,
        "profile.managed_default_content_settings.ads": 2,
        "profile.default_content_setting_values.popups": 2,
        "profile.content_settings.exceptions.automatic_downloads.*.setting": 2,
    }
    options.add_experimental_option("prefs", prefs)

    driver = uc.Chrome(options=options)
    
    try:
        # Enable blocking BEFORE navigation
        driver.execute_cdp_cmd('Network.enable', {})
        driver.execute_cdp_cmd('Network.setBlockedURLs', {
            "urls": [
                "*go.msdirectsa.com*", 
                "*koviral.xyz*", 
                "*doubleclick.net*", 
                "*adservice.google.com*",
                "*histats.com*",
                "*popads.net*",
                "*msdirectsa.com*",
                "*.xyz",
                "*clickid*"
            ]
        })
        
        print("Navigating...")
        driver.get(url)
        time.sleep(10) # Wait to see if redirect happens
        
        curr = driver.current_url
        print(f"Current URL after 10s: {curr}")
        
        with open("verification_result.txt", "w") as f:
            f.write(curr)
        
        if "cuevana" in curr:
            print("SUCCESS: Stayed on site.")
        else:
            print("FAILURE: Redirected.")
            
    finally:
        driver.quit()

if __name__ == "__main__":
    verify_fix()
