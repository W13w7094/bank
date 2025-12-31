import os
import sys
import traceback
import time
import shutil
import zipfile
import json
import base64
from typing import List, Optional
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor
from logging.handlers import RotatingFileHandler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler("app.log", maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
    ]
)
logger = logging.getLogger("BankContract")

# Excel处理
import openpyxl 
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from docxtpl import DocxTemplate

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 配置 ---
# --- 配置 ---
def get_resource_path(relative_path):
    """获取资源路径，支持 PyInstaller 打包环境"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 运行目录（exe所在目录）
CWD = os.getcwd()

def get_config_path(filename):
    """优先获取外部配置文件，如果不存在则使用内部资源"""
    external_path = os.path.join(CWD, filename)
    if os.path.exists(external_path):
        logger.info(f"使用外部配置: {external_path}")
        return external_path
    return get_resource_path(filename)

# 模板目录：优先使用外部 templates 目录
EXTERNAL_TEMPLATE_DIR = os.path.join(CWD, "templates")
if os.path.exists(EXTERNAL_TEMPLATE_DIR):
    TEMPLATE_DIR = EXTERNAL_TEMPLATE_DIR
    logger.info(f"使用外部模板目录: {TEMPLATE_DIR}")
else:
    TEMPLATE_DIR = get_resource_path("templates")
    logger.info(f"使用内置模板目录: {TEMPLATE_DIR}")

# 输出目录还是在当前运行目录下，方便用户查看
OUTPUT_DIR = os.path.join(CWD, "output")
# 临时目录
TEMP_DIR = get_resource_path("temp")

# 数据文件
DATA_FILE = get_config_path("data.json")
BRANCH_FILE = get_config_path("branches.json")

# 挂载静态文件 (前端)
# 确保 static 目录存在，PyInstaller 打包时需要将 dist 目录打包为 static
STATIC_DIR = get_resource_path("static")

# 开发环境修正：如果 static 不存在但 dist 存在，则使用 dist
if not os.path.exists(STATIC_DIR):
    dist_path = os.path.join(CWD, "dist")
    if os.path.exists(dist_path):
        STATIC_DIR = dist_path
        logger.info(f"Check mode: using dist directory: {STATIC_DIR}")

# 只有当 static 目录存在时才挂载 (在开发模式只有 backend 可能不存在)
if os.path.exists(STATIC_DIR):
    assets_dir = os.path.join(STATIC_DIR, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

@app.get("/")
async def read_root():
    if os.path.exists(STATIC_DIR):
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))
    return {"message": "Backend is running. Frontend static files not found."}

# --- 数据模型 ---
class BranchInfo(BaseModel):
    name: str = ""
    short_name: str = ""  # Added short_name
    manager: str = ""
    phone: str = ""
    address: str = ""

class Enterprise(BaseModel):
    name: str = ""
    credit_code: str = ""
    legal_rep: str = ""
    address: str = ""

class Person(BaseModel):
    name: str = ""
    id_type: str = "身份证"
    id_card: str = ""
    mobile: str = ""
    relation: str = ""
    address: Optional[str] = ""
    gender: str = ""
    birthday: str = ""
    ethnicity: str = ""
    education: str = ""
    occupation: str = ""

class Collateral(BaseModel):
    owner: str = ""
    type: str = ""
    cert_no: str = ""
    location: str = ""
    value: float = 0
    area: str = ""

class ContractRequest(BaseModel):
    customer_type: str = "personal"
    loan_type: str = "guarantee"
    branch: Optional[BranchInfo] = None
    main_borrower: Optional[Person] = None
    spouse: Optional[Person] = None
    enterprise: Optional[Enterprise] = None
    joint_borrowers: List[Person] = []
    guarantors: List[Person] = []
    collaterals: List[Collateral] = []
    
    loan_amount: float = 0
    loan_term: int = 0
    start_date: str = ""
    end_date: str = ""
    loan_use: str = ""
    
    selected_templates: List[str] = []

# --- 辅助函数 ---

def num_to_cn(num):
    """
    将数字金额转换为人民币大写
    例如: 123456.78 -> 壹拾贰万叁仟肆佰伍拾陆元柒角捌分
    """
    if num == 0:
        return "零元整"
    
    # 中文数字
    CN_NUM = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
    CN_UNIT = ['', '拾', '佰', '仟', '万', '拾', '佰', '仟', '亿']
    
    # 分离整数和小数部分
    int_part = int(num)
    decimal_part = round((num - int_part) * 100)  # 转为分
    
    # 将数字转为字符串并反转以方便处理
    str_num = str(int_part)[::-1]  # 反转，从低位开始
    result = ''
    
    for i, digit in enumerate(str_num):
        d = int(digit)
        if d != 0:
            result = CN_NUM[d] + CN_UNIT[i] + result
        else:
            # 只在需要时添加零
            if result and not result.startswith('零'):
                result = '零' + result
    
    # 清除末尾的零和多余的零
    result = result.strip('零')
    
    # 添加“元”
    if result:
        result += '元'
    else:
        result = '零元'
    
    # 处理角分
    if decimal_part > 0:
        jiao = decimal_part // 10
        fen = decimal_part % 10
        
        if jiao > 0:
            result += CN_NUM[jiao] + '角'
        elif fen > 0:
            result += '零'
        
        if fen > 0:
            result += CN_NUM[fen] + '分'
    else:
        result += '整'
    
    return result

def format_date_cn(date_str):
    if not date_str: return ""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return f"{dt.year}年{dt.month:02d}月{dt.day:02d}日"
    except:
        return date_str

def calculate_age(id_card):
    """根据身份证号计算年龄"""
    if not id_card or len(id_card) != 18:
        return ""
    try:
        birth_year = int(id_card[6:10])
        birth_month = int(id_card[10:12])
        birth_day = int(id_card[12:14])
        
        today = datetime.now()
        age = today.year - birth_year
        if (today.month, today.day) < (birth_month, birth_day):
            age -= 1
        return str(age)
    except:
        return ""

def fill_excel_template(template_path, output_path, context):
    wb = openpyxl.load_workbook(template_path)
    for sheet in wb.worksheets:
        for row in sheet.iter_rows():
            for cell in row:
                if cell.value and isinstance(cell.value, str) and "{{" in cell.value:
                    text = cell.value
                    for key, value in context.items():
                        val_str = str(value) if value is not None else ""
                        text = text.replace(f"{{{{{key}}}}}", val_str).replace(f"{{{{ {key} }}}}", val_str)
                    cell.value = text
    wb.save(output_path)
    wb.close()

# ✨✨✨ 核心逻辑：生成“三明治”报告文件 ✨✨✨
def generate_smart_report(data: ContractRequest):
    lines = []
    # --- Part 1: 人类可读部分 (用于复制粘贴) ---
    lines.append(f"====== 业务录入辅助报告 ({datetime.now().strftime('%Y-%m-%d')}) ======")
    lines.append(f"办理支行：{data.branch.name if data.branch else ''}")
    lines.append(f"客户类型：{'企业' if data.customer_type == 'enterprise' else '个人'} ({'信用' if data.loan_type == 'credit' else '担保/抵押'})")
    lines.append(f"贷款金额：{data.loan_amount} 元 ({num_to_cn(data.loan_amount)})")
    lines.append(f"期限用途：{data.loan_term}个月 | {data.loan_use}")
    lines.append("")

    if data.customer_type == 'personal' and data.main_borrower:
        p = data.main_borrower
        lines.append(f"【主借款人】 {p.name}")
        lines.append(f"证件：{p.id_card}")
        lines.append(f"电话：{p.mobile}")
        lines.append(f"地址：{p.address}")
        lines.append(f"画像：{p.gender} | {p.birthday} | {p.ethnicity} | {p.education} | {p.occupation}")
        if data.spouse:
            s = data.spouse
            lines.append(f">>> 配偶：{s.name} | {s.id_card} | {s.mobile}")
            lines.append(f"    详情：{s.gender} | {s.birthday} | {s.occupation} | {s.ethnicity} | {s.education}")
    elif data.enterprise:
        e = data.enterprise
        lines.append(f"【企业】 {e.name}")
        lines.append(f"代码：{e.credit_code} | 法人：{e.legal_rep}")
        lines.append(f"地址：{e.address}")
    
    
    if data.collaterals:
        lines.append("")
        lines.append(f"【抵押物 ({len(data.collaterals)})】")
        for i, c in enumerate(data.collaterals):
            lines.append(f"{i+1}. {c.owner} | {c.type} | {c.location} | 价值:{c.value}")
            lines.append(f"   权证：{c.cert_no} | 面积/数量：{c.area}")
    
    if data.guarantors:
        lines.append("")
        lines.append(f"【担保人 ({len(data.guarantors)})】")
        for i, g in enumerate(data.guarantors):
            lines.append(f"{i+1}. {g.name} | {g.id_card} | {g.mobile} | {g.relation}")
            lines.append(f"   详情：{g.gender} | {g.birthday} | {g.occupation} | {g.ethnicity} | {g.education}")
            lines.append(f"   地址：{g.address}")
    
    if data.joint_borrowers:
        lines.append("")
        lines.append(f"【共同借款人 ({len(data.joint_borrowers)})】")
        for i, j in enumerate(data.joint_borrowers):
            lines.append(f"{i+1}. {j.name} | {j.id_card} | {j.mobile} | {j.relation}")
            lines.append(f"   详情：{j.gender} | {j.birthday} | {j.occupation} | {j.ethnicity} | {j.education}")
            lines.append(f"   地址：{j.address}")

    lines.append("")
    lines.append("="*40)
    lines.append("⚠️ 以下内容为系统自动读取数据，请勿修改 ⚠️")
    lines.append("="*40)
    
    # --- Part 2: 机器可读部分 (JSON数据) ---
    # 使用 Base64 简单编码防止中文乱码和换行问题干扰
    json_str = json.dumps(data.model_dump(), ensure_ascii=False)
    b64_str = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    
    lines.append(f"SYSTEM_DATA_START:{b64_str}:SYSTEM_DATA_END")
    
    return "\n".join(lines)

# --- 接口 ---

@app.get("/api/branches")
async def get_branches():
    if not os.path.exists(BRANCH_FILE): return []
    try:
        with open(BRANCH_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return []

@app.get("/api/config")
async def get_system_config():
    default_config = {"options": {"education": [], "ethnicity": [], "occupation": [], "loan_use": [], "collateral_type": []}, "templates": []}
    if not os.path.exists(DATA_FILE): return default_config
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        valid_templates = []
        for tmpl in config.get("templates", []):
            if os.path.exists(os.path.join(TEMPLATE_DIR, tmpl['filename'])):
                tmpl['value'] = tmpl['filename']
                valid_templates.append(tmpl)
        config["templates"] = valid_templates
        return config
    except: return default_config

@app.post("/api/generate")
async def generate_contract(data: ContractRequest):
    # 详细记录请求数据，方便排查数据问题
    logger.info(f"====== 收到生成请求 ======")
    logger.info(f"类型: {data.customer_type} | 金额: {data.loan_amount}")
    try:
        # 记录完整的 JSON 数据（截断过长内容避免刷屏）
        debug_json = data.model_dump_json()
        if len(debug_json) > 1000:
            logger.info(f"请求数据(前1000字符): {debug_json[:1000]}...")
        else:
            logger.info(f"完整请求数据: {debug_json}")
    except:
        pass
    
    context = data.model_dump()
    context['loan_amount_cn'] = num_to_cn(data.loan_amount)
    context['start_date_cn'] = format_date_cn(data.start_date)
    context['end_date_cn'] = format_date_cn(data.end_date)
    
    # 汉化 loan_type
    loan_type_map = {
        'credit': '信用',
        'guarantee': '担保',
        'mortgage': '抵押'
    }
    context['loan_type_cn'] = loan_type_map.get(data.loan_type, data.loan_type)
    # 覆盖原 loan_type 为中文，或保留英文
    context['loan_type'] = context['loan_type_cn']

    
    # ✨ 简化方案：将列表展开为编号的独立变量
    # 共同借款人最多3个：joint_borrowers1, joint_borrowers2, joint_borrowers3
    for i in range(3):
        if context.get('joint_borrowers') and i < len(context['joint_borrowers']):
            jb = context['joint_borrowers'][i]
            context[f'joint_borrower{i+1}'] = jb
            context[f'joint_borrower{i+1}_age'] = calculate_age(jb.get('id_card'))
        else:
            context[f'joint_borrower{i+1}'] = {}
            context[f'joint_borrower{i+1}_age'] = ""
    
    # 担保人最多7个：guarantor1, guarantor2, ..., guarantor7
    for i in range(7):
        if context.get('guarantors') and i < len(context['guarantors']):
            g = context['guarantors'][i]
            context[f'guarantor{i+1}'] = g
            context[f'guarantor{i+1}_age'] = calculate_age(g.get('id_card'))
        else:
            context[f'guarantor{i+1}'] = {}
            context[f'guarantor{i+1}_age'] = ""
    
    # 抵押物也展开（假设最多5个）
    for i in range(5):
        if context.get('collaterals') and i < len(context['collaterals']):
            c = context['collaterals'][i]
            context[f'collateral{i+1}'] = c
        else:
            context[f'collateral{i+1}'] = {}
    # 扁平化数据
    if data.main_borrower:
        context.update({
            'main_name': data.main_borrower.name, 
            'main_card': data.main_borrower.id_card, 
            'main_addr': data.main_borrower.address,
            'main_age': calculate_age(data.main_borrower.id_card),
            'main_marital_status': '已婚' if (data.spouse and data.spouse.name) else '未婚'
        })
    if data.spouse:
        context['spouse_age'] = calculate_age(data.spouse.id_card)
    if data.enterprise:
        context.update({'ent_name': data.enterprise.name, 'ent_code': data.enterprise.credit_code})
    if data.branch:
        context.update({
            'branch_name': data.branch.name,
            'branch_short_name': data.branch.short_name,
            'branch_short': data.branch.short_name
        })

    task_id = str(int(time.time() * 1000))
    temp_dir = os.path.join(OUTPUT_DIR, task_id)
    os.makedirs(temp_dir, exist_ok=True)
    
    # 🌟 统一文件名格式
    date_str = datetime.now().strftime('%Y%m%d')
    prefix = data.enterprise.name if data.customer_type == 'enterprise' else (data.main_borrower.name if data.main_borrower else "客户")
    
    generated_files = []

    try:
        # 1. 生成 .TXT (含数据)
        report_name = f"{prefix}_数据存档_{date_str}.txt"
        report_path = os.path.join(temp_dir, report_name)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(generate_smart_report(data))
        generated_files.append(report_path)

        # 2. 生成合同 (多线程加速)
        def process_template(tmpl_name):
            if not tmpl_name: return None
            tmpl_path = os.path.join(TEMPLATE_DIR, tmpl_name)
            if not os.path.exists(tmpl_path): return None

            base_name, ext = os.path.splitext(tmpl_name)
            save_name = f"{prefix}_{base_name}_{date_str}{ext}"
            save_path = os.path.join(temp_dir, save_name)

            try:
                if tmpl_name.endswith('.docx'):
                    doc = DocxTemplate(tmpl_path)
                    doc.render(context)
                    doc.save(save_path)
                elif tmpl_name.endswith('.xlsx'):
                    fill_excel_template(tmpl_path, save_path, context)
                return save_path
            except Exception as e:
                logger.error(f"❌ 模板处理失败: {tmpl_name}")
                logger.error(f"错误详情: {traceback.format_exc()}")
                return None

        # 使用线程池并发处理
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(process_template, data.selected_templates))
        
        # 收集成功的文件
        for res in results:
            if res: generated_files.append(res)

        zip_name = f"{prefix}_业务文件包_{date_str}.zip"
        zip_path = os.path.join(OUTPUT_DIR, zip_name)
        with zipfile.ZipFile(zip_path, 'w') as zf:
            for file in generated_files: zf.write(file, arcname=os.path.basename(file))
        
        return FileResponse(zip_path, filename=zip_name, media_type='application/zip')

    except Exception as e:
        if e.status_code == 422:
            logger.error(f"验证错误: {e.detail}")
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)

if __name__ == "__main__":
    import uvicorn
    os.makedirs(TEMPLATE_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    logger.info("服务启动成功，请访问 http://localhost:8000")
    # log_config=None 禁止 Uvicorn 配置自己的日志（它会尝试访问 stdout 导致 noconsole 模式崩溃）
    # 我们上面已经配置了 logging.basicConfig
    print(">>> Starting Uvicorn server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)