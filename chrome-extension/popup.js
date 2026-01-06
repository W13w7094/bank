// TXT文件解析
function parseTxtFile(content) {
    const match = content.match(/SYSTEM_DATA_START:(.*):SYSTEM_DATA_END/);
    if (match && match[1]) {
        try {
            // Base64解码
            const base64Data = match[1];
            // 将Base64字符串转换为Uint8Array
            const binaryString = atob(base64Data);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }
            // UTF-8解码
            const decoder = new TextDecoder('utf-8');
            const jsonString = decoder.decode(bytes);
            // 解析JSON
            return JSON.parse(jsonString);
        } catch (e) {
            console.error('解析失败:', e);
            return null;
        }
    }
    return null;
}

// 复制到剪贴板
async function copyToClipboard(text, button) {
    try {
        await navigator.clipboard.writeText(text);
        button.textContent = '✓ 已复制';
        button.classList.add('copied');
        setTimeout(() => {
            button.textContent = '复制';
            button.classList.remove('copied');
        }, 1500);
    } catch (err) {
        button.textContent = '失败';
    }
}

// 创建字段行
function createFieldRow(label, value) {
    if (!value || value === 'undefined') return '';
    return `
    <div class="field-row">
      <div class="field-label">${label}</div>
      <div class="field-value">${value}</div>
      <button class="copy-btn" data-value="${String(value).replace(/"/g, '&quot;')}">复制</button>
    </div>
  `;
}

// 渲染数据
function renderData(data) {
    const container = document.getElementById('data-container');
    container.innerHTML = '';

    // 基本信息
    const basicCard = document.createElement('div');
    basicCard.className = 'data-card';
    basicCard.innerHTML = `
    <div class="card-title">📋 基本信息</div>
    ${createFieldRow('客户类型', data.customer_type === 'enterprise' ? '企业/对公' : '个人')}
    ${createFieldRow('贷款类型', data.loan_type)}
    ${createFieldRow('贷款金额', data.loan_amount)}
    ${createFieldRow('贷款期限', data.loan_term + '个月')}
    ${createFieldRow('起始日期', data.start_date)}
    ${createFieldRow('到期日期', data.end_date)}
  `;
    container.appendChild(basicCard);

    // 主借款人
    if (data.main_borrower) {
        const mb = data.main_borrower;
        const mainCard = document.createElement('div');
        mainCard.className = 'data-card';
        mainCard.innerHTML = `
      <div class="card-title">👤 主借款人</div>
      ${createFieldRow('姓名', mb.name)}
      ${createFieldRow('证件号', mb.id_card)}
      ${createFieldRow('联系电话', mb.mobile)}
      ${createFieldRow('地址', mb.address)}
    `;
        container.appendChild(mainCard);
    }

    // 配偶
    if (data.spouse && data.spouse.name) {
        const sp = data.spouse;
        const spouseCard = document.createElement('div');
        spouseCard.className = 'data-card';
        spouseCard.innerHTML = `
      <div class="card-title">💑 配偶</div>
      ${createFieldRow('姓名', sp.name)}
      ${createFieldRow('证件号', sp.id_card)}
      ${createFieldRow('电话', sp.mobile)}
    `;
        container.appendChild(spouseCard);
    }

    // 共同借款人
    if (data.joint_borrowers && data.joint_borrowers.length > 0) {
        data.joint_borrowers.forEach((jb, index) => {
            const jbCard = document.createElement('div');
            jbCard.className = 'data-card';
            jbCard.innerHTML = `
        <div class="card-title">🤝 共同借款人 #${index + 1}</div>
        ${createFieldRow('姓名', jb.name)}
        ${createFieldRow('证件号', jb.id_card)}
        ${createFieldRow('电话', jb.mobile)}
      `;
            container.appendChild(jbCard);
        });
    }

    // 担保人
    if (data.guarantors && data.guarantors.length > 0) {
        data.guarantors.forEach((g, index) => {
            const gCard = document.createElement('div');
            gCard.className = 'data-card';
            gCard.innerHTML = `
        <div class="card-title">🛡️ 担保人 #${index + 1}</div>
        ${createFieldRow('姓名', g.name)}
        ${createFieldRow('证件号', g.id_card)}
        ${createFieldRow('电话', g.mobile)}
      `;
            container.appendChild(gCard);
        });
    }

    // 绑定复制事件
    container.querySelectorAll('.copy-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            copyToClipboard(btn.getAttribute('data-value'), btn);
        });
    });
}

// 处理文件
function handleFile(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        const content = e.target.result;
        const data = parseTxtFile(content);

        if (data) {
            chrome.storage.local.set({ lastData: data });
            document.getElementById('upload-area').style.display = 'none';
            document.getElementById('data-area').style.display = 'flex';
            document.getElementById('empty-state').style.display = 'none';
            renderData(data);
        } else {
            document.getElementById('upload-area').style.display = 'none';
            document.getElementById('empty-state').style.display = 'flex';
        }
    };
    reader.readAsText(file);
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    const selectFileBtn = document.getElementById('select-file-btn');
    const newFileBtn = document.getElementById('new-file-btn');
    const retryBtn = document.getElementById('retry-btn');
    const searchInput = document.getElementById('search-input');

    selectFileBtn.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('click', (e) => {
        if (e.target === uploadArea || e.target.classList.contains('upload-icon') || e.target.classList.contains('upload-text') || e.target.classList.contains('upload-hint')) {
            fileInput.click();
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files[0]) handleFile(e.target.files[0]);
    });

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
    });

    newFileBtn.addEventListener('click', () => {
        document.getElementById('data-area').style.display = 'none';
        document.getElementById('upload-area').style.display = 'flex';
        fileInput.value = '';
    });

    retryBtn.addEventListener('click', () => {
        document.getElementById('empty-state').style.display = 'none';
        document.getElementById('upload-area').style.display = 'flex';
    });

    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        document.querySelectorAll('.data-card').forEach(card => {
            card.style.display = card.textContent.toLowerCase().includes(query) ? 'block' : 'none';
        });
    });

    chrome.storage.local.get(['lastData'], (result) => {
        if (result.lastData) {
            document.getElementById('upload-area').style.display = 'none';
            document.getElementById('data-area').style.display = 'flex';
            renderData(result.lastData);
        }
    });
});
