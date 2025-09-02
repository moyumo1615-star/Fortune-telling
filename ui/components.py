"""
UI共通コンポーネント
ヘッダー、詳細パネルなどの共通UI要素を管理
"""
import streamlit as st
import re
from typing import Dict
import config


class UIManager:
    """UI表示を管理するクラス"""

    @staticmethod
    def setup_page_config():
        """ページ設定"""
        st.set_page_config(
            page_title=config.PAGE_TITLE,
            page_icon=config.PAGE_ICON,
            layout="wide",
            initial_sidebar_state="collapsed"
        )

        # カスタムCSS
        st.markdown(f"""
        <style>
        .main {{ padding: 0; }}
        .block-container {{
            padding: 1rem;
        }}
        h1 {{
            color: {config.PRIMARY_COLOR};
            font-size: 28px !important;
            margin-bottom: 10px !important;
        }}
        .stButton>button {{
            background-color: {config.PRIMARY_COLOR};
            color: white;
        }}
        .detail-panel {{
            background: linear-gradient(135deg, #f5ebff 0%, #ffffff 100%);
            padding: 20px;
            border-radius: 10px;
            border: 2px solid {config.PRIMARY_COLOR};
            margin-top: 10px;
        }}
        .clickable-link {{
            color: {config.PRIMARY_COLOR};
            text-decoration: none;
            font-weight: bold;
        }}
        .clickable-link:hover {{
            text-decoration: underline;
        }}
        /* ボタンのホバー効果を改善 */
        .stButton>button:hover {{
            background-color: #6a3d7a;
            border-color: #6a3d7a;
        }}
        </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def show_header():
        """ヘッダー表示（修正版）"""
        col1, col2, col3 = st.columns([2, 5, 3])

        with col1:
            st.markdown(f"# {config.PAGE_ICON} {config.PAGE_TITLE}")

        with col2:
            search_col1, search_col2 = st.columns([4, 1])
            with search_col1:
                search_text = st.text_input(
                    "",
                    placeholder="地域や占い師名で検索...",
                    label_visibility="collapsed",
                    key="header_search"
                )
            with search_col2:
                if st.button("🔍 検索", key="header_search_btn"):
                    st.info("検索機能は開発中です")

        with col3:
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("➕ 新規登録", type="primary", key="header_submit"):
                    # 他のフラグをクリア（重要！）
                    st.session_state.show_work_request = False
                    st.session_state.show_admin = False
                    st.session_state.selected_fortuneteller = None
                    st.session_state.highlight_id = None
                    # 新規投稿フラグを設定
                    st.session_state.show_submission_form = True
                    st.rerun()
            with col_b:
                if st.button("💼 お仕事依頼", key="header_work"):
                    # 他のフラグをクリア（重要！）
                    st.session_state.show_submission_form = False
                    st.session_state.show_admin = False
                    st.session_state.selected_fortuneteller = None
                    st.session_state.highlight_id = None
                    # お仕事依頼フラグを設定
                    st.session_state.show_work_request = True
                    st.rerun()

    @staticmethod
    def show_detail_panel(fortuneteller: Dict):
        """詳細パネル表示"""
        st.markdown("### 📋 占い師詳細情報")

        with st.container():
            st.markdown(f"""
            <div class="detail-panel">
                <h3 style="color: {config.PRIMARY_COLOR};">🔮 {fortuneteller['name']}</h3>
                <hr>
                <p><b>占術:</b> {fortuneteller.get('category', '未設定')}</p>
                <p><b>特徴:</b> {fortuneteller.get('description', '説明なし')}</p>
            </div>
            """, unsafe_allow_html=True)

            # 連絡先情報
            col1, col2 = st.columns(2)

            with col1:
                if fortuneteller.get('contact'):
                    phone = fortuneteller['contact']
                    phone_clean = re.sub(r'[^\d]', '', phone)
                    st.markdown(f"""
                    <p><b>📞 電話:</b> 
                    <a href="tel:{phone_clean}" class="clickable-link">{phone}</a>
                    </p>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("<p><b>📞 電話:</b> 未登録</p>",
                                unsafe_allow_html=True)

            with col2:
                if fortuneteller.get('website'):
                    st.markdown(f"""
                    <p><b>🌐 ウェブサイト:</b> 
                    <a href="{fortuneteller['website']}" target="_blank" class="clickable-link">
                    サイトを見る
                    </a>
                    </p>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("<p><b>🌐 ウェブサイト:</b> なし</p>",
                                unsafe_allow_html=True)

            # 地図で位置を表示
            if st.button("🗺️ 地図で位置を確認", key=f"detail_map_{fortuneteller['id']}"):
                st.session_state.highlight_id = fortuneteller['id']
                st.rerun()

            # 閉じるボタン
            if st.button("✖ 詳細パネルを閉じる", key=f"detail_close_{fortuneteller['id']}"):
                st.session_state.selected_fortuneteller = None
                st.rerun()
