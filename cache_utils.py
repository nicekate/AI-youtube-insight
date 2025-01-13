import re
from functools import lru_cache
from googleapiclient.discovery import build

@lru_cache(maxsize=10)
def cached_get_video_info(api_key, video_id):
    youtube = build("youtube", "v3", developerKey=api_key)
    request = youtube.videos().list(part="snippet,statistics", id=video_id)
    response = request.execute()
    return response

def _get_all_replies(api_key, parent_comment_id, max_results=None):
    """
    获取某个顶层评论的所有回复，通过 comments().list 进行分页
    """
    youtube = build("youtube", "v3", developerKey=api_key)
    replies = []
    next_page_token = None

    while True:
        try:
            request = youtube.comments().list(
                part="snippet",
                parentId=parent_comment_id,
                maxResults=100,
                pageToken=next_page_token,
                textFormat="plainText"
            )
            response = request.execute()

            for item in response.get("items", []):
                snippet = item["snippet"]
                replies.append({
                    "text": snippet["textDisplay"],
                    "publishedAt": snippet["publishedAt"],
                    "likes": snippet["likeCount"]
                })

                # 如果指定了最大获取数且已到达则停止
                if max_results and len(replies) >= max_results:
                    return replies

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
        except Exception as e:
            print(f"获取回复失败: {e}")
            break

    return replies

@lru_cache(maxsize=10)
def cached_get_comment_threads(api_key, video_id, max_results=None):
    """
    获取视频全部评论（包括顶层评论和所有回复）。
    如果 max_results=None，则获取所有评论。
    """
    youtube = build("youtube", "v3", developerKey=api_key)
    comments = []
    next_page_token = None

    while True:
        try:
            # 构建请求，获取顶层评论
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,  # 单次最多100条
                pageToken=next_page_token,
                textFormat="plainText",
                order="time"  # 需要时可改为"relevance"
            )
            response = request.execute()

            # 提取顶层评论
            for item in response.get("items", []):
                top_comment = item["snippet"]["topLevelComment"]
                top_comment_snippet = top_comment["snippet"]
                comments.append({
                    "text": top_comment_snippet["textDisplay"],
                    "publishedAt": top_comment_snippet["publishedAt"],
                    "likes": top_comment_snippet["likeCount"]
                })

                # 如果有回复，则调用单独函数进行多次分页获取
                total_replies = item["snippet"].get("totalReplyCount", 0)
                if total_replies > 0:
                    parent_id = top_comment["id"]
                    all_replies = _get_all_replies(api_key, parent_id, None)
                    comments.extend(all_replies)

                # 如果指定了最大获取数且超出，则截断返回
                if max_results and len(comments) >= max_results:
                    comments = comments[:max_results]
                    print(f"成功获取指定数量 {len(comments)} 条评论(含回复)")
                    return comments

            # 检查下一页
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        except Exception as e:
            print(f"获取评论页面失败: {e}")
            break

    print(f"成功获取 {len(comments)} 条评论(含回复)")
    return comments

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

    formatted_text = f"共获取到 {len(comments)} 条评论：\n\n"
    for idx, comment in enumerate(comments, 1):
        formatted_text += (
            f"评论 {idx}:\n{comment['text']}\n"
            f"发布时间: {comment['publishedAt']}\n"
            f"点赞数: {comment['likes']}\n\n"
        )
    return formatted_text