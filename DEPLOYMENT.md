# 银行合同生成系统部署文档

## 1. 系统概述
本系统用于自动生成银行贷款合同、担保合同及抵押合同。后端采用 Python FastAPI，前端采用 React。支持 Windows 单文件部署 (.exe)。

## 2. 目录结构
```
bank-contract-system/
├── bank_contract_app.exe   # 主程序 (Windows)
├── app.log                 # 运行日志（自动生成）
├── data.json               # 基础配置数据（下拉选项、模板配置）
├── branches.json           # 支行信息数据（包含简称）
├── templates/              # 模板存放目录 (.docx / .xlsx)
├── output/                 # 生成文件临时目录
└── DEPLOYMENT.md           # 本文档
```

## 3. 模板变量字典

### 3.1 Word 模板 (.docx)
使用 `{{ 变量名 }}` 格式。
- **基础字段**：`{{ loan_amount }}` (小写), `{{ loan_amount_cn }}` (大写), `{{ loan_term }}`, `{{ loan_use }}`, `{{ start_date_cn }}`, `{{ end_date_cn }}`
- **办理支行**：`{{ branch.name }}` (全称), `{{ branch.short_name }}` (简称), `{{ branch.manager }}`, `{{ branch.phone }}`, `{{ branch.address }}`
- **主借款人**：`{{ main_name }}`, `{{ main_card }}`, `{{ main_addr }}`, `{{ main_borrower.gender }}`, `{{ main_borrower.age }}`, `{{ main_borrower.mobile }}`
- **配偶**：`{{ spouse.name }}`, `{{ spouse.id_card }}`, `{{ spouse.mobile }}`, `{{ spouse.age }}`
- **共同借款人** (1-3)：`{{ joint_borrower1.name }}`, `{{ joint_borrower1.id_card }}`, `{{ joint_borrower1.age }}` 等
- **担保人** (1-7)：`{{ guarantor1.name }}`, `{{ guarantor1.id_card }}`, `{{ guarantor1.age }}` 等
- **抵押物** (1-5)：`{{ collateral1.owner }}`, `{{ collateral1.location }}`, `{{ collateral1.value }}`, `{{ collateral1.value_cn }}` (大写), `{{ collateral1.cert_no }}`

### 3.2 Excel 模板 (.xlsx) **(v2.0 新增)**
Excel 模板现在支持更灵活的变量替换，支持嵌套对象格式。
- **支持所有 Word 变量**：你可以直接在单元格里写 `{{ spouse.name }}` 或 `{{ main_borrower.id_card }}`。
- **注意**：
  - 如果只要显示变量值，推荐只写变量，例如 `{{ loan_amount }}`。
  - 支持部分替换，例如单元格内容为 `贷款金额：{{ loan_amount }}元`，生成后会变成 `贷款金额：500000元`。

### 3.3 客户调查报告 **(v2.0 新增)**
调查报告（`investigation_report.docx`）拥有专用的汇总字段，用于生成叙述性的段落。

| 变量名 | 说明 | 示例内容 |
| :--- | :--- | :--- |
| `{{ main_summary }}` | 主借款人及配偶综合情况 | "张三，男，35岁，身份证... 配偶李四..." |
| `{{ joint_summary }}` | 共同借款人列表 | "1. 王五，男，30岁... \n 2. 赵六..." |
| `{{ guarantor_summary }}` | 担保人列表 | "1. 陈七，女，40岁..." |
| `{{ collateral_summary }}` | 抵押物列表 | "1. 住宅，坐落于... 评估价值：100万元..." |

## 4. 运行与配置

### 4.1 端口与启动
- **动态端口**：程序启动时默认尝试使用 **8090** 端口。如果被占用，会自动尝试 8091, 8092 等，直到找到可用端口。
- **自动打开浏览器**：Windows 版启动成功后，会自动调用默认浏览器打开系统页面。
- **手动访问**：如果自动打开失败，请查看同目录下的 `app.log`，找到 `Server started at http://localhost:xxxx` 字样，手动在浏览器输入该地址。

### 4.2 配置文件
- **branches.json**：配置支行列表。
- **data.json**：
  - `templates`: 配置在下拉框中显示的模板文件。
  - `options`: 配置“职业”、“借款用途”等下拉选项。

### 4.3 常见问题
- **Q: 模板生成报错？**
  - **A**: 系统现在会返回具体的错误原因。常见原因包括：Word文档格式损坏（尝试另存为新文件）、变量名拼写错误（如 `{{ spose.name }}`）、或使用了不支持的语法。
- **Q: 调查报告没内容？**
  - **A**: 请确保使用了 `{{ main_summary }}` 等专用汇总变量，而不是手动罗列 `{{ main_name }}`。

## 5. 开发建议
如果您需要二次开发：
- 后端开启热重载：`python main.py` (非打包模式下自动开启)
- 前端自动代理：开发时前端运行在 5173，会自动代理请求到后端的 8090 端口。
