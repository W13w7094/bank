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
    id_type: str = "身份证"  # 新增：证件类型（身份证/营业执照）
    id_card: str = ""
    mobile: str = ""
    relation: Optional[str] = ""  # 改为可选：企业担保时关系不是必填
    address: Optional[str] = ""
    gender: str = ""
    birthday: str = ""
    ethnicity: str = ""
    education: str = ""
    occupation: str = ""
    age: str = ""  # Added for persistence
    legal_rep: Optional[str] = ""  # 新增：法人代表（企业专用）

class Collateral(BaseModel):
    owner: str = ""
    type: str = ""
    cert_no: str = ""
    location: str = ""
    value: float = 0
    area: str = ""
    land_area: str = ""  # New field: 土地使用面积
    value_cn: str = ""   # New field: 大写金额


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
    
    CN_NUM = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
    CN_UNIT = ['', '拾', '佰', '仟']
    CN_SECTION = ['', '万', '亿', '兆']
    
    # 分离整数和小数部分
    int_part = int(num)
    decimal_part = round((num - int_part) * 100)
    
    # 处理整数部分
    str_num = str(int_part)
    result = ""
    
    # 分段处理，从低位到高位，每4位一段
    # 倒序处理
    reversed_str = str_num[::-1]
    sections = [reversed_str[i:i+4] for i in range(0, len(reversed_str), 4)]
    
    for section_idx, section in enumerate(sections):
        section_result = ""
        section_zero = True # 本节是否全0
        
        # 处理每一节，section是倒序的，如 1234 -> 4321
        for i, digit in enumerate(section):
            d = int(digit)
            if d != 0:
                section_zero = False
                # 如果前面有0（高位有0），且当前位不是0，需要补零
                # 但这里的逻辑是倒序构造，result = digit + unit + result
                # 比较复杂，不如正序处理每一节
                pass
    
    # 重写逻辑：正序
    int_str = str(int_part)
    length = len(int_str)
    result = ""
    zero = False # 前面是否有零需要补
    
    # 这种逐位处理逻辑对于 "万" 的插入比较麻烦
    # 采用 section 分割法 (Low to High)
    
    sections = []
    temp_str = int_str
    while len(temp_str) > 0:
        sections.append(temp_str[-4:])
        temp_str = temp_str[:-4]
        
    chinese_sections = []
    for idx, section in enumerate(sections):
        if int(section) == 0:
            # 如果本节是0，且不是最低节，且如果前面还有更高的节...
            # 这里先存空，最后处理零的连接
            if idx == 0: # 个位节全0
                chinese_sections.append("")
                continue
            else:
                # 高位节全0，如 1 0000 0001 的中间万位
                # 需要补零吗？ 1亿零1元。
                # 这种情况下，万位不仅不加万，还要作为零处理。
                chinese_sections.append("零") # 占位
                continue
        
        # 处理非0节
        sect_res = ""
        zero_flag = False # 节内零
        
        # 补齐4位方便处理？不，直接处理
        # "0101" -> 101. 
        # section is string. e.g. "101"
        for i in range(len(section)):
            d = int(section[i])
            # 单位位置：倒数第几位
            p = len(section) - 1 - i 
            
            if d == 0:
                zero_flag = True
            else:
                if zero_flag:
                    sect_res += CN_NUM[0]
                    zero_flag = False
                sect_res += CN_NUM[d] + CN_UNIT[p]
        
        # 如果本节有值，加上节单位
        if sect_res:
             # 处理 "10" -> "YiShi" or "Shi". Standard "YiShi".
             # 特殊处理：如果是 10-19，且是最高位... 还是保留壹拾吧，标准。
             pass
        
        if sect_res:
            sect_res += CN_SECTION[idx]
        
        chinese_sections.append(sect_res)
        
    # 合并
    # sections 是从低到高 [个位节, 万位节, 亿位节]
    # 需要反转回来拼接
    # 还需要处理节与节之间的零
    
    final_res = ""
    # 从高到低遍历
    for i in range(len(chinese_sections) - 1, -1, -1):
        part = chinese_sections[i]
        if part == "零":
            # 只有当后面还有内容，且 final_res 不以零结尾时才加零？
            if final_res and not final_res.endswith("零"):
                final_res += "零"
        else:
            if part:
                # 如果这个部分非空，且前面有值，且本部分原值（int）小于1000（意味着有前导0），需要补零？
                # e.g. 1 0001 -> 1 section="1", 2 section="1". "YiWan" + "Yi". -> "YiWanLingYi".
                # 检查 section 原始值
                original_val = sections[i]
                if len(original_val) == 4 and original_val.startswith('0') and final_res:
                     if not final_res.endswith("零"):
                         final_res += "零"
                
                final_res += part
    
    result = final_res
    
    # 清除末尾零
    result = result.rstrip('零')
    if not result: result = CN_NUM[0]
    
    if result != "零":
        result += "元"
    else:
        result = "零元"
        
    # 小数
    if decimal_part > 0:
        jiao = decimal_part // 10
        fen = decimal_part % 10
        if jiao > 0:
            result += CN_NUM[jiao] + '角'
        elif fen > 0 and int_part > 0:
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

