import PyInstaller.__main__
import os
import shutil

print(">>> Starting build process...")

# Clean old builds
for d in ['build', 'dist']:
    if os.path.exists(d):
        shutil.rmtree(d)

# Separator for paths (Windows uses ;, Unix uses :)
sep = ';' if os.name == 'nt' else ':'

# Build arguments
args = [
    'main.py',
    '--name=BankContractSystem',
    '--onefile',
    '--noconsole',
    '--clean',
    
    # Data files
    f'--add-data=templates{sep}templates',
    f'--add-data=data.json{sep}.',
    f'--add-data=branches.json{sep}.',
    
    # Frontend (from frontend/dist to static in exe)
    f'--add-data=frontend/dist{sep}static',
    
    # EasyOCR models (bundled into exe)
    f'--add-data=easyocr_models{sep}easyocr_models',
    
    # Hidden imports
    '--hidden-import=uvicorn.logging',
    '--hidden-import=uvicorn.loops',
    '--hidden-import=uvicorn.loops.auto',
    '--hidden-import=uvicorn.protocols',
    '--hidden-import=uvicorn.protocols.http',
    '--hidden-import=uvicorn.protocols.http.auto',
    '--hidden-import=uvicorn.lifespan',
    '--hidden-import=uvicorn.lifespan.on',
]

print("Building executable...")
PyInstaller.__main__.run(args)

print(">>> Build complete! Executable in dist/")

