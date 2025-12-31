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

# Helper to format data for command line: "src;dest" (Windows)
# Note: build_exe.py runs on the build machine (Windows CI)
def format_datas(datas):
    args_list = []
    separator = ';' if os.name == 'nt' else ':' # But we know CI is windows, safe to use ; or auto?
    # PyInstaller CLI expects OS specific separator. 
    # CI is windows-latest, so os.name should be 'nt'. 
    # But just in case, we hardcode ';' if we are strictly targeting windows build as per package.yml
    sep = ';' 
    for src, dest in datas:
        args_list.append(f'--add-data={src}{sep}{dest}')
    return args_list

extra_data_args = format_datas(paddlex_data + paddleocr_data)
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
