import os
import time
from playwright.sync_api import sync_playwright

demos_dir = "$CORTEX_ROOT/30_BABYLON-60/public/demos"
videos_dir = "$CORTEX_ROOT/30_BABYLON-60/public/videos"
os.makedirs(videos_dir, exist_ok=True)

def record_all():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        files = sorted([f for f in os.listdir(demos_dir) if f.endswith('.html')])
        
        for f in files:
            print(f"Recording {f}...")
            context = browser.new_context(
                record_video_dir=videos_dir,
                record_video_size={"width": 1280, "height": 720}
            )
            page = context.new_page()
            url = f"file://{os.path.join(demos_dir, f)}"
            page.goto(url)
            page.wait_for_timeout(5500)
            context.close()
            
            # Renombrar el video webm generado
            for v in os.listdir(videos_dir):
                if v.endswith('.webm') and len(v) == 37: # Playwright usa UUIDs 32 chars + .webm = 37
                    old_path = os.path.join(videos_dir, v)
                    new_path = os.path.join(videos_dir, f.replace('.html', '.webm'))
                    if os.path.exists(new_path):
                        os.remove(new_path)
                    os.rename(old_path, new_path)
                    break
                    
        browser.close()
        print(f"Terminado. {len(files)} videos grabados en {videos_dir}.")

if __name__ == "__main__":
    record_all()