def flatten_context(context, parent_key='', sep='.'):
    """扁平化字典，支持 nested keys 如 spouse.name"""
    items = []
    for k, v in context.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_context(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def fill_excel_template(template_path, output_path, context):
    # 扁平化数据以支持 {{ spouse.name }} 格式
    flat_context = flatten_context(context)
    # 合并原始context以防万一
    flat_context.update(context)
    
    wb = openpyxl.load_workbook(template_path)
    for sheet in wb.worksheets:
        for row in sheet.iter_rows():
            for cell in row:
                if cell.value and isinstance(cell.value, str) and "{{" in cell.value:
                    text = cell.value
                    # 优先替换长键 (如 spouse.name) 防止 spouse 被部分替换
                    # 但其实直接遍历所有key替换即可，Jinja2风格通常是独立的一块
                    for key, value in flat_context.items():
                        if value is None: value = ""
                        val_str = str(value)
                        # 简单替换 {{ key }} 和 {{ key.subkey }}
                        # 注意：需要处理空格如 {{ spouse.name }}
                        target = f"{{{{{key}}}}}"
                        target_space = f"{{{{ {key} }}}}"
                        if target in text:
                            text = text.replace(target, val_str)
                        if target_space in text:
                            text = text.replace(target_space, val_str)
                    cell.value = text
    wb.save(output_path)
    wb.close()

# ✨✨✨ 核心逻辑：生成“三明治”报告文件 ✨✨✨
def generate_smart_report(data: ContractRequest):
    # 🌟 预先计算 Derived Data 确保写入 JSON
    if data.main_borrower:
        data.main_borrower.age = calculate_age(data.main_borrower.id_card)
    if data.spouse:
        data.spouse.age = calculate_age(data.spouse.id_card)
    for p in data.joint_borrowers:
        p.age = calculate_age(p.id_card)
    for p in data.guarantors:
        p.age = calculate_age(p.id_card)
    for c in data.collaterals:
        c.value_cn = num_to_cn(c.value)

    lines = []
    # --- Part 1: 人类可读部分 (用于复制粘贴) ---
    lines.append(f"====== 业务录入辅助报告 ({datetime.now().strftime('%Y-%m-%d')}) ======")
    lines.append(f"办理支行：{data.branch.name if data.branch else ''} ({data.branch.short_name if data.branch else ''})")
    lines.append(f"客户类型：{'企业' if data.customer_type == 'enterprise' else '个人'} ({'信用' if data.loan_type == 'credit' else '担保/抵押'})")
    lines.append(f"贷款金额：{data.loan_amount} 元 ({num_to_cn(data.loan_amount)})")
    lines.append(f"期限用途：{data.loan_term}个月 | {data.loan_use}")
    lines.append("")

    marital_status = "未婚"
    if data.spouse and data.spouse.name:
        marital_status = "已婚"

    if data.customer_type == 'personal' and data.main_borrower:
        p = data.main_borrower
        lines.append(f"【主借款人】 {p.name} ({p.age}岁 | {marital_status})")
        lines.append(f"证件：{p.id_card}")
        lines.append(f"电话：{p.mobile}")
        lines.append(f"地址：{p.address}")
        lines.append(f"画像：{p.gender} | {p.birthday} | {p.ethnicity} | {p.education} | {p.occupation}")
        if data.spouse:
            s = data.spouse
            lines.append(f">>> 配偶：{s.name} ({s.age}岁) | {s.id_card} | {s.mobile}")
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
            lines.append(f"{i+1}. {c.owner} | {c.type} | {c.location} | 价值:{c.value} ({c.value_cn})")
            lines.append(f"   权证：{c.cert_no} | 建筑面积：{c.area} | 土地面积：{c.land_area}")
    
    if data.guarantors:
        lines.append("")
        lines.append(f"【担保人 ({len(data.guarantors)})】")
        for i, g in enumerate(data.guarantors):
            lines.append(f"{i+1}. {g.name} ({g.age}岁) | {g.id_card} | {g.mobile} | {g.relation}")
            lines.append(f"   详情：{g.gender} | {g.birthday} | {g.occupation} | {g.ethnicity} | {g.education}")
            lines.append(f"   地址：{g.address}")
    
    if data.joint_borrowers:
        lines.append("")
        lines.append(f"【共同借款人 ({len(data.joint_borrowers)})】")
        for i, j in enumerate(data.joint_borrowers):
            lines.append(f"{i+1}. {j.name} ({j.age}岁) | {j.id_card} | {j.mobile} | {j.relation}")
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

@app.get("/api/customers")
async def get_customers():
    """读取Excel文件，返回到期客户列表"""
    try:
        import pandas as pd
        excel_path = os.path.join(BASE_DIR, "贷款到期清单.xlsx")
        
        if not os.path.exists(excel_path):
            logger.warning(f"未找到到期清单文件: {excel_path}")
            return {"customers": []}
        
        logger.info(f"正在读取到期清单: {excel_path}")
        # 指定身份证等列为字符串类型，避免科学计数法
        df = pd.read_excel(excel_path, dtype={
            "证件号（对公情况）": str,
            "身份证": str,
            "担保人1身份证": str,
            "担保人2身份证": str,
            "担保人3身份证": str,
            "担保人4身份证": str,
            "担保人5身份证": str,
            "联系方式（对公情况）": str,
            "联系方式": str,
            "担保人1联系方式": str,
            "担保人2联系方式": str,
            "担保人3联系方式": str,
            "担保人4联系方式": str,
            "担保人5联系方式": str
        })
        customers = []
        
        for idx, row in df.iterrows():
            customer = {
                "branch_short_name": str(row.get("支行简称", "")).strip(),
                "main_name": str(row.get("贷款人", "")).strip(),
                "main_id_card": str(row.get("证件号（对公情况）", "")).strip(),
                "main_mobile": str(row.get("联系方式（对公情况）", "")).strip(),
                "main_address": str(row.get("住址", "")).strip(),
                "spouse_name": str(row.get("配偶名", "")).strip(),
                "spouse_id_card": str(row.get("身份证", "") if pd.notna(row.get("身份证")) else "").strip(),
                "spouse_mobile": str(row.get("联系方式", "") if pd.notna(row.get("联系方式")) else "").strip(),
                "guarantors": []
            }
            
            # 解析担保人1-5
            for i in range(1, 6):
                g_name_col = f"担保人{i}名称"
                g_name = str(row.get(g_name_col, "")).strip()
                if g_name and g_name != "nan":
                    guarantor = {
                        "name": g_name,
                        "id_card": str(row.get(f"担保人{i}身份证", "")).strip(),
                        "mobile": str(row.get(f"担保人{i}联系方式", "")).strip()
                    }
                    customer["guarantors"].append(guarantor)
            
            # 只添加有效的客户（至少有姓名）
            if customer["main_name"] and customer["main_name"] != "nan":
                customers.append(customer)
        
        logger.info(f"成功读取 {len(customers)} 个到期客户")
        return {"customers": customers}
    
    except Exception as e:
        logger.error(f"读取到期清单失败: {e}")
        logger.error(traceback.format_exc())
        return {"customers": [], "error": str(e)}


# Helper function to generate investigation report context
def generate_investigation_context(data: ContractRequest):
    """生成调查报告的context"""
    # Build main borrower summary
    if data.main_borrower:
        mb = data.main_borrower
        main_summary = f"{mb.name}，{mb.gender}，{mb.age}岁，身份证号：{mb.id_card}，"
        main_summary += f"联系电话：{mb.mobile}，职业：{mb.occupation or '无'}，"
        main_summary += f"学历：{mb.education or '无'}，现住址：{mb.address}。"
        
        if data.spouse and data.spouse.name:
            sp = data.spouse
            main_summary += f" 配偶{sp.name}，{sp.gender}，{sp.age}岁，"
            main_summary += f"身份证号：{sp.id_card}，联系电话：{sp.mobile}。"
    else:
        main_summary = "未填写"
    
    # Build joint borrowers summary
    if data.joint_borrowers:
        jb_items = []
        for i, jb in enumerate(data.joint_borrowers, 1):
            if not jb.name:
                continue
            jb_text = f"{i}. {jb.name}，{jb.gender}，{jb.age}岁，身份证号：{jb.id_card}，"
            jb_text += f"联系电话：{jb.mobile}，职业：{jb.occupation or '无'}，"
            jb_text += f"与借款人关系：{jb.relation or '无'}，住址：{jb.address}。"
            jb_items.append(jb_text)
        joint_summary = "\\n".join(jb_items) if jb_items else "无"
    else:
        joint_summary = "无"
    
    # Build guarantors summary
    if data.guarantors:
        g_items = []
        for i, g in enumerate(data.guarantors, 1):
            if not g.name:
                continue
            g_text = f"{i}. {g.name}，{g.gender}，{g.age}岁，身份证号：{g.id_card}，"
            g_text += f"联系电话：{g.mobile}，职业：{g.occupation or '无'}，"
            g_text += f"与借款人关系：{g.relation or '无'}，住址：{g.address}。"
            g_items.append(g_text)
        guarantors_summary = "\\n".join(g_items) if g_items else "无"
    else:
        guarantors_summary = "无"
    
    # Build collaterals summary
    if data.collaterals:
        c_items = []
        for i, c in enumerate(data.collaterals, 1):
            if not c.type:
                continue
            c_text = f"{i}. {c.type}，坐落于{c.location}，"
            c_text += f"权证号：{c.cert_no}，建筑面积：{c.area}，"
            if c.land_area:
                c_text += f"土地面积：{c.land_area}，"
            c_text += f"评估价值：{c.value}元（{c.value_cn}）。"
            c_items.append(c_text)
        collaterals_summary = "\\n".join(c_items) if c_items else "无"
    else:
        collaterals_summary = "无"
    
    # Prepare context
    return {
        "loan_use": data.loan_use,
        "loan_amount": data.loan_amount,
        "loan_amount_cn": num_to_cn(data.loan_amount) if data.loan_amount else "零元整",
        "loan_term": data.loan_term,
        # Standard full names
        "main_borrower_summary": main_summary,
        "joint_borrowers_summary": joint_summary,
        "guarantors_summary": guarantors_summary,
        "collaterals_summary": collaterals_summary,
        # Aleas (Short names often used in templates)
        "main_summary": main_summary,
        "joint_summary": joint_summary,
        "guarantor_summary": guarantors_summary,
        "collateral_summary": collaterals_summary,
        # Raw data access
        "main_borrower": data.main_borrower,
        "spouse": data.spouse,
        "enterprise": data.enterprise
    }

# ============= Context Building Helper Functions =============

def _calculate_derived_fields(data: ContractRequest) -> dict:
    """集中计算所有派生字段，避免重复计算和遗漏"""
    derived = {}
    
    # 金额中文
    if data.loan_amount:
        derived['loan_amount_cn'] = num_to_cn(data.loan_amount)
    
    # 日期中文
    if data.start_date:
        derived['start_date_cn'] = format_date_cn(data.start_date)
    if data.end_date:
        derived['end_date_cn'] = format_date_cn(data.end_date)
    
    # 年龄计算（集中处理，确保一致性）
    if data.main_borrower and data.main_borrower.id_card:
        derived['main_age'] = calculate_age(data.main_borrower.id_card)
    if data.spouse and data.spouse.id_card:
        derived['spouse_age'] = calculate_age(data.spouse.id_card)
    
    # 贷款类型中文
    loan_type_map = {'credit': '信用', 'guarantee': '担保', 'mortgage': '抵押'}
    derived['loan_type_cn'] = loan_type_map.get(data.loan_type, data.loan_type)
    derived['loan_type'] = derived['loan_type_cn']  # 覆盖为中文
    
    # 婚姻状况
    derived['main_marital_status'] = '已婚' if (data.spouse and data.spouse.name) else '未婚'
    
    return derived

def _expand_lists(data: ContractRequest) -> dict:
    """展开列表数据为独立变量，确保数据完整"""
    expanded = {}
    
    # 共同借款人 (1-3)
    for i in range(3):
        if data.joint_borrowers and i < len(data.joint_borrowers):
            jb_data = data.joint_borrowers[i].model_dump()  # 完整复制
            jb_data['age'] = calculate_age(jb_data.get('id_card', ''))
            expanded[f'joint_borrower{i+1}'] = jb_data
        else:
            expanded[f'joint_borrower{i+1}'] = {}
    
    # 担保人 (1-7)
    for i in range(7):
        if data.guarantors and i < len(data.guarantors):
            g_data = data.guarantors[i].model_dump()  # 完整复制
            g_data['age'] = calculate_age(g_data.get('id_card', ''))
            expanded[f'guarantor{i+1}'] = g_data
        else:
            expanded[f'guarantor{i+1}'] = {}
    
    # 抵押物 (1-5)
    for i in range(5):
        if data.collaterals and i < len(data.collaterals):
            c_data = data.collaterals[i].model_dump()  # 完整复制
            c_data['value_cn'] = num_to_cn(c_data.get('value', 0))
            expanded[f'collateral{i+1}'] = c_data
        else:
            expanded[f'collateral{i+1}'] = {}
    
    return expanded

def _create_aliases(data: ContractRequest) -> dict:
    """创建常用别名和快捷键"""
    aliases = {}
    
    # 主借款人快捷键
    if data.main_borrower:
        aliases.update({
            'main_name': data.main_borrower.name,
            'main_card': data.main_borrower.id_card,
            'main_addr': data.main_borrower.address
        })
    
    # 企业快捷键
    if data.enterprise:
        aliases.update({
            'ent_name': data.enterprise.name,
            'ent_code': data.enterprise.credit_code
        })
    
    # 支行快捷键
    if data.branch:
        aliases.update({
            'branch_name': data.branch.name,
            'branch_short_name': data.branch.short_name,
            'branch_short': data.branch.short_name
        })
    
    return aliases

def build_complete_context(data: ContractRequest) -> dict:
    """
    统一构建完整的context，确保数据完整性
    这是整个系统的核心数据准备函数
    """
    # 1. 基础数据（从Pydantic模型导出）
    context = data.model_dump()
    
    # 2. 预计算所有派生字段
    derived = _calculate_derived_fields(data)
    context.update(derived)
    
    # 3. 列表展开（带完整数据复制）
    expanded = _expand_lists(data)
    context.update(expanded)
    
    # 4. 别名和快捷键
    aliases = _create_aliases(data)
    context.update(aliases)
    
    # 5. 全面扁平化（支持 {{ spouse.name }} 等嵌套访问）
    flat = flatten_context(context)
    context.update(flat)
    
    return context

# ============= API Endpoints =============

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
    
    # ✨✨✨ 使用统一的context构建函数 ✨✨✨
    context = build_complete_context(data)
    logger.debug(f"✅ Context构建完成，共 {len(context)} 个键")
    logger.debug(f"关键字段检查 - spouse: {'存在' if context.get('spouse') else '缺失'}, guarantor1: {'存在' if context.get('guarantor1') else '缺失'}")

    task_id = str(int(time.time() * 1000))
    temp_dir = os.path.join(OUTPUT_DIR, task_id)
    os.makedirs(temp_dir, exist_ok=True)
    
    # 🌟 统一文件名格式
    date_str = datetime.now().strftime('%Y%m%d')
    prefix = data.enterprise.name if data.customer_type == 'enterprise' else (data.main_borrower.name if data.main_borrower else "客户")
    
    generated_files = []
    errors = []  # Initialize errors list here

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
            
            # check existence
            if not os.path.exists(tmpl_path):
                # 增强调试信息：列出目录下的文件，帮助定位文件名不匹配问题 (e.g. 隐藏后缀/编码差异)
                try:
                    existing_files = os.listdir(TEMPLATE_DIR)
                    logger.error(f"❌ 文件未找到: {os.path.abspath(tmpl_path)}")
                    logger.error(f"📂 模板目录 ({TEMPLATE_DIR}) 下的文件: {existing_files}")
                except Exception as ex:
                    logger.error(f"无法列出模板目录: {ex}")
                return {"error": f"找不到模板文件: {tmpl_name} (路径: {os.path.abspath(tmpl_path)})"}

            base_name, ext = os.path.splitext(tmpl_name)
            save_name = f"{prefix}_{base_name}_{date_str}{ext}"
            save_path = os.path.join(temp_dir, save_name)

            try:
                # Special handling for investigation report
                if tmpl_name == 'investigation_report.docx' or str(tmpl_name).endswith('investigation_report.docx'):
                    # 1. 先生成专用 summary 上下文
                    report_context = generate_investigation_context(data)
                    # 2. ✨✨✨ 关键修复：合并全局 context！✨✨✨
                    # 这样模板里既可以使用专用变量 (main_summary)，也可以使用通用变量 (main_borrower.name, joint_borrower1.age)
                    full_report_ctx = context.copy()
                    full_report_ctx.update(report_context)
                    
                    doc = DocxTemplate(tmpl_path)
                    doc.render(full_report_ctx)
                    doc.save(save_path)
                elif tmpl_name.endswith('.docx'):
                    doc = DocxTemplate(tmpl_path)
                    doc.render(context)
                    doc.save(save_path)
                elif tmpl_name.endswith('.xlsx'):
                    fill_excel_template(tmpl_path, save_path, context)
                return {"path": save_path}
            except Exception as e:
                error_detail = f"模板[{tmpl_name}]处理失败: {str(e)}"
                logger.error(f"❌ {error_detail}")
                logger.error(traceback.format_exc())
                return {"error": error_detail}

        # 使用线程池并发处理
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(process_template, data.selected_templates))
        
        # 收集成功的文件和错误
        for res in results:
            if not res: continue
            if "path" in res:
                generated_files.append(res["path"])
            elif "error" in res:
                errors.append(res["error"])
        
        # 如果有任何错误，抛出异常给前端显示
        if errors:
            raise Exception("\n".join(errors))
            
        if not generated_files:
             raise Exception("未生成任何文件，请检查模版选择")

        zip_name = f"{prefix}_业务文件包_{date_str}.zip"
        zip_path = os.path.join(OUTPUT_DIR, zip_name)
        with zipfile.ZipFile(zip_path, 'w') as zf:
            for file in generated_files: zf.write(file, arcname=os.path.basename(file))
        
        return FileResponse(zip_path, filename=zip_name, media_type='application/zip')

    except Exception as e:
        logger.error("="*60)
        logger.error("❌ 生成文件时发生错误")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误信息: {str(e)}")
        logger.error(f"选择的模板: {data.selected_templates if hasattr(data, 'selected_templates') else '未知'}")
        logger.error("详细堆栈:")
        logger.error(traceback.format_exc())
        logger.error("="*60)
        
        if hasattr(e, 'status_code') and e.status_code == 422:
            raise HTTPException(status_code=422, detail=f"数据验证失败: {e.detail}")
        
        # 返回更详细的错误信息
        error_msg = f"{type(e).__name__}: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)

