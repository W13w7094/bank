import { useState, useEffect } from 'react';
import axios from 'axios';
import { numToChinese } from './utils';
import {
  Form, Input, Button, InputNumber, Card, Checkbox, message,
  Layout, Tabs, Switch, Row, Col, Space, ConfigProvider, Tag, Typography,
  Select, Divider, Radio, Upload, DatePicker, AutoComplete, Spin
} from 'antd';
import dayjs from 'dayjs';
import {
  PlusOutlined, DeleteOutlined, UserOutlined,
  TeamOutlined, PrinterOutlined, BankOutlined,
  SolutionOutlined, IdcardOutlined,
  ShopOutlined, AppstoreOutlined,
  DownOutlined, HomeOutlined, GoldOutlined, ImportOutlined,
  ReloadOutlined
} from '@ant-design/icons';



const { Header, Content } = Layout;
const { Title, Text } = Typography;

// --- 配置 ---
// 在开发环境使用固定端口，生产环境使用相对路径（自动适配动态端口）
const BASE_URL = import.meta.env.DEV ? "http://localhost:8090" : "";
const API_URL = `${BASE_URL}/api/generate`;
const BRANCH_API_URL = `${BASE_URL}/api/branches`;
const CONFIG_API_URL = `${BASE_URL}/api/config`;
const PRIMARY_COLOR = '#1677ff';

const RULES = {
  required: { required: true, message: '必填' },
  mobile: { pattern: /^1[3-9]\d{9}$/, message: '格式错误' },
  // 宽松正则，在 onValuesChange 里做严格计算
  id_card: { pattern: /^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$/, message: '身份证无效' },
};

// --- 工具函数 ---
const parseIdCard = (idCard: string) => {
  if (!idCard) return null;
  const cleanId = idCard.trim(); // ✨ 去空格
  if (cleanId.length !== 18) return null;

  // 校验正则
  const reg = /^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$/;
  if (!reg.test(cleanId)) return null;

  const birthdayStr = cleanId.substring(6, 14);
  const year = parseInt(birthdayStr.substring(0, 4));
  const month = parseInt(birthdayStr.substring(4, 6));
  const day = parseInt(birthdayStr.substring(6, 8));
  const birthday = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;

  const genderCode = parseInt(cleanId.charAt(16));
  const gender = genderCode % 2 === 1 ? '男' : '女';

  // Calculate Age
  const today = new Date();
  let age = today.getFullYear() - year;
  const m = today.getMonth() + 1 - month;
  if (m < 0 || (m === 0 && today.getDate() < day)) {
    age--;
  }

  return { birthday, gender, age };
};

const EditableSelect = ({ value, onChange, options, placeholder, disabled }: any) => (
  <AutoComplete
    value={value} onChange={onChange} options={options} placeholder={placeholder || "可输入或选择"} disabled={disabled}
    filterOption={(input, option) => (option!.value as string).toUpperCase().indexOf(input.toUpperCase()) !== -1}
    suffixIcon={<DownOutlined style={{ fontSize: 12, color: '#ccc' }} />}
  ><Input size="large" /></AutoComplete>
);

// 金额输入组件（带单位选择和大写显示）
const AmountInput = ({ value, onChange }: { value?: number; onChange?: (val: number) => void }) => {
  const [amount, setAmount] = useState<number>(value ? value / 10000 : 0);
  const [unit, setUnit] = useState<'yuan' | 'wan'>('wan'); // 默认万元

  useEffect(() => {
    if (value !== undefined) {
      // 根据单位显示
      setAmount(unit === 'wan' ? value / 10000 : value);
    }
  }, [value, unit]);

  const handleAmountChange = (val: number | null) => {
    const newAmount = val || 0;
    setAmount(newAmount);
    // 计算实际金额（元）
    const actualAmount = unit === 'wan' ? newAmount * 10000 : newAmount;
    onChange?.(actualAmount);
  };

  const handleUnitChange = (newUnit: 'yuan' | 'wan') => {
    const currentActual = unit === 'wan' ? amount * 10000 : amount;
    setUnit(newUnit);
    // 转换显示值
    const newAmount = newUnit === 'wan' ? currentActual / 10000 : currentActual;
    setAmount(newAmount);
  };

  // 计算实际金额（元）
  const actualAmount = unit === 'wan' ? amount * 10000 : amount;
  const chineseAmount = actualAmount > 0 ? numToChinese(actualAmount) : '';

  return (
    <Space direction="vertical" style={{ width: '100%' }} size={4}>
      <Input.Group compact>
        <InputNumber
          value={amount}
          onChange={handleAmountChange}
          style={{ width: '70%' }}
          size="large"
          min={0}
          precision={unit === 'wan' ? 4 : 2}
          placeholder="请输入金额"
        />
        <Select
          value={unit}
          onChange={handleUnitChange}
          style={{ width: '30%' }}
          size="large"
        >
          <Select.Option value="yuan">元</Select.Option>
          <Select.Option value="wan">万元</Select.Option>
        </Select>
      </Input.Group>
      {chineseAmount && (
        <Text type="secondary" style={{ fontSize: 12, display: 'block', paddingLeft: 11 }}>
          {chineseAmount}
        </Text>
      )}
    </Space>
  );
};



