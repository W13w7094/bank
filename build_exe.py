import PyInstaller.__main__
import os
import shutil
import sys

def build():
    print("🚀 开始构建 Windows 可执行文件...")

    # 1. 检查前端构建资源
    current_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dist = os.path.join(os.path.dirname(current_dir), 'frontend', 'dist')
    backend_static = os.path.join(current_dir, 'static')

    if os.path.exists(frontend_dist):
        print(f"📦 发现前端构建资源 (frontend/dist)，正在复制到 {backend_static}...")
        if os.path.exists(backend_static):
            shutil.rmtree(backend_static)
        shutil.copytree(frontend_dist, backend_static)
    elif os.path.exists(os.path.join(current_dir, 'dist', 'index.html')):
        # Fallback: Check local dist folder (common in standalone backend packages)
        local_dist = os.path.join(current_dir, 'dist')
        print(f"📦 发现本地前端资源 ({local_dist})，正在复制到 {backend_static}...")
        if os.path.exists(backend_static):
            shutil.rmtree(backend_static)
        shutil.copytree(local_dist, backend_static)
    else:
        print("⚠️ 未找到前端构建资源 (frontend/dist 或 ./dist)，打包后的程序将不包含前端页面！")
        print("💡 建议先在 frontend 目录下运行: npm run build")

    # 2. 清理旧的构建文件
    print("🧹 清理旧构建文件...")
    for d in ['build', 'dist']:
        if os.path.exists(d):
            shutil.rmtree(d)

    # 3. 设置分隔符 (Windows使用;)
    sep = os.pathsep

    # 4. 执行打包
    print("🔨 正调用 PyInstaller 进行打包...")
    PyInstaller.__main__.run([
        'main.py',
        '--name=BankContractSystem',
        '--onefile',
        '--clean',
        '--noconsole',  # 如果需要看黑窗口日志，去掉这一行
        # 添加数据文件 (源路径:目标路径)
        f'--add-data=templates{sep}templates',
        f'--add-data=static{sep}static',
        f'--add-data=data.json{sep}.',
        f'--add-data=branches.json{sep}.',
        # 隐式导入
        '--hidden-import=uvicorn.logging',
        '--hidden-import=uvicorn.loops',
        '--hidden-import=uvicorn.loops.auto',
        '--hidden-import=uvicorn.protocols',
        '--hidden-import=uvicorn.protocols.http',
        '--hidden-import=uvicorn.protocols.http.auto',
        '--hidden-import=uvicorn.lifespan',
        '--hidden-import=uvicorn.lifespan.on',
    ])

    print("✅ 打包完成！")
    print(f"📂 可执行文件位于: {os.path.join(current_dir, 'dist', 'BankContractSystem.exe')}")

if __name__ == "__main__":
    if sys.platform != "win32":
        print("⚠️以此脚本专为 Windows 环境设计，Linux 下运行可能需要调整参数。")
    build()
