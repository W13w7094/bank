"""
Download EasyOCR models for offline use.
Downloads Chinese Simplified and English models.
"""

import os
import urllib.request
import zipfile
import shutil

# EasyOCR model URLs
MODELS = {
    "detector": {
        "url": "https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/craft_mlt_25k.zip",
        "filename": "craft_mlt_25k.zip"
    },
    "zh_sim": {
        "url": "https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/chinese_sim.zip", 
        "filename": "chinese_sim.zip"
    },
    "en": {
        "url": "https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/english.zip",
        "filename": "english.zip"
    }
}

def download_file(url, filepath):
    """Download file with progress"""
    print(f"Downloading {os.path.basename(filepath)}...")
    urllib.request.urlretrieve(url, filepath)
    print(f"Done: {os.path.basename(filepath)}")

def extract_zip(filepath, output_dir):
    """Extract zip file"""
    print(f"Extracting {os.path.basename(filepath)}...")
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    os.remove(filepath)
    print(f"Extracted: {os.path.basename(filepath)}")

def main():
    output_dir = "easyocr_models"
    
    # Create output directory
    if os.path.exists(output_dir):
        print(f"Removing existing {output_dir}...")
        shutil.rmtree(output_dir)
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("Downloading EasyOCR models (detector + Chinese + English)...")
    
    for model_name, info in MODELS.items():
        filepath = os.path.join(output_dir, info["filename"])
        try:
            download_file(info["url"], filepath)
            extract_zip(filepath, output_dir)
        except Exception as e:
            print(f"Error downloading {model_name}: {e}")
            print("Continuing anyway...")
    
    print("\n[OK] Model download complete!")
    print(f"Models saved to: {os.path.abspath(output_dir)}")
    
    # List downloaded files
    print("\nDownloaded models:")
    for item in os.listdir(output_dir):
        print(f"  - {item}")

if __name__ == "__main__":
    main()
