import os
import sys
import time
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def getOptions(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="This bot helps users to mass report accounts securely in a headless workflow.")
    parser.add_argument("-u", "--username", type=str, default="", help="Username to report.")
    parser.add_argument("-f", "--file", type=str, default="acc.txt", help="Accounts list (Defaults to acc.txt).")
    return parser.parse_args(args)

args = getOptions()
username = args.username
acc_file = args.file

# Fallback sequence to prevent freezing on automated runs
if username == "":
    username = os.environ.get("TARGET_USERNAME", "")

if username == "":
    username = input("Username to report: ")

# Read the accounts file safely
if not os.path.exists(acc_file):
    print(f"Error: The account file '{acc_file}' was not found. Please create it.")
    sys.exit(1)

with open(acc_file, "r") as f:
    lines = [line.strip() for line in f if line.strip()]

# Parse account lines (Format expected -> username:password)
user_list = []
pass_list = []
for item in lines:
    if ":" in item:
        parts = item.split(":")
        user_list.append(parts[0])
        pass_list.append(parts[1])

if not user_list:
    print("Error: No valid accounts found in your file. Ensure format is username:password")
    sys.exit(1)

# Configure Chrome Options for Replit's Headless Environment
chrome_options = Options()
chrome_options.add_argument("--headless")  # Runs browser invisibly in memory
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("window-size=1200x800")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# Loop through accounts to perform mass reporting
for i in range(len(user_list)):
    print(f"[{i+1}/{len(user_list)}] Logging into bot account: {user_list[i]}")
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 15)
    
    try:
        # 1. Login Phase
        driver.get("https://instagram.com")
        
        user_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        user_input.send_keys(user_list[i])
        
        pass_input = driver.find_element(By.NAME, "password")
        pass_input.send_keys(pass_list[i])
        
        login_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_btn.click()
        
        # Artificial delay to mimic human rhythm and bypass rate limits
        time.sleep(5) 
        
        # 2. Navigation Phase (Target Account Profile)
        driver.get(f"https://www.instagram.com/{username}/")
        time.sleep(4)
        
        # 3. Reporting Phase
        # Locate the Options triple-dot menu button next to the profile name
        options_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//header//button[contains(@class, '') or svg]")))
        options_btn.click()
        time.sleep(2)
        
        # Click the "Report" button on the popup modal
        report_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Report'] or //*[text()='Report User']")))
        report_option.click()
        time.sleep(2)
        
        # Select reporting category (Clicks the first reason option block, usually 'Report Account')
        reason_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div/div/div/div[2]/div/div/div/div[3]/button[1]")))
        reason_btn.click()
        time.sleep(2)
        
        # Close confirmation confirmation acknowledgment layout frame
        close_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Close']")))
        close_btn.click()
        print(f"Successfully sent report from {user_list[i]} onto target: {username}")
        
    except Exception as e:
        print(f"Failed handling execution branch for account {user_list[i]}. Exception info: {e}")
        
    finally:
        # Close the driver thread clean-up session cleanly
        driver.quit()
        time.sleep(2)

print("Mass reporting batch process completed.")
