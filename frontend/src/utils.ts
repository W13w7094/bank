/**
 * 将数字金额转换为人民币大写
 * 例如: 123456.78 -> 壹拾贰万叁仟肆佰伍拾陆元柒角捌分
 */
export function numToChinese(num: number): string {
    if (num === 0) {
        return "零元整";
    }

    // 中文数字
    const CN_NUM = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖'];
    const CN_UNIT = ['', '拾', '佰', '仟', '万', '拾', '佰', '仟', '亿'];

    // 分离整数和小数部分
    const intPart = Math.floor(num);
    const decimalPart = Math.round((num - intPart) * 100); // 转为分

    // 将数字转为字符串并反转以方便处理
    const strNum = intPart.toString().split('').reverse();
    let result = '';

    for (let i = 0; i < strNum.length; i++) {
        const d = parseInt(strNum[i]);
        if (d !== 0) {
            result = CN_NUM[d] + CN_UNIT[i] + result;
        } else {
            // 只在需要时添加零
            if (result && !result.startsWith('零')) {
                result = '零' + result;
            }
        }
    }

    // 清除末尾的零
    result = result.replace(/零+$/, '');

    // 添加"元"
    if (result) {
        result += '元';
    } else {
        result = '零元';
    }

    // 处理角分
    if (decimalPart > 0) {
        const jiao = Math.floor(decimalPart / 10);
        const fen = decimalPart % 10;

        if (jiao > 0) {
            result += CN_NUM[jiao] + '角';
        } else if (fen > 0) {
            result += '零';
        }

        if (fen > 0) {
            result += CN_NUM[fen] + '分';
        }
    } else {
        result += '整';
    }

    return result;
}
