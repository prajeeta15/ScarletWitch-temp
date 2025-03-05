import os
import time
import sqlite3
import pytesseract
import json
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

# Path to Tor Browser
TOR_BROWSER_PATH = "C:/Users/Prajeeta/Documents/prats/apps/Tor Browser/Browser/firefox.exe"

# Database file
DB_FILE = "dark_web_forums.db"


def setup_database():
    """Create SQLite database for storing forum posts."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forum_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()


def store_post(title, content):
    """Store forum posts in the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO forum_posts (title, content, timestamp) VALUES (?, ?, datetime('now'))",
                   (title, content))
    conn.commit()
    conn.close()


def fetch_and_print_posts():
    """Fetch and print all forum posts from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content, timestamp FROM forum_posts")
    rows = cursor.fetchall()
    conn.close()

    print("\n📌 **Scraped Forum Posts:**")
    if not rows:
        print("⚠️ No forum posts found.")
    else:
        for row in rows:
            print(f"\n📝 **Post ID:** {row[0]}")
            print(f"📌 **Title:** {row[1]}")
            print(f"📖 **Content:** {row[2]}")
            print(f"⏳ **Timestamp:** {row[3]}")
            print("=" * 50)


def setup_tor_selenium():
    """Setup Selenium with Tor Browser."""
    options = Options()
    options.headless = False  # Change to True to run in background
    options.binary_location = TOR_BROWSER_PATH
    return webdriver.Firefox(options=options)


def detect_captcha(driver):
    """Detect if a CAPTCHA is present."""
    try:
        captcha_element = driver.find_element(By.CLASS_NAME, "captcha")
        return captcha_element
    except:
        return None


def save_and_print_captcha(driver, captcha_element):
    """Save the CAPTCHA image and print it."""
    captcha_image = captcha_element.screenshot_as_png
    image = Image.open(BytesIO(captcha_image))
    image.save("captcha.png")  # Save for debugging
    image.show()  # Open the image so the user can see it
    return image


def solve_captcha(driver, captcha_element):
    """Solve CAPTCHA using OCR and input it."""
    image = save_and_print_captcha(driver, captcha_element)
    captcha_text = pytesseract.image_to_string(image).strip()

    print(f"🔍 Solved CAPTCHA: {captcha_text}")

    try:
        captcha_input = driver.find_element(By.ID, "captcha_input")
        captcha_input.send_keys(captcha_text)
        captcha_input.submit()
        time.sleep(3)  # Wait for page to reload
        return True
    except Exception as e:
        print(f"❌ CAPTCHA solving failed: {e}")
        return False


def bypass_login(driver):
    """Bypass login/register pages if detected."""
    try:
        login_form = driver.find_element(By.NAME, "login")
        if login_form:
            print("⚠️ Login Page Detected! Trying to bypass...")
            # Modify URL to bypass
            driver.get(driver.current_url + "?guest=true")
            time.sleep(3)
    except:
        print("✅ No login page detected.")


def scrape_forum(driver):
    """Extract forum posts."""
    print("🔍 Scraping forum posts...")

    # Update selector based on forum structure
    posts = driver.find_elements(By.CLASS_NAME, "forum-post")

    for post in posts:
        try:
            title = post.find_element(By.CLASS_NAME, "post-title").text
            content = post.find_element(By.CLASS_NAME, "post-content").text
            store_post(title, content)  # Store in DB
            print(f"📝 Saved post: {title}")
        except:
            continue  # Skip posts without valid structure


def scrape_marketplace(url):
    """Scrape dark web forum while handling CAPTCHA and login pages."""
    setup_database()  # Ensure database exists

    driver = setup_tor_selenium()
    driver.get(url)
    time.sleep(5)  # Wait for page to load

    captcha_element = detect_captcha(driver)
    if captcha_element:
        print("⚠️ CAPTCHA detected! Solving now...")
        if not solve_captcha(driver, captcha_element):
            print("❌ Failed to solve CAPTCHA. Try manually.")
            input("Press Enter after solving CAPTCHA manually...")

    bypass_login(driver)  # Try to skip login

    scrape_forum(driver)  # Scrape data

    print("✅ Scraping completed!")

    driver.quit()

    # Fetch and print the scraped posts
    fetch_and_print_posts()


# Example Usage
scrape_marketplace("https://bdfclub.com/")
