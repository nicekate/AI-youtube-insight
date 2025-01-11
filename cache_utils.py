import re
from functools import lru_cache
from googleapiclient.discovery import build

@lru_cache(maxsize=10)
def cached_get_video_info(api_key, video_id):
    youtube = build("youtube", "v3", developerKey=api_key)
    request = youtube.videos().list(part="snippet,statistics", id=video_id)
    response = request.execute()
    return response

@lru_cache(maxsize=10)
def cached_get_comment_threads(api_key, video_id, max_results=100):
    youtube = build("youtube", "v3", developerKey=api_key)
    return youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=max_results,
        textFormat="plainText"
    ).execute()

def extract_video_id(url):
    """
    从 YouTube URL 中提取视频ID
    """
    video_id_match = re.search(r'(?:v=|/)([\w-]{11})(?:\?|&|/|$)', url)
    if video_id_match:
        return video_id_match.group(1)
    return None

def format_comments(comments):
    """
    格式化评论文本
    """
    if isinstance(comments, str):
        return comments
    formatted_text = ""
    for idx, comment in enumerate(comments, 1):
        formatted_text += (
            f"评论 {idx}:\n{comment['text']}\n"
            f"发布时间: {comment['publishedAt']}\n"
            f"点赞数: {comment['likes']}\n\n"
        )
    return formatted_text