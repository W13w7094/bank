// 后台脚本 - 处理侧边栏打开
chrome.action.onClicked.addListener((tab) => {
    // 打开侧边栏
    chrome.sidePanel.open({ windowId: tab.windowId });
});

// 安装或更新时的提示
chrome.runtime.onInstalled.addListener((details) => {
    if (details.reason === 'install') {
        console.log('银行合同数据助手已安装！点击工具栏图标打开侧边栏。');
    } else if (details.reason === 'update') {
        console.log('银行合同数据助手已更新到侧边栏模式！');
    }
});