// --- 关键修复：个人画像组件 ---
// 接收 path (数组)，确保路径绝对正确
const PersonalAttributes = ({ path, isAuto = false, options }: { path: (string | number)[], isAuto?: boolean, options: any }) => (
  <>
    <Col span={6}><Form.Item shouldUpdate noStyle>{() => <Form.Item name={[...path, 'age']} label="年龄"><Input placeholder="自动" readOnly size="large" style={{ backgroundColor: '#f5f5f5', color: '#666' }} /></Form.Item>}</Form.Item></Col>
    <Col span={6}><Form.Item shouldUpdate noStyle>{() => <Form.Item name={[...path, 'gender']} label="性别"><Select options={[{ label: '男', value: '男' }, { label: '女', value: '女' }]} placeholder="自动" disabled={isAuto} size="large" /></Form.Item>}</Form.Item></Col>
    <Col span={6}><Form.Item shouldUpdate noStyle>{() => <Form.Item name={[...path, 'birthday']} label="生日"><Input placeholder="自动" disabled={isAuto} size="large" /></Form.Item>}</Form.Item></Col>
    <Col span={6}><Form.Item name={[...path, 'ethnicity']} label="民族"><EditableSelect options={options.ethnicity} placeholder="如：汉族" disabled={isAuto} /></Form.Item></Col>
    <Col span={6}><Form.Item name={[...path, 'education']} label="学历"><EditableSelect options={options.education} placeholder="如：本科" disabled={isAuto} /></Form.Item></Col>
    <Col span={12}><Form.Item name={[...path, 'occupation']} label="职业"><EditableSelect options={options.occupation} placeholder="如：农户" disabled={isAuto} /></Form.Item></Col>
  </>
);

