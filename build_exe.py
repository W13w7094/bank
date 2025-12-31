import PyInstaller.__main__
import os
import shutil

# Ensure output directory exists
if os.path.exists("dist"):
    shutil.rmtree("dist")
if os.path.exists("build"):
    shutil.rmtree("build")

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
]

print("Starting Build Process...")
print(f"Arguments: {args}")

# Run PyInstaller
PyInstaller.__main__.run(args)

print("Build Complete. Executable should be in 'dist/'.")