@app.post("/api/generate-investigation-report")
async def generate_investigation_report(data: dict):
    """生成客户调查报告（简洁版）- 接受部分数据"""
    try:
        # Extract main data with safe defaults
        loan_use = data.get('loan_use', '未填写')
        loan_amount = data.get('loan_amount', 0)
        loan_term = data.get('loan_term', 0)
        
        main_borrower = data.get('main_borrower')
        spouse = data.get('spouse')
        joint_borrowers = data.get('joint_borrowers', [])
        guarantors = data.get('guarantors', [])
        collaterals = data.get('collaterals', [])
        
        # Build main borrower summary
        if main_borrower and main_borrower.get('name'):
            mb = main_borrower
            age = calculate_age(mb.get('id_card', '')) if mb.get('id_card') else '未知'
            main_summary = f"{mb.get('name', '未知')}，{mb.get('gender', '未知')}，{age}岁，"
            main_summary += f"身份证号：{mb.get('id_card', '未填写')}，"
            main_summary += f"联系电话：{mb.get('mobile', '未填写')}，"
            main_summary += f"职业：{mb.get('occupation', '未填写')}，"
            main_summary += f"学历：{mb.get('education', '未填写')}，"
            main_summary += f"现住址：{mb.get('address', '未填写')}。"
            
            if spouse and spouse.get('name'):
                sp = spouse
                sp_age = calculate_age(sp.get('id_card', '')) if sp.get('id_card') else '未知'
                main_summary += f" 配偶{sp.get('name', '未知')}，{sp.get('gender', '未知')}，{sp_age}岁，"
                main_summary += f"身份证号：{sp.get('id_card', '未填写')}，"
                main_summary += f"联系电话：{sp.get('mobile', '未填写')}。"
        else:
            main_summary = "未填写"
        
        # Build joint borrowers summary
        if joint_borrowers:
            jb_items = []
            for i, jb in enumerate(joint_borrowers, 1):
                if not jb.get('name'):
                    continue
                jb_age = calculate_age(jb.get('id_card', '')) if jb.get('id_card') else '未知'
                jb_text = f"{i}. {jb.get('name', '未知')}，{jb.get('gender', '未知')}，{jb_age}岁，"
                jb_text += f"身份证号：{jb.get('id_card', '未填写')}，"
                jb_text += f"联系电话：{jb.get('mobile', '未填写')}，"
                jb_text += f"职业：{jb.get('occupation', '未填写')}，"
                jb_text += f"与借款人关系：{jb.get('relation', '未填写')}，"
                jb_text += f"住址：{jb.get('address', '未填写')}。"
                jb_items.append(jb_text)
            joint_summary = "\\n".join(jb_items) if jb_items else "无"
        else:
            joint_summary = "无"
        
        # Build guarantors summary
        if guarantors:
            g_items = []
            for i, g in enumerate(guarantors, 1):
                if not g.get('name'):
                    continue
                g_age = calculate_age(g.get('id_card', '')) if g.get('id_card') else '未知'
                g_text = f"{i}. {g.get('name', '未知')}，{g.get('gender', '未知')}，{g_age}岁，"
                g_text += f"身份证号：{g.get('id_card', '未填写')}，"
                g_text += f"联系电话：{g.get('mobile', '未填写')}，"
                g_text += f"职业：{g.get('occupation', '未填写')}，"
                g_text += f"与借款人关系：{g.get('relation', '未填写')}，"
                g_text += f"住址：{g.get('address', '未填写')}。"
                g_items.append(g_text)
            guarantors_summary = "\\n".join(g_items) if g_items else "无"
        else:
            guarantors_summary = "无"
        
        # Build collaterals summary
        if collaterals:
            c_items = []
            for i, c in enumerate(collaterals, 1):
                if not c.get('type'):
                    continue
                c_text = f"{i}. {c.get('type', '未知')}，坐落于{c.get('location', '未填写')}，"
                c_text += f"权证号：{c.get('cert_no', '未填写')}，"
                c_text += f"建筑面积：{c.get('area', '未填写')}，"
                if c.get('land_area'):
                    c_text += f"土地面积：{c.get('land_area')}，"
                c_value = c.get('value', 0)
                c_text += f"评估价值：{c_value}元（{num_to_cn(c_value) if c_value else '未填写'}）。"
                c_items.append(c_text)
            collaterals_summary = "\\n".join(c_items) if c_items else "无"
        else:
            collaterals_summary = "无"
        
        # Prepare context
        context = {
            "loan_use": loan_use,
            "loan_amount": loan_amount,
            "loan_amount_cn": num_to_cn(loan_amount) if loan_amount else "零元整",
            "loan_term": loan_term,
            "main_borrower_summary": main_summary,
            "joint_borrowers_summary": joint_summary,
            "guarantors_summary": guarantors_summary,
            "collaterals_summary": collaterals_summary,
        }
        
        # Load template
        template_path = os.path.join(TEMPLATE_DIR, "investigation_report.docx")
        if not os.path.exists(template_path):
            raise HTTPException(status_code=404, detail="报告模板不存在")
        
        doc = DocxTemplate(template_path)
        doc.render(context)
        
        # Save to temp file
        borrower_name = main_borrower.get('name') if main_borrower else str(loan_amount)
        filename = f"调查报告_{borrower_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.docx"
        temp_file = os.path.join(TEMP_DIR, filename)
        os.makedirs(TEMP_DIR, exist_ok=True)
        doc.save(temp_file)
        
        logger.info(f"生成调查报告: {filename}")
        
        return FileResponse(
            path=temp_file,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    
    except Exception as e:
        logger.error("="*60)
        logger.error("❌ 生成调查报告时发生错误")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误信息: {str(e)}")
        logger.error("详细堆栈:")
        logger.error(traceback.format_exc())
        logger.error("="*60)
        
        error_msg = f"{type(e).__name__}: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)

if __name__ == "__main__":
    import uvicorn
    import socket
    import webbrowser
    import threading
    import time
    
    os.makedirs(TEMPLATE_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    def find_available_port(start_port=8090, max_attempts=10):
        """寻找可用端口"""
        for port in range(start_port, start_port + max_attempts):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('localhost', port)) != 0:
                    return port
        return start_port  # 实在找不到就头铁试一下

    def open_browser(url):
        """延迟打开浏览器"""
        time.sleep(1.5)  # 等待服务器启动
        webbrowser.open(url)

    # 1. 确定端口
    PORT = find_available_port(8090)
    HOST = "0.0.0.0"
    
    logger.info(f"服务即将启动在: http://localhost:{PORT}")
    
    # 2. 检查环境
    is_packaged = getattr(sys, "frozen", False)
    
    if is_packaged:
        # 生产环境：自动打开浏览器，固定端口运行
        server_url = f"http://localhost:{PORT}"
        # 启动浏览器线程
        threading.Thread(target=open_browser, args=(server_url,), daemon=True).start()
        
        # 启动服务器 (生产环境不使用reload)
        uvicorn.run(app, host=HOST, port=PORT, log_config=None)
    else:
        # 开发环境：启用热重载
        # 注意：reload模式下不能简单地自动打开浏览器，因为它会随着reload不断重启
        # 如果需要开发环境也自动打开，可以取消下面注释，但推荐手动点链接
        # threading.Thread(target=open_browser, args=(f"http://localhost:{PORT}",), daemon=True).start()
        
        logger.info(f"🔥 开发模式：已启用热重载 (端口 {PORT})")
        # 开发模式热重载通常需要 "main:app" string
        uvicorn.run("main:app", host=HOST, port=PORT, reload=True, log_config=None)