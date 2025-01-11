# YouTube 内容分析器

本项目使用 Gradio 搭建了一个可视化 Web 界面，用于对 YouTube 视频进行以下分析：

1. 获取视频基本信息（标题、观看数、点赞数、评论数）
2. 获取并整合字幕，通过 DeepSeek API 对视频内容进行总结
3. 获取并整合评论，通过 DeepSeek API 对评论内容进行总结
4. 提供一个基于字幕内容的问答聊天功能

## 功能亮点

- **视频分析**：输入 YouTube 视频链接与 API Key，一键获取视频信息、字幕、评论并自动生成总结
- **字幕对话**：可以基于获取到的字幕内容进行问答，快速了解视频核心内容
- **缓存机制**：通过 `@lru_cache` 减少对同一视频信息和评论的重复请求，提升性能
- **多界面布局**：采用 Gradio 的 Tabs、Accordion 等组件，界面简洁、功能分区明确

## 部署与使用

### 1. 环境准备

- Python 版本：建议 >= 3.10
- 克隆或下载本项目到本地：
  ```bash
  git clone https://github.com/nicekate/AI-youtube-insight.git
  cd AI-youtube-insight
  ```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 准备 API Keys

- 访问 Google Cloud Console 获取 YouTube Data API 的密钥，启用相应 API
- DeepSeek 账号及对应的 API Key

### 4. 运行应用

```bash
python app.py
```

执行后，控制台会输出一个本地访问链接（例如 http://127.0.0.1:7860），在浏览器打开该链接即可使用。

### 5. 使用方法

#### 视频分析标签页：
1. 填入 YouTube 视频 URL
2. 填入 YouTube API Key 和 DeepSeek API Key
3. 点击「分析视频」按钮，等待分析结果输出
4. 查看「视频信息」板块了解视频标题、观看数、点赞数和评论数
5. 查看「字幕总结」「评论总结」板块，了解自动生成的摘要
6. 可展开「字幕内容」「评论内容」来查看原始文本

#### 字幕对话标签页：
- 在输入框中提问（基于获取到的字幕）
- 点击「发送」后获得回答

## 许可证

MIT License
