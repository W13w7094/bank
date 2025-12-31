import os
import requests
import tarfile
import shutil

# Model URLs (PP-OCRv4 Lightweight Chinese)
MODELS = {
    "det": "https://paddleocr.bj.bcebos.com/PP-OCRv4/chinese/ch_PP-OCRv4_det_infer.tar",
    "rec": "https://paddleocr.bj.bcebos.com/PP-OCRv4/chinese/ch_PP-OCRv4_rec_infer.tar",
    "cls": "https://paddleocr.bj.bcebos.com/dygraph_v2.0/ch/ch_ppocr_mobile_v2.0_cls_infer.tar"
}

TARGET_DIR = os.path.join(os.path.dirname(__file__), "ocr_models")

def download_and_extract(url, target_dir):
    filename = url.split("/")[-1]
    filepath = os.path.join(target_dir, filename)
    
    # Download
    print(f"Downloading {filename}...")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filepath, 'wb') as f:
            f.write(response.content)
    else:
        print(f"Failed to download {url}")
        return

    # Extract
    print(f"Extracting {filename}...")
    if filename.endswith(".tar"):
        with tarfile.open(filepath) as tar:
            tar.extractall(path=target_dir)
            
    # Cleanup tar
    os.remove(filepath)

def main():
    if os.path.exists(TARGET_DIR):
        shutil.rmtree(TARGET_DIR)
    os.makedirs(TARGET_DIR)
    
    print(f"Downloading models to {TARGET_DIR}...")
    for key, url in MODELS.items():
        download_and_extract(url, TARGET_DIR)
        
    print("Download complete.")
    
    # Flatten structure if needed? PaddleOCR expects dir paths.
    # The tars typically extract to a subdir like 'ch_PP-OCRv4_det_infer/'
    # We will point code to these subdirs.
    
if __name__ == "__main__":
    main()
