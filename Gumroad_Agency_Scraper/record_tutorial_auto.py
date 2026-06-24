"""
Tutorial Video Recorder — Complete workflow version
Fills form, clicks generate, waits for results, captures download
"""

import time
import os
import sys
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options
except ImportError as e:
    print(f"Missing dependency: {e}")
    sys.exit(1)

try:
    import imageio
except ImportError:
    print("Missing imageio. Run: pip install imageio imageio-ffmpeg")
    sys.exit(1)

os.makedirs("tutorial_video", exist_ok=True)
frames_dir = "tutorial_video/frames"
if os.path.exists(frames_dir):
    import shutil
    shutil.rmtree(frames_dir)
os.makedirs(frames_dir, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M")
output_video = f"tutorial_video/tutorial_{timestamp}.mp4"

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1280,720")
chrome_options.add_argument("--disable-gpu")

print("🎬 TUTORIAL VIDEO RECORDER - COMPLETE WORKFLOW")
print("="*70)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
wait = WebDriverWait(driver, 20)
frame_count = 0

def capture(label, delay=1):
    global frame_count
    frame_count += 1
    path = f"{frames_dir}/frame_{frame_count:04d}_{label}.png"
    driver.save_screenshot(path)
    print(f"  [{frame_count:2d}] {label}")
    if delay:
        time.sleep(delay)

try:
    # Step 1: Login page
    print("\n📝 Step 1: Access Gate / Login")
    driver.get("http://localhost:8501")
    time.sleep(4)
    capture("01_login_page")
    
    access_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password']")))
    access_input.send_keys("LEAD2026")
    time.sleep(0.5)
    capture("02_code_entered")
    
    try:
        btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Unlock Tool')]")
    except:
        try:
            btn = driver.find_element(By.XPATH, "//button[@type='submit']")
        except:
            btn = driver.find_element(By.CSS_SELECTOR, "button[kind='primary']")
    btn.click()
    time.sleep(5)
    capture("03_logged_in_hero")
    
    # Step 2: Hero header
    print("\n🏠 Step 2: Hero Header")
    capture("04_hero_badges_zoom")
    
    # Step 3: Fill form
    print("\n🎯 Step 3: Fill Target Form")
    driver.execute_script("window.scrollBy(0, 300)")
    time.sleep(1)
    capture("05_empty_form")
    
    # Service Type
    try:
        service_input = driver.find_element(By.XPATH, "//input[@placeholder*='roofer']")
        service_input.clear()
        service_input.send_keys("plumber")
        time.sleep(0.5)
        capture("06_service_filled")
    except Exception as e:
        print(f"  Service input issue: {e}")
        capture("06_service_filled_alt")
    
    # City
    try:
        city_input = driver.find_element(By.XPATH, "//input[@placeholder*='Dallas']")
        city_input.clear()
        city_input.send_keys("Dallas TX")
        time.sleep(0.5)
        capture("07_city_filled")
    except Exception as e:
        print(f"  City input issue: {e}")
        capture("07_city_filled_alt")
    
    # Coverage table
    print("\n🌍 Step 4: Coverage Table")
    driver.execute_script("window.scrollBy(0, 400)")
    time.sleep(1)
    capture("08_coverage_table")
    
    driver.execute_script("window.scrollBy(0, 350)")
    time.sleep(1)
    capture("09_coverage_more")
    
    # Pro tips
    print("\n💡 Step 5: Pro Tips")
    driver.execute_script("window.scrollBy(0, 400)")
    time.sleep(1)
    capture("10_pro_tips")
    
    # Generate button
    print("\n🚀 Step 6: Generate Leads")
    driver.execute_script("window.scrollTo(0, 0)")
    time.sleep(2)
    driver.execute_script("window.scrollBy(0, 950)")
    time.sleep(2)
    capture("11_form_ready")
    
    # Click Generate
    try:
        gen_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Generate Leads')]")
        gen_btn.click()
        print("  ✓ Clicked Generate Leads")
        capture("12_generate_clicked")
        
        # Wait and capture progress
        time.sleep(3)
        capture("13_scraping_start")
        
        time.sleep(5)
        capture("14_scraping_progress")
        
        time.sleep(5)
        capture("15_enriching_emails")
        
    except Exception as e:
        print(f"  Generate click failed: {e}")
        capture("12_generate_failed")
    
    # Results
    print("\n📊 Step 7: Results")
    time.sleep(3)
    capture("16_results_displayed")
    
    # CSV download
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)
        capture("17_csv_download")
    except:
        capture("17_download_alt")
    
    print(f"\n✅ Captured {frame_count} frames total")
    
finally:
    driver.quit()
    print("✓ Browser closed")

# Compile video
print("\n🎬 COMPILING MP4 VIDEO...")
print("-"*70)

frame_files = sorted([f for f in os.listdir(frames_dir) if f.endswith('.png')])
print(f"  Frames to process: {len(frame_files)}")

if not frame_files:
    print("❌ No frames found!")
    sys.exit(1)

writer = imageio.get_writer(output_video, fps=2, codec='libx264', quality=7, macro_block_size=8)

for idx, frame_file in enumerate(frame_files, 1):
    img = imageio.imread(os.path.join(frames_dir, frame_file))
    writer.append_data(img)
    if idx % 3 == 0:
        print(f"  Processing: {idx}/{len(frame_files)}")

writer.close()

size_mb = os.path.getsize(output_video) / (1024 * 1024)
print(f"\n{'='*70}")
print(f"✅ VIDEO CREATED SUCCESSFULLY!")
print(f"{'='*70}")
print(f"  📁 Location : {output_video}")
print(f"  📦 Size     : {size_mb:.1f} MB")
print(f"  ⏱️  Duration : ~{len(frame_files)//2} seconds at 2fps")
print(f"  🖼️  Frames   : {len(frame_files)}")
print(f"{'='*70}")

print("\n📋 VIDEO SEQUENCE:")
for i, ff in enumerate(frame_files, 1):
    label = ff.replace(f"frame_{i:04d}_", "").replace(".png", "")
    print(f"  {i:2d}. {label}")

print("\n💡 NEXT STEPS:")
print("  1. Open the video to preview: tutorial_video/tutorial_*.mp4")
print("  2. Record voiceover with Audacity or similar")
print("  3. Combine with CapCut / DaVinci Resolve")
print("  4. Export final tutorial for customers")
print("="*70)