const CollateralList = ({ options }: { options: any }) => (
  <Form.List name="collaterals">
    {(fields, { add, remove }) => (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {fields.map(({ key, name, ...restField }, index) => (
          <div key={key} style={{ background: '#fff', borderRadius: '8px', padding: '24px', borderLeft: `4px solid #faad14`, boxShadow: '0 2px 8px rgba(0,0,0,0.05)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
              <Space><Tag color="gold">#{index + 1}</Tag><Text strong>抵押物</Text></Space>
              <Button type="text" danger icon={<DeleteOutlined />} onClick={() => remove(name)}>移除</Button>
            </div>
            <Row gutter={16}>
              <Col span={8}><Form.Item {...restField} name={[name, 'owner']} label="所有权人" rules={[RULES.required]}><Input size="large" /></Form.Item></Col>
              <Col span={8}><Form.Item {...restField} name={[name, 'type']} label="类型" rules={[RULES.required]}><EditableSelect options={options.collateral_type} /></Form.Item></Col>
              <Col span={8}><Form.Item {...restField} name={[name, 'cert_no']} label="权证编号" rules={[RULES.required]}><Input size="large" /></Form.Item></Col>
              <Col span={24}><Form.Item {...restField} name={[name, 'location']} label="坐落位置" rules={[RULES.required]}><Input size="large" prefix={<HomeOutlined style={{ color: '#ccc' }} />} /></Form.Item></Col>
              <Col span={12}><Form.Item {...restField} name={[name, 'area']} label="建筑面积" rules={[RULES.required]}><Input size="large" suffix="平方米" /></Form.Item></Col>
              <Col span={12}><Form.Item {...restField} name={[name, 'land_area']} label="土地面积"><Input size="large" placeholder="如有" suffix="平方米" /></Form.Item></Col>
              <Col span={12}><Form.Item {...restField} name={[name, 'value']} label="抵押物价值" rules={[RULES.required]}><AmountInput /></Form.Item></Col>
            </Row>
          </div>
        ))}
        <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />} size="large" style={{ color: '#faad14', borderColor: '#faad14' }}>添加抵押物</Button>
      </div>
    )}
  </Form.List>
);

const PersonList = ({ name, label, color, options }: { name: string; label: string; color: string; options: any }) => (
  <Form.List name={name}>
    {(fields, { add, remove }) => (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {fields.map((field, index) => (
          <div key={field.key} style={{ background: '#fff', borderRadius: '8px', padding: '24px', borderLeft: `4px solid ${color}`, boxShadow: '0 2px 8px rgba(0,0,0,0.05)', position: 'relative' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
              <Space>
                <Tag color={color}>#{index + 1}</Tag>
                <Text strong>{label}</Text>
                {/* 标记是否为自动同步的配偶 */}
                <Form.Item shouldUpdate noStyle>
                  {({ getFieldValue }) => getFieldValue([name, field.name, 'is_spouse_auto']) ? <Tag color="blue">已关联配偶</Tag> : null}
                </Form.Item>
              </Space>
              <Button type="text" danger icon={<DeleteOutlined />} onClick={() => remove(field.name)}>移除</Button>
            </div>

            <Form.Item name={[field.name, 'is_spouse_auto']} hidden><Input /></Form.Item>

            {/* 证件类型选择 */}
            <Row gutter={16}>
              <Col span={24}>
                <Form.Item name={[field.name, 'id_type']} label="证件类型" initialValue="身份证">
                  <Radio.Group size="large" buttonStyle="solid">
                    <Radio.Button value="身份证">身份证(个人)</Radio.Button>
                    <Radio.Button value="营业执照">营业执照(企业)</Radio.Button>
                  </Radio.Group>
                </Form.Item>
              </Col>
            </Row>

            {/* 根据证件类型显示不同表单 */}
            <Form.Item noStyle shouldUpdate={(prev, cur) => prev[name]?.[field.name]?.id_type !== cur[name]?.[field.name]?.id_type}>
              {({ getFieldValue }) => {
                const idType = getFieldValue([name, field.name, 'id_type']) || '身份证';

                if (idType === '营业执照') {
                  // ========== 企业表单 ==========
                  return (
                    <Row gutter={16}>
                      <Col span={12}><Form.Item name={[field.name, 'name']} label="企业名称" rules={[RULES.required]}><Input size="large" prefix={<ShopOutlined />} /></Form.Item></Col>
                      <Col span={12}><Form.Item name={[field.name, 'id_card']} label="统一社会信用代码" rules={[RULES.required]}><Input size="large" /></Form.Item></Col>
                      <Col span={12}><Form.Item name={[field.name, 'legal_rep']} label="法人代表" rules={[RULES.required]}><Input size="large" prefix={<UserOutlined />} /></Form.Item></Col>
                      <Col span={12}><Form.Item name={[field.name, 'mobile']} label="联系电话" rules={[RULES.required, RULES.mobile]}><Input size="large" maxLength={11} /></Form.Item></Col>
                      <Col span={24}><Form.Item name={[field.name, 'address']} label="企业地址" rules={[RULES.required]}><Input size="large" prefix={<HomeOutlined style={{ color: '#ccc' }} />} /></Form.Item></Col>
                      <Col span={24}><Form.Item name={[field.name, 'relation']} label="关系（可选）"><Input size="large" placeholder="与借款人关系，可不填" /></Form.Item></Col>
                    </Row>
                  );
                } else {
                  // ========== 个人表单（原有逻辑） ==========
                  return (
                    <Row gutter={16}>
                      <Col span={8}><Form.Item name={[field.name, 'name']} label="姓名" rules={[RULES.required]}><Input size="large" /></Form.Item></Col>
                      <Col span={10}>
                        <Form.Item label="证件" required style={{ marginBottom: 0 }}>
                          <Input.Group compact>
                            <Form.Item name={[field.name, 'id_type']} noStyle initialValue="身份证"><Select style={{ width: '30%' }} size="large" options={[{ label: '身份证', value: '身份证' }, { label: '营业执照', value: '营业执照' }]} /></Form.Item>
                            <Form.Item name={[field.name, 'id_card']} noStyle rules={[RULES.required, RULES.id_card]}><Input style={{ width: '70%' }} size="large" placeholder="输入身份证自动计算" /></Form.Item>
                          </Input.Group>
                        </Form.Item>
                      </Col>
                      <Col span={6}><Form.Item name={[field.name, 'mobile']} label="手机" rules={[RULES.required, RULES.mobile]}><Input size="large" maxLength={11} /></Form.Item></Col>
                      <Col span={24}><Form.Item name={[field.name, 'address']} label="地址" rules={[RULES.required]}><Input size="large" /></Form.Item></Col>

                      <Col span={24}><Divider dashed style={{ margin: '8px 0' }} plain><span style={{ fontSize: 12, color: '#999' }}>更多信息</span></Divider></Col>
                      <Col span={6}><Form.Item name={[field.name, 'age']} label="年龄"><Input placeholder="自动" readOnly size="large" style={{ backgroundColor: '#f5f5f5', color: '#666' }} /></Form.Item></Col>
                      <Col span={6}><Form.Item name={[field.name, 'gender']} label="性别"><Select options={[{ label: '男', value: '男' }, { label: '女', value: '女' }]} placeholder="自动" size="large" /></Form.Item></Col>
                      <Col span={6}><Form.Item name={[field.name, 'birthday']} label="生日"><Input placeholder="自动" size="large" /></Form.Item></Col>
                      <Col span={6}><Form.Item name={[field.name, 'ethnicity']} label="民族"><EditableSelect options={options.ethnicity} placeholder="如：汉族" /></Form.Item></Col>
                      <Col span={6}><Form.Item name={[field.name, 'education']} label="学历"><EditableSelect options={options.education} placeholder="如：本科" /></Form.Item></Col>
                      <Col span={12}><Form.Item name={[field.name, 'occupation']} label="职业"><EditableSelect options={options.occupation} placeholder="如：农户" /></Form.Item></Col>
                      <Col span={12}> <Form.Item name={[field.name, 'relation']} label="关系（可选）"><Input size="large" placeholder="与借款人关系" /></Form.Item></Col>
                    </Row>
                  );
                }
              }}
            </Form.Item>
          </div>
        ))}
        <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />} size="large" style={{ color: color, borderColor: color }}>手动添加{label}</Button>
      </div>
    )}
  </Form.List>
);

// --- 主程序 ---
function App() {
  const [loading, setLoading] = useState(false);
  const [initLoading, setInitLoading] = useState(true);
  const [hasSpouse, setHasSpouse] = useState(false);
  const [syncSpouse, setSyncSpouse] = useState(true);
  const [customerType, setCustomerType] = useState<'personal' | 'enterprise'>('personal');
  const [loanType, setLoanType] = useState<'credit' | 'guarantee' | 'mortgage'>('guarantee');
  const [templateSearch, setTemplateSearch] = useState('');  // New: template search
  const [branchList, setBranchList] = useState<any[]>([]);
  const [branchOptions, setBranchOptions] = useState<any[]>([]);
  const [systemOptions, setSystemOptions] = useState<any>({ education: [], ethnicity: [], occupation: [], loan_use: [], collateral_type: [] });
  const [allTemplates, setAllTemplates] = useState<any[]>([]);

  // No OCR states needed

  // 到期客户相关状态
  const [customerSource, setCustomerSource] = useState<'new' | 'existing'>('new');
  const [customerList, setCustomerList] = useState<any[]>([]);

  const [form] = Form.useForm();

  // 1. 初始化
  useEffect(() => {
    const initData = async () => {
      try {
        const [branchRes, configRes, customersRes] = await Promise.all([
          axios.get(BRANCH_API_URL),
          axios.get(CONFIG_API_URL),
          axios.get(`${BASE_URL}/api/customers`)
        ]);
        if (Array.isArray(branchRes.data)) {
          setBranchList(branchRes.data);
          setBranchList(branchRes.data);
          setBranchOptions(branchRes.data.map((b: any) => ({ label: `${b.name} (${b.short_name || '无简称'})`, value: b.name })));
        }
        if (configRes.data) {
          const opts = configRes.data.options;
          setSystemOptions({
            education: (opts.education || []).map((v: string) => ({ value: v })),
            ethnicity: (opts.ethnicity || []).map((v: string) => ({ value: v })),
            occupation: (opts.occupation || []).map((v: string) => ({ value: v })),
            loan_use: (opts.loan_use || []).map((v: string) => ({ value: v })),
            collateral_type: (opts.collateral_type || []).map((v: string) => ({ value: v })),
          });
          setAllTemplates(configRes.data.templates || []);
        }
        // 加载到期客户列表
        if (customersRes.data && customersRes.data.customers) {
          setCustomerList(customersRes.data.customers);
        }
      } catch (err) { } finally { setInitLoading(false); }
    };
    initData();
  }, []);

  // 2. 导入
  const handleImport = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const content = e.target?.result as string;
        const match = content.match(/SYSTEM_DATA_START:(.*):SYSTEM_DATA_END/);
        if (match && match[1]) {
          const utf8Json = new TextDecoder().decode(Uint8Array.from(atob(match[1]), c => c.charCodeAt(0)));
          const data = JSON.parse(utf8Json);

          // 设置基础状态
          setCustomerType(data.customer_type || 'personal');
          setLoanType(data.loan_type || 'guarantee');
          if (data.spouse) setHasSpouse(true);

          // 转换日期格式
          if (data.start_date) data.start_date = dayjs(data.start_date);
          if (data.end_date) data.end_date = dayjs(data.end_date);

          console.log('Parsed Import Data:', data);

          // ✨✨✨ 关键修复：分步骤设置表单，确保列表字段正确初始化 ✨✨✨
          form.resetFields();

          // 先设置所有数据
          form.setFieldsValue(data);

          // ✨ 强制触发列表字段的重新渲染和验证
          // 这样 Form.List 可以正确识别初始值
          setTimeout(() => {
            // 再次设置一遍列表字段，确保它们被 Form.List 正确捕获
            if (data.guarantors) {
              form.setFieldValue('guarantors', data.guarantors);
            }
            if (data.joint_borrowers) {
              form.setFieldValue('joint_borrowers', data.joint_borrowers);
            }
            if (data.collaterals) {
              form.setFieldValue('collaterals', data.collaterals);
            }

            // 触发表单验证，确保所有字段状态同步
            form.validateFields().catch(() => { });
          }, 100);

          message.success('数据导入成功！');
        } else { message.error('未找到存档数据'); }
      } catch (err) { message.error('文件解析失败'); }
    };
    reader.readAsText(file);
    return false;
  };

  // 选择到期客户并自动填充
  const handleSelectCustomer = (idCard: string) => {
    const customer = customerList.find(c => c.main_id_card === idCard);
    if (!customer) return;

    // 填充支行
    const branch = branchList.find(b => b.short_name === customer.branch_short_name);
    if (branch) {
      form.setFieldsValue({ branch });
    }

    // 填充主借款人
    form.setFieldsValue({
      main_borrower: {
        name: customer.main_name,
        id_card: customer.main_id_card,
        mobile: customer.main_mobile,
        address: customer.main_address
      }
    });

    // 填充配偶（如果有）
    if (customer.spouse_name && customer.spouse_name !== 'nan' && customer.spouse_name.trim()) {
      setHasSpouse(true);
      form.setFieldsValue({
        spouse: {
          name: customer.spouse_name,
          id_card: customer.spouse_id_card,
          mobile: customer.spouse_mobile
        }
      });
    }

    // 填充担保人（如果有）
    if (customer.guarantors && customer.guarantors.length > 0) {
      form.setFieldsValue({
        guarantors: customer.guarantors
      });
    }

    message.success('客户信息已自动填充！');
  };

  // No separate investigation report handler needed



  // ✨✨✨ 核心：强力表单监听 ✨✨✨
  const onFormValuesChange = (changedValues: any, allValues: any) => {

    // 通用计算器
    const calcAndSet = (idCard: string, prefixPath: (string | number)[]) => {
      const info = parseIdCard(idCard);
      if (info) {
        form.setFieldValue([...prefixPath, 'gender'], info.gender);
        form.setFieldValue([...prefixPath, 'birthday'], info.birthday);
        form.setFieldValue([...prefixPath, 'age'], String(info.age));  // 转换为字符串
      }
    };

    // 1. 主贷人
    if (changedValues.main_borrower?.id_card) {
      calcAndSet(changedValues.main_borrower.id_card, ['main_borrower']);
    }

    // 2. 配偶 (变更时同时触发同步)
    if (changedValues.spouse) {
      if (changedValues.spouse.id_card) {
        calcAndSet(changedValues.spouse.id_card, ['spouse']);
      }
      if (syncSpouse && hasSpouse) {
        updateSpouseInJointList(allValues.spouse, allValues.main_borrower?.address);
      }
    }

    // 3. 列表监听 (担保人/共借人)
    // Antd Form.List 的变更可能是数组，也可能是对象（取决于操作类型）
    // 我们遍历变更对象，如果发现是数组且包含 id_card，就触发计算
    const checkList = (listName: string) => {
      const listChanges = changedValues[listName];
      if (!listChanges) return;

      // Antd Form.List 变更可能是数组或稀疏对象（如 {0: {id_card: "xxx"}}）
      if (Array.isArray(listChanges)) {
        listChanges.forEach((item: any, index: number) => {
          if (item && item.id_card) {
            calcAndSet(item.id_card, [listName, index]);
          }
        });
      } else if (typeof listChanges === 'object') {
        // 处理稀疏对象情况
        Object.keys(listChanges).forEach((key) => {
          const index = parseInt(key);
          const item = listChanges[key];
          if (!isNaN(index) && item && item.id_card) {
            calcAndSet(item.id_card, [listName, index]);
          }
        });
      }
    };
    checkList('guarantors');
    checkList('joint_borrowers');

    // 4. 地址回显 (主贷人 -> 配偶)
    if (changedValues.main_borrower?.address) {
      const currentSpouseAddr = form.getFieldValue(['spouse', 'address']);
      if (!currentSpouseAddr) {
        form.setFieldValue(['spouse', 'address'], changedValues.main_borrower.address);
      }
    }

    // 5. 日期计算
    if (changedValues.start_date || changedValues.loan_term) {
      if (allValues.start_date && allValues.loan_term) {
        form.setFieldValue('end_date', dayjs(allValues.start_date).add(allValues.loan_term, 'month').subtract(1, 'day'));
      }
    }
  };

  // ✨✨✨ 修复：同步配偶时强制计算一次 ✨✨✨
  const updateSpouseInJointList = (spouseData: any, mainAddr: string) => {
    if (!spouseData || !spouseData.name) return;

    let currentJointBorrowers = form.getFieldValue('joint_borrowers') || [];

    if (syncSpouse && hasSpouse && spouseData) { // Changed `spouse` to `spouseData`
      if (!currentJointBorrowers) currentJointBorrowers = [];

      // 查找已存在的自动同步配偶（优先用 is_spouse_auto 标记查找）
      const spouseIndex = currentJointBorrowers.findIndex((jb: any) => jb.is_spouse_auto === true);

      // Get current spouse info from form to ensure latest calculated fields are used
      const currentSpouseFormValues = form.getFieldValue('spouse') || {};
      const extraInfo = {
        gender: currentSpouseFormValues.gender,
        birthday: currentSpouseFormValues.birthday,
        age: currentSpouseFormValues.age,
      };

      const spouseAsBorrower = {
        ...spouseData,
        ...extraInfo, // 覆盖性别/生日/年龄
        age: extraInfo.age ? String(extraInfo.age) : (spouseData.age ? String(spouseData.age) : ''), // 强制转字符串
        relation: '夫妻',
        is_spouse_auto: true,
        address: spouseData.address || mainAddr // Added address from spouseData or mainAddr
      };

      if (spouseIndex > -1) {
        // Update existing
        const newJointBorrowers = [...currentJointBorrowers];
        newJointBorrowers[spouseIndex] = { ...newJointBorrowers[spouseIndex], ...spouseAsBorrower };
        form.setFieldsValue({ joint_borrowers: newJointBorrowers });
      } else {
        // Add to beginning
        form.setFieldsValue({ joint_borrowers: [spouseAsBorrower, ...currentJointBorrowers] });
      }
    }
  };

  const removeSpouseFromJointList = () => {
    const jointList = form.getFieldValue('joint_borrowers') || [];
    const newList = jointList.filter((item: any) => item.is_spouse_auto !== true);
    form.setFieldValue('joint_borrowers', newList);
  };

  // 开关控制
  const handleHasSpouseChange = (checked: boolean) => {
    setHasSpouse(checked);
    if (!checked) {
      form.setFieldValue('spouse', null);
      removeSpouseFromJointList();
    } else {
      if (syncSpouse) {
        const all = form.getFieldsValue();
        updateSpouseInJointList(all.spouse, all.main_borrower?.address);
      }
    }
  };

  const handleSyncSpouseChange = (e: any) => {
    const checked = e.target.checked;
    setSyncSpouse(checked);
    if (checked) {
      const all = form.getFieldsValue();
      updateSpouseInJointList(all.spouse, all.main_borrower?.address);
    } else {
      removeSpouseFromJointList();
    }
  };

  const onFinish = async (values: any) => {
    setLoading(true);
    values.customer_type = customerType;
    values.loan_type = loanType;
    if (!hasSpouse) values.spouse = null;
    if (values.start_date) values.start_date = values.start_date.format('YYYY-MM-DD');
    if (values.end_date) values.end_date = values.end_date.format('YYYY-MM-DD');

    // 处理抵押物面积单位
    if (values.collaterals && Array.isArray(values.collaterals)) {
      values.collaterals = values.collaterals.map((c: any) => ({
        ...c,
        area: c.area && !c.area.includes('平方米') ? `${c.area}平方米` : c.area,
        land_area: c.land_area && !c.land_area.includes('平方米') ? `${c.land_area}平方米` : c.land_area,
      }));
    }

    try {
      console.log('=== 提交的数据 ===', JSON.stringify(values, null, 2));
      const response = await axios.post(API_URL, values, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${customerType === 'personal' ? values.main_borrower.name : values.enterprise.name}_贷款合同包.zip`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      message.success('生成成功！(含 .txt 存档)');
    } catch (error: any) {
      // 详细的错误处理 - 处理Blob响应
      if (error.response) {
        const status = error.response.status;

        if (status === 422) {
          // 数据验证错误 - Blob需要转换为JSON
          if (error.response.data instanceof Blob) {
            error.response.data.text().then((text: string) => {
              try {
                const jsonData = JSON.parse(text);
                console.log('解析后的422错误:', jsonData);

                if (jsonData.detail && Array.isArray(jsonData.detail)) {
                  let msg = '数据验证失败：\n';
                  jsonData.detail.forEach((err: any) => {
                    const field = err.loc ? err.loc.join('.') : '未知字段';
                    msg += `- ${field}: ${err.msg}\n`;
                  });
                  message.error(msg, 8);
                } else if (typeof jsonData.detail === 'string') {
                  message.error(jsonData.detail, 5);
                } else {
                  message.error('请检查所有必填字段是否已填写', 5);
                }
              } catch (e) {
                console.error('解析Blob错误:', e);
                message.error('请检查所有必填字段是否已填写', 5);
              }
            });
          } else if (error.response.data?.detail) {
            // 非Blob的情况
            const details = error.response.data.detail;
            let errorMsg = '数据验证失败：\n';
            if (Array.isArray(details)) {
              details.forEach((err: any) => {
                const field = err.loc ? err.loc.join('.') : '未知字段';
                errorMsg += `- ${field}: ${err.msg}\n`;
              });
            } else if (typeof details === 'string') {
              errorMsg = details;
            }
            message.error(errorMsg, 5);
          } else {
            message.error('请检查所有必填字段是否已填写', 5);
          }
        } else if (status === 500) {
          // 服务器错误
          if (error.response.data instanceof Blob) {
            error.response.data.text().then((text: string) => {
              try {
                const jsonData = JSON.parse(text);
                message.error(`生成失败: ${jsonData.detail || '服务器内部错误'}`, 5);
              } catch (e) {
                message.error('生成失败: 服务器内部错误', 5);
              }
            });
          } else {
            const errorDetail = error.response.data?.detail || '服务器内部错误';
            message.error(`生成失败: ${errorDetail}`, 5);
          }
        } else {
          message.error(`请求失败 (${status})`, 3);
        }
      } else if (error.request) {
        message.error('无法连接到服务器，请检查后端是否运行');
      } else {
        message.error(`发生错误: ${error.message}`);
      }
      console.error('生成错误:', error);
    } finally {
      setLoading(false);
    }

  };

  const filteredTemplates = allTemplates.filter(t => {
    // Filter by type
    if (t.type !== 'both' && t.type !== customerType) return false;
    // Filter by loan type
    if (loanType === 'credit' && t.need_guarantee) return false;
    // Filter by search text
    if (templateSearch && !t.label.toLowerCase().includes(templateSearch.toLowerCase())) {
      return false;
    }
    return true;
  });

  // Helper to get file extension and type
  const getTemplateInfo = (filename: string) => {
    const ext = filename.split('.').pop()?.toUpperCase() || '';
    const isExcel = ext === 'XLSX' || ext === 'XLS';
    return { ext, isExcel, color: isExcel ? '#52c41a' : '#1890ff' };
  };

  const getTabItems = () => [
    {
      key: '1', label: <span style={{ padding: '0 8px' }}><BankOutlined /> 业务与主贷人</span>,
      children: (
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* 客户来源选择 */}
          <Card style={{ borderRadius: 12, background: '#f0f5ff', border: '1px solid #adc6ff' }}>
            <Row gutter={16}>
              <Col span={8}>
                <Form.Item label="客户来源">
                  <Radio.Group value={customerSource} onChange={e => setCustomerSource(e.target.value)} buttonStyle="solid">
                    <Radio.Button value="new">新客户</Radio.Button>
                    <Radio.Button value="existing">到期客户</Radio.Button>
                  </Radio.Group>
                </Form.Item>
              </Col>
              {customerSource === 'existing' && (
                <Col span={16}>
                  <Form.Item label="选择客户">
                    <Select
                      showSearch
                      placeholder="搜索客户姓名或证件号"
                      size="large"
                      options={customerList.map(c => ({
                        label: `${c.main_name} (${c.main_id_card}) - ${c.branch_short_name}`,
                        value: c.main_id_card
                      }))}
                      onChange={handleSelectCustomer}
                      filterOption={(input, option) =>
                        (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                      }
                    />
                  </Form.Item>
                </Col>
              )}
            </Row>
          </Card>

          <Card style={{ borderRadius: 12, background: '#f5faff', border: '1px solid #adc6ff' }}>
            <Row gutter={24}>
              <Col span={12}><Form.Item label="客户主体"><Radio.Group value={customerType} onChange={e => { setCustomerType(e.target.value); form.setFieldsValue({ selected_templates: [] }); }} buttonStyle="solid"><Radio.Button value="personal">个人客户</Radio.Button><Radio.Button value="enterprise">企业/对公</Radio.Button></Radio.Group></Form.Item></Col>
              <Col span={12}><Form.Item label="担保方式"><Radio.Group value={loanType} onChange={e => { setLoanType(e.target.value); form.setFieldsValue({ selected_templates: [] }); }} buttonStyle="solid"><Radio.Button value="guarantee">保证/抵押</Radio.Button><Radio.Button value="credit">信用</Radio.Button></Radio.Group></Form.Item></Col>
            </Row>
          </Card>
          <Card title="支行信息" bordered={false} style={{ borderRadius: 12 }}>
            <Row gutter={24}>
              <Col span={24}><Form.Item name={['branch', 'name']} label="办理支行" rules={[RULES.required]}><Select placeholder="请选择..." options={branchOptions} size="large" showSearch optionFilterProp="label" onChange={(v) => { const b = branchList.find(i => i.name === v); if (b) form.setFieldsValue({ branch: b }) }} /></Form.Item></Col>
              <Col span={8}><Form.Item name={['branch', 'short_name']} label="支行简称"><Input readOnly variant="filled" /></Form.Item></Col>
              <Col span={8}><Form.Item name={['branch', 'manager']} label="负责人"><Input readOnly variant="filled" /></Form.Item></Col>
              <Col span={8}><Form.Item name={['branch', 'phone']} label="电话"><Input readOnly variant="filled" /></Form.Item></Col>
              <Col span={8}><Form.Item name={['branch', 'address']} label="地址"><Input readOnly variant="filled" /></Form.Item></Col>
            </Row>
          </Card>
          {customerType === 'personal' ? (
            <Card title="个人借款人信息" bordered={false} style={{ borderRadius: 12 }}>
              <Row gutter={24}>
                <Col span={8}><Form.Item name={['main_borrower', 'name']} label="姓名" rules={[RULES.required]}><Input size="large" prefix={<UserOutlined style={{ color: '#bfbfbf' }} />} /></Form.Item></Col>
                <Col span={10}>
                  <Form.Item label="证件信息" required style={{ marginBottom: 0 }}>
                    <Input.Group compact>
                      <Form.Item name={['main_borrower', 'id_type']} noStyle initialValue="身份证"><Select style={{ width: '30%' }} size="large" options={[{ label: '身份证', value: '身份证' }]} /></Form.Item>
                      <Form.Item name={['main_borrower', 'id_card']} noStyle rules={[RULES.required, RULES.id_card]}><Input style={{ width: '70%' }} size="large" prefix={<IdcardOutlined style={{ color: '#bfbfbf' }} />} /></Form.Item>
                    </Input.Group>
                  </Form.Item>
                </Col>
                <Col span={6}><Form.Item name={['main_borrower', 'mobile']} label="手机" rules={[RULES.required, RULES.mobile]}><Input size="large" maxLength={11} /></Form.Item></Col>
                <Col span={24}><Form.Item name={['main_borrower', 'address']} label="地址" rules={[RULES.required]}><Input size="large" /></Form.Item></Col>
                <Col span={24}><Divider style={{ borderColor: '#eee', fontSize: 14, color: '#666' }}>详细信息</Divider></Col>
                <PersonalAttributes path={['main_borrower']} isAuto={false} options={systemOptions} />
              </Row>
              <Divider style={{ margin: '16px 0' }} />

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                  <Text strong>配偶信息：</Text>
                  <Switch checked={hasSpouse} onChange={handleHasSpouseChange} checkedChildren="有" unCheckedChildren="无" />
                </div>
                {hasSpouse && (
                  <Checkbox checked={syncSpouse} onChange={handleSyncSpouseChange}>
                    同时作为共同借款人
                  </Checkbox>
                )}
              </div>

              {hasSpouse && (
                <div style={{ background: '#fff0f6', padding: '24px', borderRadius: 8, border: '1px solid #ffadd2' }}>
                  <Row gutter={24}>
                    <Col span={6}><Form.Item name={['spouse', 'name']} label="配偶姓名" rules={[RULES.required]}><Input size="large" /></Form.Item></Col>
                    <Col span={6}><Form.Item name={['spouse', 'mobile']} label="手机" rules={[RULES.required, RULES.mobile]}><Input size="large" maxLength={11} /></Form.Item></Col>
                    <Col span={12}>
                      <Form.Item label="证件" required style={{ marginBottom: 0 }}>
                        <Input.Group compact>
                          <Form.Item name={['spouse', 'id_type']} noStyle initialValue="身份证"><Select style={{ width: '30%' }} size="large" options={[{ label: '身份证', value: '身份证' }]} /></Form.Item>
                          <Form.Item name={['spouse', 'id_card']} noStyle rules={[RULES.required, RULES.id_card]}><Input style={{ width: '70%' }} size="large" placeholder="自动计算性别生日" /></Form.Item>
                        </Input.Group>
                      </Form.Item>
                    </Col>
                    <PersonalAttributes path={['spouse']} isAuto={false} options={systemOptions} />
                  </Row>
                </div>
              )}
            </Card>
          ) : (
            <Card title="企业信息" bordered={false} style={{ borderRadius: 12, borderTop: '4px solid #faad14' }}><Row gutter={24}><Col span={12}><Form.Item name={['enterprise', 'name']} label="名称" rules={[RULES.required]}><Input size="large" prefix={<ShopOutlined />} /></Form.Item></Col><Col span={12}><Form.Item name={['enterprise', 'credit_code']} label="统信代码" rules={[RULES.required]}><Input size="large" /></Form.Item></Col><Col span={8}><Form.Item name={['enterprise', 'legal_rep']} label="法人" rules={[RULES.required]}><Input size="large" prefix={<UserOutlined />} /></Form.Item></Col><Col span={16}><Form.Item name={['enterprise', 'address']} label="地址" rules={[RULES.required]}><Input size="large" /></Form.Item></Col></Row></Card>
          )}
        </Space>
      )
    },
    { key: '2', label: <span style={{ padding: '0 8px' }}><SolutionOutlined /> 共同借款人</span>, children: <PersonList name="joint_borrowers" label="共同借款人" color="#13c2c2" options={systemOptions} /> },
    loanType !== 'credit' && { key: '3', label: <span style={{ padding: '0 8px' }}><GoldOutlined /> 抵押物</span>, children: <CollateralList options={systemOptions} /> },
    loanType !== 'credit' && { key: '4', label: <span style={{ padding: '0 8px' }}><TeamOutlined /> 担保人</span>, children: <PersonList name="guarantors" label="担保人" color="#52c41a" options={systemOptions} /> },
    {
      key: '5', label: <span style={{ padding: '0 8px' }}><PrinterOutlined /> 生成</span>,
      children: (
        <Card bordered={false} style={{ borderRadius: 12 }}>
          <Title level={5}>业务参数</Title>
          <Row gutter={24}>
            <Col span={8}><Form.Item name="loan_amount" label="贷款金额" rules={[RULES.required]}><AmountInput /></Form.Item></Col>
            <Col span={16}><Form.Item name="loan_use" label="用途" rules={[RULES.required]}><EditableSelect options={systemOptions.loan_use} /></Form.Item></Col>
            <Col span={6}><Form.Item name="loan_term" label="期限(月)" rules={[RULES.required]}><InputNumber style={{ width: '100%' }} size="large" /></Form.Item></Col>
            <Col span={5}><Form.Item name="start_date" label="起始日" rules={[RULES.required]}><DatePicker size="large" style={{ width: '100%' }} /></Form.Item></Col>
            <Col span={5}><Form.Item name="end_date" label="到期日" rules={[RULES.required]}><DatePicker size="large" style={{ width: '100%' }} /></Form.Item></Col>
          </Row>
          <Divider />
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <Title level={5} style={{ margin: 0 }}>选择模板</Title>
            <Input.Search
              placeholder="搜索模板..."
              allowClear
              style={{ width: 300 }}
              value={templateSearch}
              onChange={e => setTemplateSearch(e.target.value)}
            />
          </div>
          <Form.Item name="selected_templates" rules={[{ required: true, message: '请选择模板' }]}>
            <Checkbox.Group style={{ width: '100%' }}>
              <Row gutter={[16, 16]}>
                {filteredTemplates.map(t => {
                  const info = getTemplateInfo(t.filename);
                  return (
                    <Col span={12} key={t.value}>
                      <div style={{
                        border: '1px solid #f0f0f0',
                        padding: '16px',
                        borderRadius: '8px',
                        background: '#fafafa',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between'
                      }}>
                        <Checkbox value={t.value}>{t.label}</Checkbox>
                        <Tag color={info.color}>{info.ext}</Tag>
                      </div>
                    </Col>
                  );
                })}
              </Row>
            </Checkbox.Group>
          </Form.Item>
          {filteredTemplates.length === 0 && (
            <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
              <Text type="secondary">未找到匹配的模板</Text>
            </div>
          )}
          <Button type="primary" htmlType="submit" size="large" block loading={loading} icon={<PrinterOutlined />} style={{ height: '56px', fontSize: '18px', marginTop: 32 }}>一键生成文件</Button>
        </Card>
      )
    }
  ].filter(Boolean);

  if (initLoading) return <div style={{ height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center' }}><Spin size="large" tip="系统初始化中..." /></div>;

  return (
    <ConfigProvider theme={{ token: { colorPrimary: PRIMARY_COLOR, borderRadius: 6 } }}>
      <Layout style={{ minHeight: '100vh' }}>
        <Header style={{ padding: '0 32px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', boxShadow: '0 2px 8px #f0f1f2', zIndex: 10 }}>
          <div style={{ display: 'flex', alignItems: 'center' }}><AppstoreOutlined style={{ fontSize: 28, color: PRIMARY_COLOR, marginRight: 12 }} /><Title level={4} style={{ margin: 0 }}>信贷合同系统 Pro</Title></div>
          <Space>
            <Upload beforeUpload={handleImport} showUploadList={false} accept=".txt"><Button icon={<ImportOutlined />}>导入存档 (.txt)</Button></Upload>
            <Button icon={<ReloadOutlined />} onClick={() => window.location.reload()}>重置</Button>
            <Tag color="green">v1.2 调查报告</Tag>
          </Space>
        </Header>
        <Content style={{ padding: '24px' }}>
          <Row justify="center">
            <Col span={18}>
              <Form form={form} layout="vertical" onFinish={onFinish} onValuesChange={onFormValuesChange}>
                <Tabs defaultActiveKey="1" items={getTabItems() as any} type="line" size="large" />
              </Form>
            </Col>
          </Row>
        </Content>

      </Layout>
    </ConfigProvider>
  );
}

export default App;