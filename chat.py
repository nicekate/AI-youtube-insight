from openai import OpenAI

def chat_with_subtitles(
    user_message,
    history,
    subtitles_text,
    deepseek_api_key,
    system_prompt
):
    """
    与字幕进行对话的核心函数
    """
    if history is None:
        history = []

    user_msg_dict = {"role": "user", "content": user_message}

    if not subtitles_text or not deepseek_api_key:
        assistant_msg = {
            "role": "assistant",
            "content": "请先在视频分析标签页分析视频以获取字幕内容"
        }
        return history + [user_msg_dict, assistant_msg]

    # 若对话提示词为空，就给个默认
    if not system_prompt:
        system_prompt = "你是一个专业的视频内容分析专家。你将基于视频字幕内容回答用户的问题。"

    client = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": f"视频字幕内容如下：\n{subtitles_text}"}
    ]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append(user_msg_dict)

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=False
        ).choices[0].message.content

        assistant_msg = {"role": "assistant", "content": response}
        return history + [user_msg_dict, assistant_msg]

    except Exception as e:
        assistant_msg = {
            "role": "assistant",
            "content": f"与DeepSeek API对话时出错: {str(e)}"
        }
        return history + [user_msg_dict, assistant_msg]

def user_input(
    user_message,
    history,
    subtitles_text,
    api_key,
    system_prompt
):
    """
    用于Chatbot前端事件触发
    """
    if not user_message:
        if history is None:
            return []
        return history
    
    updated_history = chat_with_subtitles(
        user_message, history, subtitles_text, api_key, system_prompt
    )
    return updated_history