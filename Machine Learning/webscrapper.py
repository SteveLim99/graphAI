import selenium
from selenium import webdriver
import time
import requests
import os
from PIL import Image
import io
import hashlib
from skimage.metrics import structural_similarity as ssim
import cv2
import numpy as np


def get_url_of_img(query: str, max_imgs_count: int, wd: webdriver, sleep_timer: int = 1):
    def scroll(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_timer)

    url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"
    wd.get(url.format(q=query))

    all_image_urls = set()
    curr_img_count = 0
    res_start = 0
    while curr_img_count < max_imgs_count:
        scroll(wd)

        thumbnail_link = wd.find_elements_by_css_selector("img.Q4LuWd")
        res_count = len(thumbnail_link)

        print(
            f"Found: {res_count}. Extracting from {res_start}:{res_count}")

        for img in thumbnail_link[res_start:res_count]:
            try:
                img.click()
                time.sleep(sleep_timer)
            except Exception:
                continue

            img_links = wd.find_elements_by_css_selector('img.n3VNCb')
            for link in img_links:
                if link.get_attribute('src') and 'http' in link.get_attribute('src'):
                    all_image_urls.add(link.get_attribute('src'))

            curr_img_count = len(all_image_urls)

            if len(all_image_urls) >= max_imgs_count:
                print(f"Found: {len(all_image_urls)}, limit reached")
                break
        else:
            print("Found:", len(all_image_urls),
                  "search pending")
            time.sleep(30)
            return
            load_button = wd.find_element_by_css_selector(".mye4qd")
            if load_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")
        res_start = len(thumbnail_link)
    return all_image_urls

def compare_ssim(img1_path, img1_name, folder_path):
    files = os.listdir(folder_path)
    if len(files) != 0:
        candidate = cv2.imread(img1_path)
        candidate_gray = cv2.cvtColor(candidate, cv2.COLOR_BGR2GRAY)
        candidate_resized = cv2.resize(candidate_gray, dsize=(800, 800), interpolation=cv2.INTER_CUBIC)
        for file in files:
            if file == img1_name:
                return True
            key = cv2.imread(folder_path + "/" + file)
            key_gray = cv2.cvtColor(key, cv2.COLOR_BGR2GRAY)
            key_resized = cv2.resize(key_gray, dsize=(800, 800), interpolation=cv2.INTER_CUBIC)
            ssim_value = ssim(candidate_resized, key_resized)
            if ssim_value > 0.7:
                return True
    return False

def persist_image(folder_path: str, temporary_path:str, file_name: str, url: str):
    try:
        image_content = requests.get(url).content

    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        temporary_folder_path = os.path.join(temporary_path, file_name)
        new_name = hashlib.sha1(image_content).hexdigest()[:10]

        if os.path.exists(temporary_folder_path):
            file_path = os.path.join(temporary_folder_path, new_name + '.jpg')
        else:
            os.mkdir(temporary_folder_path)
            file_path = os.path.join(temporary_folder_path, new_name + '.jpg')
        with open(file_path, 'wb') as f:
            image.save(f, "JPEG", quality=100)

        real_folder_path = os.path.join(folder_path, file_name)
        real_file_path = os.path.join(real_folder_path, new_name + '.jpg')
        if not os.path.exists(real_folder_path):
            os.mkdir(real_folder_path)

        found_similar_image = compare_ssim(file_path, new_name + '.jpg', real_folder_path)
        if found_similar_image:
            os.remove(file_path)
            print(f"REJECTED - found picture similar to {url}")
        else:
            os.rename(file_path, real_file_path)
            print(f"SUCCESS - saved {url} - as {file_path}")
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")


if __name__ == '__main__':
    DRIVER_PATH = r'C:\Users\User\Desktop\chromedriver.exe'
    # Initiate ChromeDriver instance
    wd = webdriver.Chrome(executable_path=DRIVER_PATH)

    # Search queries
    queries = ["web application system architecture diagram"]

    for query in queries:
        wd.get('https://google.com')
        search_box = wd.find_element_by_css_selector('input.gLFyf')
        search_box.send_keys(query)

        # Number of images to scrape in each query
        number_links = 5
        links = get_url_of_img(query, number_links, wd)

        # Final save location
        TARGET_SAVE_LOCATION = os.getcwd() + "/test_ssim"

        # Temporary save location utilized for ssim comparison and hash comparison
        TEMPORARY_SAVE_LOCATION = os.getcwd() + "/test_ssim/tmp"

        # Create directory for query if nor present
        if not os.path.isdir(os.path.dirname(TARGET_SAVE_LOCATION)):
            os.makedirs(os.path.dirname(TARGET_SAVE_LOCATION))

        # Begin persisting links scrapped
        for i in links:
            persist_image(TARGET_SAVE_LOCATION, TEMPORARY_SAVE_LOCATION, query, i)
    
    # Kill ChromeDriver
    wd.quit()