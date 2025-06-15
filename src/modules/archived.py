# main.py
# require pip install python-dotenv selenium pillow pytesseract webdriver-manager opencv-python transformers torch torchvision nltk beautifulsoup4

import pytesseract
from PIL import Image
from PIL import Image as PILImage
from dotenv import load_dotenv
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import google.generativeai as genai
import datetime
import time
import random
import os
import re
from bs4 import BeautifulSoup
from modules.summarizer import extractor, noisereducer, remover, howmanyans, converter

# Auto testing module
TestMode = False  # Set to True for testing mode, False for production
HasScript = False # driver.find_elements(By.XPATH, '//input[@type="button" and @value="Read Again"]')

load_dotenv()
db_user = os.getenv("USER")
db_pass = os.getenv("PASS")
db_url = os.getenv("URL")
db_api = os.getenv("API_KEY")
db_book_number = os.getenv("ISBN")
extra_context = os.getenv("EXTRA_CONTEXT")

genai.configure(api_key=db_api)
model = genai.GenerativeModel('gemini-1.5-flash')

now = datetime.datetime.now()
timestamp = now.strftime("%Y-%m-%d-%H")
screenshot_dir = os.path.join("screenshots", timestamp)
text_output_path = f"script_{timestamp}.txt"
os.makedirs(screenshot_dir, exist_ok=True)
os.makedirs("screenshots", exist_ok=True)
with open(text_output_path, "a", encoding="utf-8") as f:
    pass

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

options = Options()
options.add_argument("--log-level=3")
options.add_experimental_option("detach", True)
# options.add_argument("--force-device-scale-factor=0.50")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.set_window_size(768, 1024)
driver.get("https://www.xreading.com/login/index.php")

time.sleep(3)

username = driver.find_element(By.ID, "username")
password = driver.find_element(By.ID, "password")

username.send_keys(db_user)
password.send_keys(db_pass)


login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
login_button.click()

time.sleep(3)

if HasScript:
    print("Already finished reading. Starting to return book...")
else:
    try:
        driver.get(db_url)
    except Exception as e:
        print("URL is not found.")
        raise Exception (f"Error: {e}")

    time.sleep(3)

    driver.execute_script("document.documentElement.style.zoom='67%'")

    page_num = 1

    while True:
        
        start_time = time.time()
        elapsed = 0

        print(f"Starting page {page_num}...")

        time.sleep(3)            

        next_wait = random.randint(45, 60)
        # next_wait = random.randint(20, 30)
        # print(f"Next page will be loaded in {next_wait} seconds.")

        screenshot_path = os.path.join(screenshot_dir, f"page_{page_num:03d}.png")
        driver.save_screenshot(screenshot_path)

        image = Image.open(screenshot_path)
        width, height = image.size
        cropped_image = image.crop((0, 64, width, height))
        cropped_image.save(screenshot_path)

        print(f"Screenshot saved to {screenshot_path}.")

        html = driver.page_source

        soup = BeautifulSoup(html, 'html.parser')

        content_div = soup.select_one('.ajax-content.reader-book-title')

        if content_div:
            text = content_div.get_text(separator='\n').strip()
            reading_text = remover(text)
        else:
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(screenshot_path, lang='eng', config=custom_config)
            reading_text = noisereducer(text) # <<< testing

        with open(text_output_path, "a", encoding="utf-8") as f:
            f.write(f"\n\n===== Page {page_num} =====\n\n")
            f.write(reading_text)
        print(f"text is saved to {text_output_path}.")

################################################################################################################################

# 画像解析 (写真)

        # try:

        #     image_cv = cv2.imread(screenshot_path)
        #     gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
        #     blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        #     edges = cv2.Canny(blurred, 30, 100)
        #     contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        #     photo_regions = []
        #     for cnt in contours:
        #         x, y, w, h = cv2.boundingRect(cnt)
        #         if w > 100 and h > 100:
        #             photo_regions.append((x, y, w, h))

        #     if photo_regions:
        #         processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        #         model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        #         model.eval()

        #         with open(text_output_path, "a", encoding="utf-8") as f:
        #             f.write("\n[Image captions:]\n")
        #             for idx, (x, y, w, h) in enumerate(photo_regions):
        #                 sub_img = image_cv[y:y+h, x:x+w]
        #                 sub_img_pil = PILImage.fromarray(cv2.cvtColor(sub_img, cv2.COLOR_BGR2RGB))
        #                 inputs = processor(sub_img_pil, return_tensors="pt")
        #                 with torch.no_grad():
        #                     output = model.generate(**inputs)
        #                 caption = processor.decode(output[0], skip_special_tokens=True)
        #                 f.write(f"[Image {idx+1}] {caption}\n")
        #         print("🖼️ Captions appended to text output.")
        #     else:
        #         print("No photo-like regions detected.")
        #         pass

        # except Exception as e:
        #     print(f"⚠️ Image captioning failed: {e}")
        #     pass

