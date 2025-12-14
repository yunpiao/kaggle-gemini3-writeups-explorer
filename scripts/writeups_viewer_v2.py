import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import json
import random
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO

# 页面配置
st.set_page_config(
    page_title="Kaggle Writeups 浏览器",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Umami 统计
components.html("""
<script defer src="https://cloud.umami.is/script.js" data-website-id="64e07ed3-9f6b-4c35-9955-5e2734f07400"></script>
""", height=0)

# 卡片样式 CSS
st.markdown("""
<style>
.writeup-card {
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 15px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    min-height: 200px;
}
.writeup-card:hover {
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    transform: translateY(-2px);
    transition: all 0.3s ease;
}
.card-title {
    font-size: 1.1em;
    font-weight: bold;
    margin-bottom: 8px;
    line-height: 1.3;
}
.card-subtitle {
    font-size: 0.85em;
    opacity: 0.9;
    margin-bottom: 10px;
}
.card-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 15px;
    font-size: 0.75em;
    background: rgba(255,255,255,0.2);
    margin-right: 5px;
}
.card-meta {
    font-size: 0.8em;
    opacity: 0.8;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# 分类中英文映射
CATEGORY_CN = {
    "Education & Learning": "教育与学习",
    "Healthcare & Medical": "医疗健康",
    "Developer Tools & IDEs": "开发工具与IDE",
    "Content Creation & Media": "内容创作与媒体",
    "Accessibility & Assistive Technology": "无障碍与辅助技术",
    "Productivity & Task Management": "效率与任务管理",
    "Research & Scientific Tools": "科研工具",
    "Safety & Security": "安全防护",
    "Mental Health & Wellness": "心理健康",
    "Business Intelligence & Analytics": "商业智能与分析",
    "Career & Professional Development": "职业发展",
    "Finance & Investment": "金融投资",
    "Fitness & Nutrition": "健身与营养",
    "Design & Architecture": "设计与建筑",
    "Gaming & Entertainment": "游戏娱乐",
    "Legal & Compliance": "法律合规",
    "Environmental & Sustainability": "环保与可持续发展",
    "E-commerce & Retail": "电商零售",
    "Emergency & Crisis Management": "应急管理",
    "Food & Culinary": "美食烹饪",
    "Travel & Navigation": "旅行导航",
    "Language & Translation": "语言翻译",
    "Agriculture & Farming": "农业",
    "Document Processing & Management": "文档处理与管理",
    "Communication & Collaboration": "沟通协作",
    "Computer Vision & Image Processing": "计算机视觉与图像处理",
    "Infrastructure & Cloud Systems": "基础设施与云系统",
    "Transportation & Logistics": "交通物流",
    "Real Estate & Property": "房地产",
    "Smart Home & IoT": "智能家居与物联网",
}

def get_category_cn(category):
    """获取分类的中文名称"""
    return CATEGORY_CN.get(category, category)

# 加载数据
@st.cache_data
def load_data(csv_path):
    try:
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        st.error(f"加载数据出错: {e}")
        return pd.DataFrame()

def extract_youtube_id(url):
    """从 URL 中提取 YouTube 视频 ID"""
    if pd.isna(url) or not url:
        return None
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, str(url))
        if match:
            return match.group(1)
    return None

def render_card(item, idx):
    """渲染单个 Writeup 卡片"""
    title = item['title'][:60] + "..." if len(str(item['title'])) > 60 else item['title']
    subtitle = item['description'][:100] + "..." if len(str(item['description'])) > 100 else item['description']

    # 根据分类哈希值选择颜色
    colors = [
        "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
        "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
        "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
        "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)",
        "linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)",
        "linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)",
    ]
    color_idx = hash(str(item['category'])) % len(colors)
    bg = colors[color_idx]

    st.markdown(f"""
    <div class="writeup-card" style="background: {bg};">
        <div class="card-title">{title}</div>
        <div class="card-subtitle">{subtitle}</div>
        <div>
            <span class="card-badge">📂 {get_category_cn(item['category'])}</span>
            <span class="card-badge">✓ {item['confidence']}</span>
        </div>
        <div class="card-meta">👤 {item['authors']}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("查看详情", key=f"btn_{idx}_{item['writeup_id']}"):
        st.session_state.selected_id = item['writeup_id']
        st.session_state.view_mode = "detail"
        st.rerun()

def main():
    st.title("🔍 Kaggle Writeups 浏览器")

    csv_path = "kaggle_writeups_export/writeups_classified.csv"
    df = load_data(csv_path)

    if df.empty:
        st.warning("未找到数据。")
        return

    # 初始化会话状态
    if 'page' not in st.session_state:
        st.session_state.page = 0
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = "cards"
    if 'selected_id' not in st.session_state:
        st.session_state.selected_id = None

    # 侧边栏筛选器
    st.sidebar.header("🎛️ 筛选条件")

    # 分类筛选 - 使用中文显示
    all_categories = sorted(df['category'].dropna().unique().tolist())
    category_options = {get_category_cn(cat): cat for cat in all_categories}
    selected_categories_cn = st.sidebar.multiselect(
        "📂 分类",
        options=list(category_options.keys()),
        default=[]
    )
    selected_categories = [category_options[cn] for cn in selected_categories_cn]

    # 置信度筛选
    if 'confidence' in df.columns:
        confidence_levels = df['confidence'].unique().tolist()
        selected_confidence = st.sidebar.multiselect(
            "✓ 置信度",
            options=confidence_levels,
            default=[]
        )
    else:
        selected_confidence = []

    # 作者筛选
    all_authors = sorted(df['authors'].dropna().unique().tolist())
    selected_authors = st.sidebar.multiselect(
        "👤 作者",
        options=all_authors[:100],  # 限制数量以提高性能
        default=[]
    )

    # 搜索筛选
    search_query = st.sidebar.text_input("🔎 搜索", "")

    # 应用筛选条件
    filtered_df = df.copy()

    if selected_categories:
        filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]
    if selected_confidence:
        filtered_df = filtered_df[filtered_df['confidence'].isin(selected_confidence)]
    if selected_authors:
        filtered_df = filtered_df[filtered_df['authors'].isin(selected_authors)]
    if search_query:
        filtered_df = filtered_df[
            filtered_df['title'].str.contains(search_query, case=False, na=False) |
            filtered_df['description'].str.contains(search_query, case=False, na=False)
        ]

    # 侧边栏操作
    st.sidebar.markdown("---")
    st.sidebar.header("🎲 操作")

    # 随机按钮
    if st.sidebar.button("🎲 随机 Writeup", use_container_width=True):
        if not filtered_df.empty:
            random_id = filtered_df.sample(1)['writeup_id'].iloc[0]
            st.session_state.selected_id = random_id
            st.session_state.view_mode = "detail"
            st.rerun()

    # 导出按钮
    if st.sidebar.button("📥 导出筛选结果 CSV", use_container_width=True):
        csv_data = filtered_df.to_csv(index=False)
        st.sidebar.download_button(
            "下载 CSV",
            csv_data,
            file_name="filtered_writeups.csv",
            mime="text/csv"
        )

    # 统计指标行
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 总数", len(df))
    col2.metric("🔍 筛选后", len(filtered_df))
    col3.metric("📂 分类数", len(filtered_df['category'].unique()))
    col4.metric("👤 作者数", len(filtered_df['authors'].unique()))

    # 视图模式切换
    view_col1, view_col2, view_col3, view_col4 = st.columns([1, 1, 1, 3])
    with view_col1:
        if st.button("🃏 卡片", use_container_width=True):
            st.session_state.view_mode = "cards"
            st.session_state.selected_id = None
            st.rerun()
    with view_col2:
        if st.button("📋 表格", use_container_width=True):
            st.session_state.view_mode = "table"
            st.session_state.selected_id = None
            st.rerun()
    with view_col3:
        if st.button("📈 统计", use_container_width=True):
            st.session_state.view_mode = "stats"
            st.session_state.selected_id = None
            st.rerun()

    st.markdown("---")

    # 详情视图
    if st.session_state.view_mode == "detail" and st.session_state.selected_id:
        if st.button("← 返回列表"):
            st.session_state.view_mode = "cards"
            st.session_state.selected_id = None
            st.rerun()

        item = df[df['writeup_id'] == st.session_state.selected_id]
        if item.empty:
            st.warning("未找到该 Writeup")
            return
        item = item.iloc[0]

        # 标题
        st.markdown(f"## {item['title']}")
        st.caption(f"*{item['description']}*")

        badge_col1, badge_col2, badge_col3 = st.columns(3)
        badge_col1.info(f"📂 **{get_category_cn(item['category'])}**")
        badge_col2.success(f"✓ 置信度: **{item['confidence']}**")
        badge_col3.warning(f"👤 **{item['authors']}**")

        # 两列布局
        left_col, right_col = st.columns([2, 1])

        with left_col:
            # 完整内容
            md_path = item.get('markdown_path')
            if pd.notna(md_path):
                full_path = f"kaggle_writeups_export/{md_path}"
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    st.markdown("### 📄 完整描述")
                    with st.container(height=500):
                        st.markdown(content)
                except Exception as e:
                    st.warning(f"无法加载: {e}")

        with right_col:
            # YouTube 嵌入
            yt_url = item.get('youtube_links')
            yt_id = extract_youtube_id(yt_url)
            if yt_id:
                st.markdown("### 🎬 视频")
                st.markdown(f"""
                <iframe width="100%" height="200"
                    src="https://www.youtube.com/embed/{yt_id}"
                    frameborder="0" allowfullscreen>
                </iframe>
                """, unsafe_allow_html=True)

            # 链接
            st.markdown("### 🔗 链接")
            st.link_button("🌐 Kaggle Writeup", f"https://www.kaggle.com{item['url']}", use_container_width=True)

            app_links = item.get('application_links')
            if pd.notna(app_links) and app_links:
                for link in str(app_links).split(';')[:3]:
                    if link.strip():
                        st.link_button("🚀 应用链接", link.strip(), use_container_width=True)

            # 元数据
            st.markdown("### 📋 元数据")
            st.json({
                "ID": str(item['writeup_id']),
                "创建时间": str(item['create_time'])[:10],
                "更新时间": str(item['update_time'])[:10],
            })

    # 卡片视图
    elif st.session_state.view_mode == "cards":
        if filtered_df.empty:
            st.info("没有符合筛选条件的 Writeup。")
            return

        # 分页
        items_per_page = 24
        total_pages = (len(filtered_df) - 1) // items_per_page + 1

        page_col1, page_col2, page_col3 = st.columns([1, 2, 1])
        with page_col1:
            if st.button("← 上一页") and st.session_state.page > 0:
                st.session_state.page -= 1
                st.rerun()
        with page_col2:
            st.markdown(f"<center>第 {st.session_state.page + 1} 页 / 共 {total_pages} 页</center>", unsafe_allow_html=True)
        with page_col3:
            if st.button("下一页 →") and st.session_state.page < total_pages - 1:
                st.session_state.page += 1
                st.rerun()

        # 网格显示卡片
        start_idx = st.session_state.page * items_per_page
        end_idx = min(start_idx + items_per_page, len(filtered_df))
        page_df = filtered_df.iloc[start_idx:end_idx]

        cols = st.columns(3)
        for idx, (_, row) in enumerate(page_df.iterrows()):
            with cols[idx % 3]:
                render_card(row, start_idx + idx)

    # 表格视图
    elif st.session_state.view_mode == "table":
        # 创建副本并转换分类为中文
        table_cols = ['writeup_id', 'title', 'category', 'confidence', 'authors', 'description']
        # 如果有中文关键词列，也显示出来
        if 'keywords_cn' in filtered_df.columns:
            table_cols.append('keywords_cn')
        table_df = filtered_df[table_cols].copy()
        table_df['category'] = table_df['category'].apply(get_category_cn)

        rename_cols = {
            'writeup_id': 'ID',
            'title': '标题',
            'category': '分类',
            'confidence': '置信度',
            'authors': '作者',
            'description': '描述',
            'keywords_cn': '中文关键词'
        }
        st.dataframe(
            table_df.rename(columns=rename_cols),
            use_container_width=True,
            height=600
        )

    # 统计视图
    elif st.session_state.view_mode == "stats":
        # 检查是否有中文关键词列
        has_keywords_cn = 'keywords_cn' in filtered_df.columns

        # 中文停用词列表（过滤掉过于通用的词）
        STOPWORDS_CN = {
            # AI/技术通用词
            '人工智能', 'AI', 'AI助手', 'AI代理', 'AI导师', 'AI教育',
            '智能助手', '智能代理', '智能辅导', '智能诊断',
            # Gemini 相关
            'Gemini', 'Gemini模型', 'Gemini技术', 'Gemini AI', 'Gemini驱动',
            'Gemini 3 Pro', 'Gemini 3', 'Gemini Pro',
            # 多模态相关
            '多模态AI', '多模态', '多模态推理',
            # 其他通用词
            '数据分析', '效率提升', '移动应用', '开发工具',
            '决策支持', '知识管理', '创意工具',
        }

        # 词云生成辅助函数（支持中文）
        def generate_wordcloud(text, colormap='viridis', is_chinese=False):
            if not text.strip():
                return None
            # 中文词云需要指定字体
            font_path = None
            if is_chinese:
                # 尝试常见的中文字体路径
                chinese_fonts = [
                    '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
                    '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
                    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
                    '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',
                    '/System/Library/Fonts/PingFang.ttc',  # macOS
                    'C:/Windows/Fonts/msyh.ttc',  # Windows
                ]
                import os
                for fp in chinese_fonts:
                    if os.path.exists(fp):
                        font_path = fp
                        break

            return WordCloud(
                width=800,
                height=400,
                background_color='white',
                colormap=colormap,
                relative_scaling=0.5,
                min_font_size=8,
                max_words=80,
                prefer_horizontal=0.7,
                font_path=font_path
            ).generate(text)

        # 获取词云文本的辅助函数
        def get_wordcloud_text(df_subset):
            """优先使用中文关键词，否则使用标题"""
            if has_keywords_cn:
                keywords = df_subset['keywords_cn'].dropna().astype(str).tolist()
                # 关键词是逗号分隔的，过滤停用词后转换为空格分隔
                filtered_words = []
                for kw in keywords:
                    words = [w.strip() for w in kw.split(',') if w.strip()]
                    # 过滤停用词
                    words = [w for w in words if w not in STOPWORDS_CN]
                    filtered_words.extend(words)
                text = ' '.join(filtered_words)
                if text.strip():
                    return text, True  # 返回文本和是否为中文
            # 回退到英文标题
            return ' '.join(df_subset['title'].dropna().astype(str).tolist()), False

        # 总词云部分
        if has_keywords_cn:
            st.markdown("### ☁️ 总词云（中文关键词）")
        else:
            st.markdown("### ☁️ 总词云（英文标题）")

        all_text, is_chinese = get_wordcloud_text(filtered_df)

        if all_text.strip():
            total_wc = generate_wordcloud(all_text, 'viridis', is_chinese)
            if total_wc:
                # 重新生成大尺寸词云
                font_path = total_wc.font_path
                total_wc = WordCloud(
                    width=1600,
                    height=600,
                    background_color='white',
                    colormap='viridis',
                    relative_scaling=0.5,
                    min_font_size=10,
                    max_words=150,
                    prefer_horizontal=0.7,
                    font_path=font_path
                ).generate(all_text)

                fig, ax = plt.subplots(figsize=(16, 6))
                ax.imshow(total_wc, interpolation='bilinear')
                ax.axis('off')
                plt.tight_layout(pad=0)
                st.pyplot(fig)
                plt.close()
        else:
            st.info("没有可用于生成词云的数据")

        st.markdown("---")

        # 按分类的词云
        st.markdown("### ☁️ 分类词云")

        categories = filtered_df['category'].dropna().unique().tolist()
        colormaps = ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'cool', 'spring', 'summer', 'autumn', 'winter']

        # 两列网格显示
        cols = st.columns(2)
        for idx, category in enumerate(sorted(categories)):
            cat_df = filtered_df[filtered_df['category'] == category]
            cat_text, is_chinese = get_wordcloud_text(cat_df)

            if cat_text.strip():
                with cols[idx % 2]:
                    st.markdown(f"**{get_category_cn(category)}**（{len(cat_df)} 条）")
                    wc = generate_wordcloud(cat_text, colormaps[idx % len(colormaps)], is_chinese)
                    if wc:
                        fig, ax = plt.subplots(figsize=(8, 4))
                        ax.imshow(wc, interpolation='bilinear')
                        ax.axis('off')
                        plt.tight_layout(pad=0)
                        st.pyplot(fig)
                        plt.close()

        st.markdown("---")

        stat_col1, stat_col2 = st.columns(2)

        with stat_col1:
            st.markdown("### 📂 分类分布")
            counts = filtered_df['category'].value_counts().reset_index()
            counts.columns = ['category', '数量']
            counts['分类'] = counts['category'].apply(get_category_cn)
            fig1 = px.bar(counts, x='分类', y='数量', color='数量', height=500)
            fig1.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig1, use_container_width=True)

        with stat_col2:
            st.markdown("### ✓ 置信度分布")
            conf_counts = filtered_df['confidence'].value_counts().reset_index()
            conf_counts.columns = ['置信度', '数量']
            fig2 = px.pie(conf_counts, values='数量', names='置信度', height=400)
            st.plotly_chart(fig2, use_container_width=True)

            st.markdown("### 🏆 热门作者 Top 10")
            author_counts = filtered_df['authors'].value_counts().head(10).reset_index()
            author_counts.columns = ['作者', '数量']
            st.dataframe(author_counts, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
