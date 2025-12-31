# Windows 部署与打包指南

本指南将指导您如何在 Windows Server (64位) 环境下，将前端和后端打包成一个独立的 `.exe` 可执行文件。

## 1. 环境准备 (仅需在打包机器上，例如您的个人电脑)

**注意**：您**不需要**在服务器上安装 Python！
建议在您自己的 Windows 电脑（或任意一台可联网的 Windows PC）上进行打包，生成 `.exe` 后再复制到服务器即可。

### 1.1 安装 Python
1. 下载并安装 [Python 3.10+](https://www.python.org/downloads/windows/)
2. **重要**：安装时勾选 "Add Python to PATH"

### 1.2 安装 Node.js (用于构建前端)
1. 下载并安装 [Node.js (LTS版本)](https://nodejs.org/en/download/)

## 2. 构建步骤

请按顺序执行以下步骤：

### 步骤 1：构建前端
打开命令提示符 (CMD) 或 PowerShell，进入 `frontend` 目录：
```powershell
cd path\to\frontend
npm install
npm run build
```
成功后，`frontend` 目录下会出现 `dist` 文件夹。

### 步骤 2：安装后端依赖
进入 `backend` 目录：
```powershell
cd ..\backend
pip install -r requirements.txt
```

### 步骤 3：一键打包
在 `backend` 目录下，直接运行我为您准备好的打包脚本：
```powershell
python build_exe.py
```

该脚本会自动执行以下操作：
1. 自动将前端的 `dist` 文件夹复制到后端的 `static` 目录
2. 清理旧的构建文件
3. 调用 PyInstaller 生成单文件 EXE

## 3. 部署运行

打包成功后，在 `backend\dist` 目录下会生成一个 `BankContractSystem.exe`。

### 部署文件清单
您只需要将以下 **3个文件** 复制到服务器的同一文件夹下即可运行：

1. `BankContractSystem.exe` (程序主体，已包含前端)
2. `branches.json` (支行配置，可随时修改)
3. `data.json` (下拉选项配置，可随时修改)

*注：`app.log` (日志文件) 和 `templates` 文件夹 (如果需要修改模板) 也会出现在此目录下。*

### 目录结构示例
```
D:\BankSystem\
  ├── BankContractSystem.exe  <-- 双击运行
  ├── branches.json           <-- 配置文件
  ├── data.json               <-- 配置文件
  ├── app.log                 <-- (自动生成) 运行日志
  └── templates\              <-- (可选) 如果想用自定义模板，请新建此文件夹放入 docx
```

### 访问系统
双击运行 exe 后，会弹出一个黑窗口（显示日志）。
打开浏览器访问：`http://localhost:8000` 即可使用。