################################################################################################################################

        while elapsed < next_wait:
            scroll_wait = random.randint(10, 20)
            time.sleep(scroll_wait)

            scroll_y = random.randint(768, 876) # Scroll amount
            driver.execute_script(f"window.scrollBy(0, {scroll_y});")

            elapsed = time.time() - start_time
            print(f" ⏳ {int(elapsed)} sec elapsed, scrolling...")

        try:
            time.sleep(3)
            next_button = driver.find_element(By.XPATH, '//button[contains(text(), "Next") or contains(text(), "次へ")]')
            next_button.click()
            print("Going to next page...")
            page_num += 1
            time.sleep(3)
        except Exception as e:
            print(f"Error: Next button not found or no more pages.")
            screenshot_path = os.path.join(screenshot_dir, f"page_end.png")
            driver.save_screenshot(screenshot_path)
            pass
            break

    driver.get("https://www.xreading.com/blocks/institution/dashboard.php")

wait = WebDriverWait(driver, 5)

driver.implicitly_wait(5)

if TestMode:
    print("Test mode is enabled. If you don't want it to be automaticallu tested, please shut down the program in 10 seconds...")
    time.sleep(10)
    print("Test starting...")
    pass
else:
    print("Reading done. Shutting down...")
    driver.quit()

try:
    return_button = driver.find_element(By.XPATH, '//input[@type="button" and @value="Return Book"]')
    return_button.click()
except:
    pass

time.sleep(3)

try:
    quiz_button = driver.find_element(By.XPATH, '//input[@type="button" and @value="Take Quiz"]')
    quiz_button.click()
except:
    pass

driver.implicitly_wait(5)

try:
    iframe = driver.find_element(By.TAG_NAME, "iframe")
    driver.switch_to.frame(iframe)
except:
    pass

try:
    attempt_button = driver.find_element(By.ID, 'id_submitbutton')
    attempt_button.click()
except:
    print("Attemption failed.")
    driver.quit()

load_dotenv(override = True)
db_protagonist = os.getenv("MAIN_CHARACTER_INFO")

qnum = 1

while True:

    driver.implicitly_wait(5)

    question_path = os.path.join(screenshot_dir, f"question_{qnum:03d}.png")
    driver.save_screenshot(question_path)

    question_image = Image.open(question_path)
    width, height = question_image.size
    cropped_question = question_image.crop((256, 224, width, height - 192))
    cropped_question.save(question_path)

    print(f"Quiz is saved to {question_path}.")

    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(question_path, lang='eng', config=custom_config)
    match = re.search(r'book\s*id:\s*(\d+)', text, re.IGNORECASE)
    if match:
        book_id = match.group(1)
    else:
        print("Book  ID not found.")
        book_id = "N/A"
        pass
    
    question_match = re.search(r"Question:\s*\d+\s*[\n‘']?(.*?)(?:\nSelect one:)", text, re.DOTALL)
    question = question_match.group(1).strip() if question_match else None
    options = re.findall(r"^[©O○\-•]\s+(.*)", text, re.MULTILINE)

    question_prompt = f"Question: {question}\nOption:\n" + "\n".join(f"{i}: {opt.strip()}" for i, opt in enumerate(options))

    print("Book ID obtained:", book_id + "\n")
    print(question_prompt)

    with open(text_output_path, "r", encoding="utf-8") as f:
        full_context = f.read()
#       ^^^^^^^^^^^^Script
################################################################################################################################

    #GPT推論

    relevant_context = extractor(full_context, question)

    prompt = f"""You are a smart robot. Based on the following script, choose the option which is the closest answer of the question, and output the option number only.

    Script:
    \"\"\"
    {relevant_context}
    \"\"\"

    Extra Context:
    \"\"\"
    {extra_context}
    \"\"\"

    {question_prompt}

    Remember that even if you do not understand, you may need to choose only one option that seems like the closest answer."""

    response = model.generate_content(prompt)
    print("Response:", response.text.strip())

    raw_response = response.text.strip()
    match = re.search(r'\b([0-9])\b', raw_response)
    answer_index = match.group(1)
    if not match:
        print("match is not found. Randomizing answer...")
        answer_index = random.randint(0,howmanyans(question_prompt))

    # answer_indexに番号が入る

################################################################################################################################

    answer_radio = driver.find_element(By.XPATH, f'//input[@type="radio" and @value="{answer_index}"]')
    print("Selecting answer...")

    time.sleep(random.randint(3, 5))

    answer_radio.click()

    time.sleep(random.randint(10, 15))

    try:
        print("Going to the next question...")
        next_question = driver.find_element(By.XPATH, '//input[@type="submit" and @value="Next Question"]')
        next_question.click()
    except Exception as e:
        print(f"Error: Next question button not found or no more questions.")
        next_question = driver.find_element(By.XPATH, '//input[@type="submit" and @value="Finish Quiz"]')
        next_question.click()
        print("Reading and Testing are done.")
        driver.implicitly_wait(10)
        driver.get("https://www.xreading.com/blocks/institution/mybooks.php?tm=mybooks")
        converter(screenshot_dir)
        pass
        break

    qnum += 1



# driver.quit()