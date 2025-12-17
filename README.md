# Kaggle Gemini 3 Writeups Explorer

浏览 Kaggle Gemini 3 竞赛的 4100+ 条 writeups。

**在线体验**：https://kaggle-gemini3-writeups-explorer.streamlit.app/

## 功能

- 按分类/作者/关键词筛选
- 卡片视图 + 表格视图
- 详情页带 YouTube demo 嵌入
- 随机抽取
- 统计图表 + 词云

## 数据

- 4100+ 条 writeups
- 30 个分类（教育、医疗、开发工具、内容创作等）
- 中文关键词

## 本地运行

```bash
pip install -r requirements.txt
streamlit run scripts/writeups_viewer_v2.py
```

## 分类列表

| English | 中文 |
|---------|------|
| Education & Learning | 教育与学习 |
| Healthcare & Medical | 医疗健康 |
| Developer Tools & IDEs | 开发工具与IDE |
| Content Creation & Media | 内容创作与媒体 |
| Productivity & Task Management | 效率与任务管理 |
| Finance & Investment | 金融投资 |
| Gaming & Entertainment | 游戏娱乐 |
| ... | ... |

完整分类见 [writeups_viewer_v2.py](scripts/writeups_viewer_v2.py)

## 数据来源

数据整理自 Kaggle Gemini 3 竞赛的公开 writeups，所有内容版权归原作者所有。

## License

MIT
