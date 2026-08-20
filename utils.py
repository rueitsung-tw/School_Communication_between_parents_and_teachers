import os
import re
import json
import hashlib
import datetime
import urllib.request
import openai
import google.generativeai as genai
from typing import Dict, List, Tuple, Optional

def clean_base_url(url: str) -> str:
    """
    清理 API URL，移除尾隨的斜線及 /v1
    """
    cleaned = url.strip().rstrip("/")
    if cleaned.endswith("/v1"):
        cleaned = cleaned[:-3].rstrip("/")
    return cleaned

def get_ollama_models(base_url: str = "http://localhost:11434", api_key: str = "") -> list:
    """
    向本地 Ollama / OpenAI 相容伺服器獲取模型列表。
    """
    clean_url = clean_base_url(base_url)
    
    # 嘗試 1: Ollama api/tags
    try:
        url = f"{clean_url}/api/tags"
        req = urllib.request.Request(url, method="GET")
        if api_key and api_key != "ollama":
            req.add_header("Authorization", f"Bearer {api_key}")
        with urllib.request.urlopen(req, timeout=2) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                return [model["name"] for model in data.get("models", [])]
    except Exception:
        pass
        
    # 嘗試 2: OpenAI 相容的 /v1/models (適用於 LiteLLM, One-API, vLLM 等)
    try:
        url = f"{clean_url}/v1/models"
        req = urllib.request.Request(url, method="GET")
        if api_key and api_key != "ollama":
            req.add_header("Authorization", f"Bearer {api_key}")
        with urllib.request.urlopen(req, timeout=2) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                return [model["id"] for model in data.get("data", [])]
    except Exception:
        pass
        
    # 預設回傳常見模型列表以防伺服器未啟動
    return ["qwen2.5:7b", "llama3", "gemma2", "mistral"]

def extract_prompt_from_markdown(content: str, section_title: str) -> Optional[str]:
    """
    從 Markdown 內容中，根據小標題（例如 '## Type A' 或 '## 提示詞'）
    提取緊隨其後的第一個 code block 內容。
    """
    pattern = rf"(##\s+{re.escape(section_title)}.*?)\n(.*?)(?=\n##\s+|\Z)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    if not match:
        pattern = rf"(##\s*.*{re.escape(section_title)}.*?)\n(.*?)(?=\n##\s*|\Z)"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if not match:
            return None
            
    section_content = match.group(2)
    code_match = re.search(r"```[a-zA-Z]*\n(.*?)```", section_content, re.DOTALL)
    if code_match:
        return code_match.group(1).strip()
    return None

