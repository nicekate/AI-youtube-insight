import re
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from openai import OpenAI

from prompts import DEFAULT_SUBTITLE_PROMPT, DEFAULT_COMMENTS_PROMPT
from cache_utils import (
    cached_get_video_info,
    cached_get_comment_threads,
    extract_video_id,
    format_comments
)

def analyze_single_video_with_progress(
    youtube_api_key,
    video_id,
    deepseek_api_key,
    subtitle_prompt,
    comments_prompt
):
    """
    以生成器方式返回多次输出(6个)。
    每次 yield 都返回 (progress, video_info_md, subtitle_summary_md, comments_summary_md, transcript_text, comments_text)
    """
    # 若用户未填自定义字幕总结提示词，就用内置默认值
    if not subtitle_prompt:
        subtitle_prompt = DEFAULT_SUBTITLE_PROMPT

    # 若用户未填自定义评论总结提示词，就用内置默认值
    if not comments_prompt:
        comments_prompt = DEFAULT_COMMENTS_PROMPT

    # 1) 正在获取视频信息
    yield ("正在获取视频信息...", "", "", "", "", "")
    video_response = cached_get_video_info(youtube_api_key, video_id)
    if not video_response.get("items"):
        yield ("未找到视频信息", "", "", "", "", "")
        return

    video_info = video_response["items"][0]
    video_title = video_info["snippet"]["title"]
    view_count = video_info["statistics"].get("viewCount", "0")
    like_count = video_info["statistics"].get("likeCount", "0")
    comment_count = video_info["statistics"].get("commentCount", "0")

    # 2) 正在获取字幕
    yield ("正在获取字幕...", "", "", "", "", "")
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = None
        try:
            transcript = transcript_list.find_generated_transcript(["zh-Hans", "zh-CN", "en"])
        except:
            try:
                transcript = transcript_list.find_manually_created_transcript(["zh-Hans", "zh-CN", "en"])
            except:
                yield (f"未找到字幕（ID={video_id}）", "", "", "", "", "")
                return
        transcript_text = " ".join([item["text"] for item in transcript.fetch()])
    except Exception as e:
        yield (f"获取字幕出错: {str(e)} (ID={video_id})", "", "", "", "", "")
        return

    # 3) 正在获取评论
    yield ("正在获取评论...", "", "", "", "", "")
    try:
        comments = cached_get_comment_threads(youtube_api_key, video_id)
        if not comments:
            comments = ["无法获取评论"]
        yield (f"已获取 {len(comments)} 条评论...", "", "", "", "", "")
    except Exception as e:
        print(f"获取评论失败: {e}")
        comments = ["无法获取评论"]
    comments_text = format_comments(comments)

    # 4) 正在调用 DeepSeek...
    yield ("正在调用DeepSeek生成摘要...", "", "", "", "", "")
    client = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com")

    # ---- 字幕总结 ----
    subtitle_summary_response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": subtitle_prompt
            },
            {
                "role": "user",
                "content": f"请总结以下视频内容：\n\n{transcript_text}"
            }
        ]
    )
    subtitle_summary = subtitle_summary_response.choices[0].message.content

    # ---- 评论总结 ----
    comments_summary_response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": comments_prompt
            },
            {
                "role": "user",
                "content": f"请总结以下全部 {len(comments)} 条评论内容：\n\n{comments_text}"
            }
        ]
    )
    comments_summary = comments_summary_response.choices[0].message.content

    # 5) 组装 MD 并写文件
    video_info_md = f"""## 视频信息

- 标题：{video_title}
- 观看次数：{view_count}
- 点赞数：{like_count}
- 评论数：{comment_count}
"""

    subtitle_summary_md = f"""## 字幕总结

{subtitle_summary}
"""

    comments_summary_md = f"""## 评论总结

{comments_summary}
"""

    md_content = (
        f"# {video_title}\n\n"
        f"{video_info_md}\n"
        f"{subtitle_summary_md}\n"
        f"{comments_summary_md}\n"
        f"## 字幕内容\n\n{transcript_text}\n\n"
        f"## 评论内容\n\n{comments_text}\n"
    )

    safe_title = re.sub(r'[\\/*?:"<>|]', '_', video_title)
    md_filename = f"{safe_title}.md"
    try:
        with open(md_filename, "w", encoding="utf-8") as f:
            f.write(md_content)
    except Exception as err:
        yield (f"写入 {md_filename} 文件时出错: {err}", "", "", "", "", "")
        return

    # 6) 最终输出
    yield (
        "",
        video_info_md,
        subtitle_summary_md,
        comments_summary_md,
        transcript_text,
        comments_text
    )

def process_youtube_content(
    youtube_api_key,
    video_url,
    deepseek_api_key,
    subtitle_prompt,
    comments_prompt
):
    """
    生成器函数，多次yield以实时显示进度
    前端需要 6 个输出，因此每次都返回 6 元组：
    (progress, video_info_md, subtitle_summary_md, comments_summary_md, transcript_text, comments_text)
    """
    video_id = extract_video_id(video_url)
    if not video_id:
        yield ("无效的YouTube视频URL", "", "", "", "", "")
        return

    yield from analyze_single_video_with_progress(
        youtube_api_key,
        video_id,
        deepseek_api_key,
        subtitle_prompt,
        comments_prompt
    )

def batch_process_callback(
    youtube_api,
    channel_id,
    max_videos,
    ds_api,
    subtitle_prompt,
    comments_prompt
):
    """
    生成器函数：
      1) 搜索频道最新视频
      2) 逐个调用 analyze_single_video_with_progress
      3) 实时输出进度
    前端需要 3 个输出 => 每次yield都返回 (progress_str, batch_md, batch_result)
    """
    try:
        yield ("正在搜索频道最新视频...", "", "")
        youtube = build("youtube", "v3", developerKey=youtube_api)
        search_response = youtube.search().list(
            part="id",
            channelId=channel_id,
            maxResults=int(max_videos),
            order="date",
            type="video"
        ).execute()
        items = search_response.get("items", [])
        if not items:
            yield (f"未在频道 {channel_id} 中找到视频", "", "")
            return

        summary_lines = []
        for i, item in enumerate(items, 1):
            vid_id = item["id"]["videoId"]
            yield (f"正在分析第 {i} 个视频 (ID={vid_id})...", "", "")
            # 调用 analyze_single_video_with_progress
            for partial in analyze_single_video_with_progress(
                youtube_api,
                vid_id,
                ds_api,
                subtitle_prompt,
                comments_prompt
            ):
                progress_msg = partial[0]
                yield (f"[第 {i} 个视频] {progress_msg}", "", "")
                if progress_msg == "":
                    info_str = f"第 {i} 个视频(ID={vid_id}) 已生成MD。"
                    summary_lines.append(info_str)
                    break

        final_info = "批量生成完成："
        final_result = "\n".join(summary_lines)
        yield ("", final_info, final_result)

    except Exception as e:
        error_message = f"处理频道视频时出错: {str(e)}"
        yield (error_message, "", "")