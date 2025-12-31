# Word 模板中如何使用担保人和共同借款人数据

## 背景

后端已经将所有数据（包括担保人和共同借款人）正确传递给 Word 模板。如果 Word 文档中没有显示担保人信息，是因为模板文件中没有引用这些变量。

## 可用的数据变量

后端传递给 Word 模板的数据包括：

### 基本信息
- `loan_amount` - 贷款金额（数字）
- `loan_amount_cn` - 贷款金额大写
- `loan_term` - 贷款期限（月）
- `loan_use` - 贷款用途
- `start_date` / `start_date_cn` - 起始日期
- `end_date` / `end_date_cn` - 到期日期

### 担保人列表 (`guarantors`)
这是一个数组，每个元素包含：
- `name` - 姓名
- `id_card` - 身份证号
- `mobile` - 手机号
- `address` - 地址
- `relation` - 关系
- `gender` - 性别
- `birthday` - 生日
- `ethnicity` - 民族
- `education` - 学历
- `occupation` - 职业

### 共同借款人列表 (`joint_borrowers`)
结构与 `guarantors` 相同

### 抵押物列表 (`collaterals`)
每个元素包含：
- `owner` - 所有权人
- `type` - 类型
- `location` - 坐落位置
- `value` - 价值
- `area` - 面积/数量

## 在 Word 模板中使用

Word 模板使用 **Jinja2 语法**（通过 python-docx-template 库）。

### 显示单个担保人（第一个）

```
担保人姓名：{{ guarantors[0].name }}
担保人身份证：{{ guarantors[0].id_card }}
担保人电话：{{ guarantors[0].mobile }}
```

### 循环显示所有担保人

```
{% for guarantor in guarantors %}
{{ loop.index }}. 担保人：{{ guarantor.name }}
   身份证号：{{ guarantor.id_card }}
   联系电话：{{ guarantor.mobile }}
   关系：{{ guarantor.relation }}
{% endfor %}
```

### 条件判断

```
{% if guarantors %}
本合同共有 {{ guarantors|length }} 名担保人。
{% endif %}
```

### 表格中循环

在 Word 表格中，可以使用 `{%tr for guarantor in guarantors %}` 来循环行：

```
┌─────────┬──────────────┬─────────────┐
│  姓名   │   身份证号    │   联系电话  │
├─────────┼──────────────┼─────────────┤
│{%tr for guarantor in guarantors %}
│{{ guarantor.name }}│{{ guarantor.id_card }}│{{ guarantor.mobile }}│
│{% endfor %}
└─────────┴──────────────┴─────────────┘
```

## 修复步骤

如果 Word 文档中没有显示担保人信息，需要：

1. 打开对应的 Word 模板文件（如 `guarantee.docx`）
2. 找到需要显示担保人的位置
3. 插入上述 Jinja2 语法
4. 保存模板
5. 重新生成合同测试

## 示例

**担保合同模板示例**：

```
甲方（贷款人）：XX银行
乙方（借款人）：{{ main_borrower.name }}
担保人信息：

{% for g in guarantors %}
第{{ loop.index }}担保人：
   姓名：{{ g.name }}
   身份证号：{{ g.id_card }}
   联系电话：{{ g.mobile }}
   住址：{{ g.address }}
   与借款人关系：{{ g.relation }}

{% endfor %}
```

## 注意事项

- 确保使用正确的变量名（`guarantors` 不是 `guarantor`）
- 列表索引从 0 开始：`guarantors[0]` 是第一个担保人
- `loop.index` 在循环中从 1 开始计数
- 使用 `|length` 过滤器获取列表长度
