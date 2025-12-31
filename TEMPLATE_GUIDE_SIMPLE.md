# Word 模板变量使用指南（简化版）

## 变量命名规则

不再使用循环，直接使用编号的变量名：

### 共同借款人（最多3个）
- `{{ joint_borrower1.name }}` - 第1个共同借款人姓名
- `{{ joint_borrower1.id_card }}` - 身份证
- `{{ joint_borrower1.mobile }}` - 电话
- `{{ joint_borrower1.address }}` - 地址
- `{{ joint_borrower1.relation }}` - 关系
- ... 其他字段同理

- `{{ joint_borrower2.name }}` - 第2个共同借款人
- `{{ joint_borrower3.name }}` - 第3个共同借款人

### 担保人（最多7个）
- `{{ guarantor1.name }}` - 第1个担保人姓名
- `{{ guarantor1.id_card }}` - 身份证
- `{{ guarantor1.mobile }}` - 电话
- `{{ guarantor1.address }}` - 地址
- `{{ guarantor1.relation }}` - 关系
- ... 其他字段：gender, birthday, ethnicity, education, occupation

- `{{ guarantor2.name }}` - 第2个担保人
- ... 依此类推到 `{{ guarantor7.name }}`

### 抵押物（最多5个）
- `{{ collateral1.owner }}` - 第1个抵押物所有人
- `{{ collateral1.type }}` - 类型
- `{{ collateral1.location }}` - 位置
- `{{ collateral1.value }}` - 价值
- `{{ collateral1.area }}` - 面积

- `{{ collateral2.owner }}` - 第2个抵押物
- ... 依此类推到 `{{ collateral5.owner }}`

## 在 Word 模板中使用

### 借款合同模板示例

```
借款人：{{ main_borrower.name }}
身份证：{{ main_borrower.id_card }}

共同借款人：
1. {{ joint_borrower1.name }}（{{ joint_borrower1.id_card }}）
2. {{ joint_borrower2.name }}（{{ joint_borrower2.id_card }}）
3. {{ joint_borrower3.name }}（{{ joint_borrower3.id_card }}）
```

### 担保合同模板示例

```
担保人信息：
1. {{ guarantor1.name }}，身份证：{{ guarantor1.id_card }}，电话：{{ guarantor1.mobile }}
2. {{ guarantor2.name }}，身份证：{{ guarantor2.id_card }}，电话：{{ guarantor2.mobile }}
3. {{ guarantor3.name }}，身份证：{{ guarantor3.id_card }}，电话：{{ guarantor3.mobile }}
... 依此类推到第7个
```

### 抵押合同模板示例

```
抵押物清单：
1. 所有人：{{ collateral1.owner }}，类型：{{ collateral1.type }}
   价值：{{ collateral1.value }}，位置：{{ collateral1.location }}
   
2. 所有人：{{ collateral2.owner }}，类型：{{ collateral2.type }}
   价值：{{ collateral2.value }}，位置：{{ collateral2.location }}
```

## 优点

1. **简单**：不需要 Jinja2 循环和条件判断
2. **可靠**：不会有模板语法错误
3. **灵活**：想显示哪个就显示哪个
4. **清晰**：一目了然，容易修改

## 注意事项

- 如果某个位置没有数据（如只有2个担保人），对应变量会是空字典 `{}`
- 访问空字典的属性会显示为空白（不会报错）
- 例如：只有3个担保人时，`{{ guarantor4.name }}` 会显示为空
