import PyInstaller.__main__
import os
import shutil

# Ensure output directory exists
if os.path.exists("dist"):
    shutil.rmtree("dist")
if os.path.exists("build"):
    shutil.rmtree("build")

# --- Dynmaic Data Collection for Paddle ---
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
# Collect data for paddlex and paddleocr
paddlex_data = collect_data_files('paddlex')
paddleocr_data = collect_data_files('paddleocr')

def format_datas(datas):
    args_list = []
    sep = ';' 
    for src, dest in datas:
        args_list.append(f'--add-data={src}{sep}{dest}')
    return args_list

extra_data_args = format_datas(paddlex_data + paddleocr_data)
# Also include our downloaded models
# ocr_models/ -> ocr_models/
extra_data_args.append('--add-data=ocr_models;ocr_models')

print(f"Collecting {len(extra_data_args)} extra data files for Paddle...")

# Define build arguments
args = [
    'main.py',                       # Script to build
    '--name=BankContractSystem',     # Name of the executable
    '--onefile',                     # Create a single executable
    '--noconsole',                   # No console window
    '--clean',                       # Clean cache
    
    # Include Data Files
    '--add-data=templates;templates',
    '--add-data=data.json;.',
    '--add-data=branches.json;.',
    
    # Include Frontend (Pack 'frontend/dist' into 'static' for backend)
    '--add-data=frontend/dist;static',
    
    # Hidden imports that might be missed
    '--hidden-import=uvicorn',
    '--hidden-import=fastapi',
    '--hidden-import=jinja2',
    '--hidden-import=python-docx',
    '--hidden-import=paddleocr', 
    '--hidden-import=paddlex',
    '--hidden-import=shapely',
] + extra_data_args

print("Starting Build Process...")
print(f"Arguments: {args}")

# Run PyInstaller
PyInstaller.__main__.run(args)

print("Build Complete. Executable should be in 'dist/'.")
