import gradio as gr

# 导入拆分出去的模块
from prompts import (
    DEFAULT_SUBTITLE_PROMPT,
    DEFAULT_COMMENTS_PROMPT,
    DEFAULT_SYSTEM_PROMPT
)
from analysis import process_youtube_content, batch_process_callback
from chat import user_input
from store import save_prompts, load_prompts

def store_apis_from_single(y_api, ds_api):
    return (
        y_api,
        ds_api,
        gr.update(value=y_api),
        gr.update(value=ds_api)
    )

def store_apis_from_batch(y_api_batch, ds_api_batch):
    return (
        y_api_batch,
        ds_api_batch,
        gr.update(value=y_api_batch),
        gr.update(value=ds_api_batch)
    )

with gr.Blocks(theme=gr.themes.Soft()) as iface:
    gr.Markdown("## YouTube 内容分析器（含进度提醒 + 自定义字幕/评论总结提示词 + 批量生成）")

    stored_subtitles = gr.State()
    stored_api_key = gr.State()
    stored_youtube_api_key = gr.State("")
    stored_deepseek_api_key = gr.State("")

    stored_subtitle_prompt = gr.State()
    stored_comments_prompt = gr.State()
    stored_system_prompt = gr.State()

    with gr.Tabs():
        with gr.TabItem("视频分析"):
            with gr.Row():
                video_url = gr.Textbox(
                    label="YouTube 视频 URL", 
                    placeholder="输入要分析的 YouTube 视频链接",
                    scale=2
                )
            with gr.Row():
                with gr.Column(scale=1):
                    youtube_api = gr.Textbox(
                        label="YouTube API Key",
                        placeholder="请输入 YouTube API Key",
                        type="password",
                        scale=1
                    )
                with gr.Column(scale=1):
                    deepseek_api = gr.Textbox(
                        label="DeepSeek API Key",
                        placeholder="用于调用DeepSeek生成摘要",
                        type="password",
                        scale=1
                    )

            single_progress = gr.Markdown(label="进度提醒")
            single_video_info = gr.Markdown(label="视频信息")
            
            with gr.Accordion("字幕总结", open=True):
                subtitles_summary_box = gr.Markdown(label="字幕总结", show_copy_button=True)
            with gr.Accordion("评论总结", open=True):
                comments_summary_box = gr.Markdown(label="评论总结", show_copy_button=True)
            with gr.Accordion("字幕内容", open=False):
                subtitles = gr.Textbox(label="字幕", lines=10, show_copy_button=True)
            with gr.Accordion("评论内容", open=False):
                comments = gr.Textbox(label="评论", lines=10, show_copy_button=True)

            submit_btn = gr.Button("分析视频", variant="primary")

            def store_data(info, summary1, summary2, subtitles_text, comments_text, api_key):
                return subtitles_text, api_key

            submit_btn.click(
                fn=process_youtube_content,
                inputs=[
                    youtube_api, 
                    video_url, 
                    deepseek_api,
                    stored_subtitle_prompt,
                    stored_comments_prompt
                ],
                outputs=[
                    single_progress,
                    single_video_info,
                    subtitles_summary_box,
                    comments_summary_box,
                    subtitles,
                    comments
                ]
            ).then(
                fn=store_data,
                inputs=[
                    single_video_info,
                    subtitles_summary_box,
                    comments_summary_box,
                    subtitles,
                    comments,
                    deepseek_api
                ],
                outputs=[stored_subtitles, stored_api_key]
            ).then(
                fn=store_apis_from_single,
                inputs=[youtube_api, deepseek_api],
                outputs=[
                    stored_youtube_api_key,
                    stored_deepseek_api_key
                ]
            )

        with gr.TabItem("字幕对话"):
            chatbot = gr.Chatbot(
                value=[], 
                elem_id="chatbot",
                type="messages",
                bubble_full_width=False,
                height=500,
                show_copy_button=True
            )
            with gr.Row():
                msg = gr.Textbox(
                    label="输入您的问题",
                    placeholder="基于字幕内容提问...",
                    lines=1,
                    scale=4
                )
                submit_chat = gr.Button("发送", scale=1)

            msg.submit(
                user_input, 
                [msg, chatbot, stored_subtitles, stored_api_key, stored_system_prompt], 
                chatbot
            )
            submit_chat.click(
                user_input, 
                [msg, chatbot, stored_subtitles, stored_api_key, stored_system_prompt], 
                chatbot
            )
            msg.submit(lambda: "", None, [msg])
            submit_chat.click(lambda: "", None, [msg])

        with gr.TabItem("批量生成"):
            gr.Markdown("### 根据频道ID批量获取最近视频并分析（含进度提醒）")
            with gr.Row():
                channel_id = gr.Textbox(
                    label="频道ID",
                    placeholder="输入频道ID，如 UCxxxxxxx",
                    lines=1,
                    scale=2
                )
            with gr.Row():
                max_videos = gr.Number(
                    label="获取最近视频数量",
                    value=5,
                    precision=0,
                    interactive=True
                )
            with gr.Row():
                with gr.Column(scale=1):
                    youtube_api_batch = gr.Textbox(
                        label="YouTube API Key（批量）",
                        placeholder="请输入 YouTube API Key 用于批量生成",
                        type="password"
                    )
                with gr.Column(scale=1):
                    deepseek_api_batch = gr.Textbox(
                        label="DeepSeek API Key（批量）",
                        placeholder="用于调用DeepSeek批量生成摘要",
                        type="password"
                    )

            batch_progress = gr.Markdown(label="批量进度提醒")
            batch_md = gr.Markdown()
            batch_result = gr.Markdown()

            batch_btn = gr.Button("批量获取并分析", variant="primary")

            batch_btn.click(
                fn=batch_process_callback,
                inputs=[
                    youtube_api_batch, 
                    channel_id, 
                    max_videos, 
                    deepseek_api_batch,
                    stored_subtitle_prompt,
                    stored_comments_prompt
                ],
                outputs=[batch_progress, batch_md, batch_result]
            ).then(
                fn=store_apis_from_batch,
                inputs=[youtube_api_batch, deepseek_api_batch],
                outputs=[
                    stored_youtube_api_key,
                    stored_deepseek_api_key
                ]
            )

        with gr.TabItem("提示词管理"):
            gr.Markdown("#### 在这里可自定义【字幕总结】、【评论总结】、以及【字幕对话】的提示词。")

            with gr.Row():
                with gr.Column():
                    subtitle_prompt_box = gr.Textbox(
                        label="自定义【字幕总结】提示词",
                        placeholder="请输入字幕总结提示词...",
                        lines=8,
                        value=DEFAULT_SUBTITLE_PROMPT
                    )
                    subtitle_prompt_save_btn = gr.Button("更新字幕总结提示词")

                with gr.Column():
                    comments_prompt_box = gr.Textbox(
                        label="自定义【评论总结】提示词",
                        placeholder="请输入评论总结提示词...",
                        lines=8,
                        value=DEFAULT_COMMENTS_PROMPT
                    )
                    comments_prompt_save_btn = gr.Button("更新评论总结提示词")

            system_prompt_box = gr.Textbox(
                label="自定义【字幕对话】提示词",
                placeholder="在字幕对话中替换原有默认 Prompt...",
                lines=3,
                value=DEFAULT_SYSTEM_PROMPT
            )
            system_prompt_save_btn = gr.Button("更新对话提示词")

            status_subtitle = gr.Markdown("当前字幕总结提示词：<空>")
            status_comments = gr.Markdown("当前评论总结提示词：<空>")
            status_system = gr.Markdown("当前对话提示词：<空>")

            def update_subtitle_prompt(new_prompt):
                new_prompt_str = new_prompt.strip()
                if not new_prompt_str:
                    return gr.update(value="当前字幕总结提示词：<空>"), ""
                else:
                    return gr.update(value=f"当前字幕总结提示词：\n\n{new_prompt_str}"), new_prompt_str

            def update_comments_prompt(new_prompt):
                new_prompt_str = new_prompt.strip()
                if not new_prompt_str:
                    return gr.update(value="当前评论总结提示词：<空>"), ""
                else:
                    return gr.update(value=f"当前评论总结提示词：\n\n{new_prompt_str}"), new_prompt_str

            def update_system_prompt(new_prompt):
                new_prompt_str = new_prompt.strip()
                if not new_prompt_str:
                    return gr.update(value="当前对话提示词：<空>"), ""
                else:
                    return gr.update(value=f"当前对话提示词：\n\n{new_prompt_str}"), new_prompt_str

            # 修正点：在使用strip()前先判断None，或将其转换为""。
            def handle_save_prompts(subtitle_p, comments_p, system_p):
                # 将 None 转成空字符串
                subtitle_p = subtitle_p or ""
                comments_p = comments_p or ""
                system_p = system_p or ""

                # 保存提示词到本地
                save_prompts(subtitle_p, comments_p, system_p)

                # 再次读取
                new_subtitle, new_comments, new_system = load_prompts()
                # 同样先避免 None
                new_subtitle = new_subtitle or ""
                new_comments = new_comments or ""
                new_system = new_system or ""

                updates = []
                if not new_subtitle.strip():
                    updates.append(gr.update(value=""))
                else:
                    updates.append(gr.update(value=new_subtitle))

                if not new_comments.strip():
                    updates.append(gr.update(value=""))
                else:
                    updates.append(gr.update(value=new_comments))

                if not new_system.strip():
                    updates.append(gr.update(value=""))
                else:
                    updates.append(gr.update(value=new_system))

                return tuple(updates)

            subtitle_prompt_save_btn.click(
                fn=update_subtitle_prompt,
                inputs=[subtitle_prompt_box],
                outputs=[status_subtitle, stored_subtitle_prompt]
            ).then(
                fn=handle_save_prompts,
                inputs=[
                    stored_subtitle_prompt,
                    stored_comments_prompt,
                    stored_system_prompt
                ],
                outputs=[
                    subtitle_prompt_box,
                    comments_prompt_box,
                    system_prompt_box
                ]
            )

            comments_prompt_save_btn.click(
                fn=update_comments_prompt,
                inputs=[comments_prompt_box],
                outputs=[status_comments, stored_comments_prompt]
            ).then(
                fn=handle_save_prompts,
                inputs=[
                    stored_subtitle_prompt,
                    stored_comments_prompt,
                    stored_system_prompt
                ],
                outputs=[
                    subtitle_prompt_box,
                    comments_prompt_box,
                    system_prompt_box
                ]
            )

            system_prompt_save_btn.click(
                fn=update_system_prompt,
                inputs=[system_prompt_box],
                outputs=[status_system, stored_system_prompt]
            ).then(
                fn=handle_save_prompts,
                inputs=[
                    stored_subtitle_prompt,
                    stored_comments_prompt,
                    stored_system_prompt
                ],
                outputs=[
                    subtitle_prompt_box,
                    comments_prompt_box,
                    system_prompt_box
                ]
            )

if __name__ == "__main__":
    iface.launch()