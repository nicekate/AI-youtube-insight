from store import load_prompts

# 程序内置的默认提示词
DEFAULT_SUBTITLE_PROMPT_BUILTIN = """你是一个专业的视频内容分析专家。请对视频内容进行全面总结：

1. 视频主题：视频的核心主题和目的是什么？
2. 主要内容：视频讲述了哪些具体内容？
3. 重点信息：有哪些关键的数据、事实或观点？
4. 内容亮点：视频中最有价值或最有趣的部分是什么？
5. 核心结论：视频传达的主要观点或结论是什么？
6. 特别之处：有什么特别的见解或独特的表达方式？

请用清晰的语言进行总结，突出重点内容，确保内容丰富且易于理解。"""

DEFAULT_COMMENTS_PROMPT_BUILTIN = """你是一个专业的评论分析专家。请对评论进行全面总结：

1. 评论概况：评论的整体情况如何？数量、质量、参与度如何？
2. 主要观点：评论中表达了哪些主要观点和看法？
3. 热点话题：哪些话题或内容点最受关注和讨论？
4. 情感倾向：评论的情感态度如何？正面、负面、中性的比例？
5. 有价值观点：哪些评论提供了独特的见解或有价值的反馈？
6. 问题建议：评论中提出了哪些问题或建议？

请具体列举评论中的代表性观点，用数据支持你的分析，确保总结全面且有深度。"""

# 从本地JSON加载上次保存的提示词
loaded_subtitle, loaded_comments, loaded_system = load_prompts()

# 判空，防止NoneType错误
if loaded_subtitle is None:
    loaded_subtitle = ""
if loaded_comments is None:
    loaded_comments = ""
if loaded_system is None:
    loaded_system = ""

# 若加载成功并非空，则覆盖默认
DEFAULT_SUBTITLE_PROMPT = loaded_subtitle.strip() if loaded_subtitle.strip() else DEFAULT_SUBTITLE_PROMPT_BUILTIN
DEFAULT_COMMENTS_PROMPT = loaded_comments.strip() if loaded_comments.strip() else DEFAULT_COMMENTS_PROMPT_BUILTIN

# system_prompt 没有固定的内置默认值，通常在app.py中使用
DEFAULT_SYSTEM_PROMPT = loaded_system.strip()  # 可能为空