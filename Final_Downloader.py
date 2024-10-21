import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

INSTAGRAM_USERNAME = '안알랴줌'
INSTAGRAM_PASSWORD = '안알랴줌'

def Downloader(username):
    def save_image(img_url, user_folder):
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)
        img_data = requests.get(img_url).content
        img_name = os.path.join(user_folder, img_url.split('/')[-1].split('?')[0])
        with open(img_name, 'wb') as f:
            f.write(img_data)
        print(f"Saved image: {img_name}")

    def collect_images(driver, user_folder):
        collected_images = set()
        while True:
            time.sleep(2)
            images = driver.find_elements(By.TAG_NAME, 'img')
            img_data = []

            for img in images:
                src = img.get_attribute('src')
                alt = img.get_attribute('alt')
                if src.startswith("https") and alt and 'profile' not in alt.lower():
                    img_data.append(src)

            if img_data:
                for img_url in img_data:
                    if img_url not in collected_images:
                        save_image(img_url, user_folder)
                        collected_images.add(img_url)
            else:
                print("No more images to download in this post. Scrolling to the next post.")
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                continue

            try:
                next_buttons = driver.find_elements(By.XPATH, "//button[@aria-label='다음']")
                for button in next_buttons:
                    if button.is_displayed():
                        driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        time.sleep(1)
                        button.click()
                        time.sleep(2)
                        break
                else:
                    print("No more next button found.")
                    break
            except Exception as e:
                print(f"Error finding next button: {e}")
                break

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    user_folder = os.path.join(current_dir, 'images')

    options = Options()
    options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 17_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"
    )
    options.add_experimental_option("detach", True)

    service = Service('./chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get('https://www.instagram.com/accounts/login/')
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, 'username'))
        )

        username_input = driver.find_element(By.NAME, 'username')
        password_input = driver.find_element(By.NAME, 'password')

        username_input.send_keys(INSTAGRAM_USERNAME)
        password_input.send_keys(INSTAGRAM_PASSWORD)

        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        login_button.click()
        time.sleep(5)

        driver.get(f'https://www.instagram.com/{username}/feed')
        time.sleep(3)

        collect_images(driver, user_folder)

    finally:
        driver.quit()

if __name__ == "__main__":
    Downloader('siyo.co.kr')
