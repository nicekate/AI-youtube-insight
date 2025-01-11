import json
import os

# 取得当前脚本所在文件夹的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_FILE = os.path.join(BASE_DIR, "prompts_storage.json")

def load_prompts():
    """
    从本地 JSON 文件中加载提示词
    返回 (subtitle_prompt, comments_prompt, system_prompt)
    如果文件不存在或读取失败，则返回空字符串
    """
    if os.path.exists(PROMPT_FILE):
        try:
            with open(PROMPT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return (
                data.get("subtitle_prompt", ""),
                data.get("comments_prompt", ""),
                data.get("system_prompt", "")
            )
        except Exception:
            pass
    return "", "", ""

def save_prompts(subtitle_prompt, comments_prompt, system_prompt):
    """
    将提示词写入本地 JSON 文件
    """
    data = {
        "subtitle_prompt": subtitle_prompt,
        "comments_prompt": comments_prompt,
        "system_prompt": system_prompt
    }
    try:
        with open(PROMPT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"写入 {PROMPT_FILE} 出错: {str(e)}")