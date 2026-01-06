# 银行合同套打系统

## 📋 功能特性

### 1. 智能合同生成
- 支持个人和企业客户
- 自动填充字段
- 多模板支持（保证/信用/抵押）
- Word文档生成

### 2. Excel到期客户导入 ✅
- 启动时自动加载到期客户列表
- 快速选择客户并自动填充所有信息
- 支持共同借款人和担保人
- 企业/个人智能识别

### 3. Chrome浏览器插件 ✅
- 解析生成的txt文件
- 分类展示所有数据
- 一键复制任意字段
- 实时搜索功能

## 🚀 快速开始

### 后端服务
```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python3 main.py
```
访问: http://localhost:8090

### 前端界面
```bash
cd frontend
npm install
npm run dev
```
访问: http://localhost:5173

### Chrome插件安装
1. Chrome访问 `chrome://extensions/`
2. 启用"开发者模式"
3. 点击"加载已解压的扩展程序"
4. 选择 `chrome-extension` 文件夹

## 📦 发布说明

### GitHub Releases
每次推送tag时，GitHub Actions会自动打包：
- 完整系统压缩包
- Chrome插件独立包

```bash
# 创建发布
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

## 📁 项目结构
```
├── main.py              # FastAPI后端
├── frontend/            # React前端
├── chrome-extension/    # Chrome插件
├── templates/           # Word模板
├── 贷款到期清单.xlsx   # 客户数据
└── .github/workflows/   # CI/CD配置
```

## 🔧 依赖
- Python 3.10+
- Node.js 18+
- FastAPI, pandas, python-docx

## 📄 License
MIT
