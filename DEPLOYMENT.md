# 银行合同生成系统部署文档

## 1. 系统概述
本系统用于自动生成银行贷款合同、担保合同及抵押合同。后端采用 Python FastAPI，前端采用 React。

## 2. 目录结构
```
bank-contract-system/
├── backend/
│   ├── main.py             # 主程序（已集成日志记录）
│   ├── app.log             # 运行日志（自动生成）
│   ├── data.json           # 基础配置数据（下拉选项等）
│   ├── branches.json       # 支行信息数据
│   ├── templates/          # Word 模板存放目录 (.docx)
│   └── output/             # 生成文件临时目录
└── frontend/               # 前端代码
```

## 3. 模板变量字典 (详细版)

所有的 Word 模板 (`.docx`) 必须存放在 `backend/templates/` 目录下。请在 Word 中使用 `{{ 变量名 }}` 格式。

### 3.1 贷款业务信息
| 变量名 | 说明 | 示例 |
| :--- | :--- | :--- |
| `{{ loan_amount }}` | 贷款金额（小写） | 500000 |
| `{{ loan_amount_cn }}` | 贷款金额（大写） | 伍拾万元整 |
| `{{ loan_term }}` | 贷款期限（月） | 36 |
| `{{ loan_use }}` | 贷款用途 | 经营周转 |
| `{{ start_date_cn }}` | 起始日期（中文） | 2024年01月01日 |
| `{{ end_date_cn }}` | 到期日期（中文） | 2027年01月01日 |
| `{{ start_date }}` | 起始日期（短横线） | 2024-01-01 |
| `{{ end_date }}` | 到期日期（短横线） | 2027-01-01 |

### 3.2 办理网点信息
| 变量名 | 说明 |
| :--- | :--- |
| `{{ branch.name }}` | 支行全称 |
| `{{ branch.manager }}` | 负责人 |
| `{{ branch.phone }}` | 联系电话 |
| `{{ branch.address }}` | 地址 |

### 3.3 主借款人信息
可以使用快捷变量或完整对象访问：
| 快捷变量 | 完整变量 | 说明 |
| :--- | :--- | :--- |
| `{{ main_name }}` | `{{ main_borrower.name }}` | 姓名 |
| `{{ main_card }}` | `{{ main_borrower.id_card }}` | 身份证号 |
| `{{ main_addr }}` | `{{ main_borrower.address }}` | 住址 |
| - | `{{ main_borrower.mobile }}` | 手机号 |
| - | `{{ main_borrower.gender }}` | 性别 |
| - | `{{ main_borrower.birthday }}` | 生日 (YYYY-MM-DD) |
| - | `{{ main_borrower.ethnicity }}` | 民族 |
| - | `{{ main_borrower.education }}` | 学历 |
| - | `{{ main_borrower.occupation }}` | 职业 |

### 3.4 配偶信息 (如果有)
| 变量名 | 说明 |
| :--- | :--- |
| `{{ spouse.name }}` | 配偶姓名 |
| `{{ spouse.id_card }}` | 身份证号 |
| `{{ spouse.mobile }}` | 手机号 |
| `{{ spouse.relation }}` | 关系 |

### 3.5 共同借款人 (支持3个)
使用 `joint_borrower1` 到 `joint_borrower3`。
| 变量名 (以第1个为例) | 说明 |
| :--- | :--- |
| `{{ joint_borrower1.name }}` | 姓名 |
| `{{ joint_borrower1.id_card }}` | 身份证号 |
| `{{ joint_borrower1.mobile }}` | 手机号 |
| `{{ joint_borrower1.address }}` | 住址 |
| `{{ joint_borrower1.relation }}` | 与主借款人关系 |
| `{{ joint_borrower1.gender }}` | 性别 |
| `{{ joint_borrower1.ethnicity }}` | 民族 |

### 3.6 担保人 (支持7个)
使用 `guarantor1` 到 `guarantor7`。
| 变量名 (以第1个为例) | 说明 |
| :--- | :--- |
| `{{ guarantor1.name }}` | 姓名 |
| `{{ guarantor1.id_card }}` | 身份证号 |
| `{{ guarantor1.mobile }}` | 手机号 |
| `{{ guarantor1.address }}` | 住址 |
| `{{ guarantor1.relation }}` | 与借款人关系 |
| `{{ guarantor1.gender }}` | 性别 |
| `{{ guarantor1.ethnicity }}` | 民族 |
| `{{ guarantor1.education }}` | 学历 |
| `{{ guarantor1.occupation }}` | 职业 |

### 3.7 抵押物 (支持5个)
使用 `collateral1` 到 `collateral5`。
| 变量名 (以第1个为例) | 说明 |
| :--- | :--- |
| `{{ collateral1.owner }}` | 所有权人 |
| `{{ collateral1.type }}` | 抵押物类型 |
| `{{ collateral1.cert_no }}` | 权证编号 |
| `{{ collateral1.location }}` | 坐落位置 |
| `{{ collateral1.value }}` | 价值 |
| `{{ collateral1.area }}` | 面积/数量 |

## 4. 生产环境配置

### 4.1 日志记录
系统已配置自动日志记录，日志文件位于 `backend/app.log`。
- **日志级别**：INFO
- **文件大小限制**：10MB（自动轮转，保留5个备份）

### 4.2 数据维护
- **支行信息**：修改 `backend/branches.json`
- **下拉选项**：修改 `backend/data.json`

## 5. 常见问题
- **Q**: 模板里写了 `guarantor2` 但实际只有一个担保人怎么办？
- **A**: 系统会自动用空值填充，Word 文档对应位置会显示为空白，不会报错。
