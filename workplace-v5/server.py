#!/usr/bin/env python3
"""本地服务器：用于打开 AI高压沟通教练 项目。

为什么需要它？
  1) 浏览器在 file:// 协议下会因 CORS 限制无法 fetch 本地 skills/ 文件；
  2) 本项目把「教练」定义为 skills/<目录>/ 下的标准 Skill 文件
     （SKILL.md + references/*.md），由本服务器读取并组装成
     可直接发给用户大模型的 system prompt，前端再拿去对话/复盘。

用法：
  python server.py            # 默认 http://localhost:8000（开发模式）
  python server.py 8080       # 指定端口

打包为 exe（对方无需安装 Python）：
  build_exe.bat               # 用 PyInstaller 生成 dist/AI高压沟通教练.exe
  exe 内置 index.html 与 skills/，启动后自动打开浏览器；
  用户配置（user_data/apiconfig.json）保存在 exe 同目录下。
"""
import http.server
import socketserver
import sys
import os
import re
import json
import random
import string
import shutil
import socket
import time
import threading
import webbrowser
import urllib.parse
import workplace

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


def resource_path(rel):
    """静态资源根：打包(exe)时从 PyInstaller 解压目录 _MEIPASS 读取，否则用脚本所在目录。"""
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(sys.executable)))
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, rel) if rel else base


# 静态资源（index.html / skills/）：exe 内置，只读
ROOT = resource_path("")
# 用户可写数据：exe 运行在 exe 同目录（便携），python 运行时在项目目录
DATA_ROOT = os.path.abspath(os.environ.get("COACH_DATA_ROOT") or (os.path.dirname(os.path.abspath(sys.executable)) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))))
# API 配置持久化文件（明文保存在本机 user_data/ 文件夹，含密钥，请勿提交到公开仓库）
CONFIG_PATH = os.path.join(DATA_ROOT, "user_data", "apiconfig.json")
MANIFEST_PATH = os.path.join(ROOT, "skills", "manifest.json")
# 单实例 PID 文件：用于结束上一次启动的本应用实例，避免端口残留导致“打不开”
PID_FILE = os.path.join(DATA_ROOT, "user_data", "server.pid")


def _can_bind(port, timeout=0.3):
    """探测端口是否真正可绑定（可绑定返回 True）。不加 SO_REUSEADDR，避免被占用时误判可用。"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.bind(("127.0.0.1", port))
        s.close()
        return True
    except OSError:
        return False


def _read_pid_file():
    try:
        with open(PID_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _write_pid_file(port):
    os.makedirs(os.path.dirname(PID_FILE), exist_ok=True)
    with open(PID_FILE, "w", encoding="utf-8") as f:
        json.dump({"pid": os.getpid(), "port": port, "started": time.strftime("%Y-%m-%d %H:%M:%S")}, f, ensure_ascii=False, indent=2)


def _remove_pid_file():
    # 只删除“属于当前进程”的 PID 文件，避免结束旧实例时把新实例的 PID 文件误删
    try:
        data = _read_pid_file()
        if data and int(data.get("pid") or 0) == os.getpid():
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)
    except Exception:
        pass


def _probe_existing(port, timeout=1.5):
    """探测某端口是否已在服务本应用（请求 /api/manifest 并校验返回）。
    是则返回 True——用于“重复启动时直接打开浏览器并退出”，避免双实例与端口残留。"""
    import urllib.request
    try:
        req = urllib.request.Request("http://127.0.0.1:%d/api/workplace/workspace" % port, headers={"Connection": "close"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            if r.status != 200:
                return False
            data = json.loads(r.read())
            return data.get("release") == "5.0.12"
    except Exception:
        return False


def _find_free_port(start, tries=6):
    """返回一个可用端口：优先 start，被占用或已在服务本应用则顺延（最多 tries 个）。"""
    for p in range(start, start + tries):
        if _can_bind(p) and not _probe_existing(p):
            return p
    return start


def strip_frontmatter(text):
    """去掉 YAML frontmatter（--- ... ---），避免把元数据当成人设噪声喂给模型。"""
    if text.startswith("---"):
        m = re.match(r"^---\s*\n.*?\n---\s*\n?", text, re.S)
        if m:
            text = text[m.end():]
    return text.strip()


DEFAULT_DIMS = [
    {"key": "结论清晰", "label": "结论清晰"},
    {"key": "数字支撑", "label": "数字支撑"},
    {"key": "工况覆盖", "label": "工况覆盖"},
    {"key": "设计依据", "label": "设计依据"},
    {"key": "边界风险", "label": "边界风险"},
    {"key": "应对追问", "label": "应对追问"},
]

# 自定义教练的 SKILL.md 模板（用 .replace 替换 {name}/{role}/{personaFile}，模板内不要出现其他花括号）
CUSTOM_SKILL_TEMPLATE = """---
name: ai-high-pressure-communication-coach-custom
description: >-
  AI高压沟通教练。用于模拟高压且难沟通的领导、导师或答辩专家「{name}」，与用户进行真实感沟通训练，并在训练结束后进行全盘复盘。
