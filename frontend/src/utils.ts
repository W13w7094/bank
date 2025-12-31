/**
 * 将数字金额转换为人民币大写
 * 例如: 123456.78 -> 壹拾贰万叁仟肆佰伍拾陆元柒角捌分
 */
export function numToChinese(num: number): string {
    if (num === 0) {
        return "零元整";
    }

    const CN_NUM = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖'];
    const CN_UNIT = ['', '拾', '佰', '仟'];
    const CN_SECTION = ['', '万', '亿', '兆']; // Sections for every 4 digits

    // Separate integer and decimal parts
    const intPart = Math.floor(num);
    const decimalPart = Math.round((num - intPart) * 100);

    // Convert integer part
    let intStr = intPart.toString();
    let result = '';

    // Process 4 digits at a time from right to left
    let zeroCount = 0;
    let sectionIndex = 0;

    while (intStr.length > 0) {
        let section = intStr.slice(-4); // Get last 4 chars
        intStr = intStr.slice(0, -4); // Remove last 4 chars

        let sectionResult = '';
        let sectionZero = true; // Track if this section is all zeros

        // Reverse to process from low to high within section
        const revSection = section.split('').reverse().join('');

        for (let i = 0; i < revSection.length; i++) {
            const digit = parseInt(revSection[i]);
            if (digit === 0) {
                zeroCount++;
            } else {
                sectionZero = false;
                if (zeroCount > 0) {
                    sectionResult = CN_NUM[0] + sectionResult;
                }
                zeroCount = 0;
                sectionResult = CN_NUM[digit] + CN_UNIT[i] + sectionResult;
            }
        }

        // Add section unit (Wan, Yi, etc.) if section is not empty or it's the only section (for 0 but checked at top)
        // Check if sectionResult is empty (all zeros in this section), but we need to handle "Zero" connecting sections?
        // Actually simplified: if section has value, append section unit.

        if (!sectionZero) {
            sectionResult += CN_SECTION[sectionIndex];
        }

        // Handling the zero between sections usually complex, but simplified:
        // if this section had value, and previous (higher) section has... wait.
        // Let's stick to standard append: result is built from low to high sections.

        // Correct logic for inter-section zero:
        // If current section has value, add it to result.
        // But need to handle leading zeros of lower section?
        // E.g. 10001 -> 1(Wan) 0001(Yuan) -> YW Ling Y.
        // With current loop logic:
        // 1st pass (0001): i=0(1)->Yi; i=1,2,3(0)->zeros. sectionResult="Yi".
        // 2nd pass (1): i=0(1)->Yi. sectionResult="YiWan".
        // Result = "YiWan" + "Yi". Need "Ling"?

        // Re-evaluating the zero logic.
        // It's easier to verify 100,000.
        // 1st pass (0000): all zero. sectionZero=true. sectionResult="".
        // 2nd pass (10): 0->zero; 1->YiShi. sectionResult="YiShiWan".
        // Result="YiShiWan". Correct.

        // 1,000,010: 
        // 1st pass (0010): 0(0)->0count; 1(1)->YiShi; ... -> YiShi.
        // 2nd pass (100): 0(0), 0(1), 1(2)->YiBai. -> YiBaiWan.
        // Result: YiBaiWanYiShi. (Should be Yi Bai Wan Ling Yi Shi).
        // To handle "Ling" between sections: if section < 1000 and section > 0 and exists higher section?

        // Let's use a robust implementation pattern.

        // Simple fix approach for now:
        // If intPart is 0 and we only have decimals, loop doesn't run, result empty.

        if (result.length > 0 && !sectionZero && section.length === 4 && parseInt(section) < 1000) {
            // This condition is tricky.
        }

        result = sectionResult + result;
        sectionIndex++;
    }

    // Fix pure zero
    if (result === '') result = CN_NUM[0];

    // Remove initial Ling if incorrectly added (though current logic avoids leading zero in sectionResult)
    // But need to handle "YiShi" (10) -> "YiShi".
    // 100010 -> YiShiWan Ling YiShi?

    // Current simple logic result for 100000 -> "YiShiWan". Correct.

    // Let's refine the zero handling for inter-section.
    // Actually, simply processing the full string with state machine is often cleaner.

    // Let's try the string index based approach again but corrected for units.

    // Resetting to a known working algorithm for 4-digit grouping.

    result = '';
    let str = intPart.toString();
    let len = str.length;
    let zero = false;

    for (let i = 0; i < len; i++) {
        let n = parseInt(str[i]);
        let p = len - i - 1; // position power
        let q = p / 4;
        let m = p % 4;

        if (n !== 0) {
            if (zero) {
                result += CN_NUM[0];
                zero = false;
            }
            result += CN_NUM[n] + CN_UNIT[m];
        } else {
            zero = true;
        }

        if (m === 0 && zero && result.length > 0) {
            // Handle end of section (Wan/Yi) when ending with 0
            // e.g. 100000 -> 1(0) 0 0 0 0 0
            // 5: 1 -> Yi + Shi.
            // 4: 0 -> zero=true. m=0. -> add Wan?
            // Yes, always add section unit if section is not empty?
            // But we need to know if the section had ANY value.
            // The previous logic was better for section tracking.
        }
        // ... this loop is hard to get right in one go.
    }

    // Going back to the split-4 method which is safer.
    // Implementing a simplified version that definitely works for 100,000.

    const unitOps = ['', '万', '亿', '兆'];
    let newResult = '';
    let sectionPos = 0;
    let strNum2 = intPart.toString();

    while (strNum2.length > 0) {
        let section = strNum2.slice(Math.max(0, strNum2.length - 4));
        strNum2 = strNum2.slice(0, Math.max(0, strNum2.length - 4));

        let sectionChinese = '';
        let hasValue = false;
        let zeroFlag = false; // trailing zero in section

        for (let j = 0; j < section.length; j++) {
            let digit = parseInt(section[j]);
            // Real index in section (from left)
            // But unit depends on position from right.
            let unitIdx = section.length - 1 - j;

            if (digit === 0) {
                zeroFlag = true;
            } else {
                if (zeroFlag) {
                    sectionChinese += CN_NUM[0];
                    zeroFlag = false;
                }
                hasValue = true;
                sectionChinese += CN_NUM[digit] + CN_UNIT[unitIdx];
            }
        }

        if (hasValue) {
            // Check if we need leading Zero for this section (if original section starts with 0 and there are higher sections)
            // e.g. 1 0001. Section "0001".
            if (section.length === 4 && section[0] === '0' && strNum2.length > 0) {
                // But wait, strNum2 is the HIGHER part.
                // If we have higher part, and THIS section starts with 0, we need Ling.
                // Actually the loop above handles internal zeros.
                // We need to handle connection.
                // If previous result (lower sections) exists? No.
                // If higher section exists (strNum2 > 0) AND current section < 1000?
                // No, standard is: 10001 -> Yi Wan Ling Yi.

                // If strNum2.length > 0 (there is a higher section), 
                // and this section's value < 1000 (meaning it has leading zeros as 4-digit block),
                // then pre-pend Ling? 
                // Wait, "Yi Wan" is higher. "Ling Yi" is lower.
                // We are building `newResult` from lower to higher?
                // Current loop builds from low section.

                // Correct: newResult = sectionChinese + unitOps[sectionPos] + newResult

                if (section.length === 4 && section[0] === '0' && newResult !== '') {
                    // This logic is for "10001" -> 1(Wan) 0001.
                    // Lower section is 0001. newResult is "".
                    // Higher section 1.
                    // When processing higher section, we see lower section had leading zero?
                    // No, easier to check when adding lower section to result.
                }
            }

            newResult = sectionChinese + unitOps[sectionPos] + newResult;

            // Add 'Ling' if needed between this section and the previous (lower) one?
            // Actually, usually 'Ling' is added at the START of the lower section if needed.
            // My loop handles internal zeros. Leading zeros of a section?
            // "0001" -> zeroFlag=true at start. -> adds Ling if next digit > 0.
            // If section is "0001", j=0(0)->zeroFlag. j=1(0), j=2(0). j=3(1)-> adds Ling + Yi + Unit(0).
            // So "Ling Yi". 
            // So 10001 -> "Yi" + "Wan" + "Ling Yi". -> "YiWanLingYi". Correct!
        } else {
            // Section is all zeros. e.g. 1 0000 0001.
            // Middle section empty.
            // If we have higher and lower, we need a Ling?
            // 100000001 -> Yi Yi Ling Yi.
            // If section is empty, we don't add Unit.
            // But we might need to prompt a Ling for the NEXT lower section?

            if (newResult.length > 0 && newResult[0] !== CN_NUM[0]) {
                newResult = CN_NUM[0] + newResult;
            }
        }

        sectionPos++;
    }

    // Result
    if (newResult === '') newResult = CN_NUM[0];
    // remove initial Ling if exists?? 
    // 10001 -> "YiWanLingYi".
    // 0001 -> "LingYi". Should be "Yi".
    // If pure number < 1, output "Ling Yuan"?
    // The intPart logic above handles leading zero of first section if num < 1.
    // But if num=1, section="1". Loop: 1->Yi. Result "Yi". Correct.

    // One edge case: 10 -> "YiShi".
    // Some prefer "Shi". Standard is "YiShi".

    // 100000 -> "10" "0000".
    // Lower: empty. zeroFlag?
    // Higher: 10 -> YiShi. + Wan.
    // Result: YiShiWan.

    // 1000000: "100" "0000". -> YiBaiWan.

    let finalStr = newResult;
    // Handle final cleanup
    while (finalStr.startsWith('零') && finalStr.length > 1) finalStr = finalStr.substring(1);

    // Yuan
    result = finalStr + '元';
    // Decimals
    if (decimalPart > 0) {
        let jiao = Math.floor(decimalPart / 10);
        let fen = decimalPart % 10;
        if (jiao > 0) result += CN_NUM[jiao] + '角';
        else if (fen > 0 && intPart > 0) result += '零'; // 1.01 -> Yi Yuan Ling Yi Fen

        if (fen > 0) result += CN_NUM[fen] + '分';
    } else {
        result += '整';
    }

    return result;
}
