# 银行合同生成与调查报告系统

## 简介
这是一个用于自动化生成银行贷款合同及客户调查报告的系统。它包含一个基于 React 的前端界面和一个基于 FastAPI 的后端服务，支持Windows单文件部署（EXE）。

## 主要功能

### 1. 自动化合同生成
- 填写客户信息（主贷人、配偶、共同借款人、担保人）
- 自动计算年龄、性别、生日（基于身份证号）
- 支持多人信息录入
- **模板选择**：支持生成多种合同模板（个人/企业、信用/担保/抵押）
- **一键打包**：生成所有选定的合同文件并打包为ZIP下载

### 2. 客户调查报告
- **集成模板**：调查报告作为标准模板之一供选择
- **自动生成**：基于填写的客户信息自动生成包含“借款人情况”、“共同借款人”、“担保人”、“抵押物”等章节的调查报告
- **智能摘要**：自动生成简洁的叙述性摘要，而非简单的表格填充

### 3. 用户体验优化
- **模板搜索**：支持关键词搜索模板
- **类型标签**：清晰区分 Word (.docx) 和 Excel (.xlsx) 模板
- **热重载**：开发环境下支持后端热重载，提升开发效率
- **详细错误提示**：验证失败时显示具体出错的字段和原因

## 使用指南

### 运行开发环境
1. **启动后端**
   ```bash
   python3 main.py
   # 后端运行在 http://localhost:8000
   # 开发模式自动启用热重载
   ```

2. **启动前端**
   ```bash
   cd frontend
   npm run dev
   # 前端运行在 http://localhost:5173
   ```

### 部署（Windows）
项目配置了 GitHub Actions，每次推送到 `main` 分支都会自动构建 Windows 可执行文件 (.exe)。
构建完成后，在 GitHub Releases 页面下载最新的 `bank_contract_app.exe`。

**使用方法：**
1. 双击 `bank_contract_app.exe` 运行
2. 程序会自动打开浏览器访问系统
3. 填写信息并点击生成

### 配置文件
系统使用以下配置文件（与exe同级目录下）：
- `data.json`: 模板配置、下拉选项配置
- `branches.json`: 支行信息配置
- `templates/`: 存放所有Word/Excel模板文件

## 技术栈
- **Frontend**: React, Ant Design, TypeScript, Vite
- **Backend**: Python, FastAPI, python-docx, openpyxl
- **Packaging**: PyInstaller (单文件打包)
