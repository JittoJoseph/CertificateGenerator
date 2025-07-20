import pandas as pd
import os
from tqdm import tqdm
from playwright.sync_api import sync_playwright

TEMPLATE_PATH = "template.html"
CSV_PATH = "data/names.csv"
OUTPUT_DIR = "certificates"

def generate_certificate_html(name):
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html = f.read()
    # Replace the participant name placeholder
    html = html.replace("[Participant Name]", name)
    return html

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = pd.read_csv(CSV_PATH)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for _, row in tqdm(df.iterrows(), total=len(df), desc="Generating certificates", ncols=80):
            name = str(row["name"]).strip()
            no = str(row["no"]).strip()
            html_content = generate_certificate_html(name)
            temp_html_path = f"temp_{no}.html"
            with open(temp_html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            page = browser.new_page()
            page.set_viewport_size({"width": 2400, "height": 900})
            page.goto(f"file://{os.path.abspath(temp_html_path)}")
            page.wait_for_timeout(2000)
            # Zoom in the page for a more filled certificate
            page.evaluate("document.body.style.zoom='2.1'")
            output_path = os.path.join(OUTPUT_DIR, f"{name}_{no}.png")
            page.screenshot(path=output_path, full_page=True)
            page.close()
            os.remove(temp_html_path)
        browser.close()
    print("Certificates generated in the 'certificates' folder.")

if __name__ == "__main__":
    main()