"""
Screenshot capture script — covers the ENTIRE app end-to-end
10 unique screenshots with no overlap
"""

import time
import os
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

os.makedirs("screenshots", exist_ok=True)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
wait = WebDriverWait(driver, 15)

try:
    driver.get("http://localhost:8501")
    time.sleep(4)
    print("[DEBUG] Page loaded")

    # --- 1. ACCESS GATE (login screen) ---
    driver.save_screenshot("screenshots/01_access_gate.png")
    print("✓ Captured: 01 Access Gate")

    # Login
    access_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password']")))
    access_input.send_keys("LEAD2026")
    print("[DEBUG] Entered access code")
    
    try:
        unlock_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Unlock Tool')]")
        print("[DEBUG] Found button by text")
    except:
        try:
            unlock_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
            print("[DEBUG] Found button by type")
        except:
            unlock_btn = driver.find_element(By.CSS_SELECTOR, "button[kind='primary']")
            print("[DEBUG] Found button by kind")
    
    unlock_btn.click()
    print("[DEBUG] Clicked unlock button")
    time.sleep(5)
    print(f"[DEBUG] Current URL after login: {driver.current_url}")

    # --- 2. HERO HEADER (top of main app) ---
    driver.save_screenshot("screenshots/02_hero_header.png")
    print("✓ Captured: 02 Hero Header")

    # --- 3. DEFINE YOUR TARGET card (input section) ---
    driver.execute_script("window.scrollBy(0, 350)")
    time.sleep(2)
    driver.save_screenshot("screenshots/03_target_input_card.png")
    print("✓ Captured: 03 Target Input Card")

    # --- 4. SERVICE TYPE CHIPS (quick-select buttons) ---
    driver.execute_script("window.scrollBy(0, 250)")
    time.sleep(2)
    driver.save_screenshot("screenshots/04_service_chips.png")
    print("✓ Captured: 04 Service Chips")

    # --- 5. REGION & SERVICE COVERAGE TABLE (top rows visible) ---
    driver.execute_script("window.scrollBy(0, 400)")
    time.sleep(2)
    driver.save_screenshot("screenshots/05_coverage_table_start.png")
    print("✓ Captured: 05 Coverage Table (Start)")

    # --- 6. COVERAGE TABLE MIDDLE ROWS (different services) ---
    driver.execute_script("window.scrollBy(0, 500)")
    time.sleep(2)
    driver.save_screenshot("screenshots/06_coverage_table_middle.png")
    print("✓ Captured: 06 Coverage Table (Middle)")

    # --- 7. COVERAGE TABLE END ROWS ---
    driver.execute_script("window.scrollBy(0, 500)")
    time.sleep(2)
    driver.save_screenshot("screenshots/07_coverage_table_end.png")
    print("✓ Captured: 07 Coverage Table (End)")

    # --- 8. PRO TIPS SECTION ---
    driver.execute_script("window.scrollBy(0, 500)")
    time.sleep(2)
    driver.save_screenshot("screenshots/08_pro_tips.png")
    print("✓ Captured: 08 Pro Tips")

    # --- 9. GENERATE BUTTONS (bottom controls) ---
    driver.execute_script("window.scrollTo(0, 0)")
    time.sleep(2)
    driver.execute_script("window.scrollBy(0, 950)")
    time.sleep(2)
    driver.save_screenshot("screenshots/09_generate_controls.png")
    print("✓ Captured: 09 Generate Controls")

    # --- 10. FULL PAGE OVERVIEW (top with scrollbar) ---
    driver.execute_script("window.scrollTo(0, 0)")
    time.sleep(2)
    driver.save_screenshot("screenshots/10_full_page_overview.png")
    print("✓ Captured: 10 Full Page Overview")

    print("\n✅ All 10 screenshots saved!")
    print("Files:")
    for i in range(1, 11):
        print(f"  0{i}_*.png")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    traceback.print_exc()
    print("\nAttempting to save screenshot of current state...")
    try:
        driver.save_screenshot("screenshots/error_state.png")
        print("✓ Saved error_state.png")
    except:
        pass

finally:
    driver.quit()
    print("\n[DEBUG]Driver closed")