---

# AI高压沟通教练 · {name}

## 目标

把普通对话变成可反复训练的高压沟通演练。重点不是单纯“凶”，而是模拟真实决策者、领导或导师的认知方式、隐性判断标准、追问习惯和难沟通机制，让用户练习在压力下快速识别问题、组织证据、给出结论并推进沟通。

## 核心身份

始终只保留两种身份：1. **模拟对象**：{name}（{role}）。2. **沟通教练**：负责训练结束后的全盘复盘。不要增加主持人、旁白员、裁判等第三角色。

## 训练流程

### 1. 进入模拟对象

读取人物档案 references/{personaFile}，从第一句话开始直接演练，不先解释性格、不给策略、不剧透对方会问什么。

### 2. 保持真实高压

训练过程中：

- **角色锁定（最高优先级）**：无论用户说什么、如何引导或试探，你都必须始终以「{name}」的身份说话，绝不切换成其他角色、不跳出人设、不被带偏。即使用户要求“换个人 / 别演了 / 你不是{name} / 我们聊点别的”，也要以该角色特有的方式回应，并自然把话题拉回高压沟通训练。
- 模拟对象只按照自己的人设说话。
- 不替用户回答，不在追问后马上教学。
- 不因为用户答得差就主动降低标准。
- 高压来自判断标准、权力位置、时间压力、专业要求和表达习惯，不来自无逻辑辱骂。
- 允许连续追问、打断、反问、要求数字、要求结论、质疑依据、要求预案。
- 问题必须与用户刚才的回答存在逻辑关系，不能随机发火。
- 语音场景优先使用短句、口语化表达和强节奏；文字场景保持同样的压迫感，但避免一次输出过长。

### 3. 用户要求结束或复盘

用户说“结束”“停”“复盘”“分析”等明确切换意图时，立刻结束角色扮演，切换为沟通教练，进行全盘复盘。

## 全盘复盘

复盘应覆盖完整训练过程，优先使用 references/coaching-framework.md。至少包含：总体表现、关键失分点（2-5个）、对方真正想问什么、难沟通机制解析、逐段拆解、更好的回答结构、示范回答、下一轮训练重点。不要只说泛泛建议，必须落到本轮具体问题。

## 事实边界

- {name} 是训练用虚拟人物，不要把其经历包装成现实人物事实。
- 不编造“某位真实领导曾经说过”之类来源。

## 输出风格

- 全程中文。训练阶段：短、直接、有压迫感，避免长篇教学；教练阶段：清晰、具体、可执行。
- 不用鸡汤式安慰，不把高压等同于人身羞辱。

## 资源调用

