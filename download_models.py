"""
Download minimal PaddleOCR models for offline use.
Only downloads the essential Chinese OCR models (detection + recognition).
"""

import os
import urllib.request
import tarfile
import shutil

# Model download URLs (using smaller mobile models for size optimization)
MODELS = {
    "det": {
        "url": "https://paddleocr.bj.bcebos.com/PP-OCRv3/chinese/ch_PP-OCRv3_det_slim_infer.tar",
        "dir": "ch_PP-OCRv3_det_slim_infer"
    },
    "rec": {
        "url": "https://paddleocr.bj.bcebos.com/PP-OCRv4/chinese/ch_PP-OCRv4_rec_infer.tar",
        "dir": "ch_PP-OCRv4_rec_infer"
    }
}

def download_and_extract(url, output_dir):
    """Download and extract tar file"""
    filename = url.split("/")[-1]
    filepath = os.path.join(output_dir, filename)
    
    print(f"Downloading {filename}...")
    urllib.request.urlretrieve(url, filepath)
    
    print(f"Extracting {filename}...")
    with tarfile.open(filepath, 'r') as tar:
        tar.extractall(output_dir)
    
    # Clean up tar file
    os.remove(filepath)
    print(f"Done: {filename}")

def main():
    output_dir = "ocr_models"
    
    # Create output directory
    if os.path.exists(output_dir):
        print(f"Removing existing {output_dir}...")
        shutil.rmtree(output_dir)
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("Downloading minimal OCR models (det + rec only)...")
    
    for model_type, info in MODELS.items():
        download_and_extract(info["url"], output_dir)
    
    print("\n[OK] Model download complete!")
    print(f"Models saved to: {os.path.abspath(output_dir)}")
    
    # List downloaded files
    print("\nDownloaded models:")
    for item in os.listdir(output_dir):
        print(f"  - {item}")

if __name__ == "__main__":
    main()
