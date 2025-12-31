"""
Download EasyOCR models using the official EasyOCR downloader.
This ensures we get the correct models that EasyOCR expects.
"""

import os
import shutil

def main():
    print("Downloading EasyOCR models using official method...")
    print("This will download models to the default EasyOCR location.")
    
    try:
        import easyocr
        
        # Initialize reader - this will download models automatically
        print("Initializing EasyOCR to download models...")
        reader = easyocr.Reader(['ch_sim', 'en'], gpu=False, download_enabled=True)
        
        print("\n[OK] Models downloaded successfully!")
        print("EasyOCR will use these models from its cache.")
        
        # Get the model directory
        model_storage = reader.model_storage_directory
        print(f"\nModels stored in: {model_storage}")
        
        # Copy models to our bundle directory
        output_dir = "easyocr_models"
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        
        print(f"\nCopying models to {output_dir} for bundling...")
        shutil.copytree(model_storage, output_dir)
        
        print(f"\n[OK] Models ready for bundling!")
        print(f"Bundle directory: {os.path.abspath(output_dir)}")
        
        # List files
        print("\nBundled files:")
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), output_dir)
                print(f"  - {rel_path}")
        
    except ImportError:
        print("ERROR: EasyOCR not installed!")
        print("Please run: pip install easyocr")
        return 1
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