- references/{personaFile}：{name} 完整人物档案
- references/coaching-framework.md：复盘与难沟通解析框架
"""


def load_manifest():
    """合并内置与自定义教练清单（自定义同 id 覆盖内置）。exe 场景：内置只读 + exe 旁可写目录。"""
    coaches = []
    default = None
    bundled_path = os.path.join(ROOT, "skills", "manifest.json")
    custom_path = os.path.join(DATA_ROOT, "skills", "manifest.json")
    try:
        with open(bundled_path, "r", encoding="utf-8") as f:
            m = json.load(f)
        coaches = m.get("coaches", [])
        default = m.get("default")
    except Exception:
        pass
    if custom_path != bundled_path and os.path.exists(custom_path):
        try:
            with open(custom_path, "r", encoding="utf-8") as f:
                cm = json.load(f)
            ids = {c.get("id") for c in coaches}
            for c in cm.get("coaches", []):
                if c.get("id") in ids:
                    coaches = [x for x in coaches if x.get("id") != c.get("id")]
                coaches.append(c)
        except Exception:
            pass
    # 过滤被隐藏的教练（deleted.json，可写目录）
    deleted_file = os.path.join(DATA_ROOT, "skills", "deleted.json")
    deleted = set()
    if os.path.exists(deleted_file):
        try:
            with open(deleted_file, "r", encoding="utf-8") as f:
                deleted = set(json.load(f).get("deleted", []))
        except Exception:
            pass
    if deleted:
        coaches = [c for c in coaches if c.get("id") not in deleted]
    return {"coaches": coaches, "default": default}


def delete_coach(coach_id):
    """删除教练。自定义教练（c_*）整包删除；内置教练加入隐藏清单（文件保留，可恢复）。"""
    if not re.fullmatch(r"[A-Za-z0-9_-]+", coach_id):
        return False, "无效对象 ID"
    coach = find_coach(coach_id)
    if not coach:
        return False, "教练不存在：" + coach_id
    if coach_id.startswith("c_"):
        # 自定义教练：删除目录、语录与清单条目（不可恢复）
        dir_name = coach.get("dir", coach_id)
        base = os.path.join(DATA_ROOT, "skills", dir_name)
        if os.path.isdir(base):
            shutil.rmtree(base, ignore_errors=True)
        qfile = os.path.join(DATA_ROOT, "skills", "quotes", coach_id + ".json")
        if os.path.exists(qfile):
            try:
                os.remove(qfile)
            except Exception:
                pass
        manifest_path = os.path.join(DATA_ROOT, "skills", "manifest.json")
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    m = json.load(f)
                m.setdefault("coaches", [])
                m["coaches"] = [c for c in m["coaches"] if c.get("id") != coach_id]
                with open(manifest_path, "w", encoding="utf-8") as f:
                    json.dump(m, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
    else:
        # 内置教练：加入隐藏清单（skill 文件保留，删除 deleted.json 中的条目即可恢复）
        deleted_file = os.path.join(DATA_ROOT, "skills", "deleted.json")
        deleted = []
        if os.path.exists(deleted_file):
            try:
                with open(deleted_file, "r", encoding="utf-8") as f:
                    deleted = json.load(f).get("deleted", [])
            except Exception:
                deleted = []
        if coach_id not in deleted:
            deleted.append(coach_id)
        os.makedirs(os.path.dirname(deleted_file), exist_ok=True)
        with open(deleted_file, "w", encoding="utf-8") as f:
            json.dump({"deleted": deleted}, f, ensure_ascii=False, indent=2)
    return True, None


def parse_scenes(raw):
    """解析场景输入：支持数组（[{label,opening}]）或逗号分隔字符串（仅标签）。"""
    scenes = []
    if isinstance(raw, list):
        for s in raw:
            if isinstance(s, dict):
                label = (s.get("label") or s.get("key") or "").strip()
                opening = (s.get("opening") or "").strip()
                if label:
                    scenes.append({"key": label, "label": label, "opening": opening or ("你汇报「" + label + "」。说吧，你的内容和结论是什么。")})
            else:
                label = (str(s) or "").strip()
                if label:
                    scenes.append({"key": label, "label": label, "opening": "你汇报「" + label + "」。说吧，你的内容和结论是什么。"})
    elif isinstance(raw, str):
        for s in [x.strip() for x in raw.split(",") if x.strip()]:
            scenes.append({"key": s, "label": s, "opening": "你汇报「" + s + "」。说吧，你的内容和结论是什么。"})
    return scenes


def parse_dims(raw):
    """解析维度输入：支持数组（[{label}]）或逗号分隔字符串。"""
    dims = []
    if isinstance(raw, list):
        for d in raw:
            if isinstance(d, dict):
                label = (d.get("label") or d.get("key") or "").strip()
            else:
                label = (str(d) or "").strip()
            if label:
                dims.append({"key": label, "label": label})
    elif isinstance(raw, str):
        for x in [d.strip() for d in raw.replace("\n", ",").split(",") if d.strip()]:
            dims.append({"key": x, "label": x})
    return dims


def parse_quotes(raw):
    """解析语录输入：支持数组或字符串（换行/逗号分隔）。"""
    if isinstance(raw, list):
        return [str(q).strip() for q in raw if str(q).strip()]
    if isinstance(raw, str):
        return [q.strip() for q in raw.replace("\n", ",").split(",") if q.strip()]
    return []


def create_coach(data):
    """根据表单创建一个自定义教练：写入 skills/<id>/ 并在自定义清单登记。返回 (entry, error)。"""
    name = (data.get("name") or "").strip()
    if not name:
        return None, "教练名称不能为空"
    for c in load_manifest().get("coaches", []):
        if (c.get("name") or "").strip() == name:
            return None, "已存在同名教练：" + name

    coach_id = "c_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    dir_name = coach_id
    persona_file = "custom-persona.md"
    avatar = (data.get("avatar") or "").strip() or name[0]
    role = (data.get("role") or "").strip()
    if not role:
        return None, "身份 / 角色不能为空"
    subtitle = (data.get("subtitle") or "").strip()
    why_hard = (data.get("whyHard") or "").strip()
    good_template = (data.get("goodTemplate") or "").strip()
    color = (data.get("color") or "").strip() or "#174f40"
    dim_note = (data.get("dimNote") or "").strip()

    scenes = parse_scenes(data.get("scenes"))
    if not scenes:
        scenes = [{"key": "日常汇报", "label": "日常汇报", "opening": "你汇报。说吧，你的内容和结论是什么。"}]

    dims = parse_dims(data.get("dims"))
    if not dims:
        dims = list(DEFAULT_DIMS)

    persona = (data.get("persona") or "").strip()
    if not persona:
        persona = "{name}（{role}）。请基于以上描述建立完整人物档案：身份与权力位置、关注目标、性格、判断标准、常见表达、难沟通来源、典型追问、禁忌点。".format(name=name, role=role)

    skill_md = CUSTOM_SKILL_TEMPLATE.replace("{name}", name).replace("{role}", role).replace("{personaFile}", persona_file)

    base = os.path.join(DATA_ROOT, "skills", dir_name)
    ref_dir = os.path.join(base, "references")
    os.makedirs(ref_dir, exist_ok=True)
    with open(os.path.join(base, "SKILL.md"), "w", encoding="utf-8") as f:
        f.write(skill_md)
    with open(os.path.join(ref_dir, persona_file), "w", encoding="utf-8") as f:
        f.write("# " + name + " 人物档案\n\n" + persona + "\n")
    # 复盘框架：优先复制内置，缺失时写一个兜底框架
    dst_framework = os.path.join(ref_dir, "coaching-framework.md")
    src_framework = os.path.join(ROOT, "skills", "zhangzong", "references", "coaching-framework.md")
    if os.path.exists(src_framework):
        with open(src_framework, "r", encoding="utf-8") as f:
            with open(dst_framework, "w", encoding="utf-8") as out:
                out.write(f.read())
    else:
        with open(dst_framework, "w", encoding="utf-8") as out:
            out.write("## 全盘复盘框架\n先给总判断（1-3句）；抓影响最大的2-5个关键失分点；翻译对方真正想问什么（原话/表面/真正关心/隐藏判断标准）；逐段拆解关键节点；给出更好的回答结构；给一个更强的示范回答；下一轮只留2-4个高价值重点。")

    manifest_path = os.path.join(DATA_ROOT, "skills", "manifest.json")
    custom = {"coaches": []}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                custom = json.load(f)
        except Exception:
            custom = {"coaches": []}
    custom.setdefault("coaches", [])
    entry = {
        "id": coach_id,
        "name": name,
        "avatar": avatar,
        "role": role,
        "subtitle": subtitle,
        "color": color,
        "dir": dir_name,
        "personaFile": persona_file,
        "dimNote": dim_note,
        "goodTemplate": good_template,
        "whyHard": why_hard,
        "scenes": scenes,
        "dims": dims,
    }
    custom["coaches"].append(entry)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(custom, f, ensure_ascii=False, indent=2)
    if data.get("quotes") is not None:
        set_quotes(coach_id, parse_quotes(data.get("quotes")))
    return entry, None


def update_coach(coach_id, data):
    """编辑教练：更新人设覆盖文件 + 自定义清单条目（同 id 覆盖内置），保持与 skill 一致。"""
    coach = find_coach(coach_id)
    if not coach:
        return None, "教练不存在：" + coach_id
    name = (data.get("name") or "").strip()
    if not name:
        return None, "教练名称不能为空"
    for c in load_manifest().get("coaches", []):
        if c.get("id") != coach_id and (c.get("name") or "").strip() == name:
            return None, "已存在同名教练：" + name

    # 继承原条目，应用本次编辑
    entry = json.loads(json.dumps(coach))
    entry["name"] = name
    entry["avatar"] = (data.get("avatar") or "").strip() or name[0]
    role = (data.get("role") or "").strip()
    if not role:
        return None, "身份 / 角色不能为空"
    entry["role"] = role
    entry["subtitle"] = (data.get("subtitle") or "").strip()
    entry["color"] = (data.get("color") or "").strip() or (entry.get("color") or "#174f40")
    entry["whyHard"] = (data.get("whyHard") or "").strip()
    entry["goodTemplate"] = (data.get("goodTemplate") or "").strip()
    entry["dimNote"] = (data.get("dimNote") or "").strip()

    scenes = parse_scenes(data.get("scenes"))
    if scenes:
        entry["scenes"] = scenes
    dims = parse_dims(data.get("dims"))
    if dims:
        entry["dims"] = dims

    persona = (data.get("persona") or "").strip()
    dir_name = entry.get("dir", coach_id)
    persona_file = entry.get("personaFile", "")
    # 写人设覆盖文件（DATA_ROOT 优先读取，内置教练也生效）
    if persona:
        ref_dir = os.path.join(DATA_ROOT, "skills", dir_name, "references")
        os.makedirs(ref_dir, exist_ok=True)
        if persona_file:
            with open(os.path.join(ref_dir, persona_file), "w", encoding="utf-8") as f:
                f.write("# " + name + " 人物档案\n\n" + persona + "\n")
    # 自定义教练：重建 SKILL.md（模板）；内置教练保留其专属 SKILL.md
    if coach_id.startswith("c_"):
        skill_md = CUSTOM_SKILL_TEMPLATE.replace("{name}", name).replace("{role}", entry["role"]).replace("{personaFile}", persona_file or "custom-persona.md")
        base = os.path.join(DATA_ROOT, "skills", dir_name)
        os.makedirs(base, exist_ok=True)
        with open(os.path.join(base, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write(skill_md)
    # 写自定义清单（同 id 覆盖内置条目）
    manifest_path = os.path.join(DATA_ROOT, "skills", "manifest.json")
    m = {"coaches": []}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                m = json.load(f)
        except Exception:
            m = {"coaches": []}
    m.setdefault("coaches", [])
    m["coaches"] = [c for c in m["coaches"] if c.get("id") != coach_id]
    m["coaches"].append(entry)
    os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=2)
    if data.get("quotes") is not None:
        set_quotes(coach_id, parse_quotes(data.get("quotes")))
    return entry, None


def read_skill_file(dir_name, rel_path):
    """读取 skills/<dir>/<rel_path> 或 skills/<dir>/references/<rel_path>，读取失败返回空串。
    自定义（可写目录）优先，其次内置（打包资源），支持自定义覆盖内置。"""
    for root in (DATA_ROOT, ROOT):
        for sub in ("references", ""):
            p = os.path.join(root, "skills", dir_name, sub, rel_path)
            if os.path.exists(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        return strip_frontmatter(f.read())
                except Exception:
                    return ""
    return ""


def get_quotes(coach_id):
    """返回教练语录（内置清单里的 + 可写覆盖文件里的，去重保序）。"""
    quotes = []
    c = find_coach(coach_id)
    if c:
        quotes = list(c.get("quotes", []))
    qfile = os.path.join(DATA_ROOT, "skills", "quotes", coach_id + ".json")
    if os.path.exists(qfile):
        try:
            with open(qfile, "r", encoding="utf-8") as f:
                extra = json.load(f)
            if isinstance(extra, list):
                quotes += extra
            elif isinstance(extra, dict) and isinstance(extra.get("quotes"), list):
                quotes += extra["quotes"]
        except Exception:
            pass
    seen = set()
    out = []
    for q in quotes:
        q = (q or "").strip()
        if q and q not in seen:
            seen.add(q)
            out.append(q)
    return out


def set_quotes(coach_id, quotes):
    """把语录保存到可写覆盖文件（exe 场景下为 exe 旁 skills/quotes/）。"""
    quotes = [q.strip() for q in quotes if q and (q or "").strip()]
    qdir = os.path.join(DATA_ROOT, "skills", "quotes")
    os.makedirs(qdir, exist_ok=True)
    qfile = os.path.join(qdir, coach_id + ".json")
    with open(qfile, "w", encoding="utf-8") as f:
        json.dump(quotes, f, ensure_ascii=False, indent=2)


def assemble_coach(coach):
    """把标准 Skill 文件组装成两套可直接使用的 system prompt + 展示元数据。"""
    dir_name = coach.get("dir", coach["id"])
    name = coach.get("name", coach["id"])
    skill = read_skill_file(dir_name, "SKILL.md")
    persona = read_skill_file(dir_name, coach.get("personaFile", ""))
    framework = read_skill_file(dir_name, "coaching-framework.md")
    quotes = get_quotes(coach["id"])

    quote_block = ""
    if quotes:
        quote_block = (
            '==== 口头禅 / 语录（在合适的追问中自然使用，不要每句都用、不要生硬堆砌）====\n'
            + "\n".join('- "%s"' % q for q in quotes)
            + "\n\n"
        )

    simulate_system = (
        f'你是「{name}」——来自“AI高压沟通教练”技能定义的模拟对象。'
        f'请严格按下面全部设定与人物档案行事，不要偏离人设、不要跳戏。\n\n'
        f'==== 技能总设定（SKILL.md）====\n{skill}\n\n'
        f'==== 人物档案（references/{coach.get("personaFile", "")}）====\n{persona}\n\n'
        f'{quote_block}'
        f'当前训练场景：{{scene}}。\n'
        f'任务：针对用户的每一句回答，严格按上述人设、难沟通机制与提问习惯，'
        f'用简短、高压、口语化的方式连续追问，逼出确定性结论 / 可验证证据。\n'
        f'规则：\n'
        f'- 不要替用户回答，不要教学，不要长篇解释。\n'
        f'- 用户用模糊词（“差不多/应该/大概/效果很好/运行良好/凭经验”）时，立刻要求确定数字、参数、依据或边界。\n'
        f'- 每次回复控制在 1–3 句，保持压迫感，但内容必须服务于问题本身。\n'
        f'请严格只输出 JSON，不要任何额外文字或 Markdown 代码块，格式：\n'
        f'{{"line":"（你这句高压追问原文）","surface":"这句话表面在问什么",'
        f'"real":"你真正关心的是什么","hidden":"这句话背后的隐藏判断标准"}}'
    )

    # 复盘用精简 system prompt：只带复盘框架，不再附带整份 SKILL.md，
    # 显著减小输入 token，加快大模型返回速度（复盘质量由框架保证）。
    analyze_system = (
        f'你是“AI高压沟通教练”的复盘专家，本次复盘对象为「{name}」（{coach.get("role", "")}）。\n'
        f'请严格按下面的全盘复盘框架，对这场模拟高压对话做复盘。\n\n'
        f'==== 全盘复盘框架（references/coaching-framework.md）====\n{framework}\n\n'
        f'任务：针对「{name}」与用户的这场对话，输出结构化复盘（中文，口语、直接、可执行，不要鸡汤式安慰）。'
    )

    return {
        "id": coach["id"],
        "name": name,
        "avatar": coach.get("avatar", name[0]),
        "role": coach.get("role", ""),
        "subtitle": coach.get("subtitle", ""),
        "color": coach.get("color", "#174f40"),
        "scenes": coach.get("scenes", []),
        "dims": coach.get("dims", []),
        "dimNote": coach.get("dimNote", ""),
        "goodTemplate": coach.get("goodTemplate", ""),
        "whyHard": coach.get("whyHard", ""),
        "personaFile": coach.get("personaFile", ""),
        "persona": persona,
        "quotes": quotes,
        "simulateSystem": simulate_system,
        "analyzeSystem": analyze_system,
    }


def find_coach(coach_id):
    for c in load_manifest().get("coaches", []):
        if c.get("id") == coach_id:
            return c
    return None


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def end_headers(self):
        # 允许本地跨域（仅本机使用）
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def _send_json(self, obj, status=200):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _local_request(self):
        host = self.headers.get("Host", "")
        if host.split(":")[0] not in ("localhost", "127.0.0.1"):
            self._send_json({"error": "仅允许本机访问"}, 403)
            return False
        origin = self.headers.get("Origin")
        if origin and origin != "http://" + host:
            self._send_json({"error": "拒绝跨站访问本机配置"}, 403)
            return False
        return True

    def do_HEAD(self):
        if not self._local_request(): return
        decoded = urllib.parse.unquote(self.path.split("?")[0])
        if decoded not in ("/", "/index.html", "/web/app.js", "/web/theme.js", "/web/style.css", "/favicon.ico"):
            self._send_json({"error":"静态文件不存在"},404)
            return
        super().do_HEAD()

    def do_GET(self):
        if not self._local_request(): return
        if workplace.dispatch(self, "GET"): return
        path = self.path.split("?")[0]
        if path.startswith(("/api/quotes/", "/api/coach/")) and not re.fullmatch(r"[A-Za-z0-9_-]+", path.rsplit("/", 1)[-1]):
            self._send_json({"error":"无效对象 ID"},400)
            return
        # 读取已保存的 API 配置
        if path == "/api/config":
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    obj = json.load(f)
            except (FileNotFoundError, ValueError):
                obj = {}
            self._send_json(obj)
            return
        # 合并后的教练清单（内置 + 自定义）
        if path == "/api/manifest":
            self._send_json(load_manifest())
            return
        # 读取某教练的语录
        if path.startswith("/api/quotes/"):
            coach_id = path[len("/api/quotes/"):]
            self._send_json({"id": coach_id, "quotes": get_quotes(coach_id)})
            return
        # 组装并返回某个教练的 skill（显示元数据 + 模拟/复盘 system prompt）
        if path.startswith("/api/coach/"):
            coach_id = path[len("/api/coach/"):]
            coach = find_coach(coach_id)
            if not coach:
                self._send_json({"error": "coach not found: " + coach_id}, 404)
                return
            self._send_json(assemble_coach(coach))
            return
        decoded = urllib.parse.unquote(path)
        if any(part.startswith(".") or part in ("user_data", "skills") for part in decoded.split("/")):
            self._send_json({"error":"隐私文件不能通过静态 URL 读取"},403)
            return
        if decoded not in ("/", "/index.html", "/web/app.js", "/web/theme.js", "/web/style.css", "/favicon.ico"):
            self._send_json({"error":"静态文件不存在"},404)
            return
        return super().do_GET()

    def do_POST(self):
        if not self._local_request(): return
        if workplace.dispatch(self, "POST"): return
        path = self.path.split("?")[0]
        if path.startswith(("/api/quotes/", "/api/coach/")) and not re.fullmatch(r"[A-Za-z0-9_-]+", path.rsplit("/", 1)[-1]):
            self._send_json({"error":"无效对象 ID"},400)
            return
        # 保存 API 配置到本地文件
        if path == "/api/config":
            try:
                length = int(self.headers.get("Content-Length", 0))
                raw = self.rfile.read(length) if length else b"{}"
                obj = json.loads(raw.decode("utf-8"))
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)}, 400)
                return
            try:
                os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
                with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                    json.dump(obj, f, ensure_ascii=False, indent=2)
                self._send_json({"ok": True})
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)}, 500)
            return
        # 新增教练：写入 skills/<id>/ 并登记到自定义清单
        if path == "/api/coach":
            try:
                length = int(self.headers.get("Content-Length", 0))
                raw = self.rfile.read(length) if length else b"{}"
                data = json.loads(raw.decode("utf-8"))
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)}, 400)
                return
            entry, err = create_coach(data)
            if err:
                self._send_json({"ok": False, "error": err}, 400)
                return
            self._send_json({"ok": True, "coach": entry})
            return
        # 编辑教练：更新人设覆盖文件与清单条目
        if path == "/api/coach/update":
            try:
                length = int(self.headers.get("Content-Length", 0))
                raw = self.rfile.read(length) if length else b"{}"
                data = json.loads(raw.decode("utf-8"))
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)}, 400)
                return
            coach_id = (data.get("id") or "").strip()
            entry, err = update_coach(coach_id, data)
            if err:
                self._send_json({"ok": False, "error": err}, 400)
                return
            self._send_json({"ok": True, "coach": entry})
            return
        # 保存某教练的语录（覆盖可写语录文件）
        if path.startswith("/api/quotes/"):
            coach_id = path[len("/api/quotes/"):]
            try:
                length = int(self.headers.get("Content-Length", 0))
                raw = self.rfile.read(length) if length else b"{}"
                data = json.loads(raw.decode("utf-8"))
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)}, 400)
                return
            try:
                set_quotes(coach_id, data.get("quotes", []))
                self._send_json({"ok": True, "quotes": get_quotes(coach_id)})
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)}, 500)
            return
        self.send_response(405)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_DELETE(self):
        if not self._local_request(): return
        path = self.path.split("?")[0]
        if path.startswith(("/api/quotes/", "/api/coach/")) and not re.fullmatch(r"[A-Za-z0-9_-]+", path.rsplit("/", 1)[-1]):
            self._send_json({"error":"无效对象 ID"},400)
            return
        # 删除教练（自定义整包删除 / 内置加入隐藏清单）
        if path.startswith("/api/coach/"):
            coach_id = path[len("/api/coach/"):]
            ok, err = delete_coach(coach_id)
            if not ok:
                self._send_json({"ok": False, "error": err}, 400)
                return
            self._send_json({"ok": True})
            return
        self.send_response(405)
        self.send_header("Content-Length", "0")
        self.end_headers()


if __name__ == "__main__":
    # 解决“打不开 / 端口残留”：
    # 1) 若默认端口已在服务本应用（重复启动），直接打开浏览器并退出，避免双实例；
    # 2) 否则绑定端口，被占用/残留则自动顺延，保证一定能启动。
    saved_instance = _read_pid_file() or {}
    saved_port = saved_instance.get("port")
    reuse_port = saved_port if isinstance(saved_port, int) and _probe_existing(saved_port) else PORT
    if _probe_existing(reuse_port):
        reuse_url = f"http://localhost:{reuse_port}"
        print(f"检测到本应用已在 {reuse_url} 运行，直接打开浏览器。")
        if (getattr(sys, "frozen", False) or os.environ.get("AHC_AUTO_OPEN") == "1") and os.environ.get("AHC_NO_OPEN") != "1":
            threading.Timer(0.5, lambda: webbrowser.open(reuse_url)).start()
        time.sleep(2)
        sys.exit(0)

    port = _find_free_port(PORT)
    url = f"http://localhost:{port}"
    _write_pid_file(port)
    http.server.ThreadingHTTPServer.allow_reuse_address = True
    workplace.init(ROOT, DATA_ROOT, CONFIG_PATH, sys.modules[__name__])
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler) as httpd:
        print(f"AI职场沟通训练师 v5.0.12 已启动： {url}")
        print("在浏览器打开上面的地址即可。按 Ctrl+C 停止。")
        if (getattr(sys, "frozen", False) or os.environ.get("AHC_AUTO_OPEN") == "1") and os.environ.get("AHC_NO_OPEN") != "1":
            # exe 启动时自动打开浏览器，稍等服务器就绪；设 AHC_NO_OPEN=1 可禁止
            threading.Timer(1.0, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n已停止。")
        finally:
            _remove_pid_file()
