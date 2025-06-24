from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pytesseract
from PIL import Image
import io
import base64


def get_tor_driver(headless=True):
    """Launches Firefox routed through Tor."""
    options = Options()
    options.headless = headless

    profile = webdriver.FirefoxProfile()
    profile.set_preference('network.proxy.type', 1)
    profile.set_preference('network.proxy.socks', '127.0.0.1')
    profile.set_preference('network.proxy.socks_port', 9150)
    profile.set_preference("network.proxy.socks_remote_dns", True)
    profile.update_preferences()

    driver = webdriver.Firefox(firefox_profile=profile, options=options)
    return driver


def login_with_captcha(url, username, password, captcha_field='captcha', submit_field='submit'):
    """Attempts login on a Tor-routed page with CAPTCHA solving."""
    driver = get_tor_driver()

    try:
        driver.get(url)
        print("🔍 Page loaded.")

        # Wait for login fields to appear
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "username")))
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "password")))

        # Fill in credentials
        driver.find_element(By.NAME, 'username').send_keys(username)
        driver.find_element(By.NAME, 'password').send_keys(password)

        # Attempt to detect CAPTCHA image
        captcha_image = driver.find_element(By.TAG_NAME, 'img')
        captcha_base64 = captcha_image.screenshot_as_base64
        captcha_bytes = base64.b64decode(captcha_base64)

        # Use OCR to extract text
        img = Image.open(io.BytesIO(captcha_bytes))
        captcha_text = pytesseract.image_to_string(img).strip()
        print(f"🔐 Detected CAPTCHA text: {captcha_text}")

        # Fill CAPTCHA field (fallback to dynamic detection)
        try:
            driver.find_element(By.NAME, captcha_field).send_keys(captcha_text)
        except:
            print(
                f"⚠️ Could not locate CAPTCHA field '{captcha_field}', trying fallback.")
            captcha_fields = driver.find_elements(
                By.XPATH, "//input[@type='text']")
            for field in captcha_fields:
                try:
                    field.send_keys(captcha_text)
                    break
                except:
                    continue

        # Submit the form
        driver.find_element(By.NAME, submit_field).click()
        print("🚀 Submitted login form.")
        time.sleep(3)

        html = driver.page_source
        return html

    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None
    finally:
        driver.quit()
