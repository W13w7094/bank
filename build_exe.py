import PyInstaller.__main__
import os
import shutil
import sys
import io

# Force UTF-8 for stdout to avoid encoding errors on Windows runners
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def build():
    print(">>> Starting Windows build...")

    # 1. Check frontend resources
    current_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dist = os.path.join(os.path.dirname(current_dir), 'frontend', 'dist')
    backend_static = os.path.join(current_dir, 'static')

    if os.path.exists(frontend_dist):
        print(f">>> Found frontend build (frontend/dist), copying to {backend_static}...")
        if os.path.exists(backend_static):
            shutil.rmtree(backend_static)
        shutil.copytree(frontend_dist, backend_static)
    elif os.path.exists(os.path.join(current_dir, 'dist', 'index.html')):
        # Fallback: Check local dist folder (common in standalone backend packages)
        local_dist = os.path.join(current_dir, 'dist')
        print(f">>> Found local frontend resources ({local_dist}), copying to {backend_static}...")
        if os.path.exists(backend_static):
            shutil.rmtree(backend_static)
        shutil.copytree(local_dist, backend_static)
    else:
        print("!!! No frontend resources found (frontend/dist or ./dist). Build will rely on external static files.")

    # 2. Clean old build files
    print(">>> Cleaning old build files...")
    for d in ['build', 'dist']:
        if os.path.exists(d):
            shutil.rmtree(d)

    # 3. Separator
    sep = os.pathsep

    # 4. PyInstaller
    print(">>> Calling PyInstaller...")
    PyInstaller.__main__.run([
        'main.py',
        '--name=BankContractSystem',
        '--onefile',
        '--clean',
        '--noconsole',
        # Add data files
        f'--add-data=templates{sep}templates',
        f'--add-data=static{sep}static',
        f'--add-data=data.json{sep}.',
        f'--add-data=branches.json{sep}.',
        # Hidden imports
        '--hidden-import=uvicorn.logging',
        '--hidden-import=uvicorn.loops',
        '--hidden-import=uvicorn.loops.auto',
        '--hidden-import=uvicorn.protocols',
        '--hidden-import=uvicorn.protocols.http',
        '--hidden-import=uvicorn.protocols.http.auto',
        '--hidden-import=uvicorn.lifespan',
        '--hidden-import=uvicorn.lifespan.on',
    ])

    print(">>> Build Complete!")
    print(f">>> EXE is located at: {os.path.join(current_dir, 'dist', 'BankContractSystem.exe')}")

if __name__ == "__main__":
    if sys.platform != "win32":
        print("Note: This script is designed for Windows. Linux usage may require adjustments.")
    build()