def parse_prompt_file(filepath: str) -> Dict[str, str]:
    """
    解析單個提示詞 md 檔案，回傳一個包含 Type A 和 Type B 提示詞的字典。
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    filename = os.path.basename(filepath)
    result = {}
    
    if "00_通用" in filename:
        prompt_text = extract_prompt_from_markdown(content, "提示詞")
        if prompt_text:
            if "TypeA" in filename:
                result["Type A"] = prompt_text
            else:
                result["Type B"] = prompt_text
    else:
        prompt_a = extract_prompt_from_markdown(content, "Type A")
        prompt_b = extract_prompt_from_markdown(content, "Type B")
        if prompt_a:
            result["Type A"] = prompt_a
        if prompt_b:
            result["Type B"] = prompt_b
            
    return result

def load_all_prompts(prompts_dir: str) -> Dict[str, Dict[str, str]]:
    """
    讀取 prompts 目錄下所有提示詞，並依主題分類。
    """
    prompts_db = {}
    if not os.path.exists(prompts_dir):
        return prompts_db
        
    for filename in os.listdir(prompts_dir):
        if filename.endswith(".md"):
            filepath = os.path.join(prompts_dir, filename)
            theme_key = filename.replace(".md", "")
            prompts_db[theme_key] = parse_prompt_file(filepath)
            
    return prompts_db

def load_theme_taxonomy(filepath: str) -> Dict[int, Dict]:
    """
    解析 theme_taxonomy.md，提取出各主題的背景資料。
    """
    taxonomy = {}
    if not os.path.exists(filepath):
        return taxonomy
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    parts = content.split("### 主題 ")
    for part in parts[1:]:
        lines = part.strip().split("\n")
        title_line = lines[0].strip()
        match = re.match(r"(\d+)[：:](.*)", title_line)
        if not match:
            continue
        theme_id = int(match.group(1))
        theme_name = match.group(2).strip()
        
        data = {}
        for line in lines:
            if "|" in line and "**" in line:
                cols = [c.strip() for c in line.split("|") if c.strip()]
                if len(cols) >= 2:
                    key = cols[0].replace("**", "").strip()
                    val = cols[1].strip()
                    data[key] = val
        taxonomy[theme_id] = {
            "name": theme_name,
            "data": data
        }
    return taxonomy

def load_vocab_rules(vocab_filepath: str) -> str:
    """
    讀取 taiwan_vocab.md 辭彙對照表，提取「文體風格指引」段落，
    組合成 AI 可直接套用的語言約束指令。
    """
    base_rules = (
        "【語言與辭彙強制規範 - 台灣繁體中文】\n"
        "1. 所有回覆必須使用「繁體中文」，嚴禁輸出簡體字或日文假名。\n"
        "2. 必須使用台灣在地慣用辭彙：\n"
        "   - 說「導師」不說「班主任」\n"
        "   - 說「傳 LINE / 傳訊息」不說「發訊息 / 發微信」\n"
        "   - 說「聯絡簿」不說「聯絡册」\n"
        "   - 說「班親會」不說「家長會（大陸用法）」\n"
        "   - 說「回家作業」不說「課外作業」\n"
        "   - 說「才藝班」不說「興趣班」\n"
        "   - 說「特殊生」不說「特殊兒童」\n"
        "   - 說「視訊」不說「視頻」\n"
        "   - 說「網路」不說「互聯網」\n"
        "   - 說「應用程式」不說「應用程序」\n"
        "3. 語氣風格要求：半正式、溫暖、有呼吸感。\n"
        "   - 正確示範：「謝謝您讓我知道，我也很關心這件事……」\n"
        "   - 正確示範：「您說的這個狀況，我完全能理解您的擔心……」\n"
        "   - 嚴禁官腔：「敬悉您的反映，已依規定辦理。」\n"
        "   - 嚴禁條列：強制禁止使用「1. 2. 3.」或「•」開頭的條列清單。\n"
        "   - 嚴禁推責：「這個問題您應該在家教好孩子……」\n"
        "4. 斷句須有「呼吸感」：適當使用省略號（……）、長破折號（──）或換行，\n"
        "   讓回覆讀起來像一個真實的人在說話，而非機器輸出的公文。\n"
        "5. 日期格式優先使用民國年份（例：113年9月1日），次選西元年份。\n"
    )
    
    if vocab_filepath and os.path.exists(vocab_filepath):
        # 如果辭彙表存在，附上一行提示確認已載入
        base_rules += "\n（本次已載入 taiwan_vocab.md 台灣辭彙對照表作為參考依據）"
    
    return base_rules

def build_knowledge_context(theme_key: str, taxonomy_db: dict, vocab_filepath: str = "") -> str:
    """
    從本地知識庫 (theme_taxonomy.md 等) 動態擷取與當前主題相關的學理、法規與溝通準則，
    並整合台灣繁體中文語言規範，組合為結構化的本地知識庫脈絡 (Context)，
    以增強本地模型 (Ollama) 的回答準確度。
    """
    # 載入語言強制規範
    lang_rules = load_vocab_rules(vocab_filepath)
    
    theme_id_match = re.search(r"(\d+)", theme_key)
    if not theme_id_match:
        return (
            "【本地專案知識庫核心指引】\n"
            "- 溝通方法論：非暴力溝通 (NVC) 三段式架構（同理情緒、說明事實、提出解方）。\n"
            "- 心理學原則：先同理家長焦慮（接住情緒），化解認知失調與防衛心理。\n"
            f"\n{lang_rules}"
        )
    
    theme_id = int(theme_id_match.group(1))
    if theme_id not in taxonomy_db:
        return f"【本地專案知識庫指引】\n請依據非暴力溝通 (NVC) 三段式架構回應。\n\n{lang_rules}"
        
    theme_info = taxonomy_db[theme_id]
    data = theme_info.get("data", {})
    
    context_lines = [
        f"【本專案本地知識庫參考內容 - 主題：{theme_info['name']}】",
        f"• 常見家長訴求：{data.get('常見家長訴求', '無')}",
        f"• 底層心理需求（薩提爾冰山與依附理論）：{data.get('底層心理需求', '無')}",
        f"• 相關法令依據（台灣教育法規）：{data.get('相關法令依據', '無')}",
        f"• 常見教師地雷句型（嚴禁使用）：{data.get('常見教師地雷', '無')}",
        f"• 建議溝通策略（NVC / GROW / SFBT）：{data.get('建議溝通策略', '無')}",
        "\n【生成指令】請務必將上述本地知識庫中的法令依據與心理需求同理融入您的分析與回覆中，切勿違反地雷句限制。",
        f"\n{lang_rules}"
    ]
    return "\n".join(context_lines)

def call_llm_api(
    provider: str,
    api_key: str,
    model_name: str,
    system_prompt: str,
    user_message: str,
    base_url: Optional[str] = None
) -> str:
    """
    統一呼叫 LLM API。
    """
    if provider.lower() == "openai":
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
        
    elif provider.lower() == "gemini":
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_prompt,
            generation_config={"temperature": 0.7}
        )
        response = model.generate_content(user_message)
        return response.text
        
    elif provider.lower() == "ollama":
        endpoint = clean_base_url(base_url) if base_url else "http://localhost:11434"
        client = openai.OpenAI(base_url=f"{endpoint}/v1", api_key=api_key)
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
        
    else:
        raise ValueError(f"不支援的 AI 供應商: {provider}")
