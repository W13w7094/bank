import React, { useState, useEffect } from 'react';
import { Modal, Form, InputNumber, Select, Descriptions, Typography } from 'antd';
import { CalculatorOutlined } from '@ant-design/icons';

const { Text } = Typography;

interface LoanCalculatorProps {
    open: boolean;
    onCancel: () => void;
    initialAmount?: number;
    initialTerm?: number; // months
}

export const LoanCalculator: React.FC<LoanCalculatorProps> = ({
    open,
    onCancel,
    initialAmount = 100000,
    initialTerm = 12
}) => {
    const [form] = Form.useForm();
    const [result, setResult] = useState<any>(null);

    useEffect(() => {
        if (open) {
            form.setFieldsValue({
                amount: initialAmount,
                term: initialTerm,
                rate: 4.35, // Default LPR roughly
                method: 'equal_principal_interest'
            });
            handleCalculate();
        }
    }, [open, initialAmount, initialTerm]);

    const handleCalculate = () => {
        form.validateFields().then(values => {
            const { amount, term, rate, method } = values;
            const r = rate / 100 / 12; // Monthly rate
            const N = term;
            const P = amount;

            let res = {};

            if (r === 0) {
                // Zero interest case
                const monthly = P / N;
                res = {
                    monthly: monthly.toFixed(2),
                    totalInterest: "0.00",
                    total: P.toFixed(2),
                    firstMonth: monthly.toFixed(2),
                    desc: "无利息"
                };
            } else if (method === 'equal_principal_interest') { // 等额本息
                const monthly = (P * r * Math.pow(1 + r, N)) / (Math.pow(1 + r, N) - 1);
                const total = monthly * N;
                res = {
                    monthly: monthly.toFixed(2),
                    totalInterest: (total - P).toFixed(2),
                    total: total.toFixed(2),
                    firstMonth: monthly.toFixed(2),
                    desc: "每月还款金额固定"
                };
            } else if (method === 'equal_principal') { // 等额本金
                const monthlyP = P / N;
                const firstMonthInterest = P * r;
                const firstMonth = monthlyP + firstMonthInterest;
                // const lastMonth = monthlyP + (monthlyP * r); // Unused
                const totalInterest = (N + 1) * P * r / 2;
                const total = P + totalInterest;
                const diff = monthlyP * r;
                res = {
                    monthly: `首月 ${firstMonth.toFixed(2)}`,
                    monthlyDiff: `每月递减 ${diff.toFixed(2)}`,
                    totalInterest: totalInterest.toFixed(2),
                    total: total.toFixed(2),
                    firstMonth: firstMonth.toFixed(2),
                    desc: "首月还得最多，之后逐月递减"
                };
            } else if (method === 'interest_only') { // 按月付息
                const monthlyInterest = P * r;
                const totalInterest = monthlyInterest * N;
                res = {
                    monthly: monthlyInterest.toFixed(2),
                    totalInterest: totalInterest.toFixed(2),
                    total: (P + totalInterest).toFixed(2),
                    firstMonth: monthlyInterest.toFixed(2),
                    lastMonth: (P + monthlyInterest).toFixed(2),
                    desc: "每月只还利息，最后一期还本金+当月利息"
                };
            } else if (method === 'one_time') { // 利随本清
                const totalInterest = P * r * N;
                res = {
                    monthly: "0.00",
                    totalInterest: totalInterest.toFixed(2),
                    total: (P + totalInterest).toFixed(2),
                    firstMonth: "0.00",
                    lastMonth: (P + totalInterest).toFixed(2),
                    desc: "到期一次性还本付息"
                };
            }

            setResult(res);
        });
    };

    return (
        <Modal
            title={<><CalculatorOutlined /> 贷款还款试算</>}
            open={open}
            onCancel={onCancel}
            footer={null}
            width={600}
        >
            <Form
                form={form}
                layout="vertical"
                onValuesChange={handleCalculate}
                initialValues={{ rate: 4.35, method: 'equal_principal_interest' }}
            >
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                    <Form.Item label="贷款金额 (元)" name="amount">
                        <InputNumber style={{ width: '100%' }} />
                    </Form.Item>
                    <Form.Item label="贷款期限 (月)" name="term">
                        <InputNumber style={{ width: '100%' }} />
                    </Form.Item>
                    <Form.Item label="年利率 (%)" name="rate">
                        <InputNumber step={0.01} style={{ width: '100%' }} />
                    </Form.Item>
                    <Form.Item label="还款方式" name="method">
                        <Select>
                            <Select.Option value="equal_principal_interest">等额本息</Select.Option>
                            <Select.Option value="equal_principal">等额本金</Select.Option>
                            <Select.Option value="interest_only">按月付息，到期还本</Select.Option>
                            <Select.Option value="one_time">利随本清 (一次性还本付息)</Select.Option>
                        </Select>
                    </Form.Item>
                </div>
            </Form>

            {result && (
                <div style={{ background: '#f5f5f5', padding: '16px', borderRadius: '8px', marginTop: '16px' }}>
                    <Descriptions title="试算结果" column={1} bordered size="small">
                        <Descriptions.Item label="还款总额">
                            <Text strong style={{ fontSize: '18px', color: '#1677ff' }}>{result.total} 元</Text>
                        </Descriptions.Item>
                        <Descriptions.Item label="支付利息">
                            <Text type="danger">{result.totalInterest} 元</Text>
                        </Descriptions.Item>
                        <Descriptions.Item label="首月还款">
                            <Text strong>{result.firstMonth} 元</Text>
                        </Descriptions.Item>
                        {result.lastMonth && (
                            <Descriptions.Item label="末月还款">
                                {result.lastMonth} 元
                            </Descriptions.Item>
                        )}
                        <Descriptions.Item label="每月还款">
                            {result.monthly} {result.monthlyDiff && <Text type="secondary">({result.monthlyDiff})</Text>}
                        </Descriptions.Item>
                        <Descriptions.Item label="说明">
                            <Text type="secondary">{result.desc}</Text>
                        </Descriptions.Item>
                    </Descriptions>
                </div>
            )}
        </Modal>
    );
};
