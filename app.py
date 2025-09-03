"""
占い師マップ - メインアプリケーション
シンプル解決版：座標ベースでの確実な検出
スマホ・タブレット対応版
"""
import config
from pages.work_request import WorkRequestForm
from pages.submission import SubmissionForm
from pages.admin import AdminPage
from ui.map_manager import MapManager
from ui.components import UIManager
from database import DatabaseManager
import streamlit as st
from streamlit_folium import st_folium
import json
import re
import time
import sys
import os
import math

# パッケージパスの設定
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 起動時にキャッシュをクリア
st.cache_data.clear()


def hide_streamlit_style():
    """Streamlitの標準ヘッダーを非表示"""
    hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {visibility: hidden;}
    .stDeployButton {display: none;}
    .stToolbar {display: none;}
    .stDecoration {display: none;}
    </style>
    """
    st.markdown(hide_st_style, unsafe_allow_html=True)


class FortunetellerMapApp:
    """メインアプリケーションクラス - レスポンシブ対応版"""

    def __init__(self):
        """初期化"""
        try:
            self.db = DatabaseManager()
            self.admin_page = AdminPage(self.db)
            self.submission_form = SubmissionForm(self.db)
            self.work_request_form = WorkRequestForm(self.db)
            self._init_session_state()
            self._init_settings()
        except Exception as e:
            st.error(f"初期化エラー: {str(e)}")
            st.stop()

    def _init_session_state(self):
        """セッション状態の初期化（エラー耐性強化版）"""
        defaults = {
            'show_submission_form': False,
            'show_admin': False,
            'show_work_request': False,
            'highlight_id': None,
            'selected_fortuneteller': None,
            'admin_authenticated': False,
            'password_changed_success': False,
            'detail_refresh_flag': False,
            'last_render_time': 0,
            'delete_confirm_pending': None,
            'delete_confirm_approved': None,
            'delete_confirm_work_request': None,
            'permanent_delete_confirm': None,
            'selected_for_permanent_delete': set(),
            'checkbox_changes': {},
            # レスポンシブ対応用の状態
            'device_type': 'desktop',  # desktop, tablet, mobile
            'is_mobile_view': False
        }

        for key, default_value in defaults.items():
            if key not in st.session_state:
                try:
                    st.session_state[key] = default_value
                except Exception as e:
                    print(f"セッション状態初期化エラー ({key}): {e}")
                    pass

        # セッション状態の整合性チェック（エラー発生時の復旧処理）
        try:
            if not isinstance(st.session_state.get('selected_for_permanent_delete'), set):
                st.session_state.selected_for_permanent_delete = set()

            if not isinstance(st.session_state.get('checkbox_changes'), dict):
                st.session_state.checkbox_changes = {}

        except Exception as e:
            print(f"セッション状態整合性チェックエラー: {e}")
            st.session_state.selected_for_permanent_delete = set()
            st.session_state.checkbox_changes = {}

    def _init_settings(self):
        """初期設定"""
        try:
            if not self.db.get_setting('announcements'):
                self.db.update_setting(
                    'announcements',
                    json.dumps(config.DEFAULT_ANNOUNCEMENTS,
                               ensure_ascii=False)
                )

            if not self.db.get_setting('contact_email'):
                self.db.update_setting(
                    'contact_email', config.DEFAULT_CONTACT_EMAIL)
        except Exception as e:
            st.error(f"設定初期化エラー: {str(e)}")

    def _detect_device_type(self):
        """デバイスタイプの検出（JavaScript連携）"""
        # JavaScriptでデバイス判定を行い、結果をセッション状態に保存
        device_detection_script = """
        <script>
        function updateDeviceType() {
            const width = window.innerWidth;
            let deviceType = 'desktop';
            
            if (width <= 767) {
                deviceType = 'mobile';
            } else if (width <= 1024) {
                deviceType = 'tablet';
            }
            
            // Streamlitのセッション状態を更新
            window.parent.postMessage({
                type: 'device_info', 
                deviceType: deviceType,
                width: width,
                isMobile: width <= 767
            }, '*');
        }
        
        updateDeviceType();
        window.addEventListener('resize', updateDeviceType);
        </script>
        """

        st.markdown(device_detection_script, unsafe_allow_html=True)

    def _get_responsive_map_height(self) -> int:
        """デバイスタイプに応じた地図の高さを取得"""
        device_type = st.session_state.get('device_type', 'desktop')

        if device_type == 'mobile':
            return 300
        elif device_type == 'tablet':
            return 400
        else:
            return 500

    def _get_responsive_column_ratio(self) -> list:
        """デバイスタイプに応じた列の比率を取得"""
        device_type = st.session_state.get('device_type', 'desktop')

        if device_type == 'mobile':
            # モバイルでは縦並びレイアウトに近い比率
            return [1]  # 単一列
        elif device_type == 'tablet':
            return [2, 1]  # タブレット用
        else:
            return [7, 3]  # デスクトップ用

    def find_closest_fortuneteller(self, clicked_lat: float, clicked_lng: float, fortunetellers_df) -> int:
        """クリック座標に最も近い占い師を特定 - 改良版"""
        if fortunetellers_df.empty:
            return None

        min_distance = float('inf')
        closest_id = None

        for idx, row in fortunetellers_df.iterrows():
            # 距離計算
            lat_diff = clicked_lat - row['latitude']
            lng_diff = clicked_lng - row['longitude']
            distance = math.sqrt(lat_diff**2 + lng_diff**2)

            if distance < min_distance:
                min_distance = distance
                closest_id = row['id']

        # 距離の閾値を緩める（0.1度 = 約10km以内）
        if min_distance < 0.1:
            return closest_id
        else:
            return None

    def force_update_detail_panel(self, selected_id: int):
        """詳細パネルの強制更新"""
        # すべての関連状態をクリア
        keys_to_clear = [
            'detail_container',
            'detail_placeholder',
            'last_detail_data',
            'cached_detail_id'
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]

        # キャッシュクリア
        st.cache_data.clear()

        # 状態を確実に更新
        st.session_state.selected_fortuneteller = selected_id
        st.session_state.highlight_id = selected_id
        st.session_state.detail_refresh_flag = True
        st.session_state.last_render_time = time.time()

        # 確実にリラン
        st.rerun()

    def show_responsive_info_panel(self):
        """レスポンシブ対応の情報パネル（修正版 - 不明表示削除）"""
        device_type = st.session_state.get('device_type', 'desktop')

        try:
            stats = self.db.get_statistics()

            st.markdown("### 📊 サイト情報")

            # **修正: 不明なメトリクス表示を削除**
            # 「3個」「勝負5件」などの不明な表示を完全削除
            # シンプルに登録数のみ表示
            st.write(f"**登録占い師数**: {stats['approved']}件")

            # 新着情報
            st.markdown("### 🆕 新着情報")
            st.caption("クリックで詳細パネル表示")

            recent_df = self.db.get_fortunetellers("approved")
            if not recent_df.empty:
                # モバイルでは表示件数を制限
                display_count = 3 if device_type == 'mobile' else 5
                recent_df = recent_df.head(display_count)

                for idx, row in recent_df.iterrows():
                    current_selected = st.session_state.get(
                        'selected_fortuneteller')
                    is_selected = (current_selected == row['id'])

                    button_key = f"info_{row['id']}_{idx}_responsive"

                    # モバイルでは短縮表示
                    if device_type == 'mobile':
                        name_display = row['name'][:8] + \
                            "..." if len(row['name']) > 8 else row['name']
                        category_display = row.get('category', '未設定')[
                            :3] + "..." if len(row.get('category', '未設定')) > 3 else row.get('category', '未設定')
                        button_text = f"{'✅' if is_selected else '🔮'} {name_display} - {category_display}"
                    else:
                        button_text = f"{'✅' if is_selected else '🔮'} {row['name']} - {row.get('category', '未設定')}"

                    if st.button(
                        button_text,
                        key=button_key,
                        use_container_width=True,
                        type="primary" if is_selected else "secondary"
                    ):
                        self.force_update_detail_panel(row['id'])

            # お知らせ
            st.markdown("### 📰 お知らせ")
            announcements_json = self.db.get_setting('announcements')
            if announcements_json:
                try:
                    announcements = json.loads(announcements_json)

                    if device_type == 'mobile':
                        # モバイルでは最初の2件のみ表示
                        for announcement in announcements[:2]:
                            st.markdown(f"• {announcement}")
                        if len(announcements) > 2:
                            with st.expander("さらに表示..."):
                                for announcement in announcements[2:]:
                                    st.markdown(f"• {announcement}")
                    else:
                        # PC・タブレットでは全件表示
                        for announcement in announcements:
                            st.markdown(f"• {announcement}")

                except json.JSONDecodeError:
                    st.warning("お知らせの読み込みエラー")

            # ★★★ アクションボタン（お知らせの下に追加）★★★
            st.markdown("---")
            st.markdown("### 🎯 アクション")

            # ★★★ 強力な紫色統一CSS（修正版）★★★
            st.markdown(f"""
            <style>
            /* 全ボタンを強制的に紫色統一 - より強力なセレクタ */
            div[data-testid="stButton"] > button,
            .stButton > button,
            button[kind="primary"],
            button[kind="secondary"],
            .st-emotion-cache-1x8cf1d > button,
            .st-emotion-cache-19ih6ej > button {{
                background-color: {config.PRIMARY_COLOR} !important;
                color: white !important;
                border: 2px solid {config.PRIMARY_COLOR} !important;
                border-radius: 8px !important;
                width: 100% !important;
                padding: 0.6rem 1rem !important;
                font-weight: 500 !important;
                transition: all 0.3s ease !important;
            }}
            
            div[data-testid="stButton"] > button:hover,
            .stButton > button:hover,
            button[kind="primary"]:hover,
            button[kind="secondary"]:hover,
            .st-emotion-cache-1x8cf1d > button:hover,
            .st-emotion-cache-19ih6ej > button:hover {{
                background-color: #6a3d7a !important;
                border-color: #6a3d7a !important;
                color: white !important;
                box-shadow: 0 4px 8px rgba(139, 79, 159, 0.3) !important;
            }}
            
            div[data-testid="stButton"] > button:focus,
            .stButton > button:focus,
            button[kind="primary"]:focus,
            button[kind="secondary"]:focus {{
                background-color: #6a3d7a !important;
                border-color: #6a3d7a !important;
                color: white !important;
                box-shadow: 0 0 0 3px rgba(139, 79, 159, 0.5) !important;
                outline: none !important;
            }}
            
            /* プライマリボタン特別指定 */
            div[data-testid="stButton"] > button[kind="primary"] {{
                background-color: {config.PRIMARY_COLOR} !important;
                border-color: {config.PRIMARY_COLOR} !important;
                color: white !important;
            }}
            
            /* セカンダリボタンも紫色に統一 */
            div[data-testid="stButton"] > button[kind="secondary"] {{
                background-color: {config.PRIMARY_COLOR} !important;
                border-color: {config.PRIMARY_COLOR} !important;
                color: white !important;
            }}
            </style>
            """, unsafe_allow_html=True)

            # 占い師登録ボタン（実際に機能するStreamlitボタンのみ）
            if st.button(
                "🔮 占い師登録",
                type="primary",
                key="sidebar_submit_app",
                use_container_width=True,
                help="新しい占い師情報を登録します"
            ):
                st.session_state.show_work_request = False
                st.session_state.show_admin = False
                st.session_state.selected_fortuneteller = None
                st.session_state.highlight_id = None
                st.session_state.show_submission_form = True
                st.rerun()

            # お仕事依頼ボタン（実際に機能するStreamlitボタンのみ）
            if st.button(
                "💼 お仕事のご依頼",
                key="sidebar_work_app",
                use_container_width=True,
                help="占い師への仕事依頼を送信します"
            ):
                st.session_state.show_submission_form = False
                st.session_state.show_admin = False
                st.session_state.selected_fortuneteller = None
                st.session_state.highlight_id = None
                st.session_state.show_work_request = True
                st.rerun()

            # カテゴリ統計
            st.markdown("### 🎴 占術カテゴリ")
            if not stats['categories'].empty:
                # モバイルでは上位3件のみ表示
                display_count = 3 if device_type == 'mobile' else len(
                    stats['categories'])
                display_categories = stats['categories'].head(display_count)

                for idx, row in display_categories.iterrows():
                    st.markdown(f"• {row['category']}: {row['count']}件")

                if device_type == 'mobile' and len(stats['categories']) > 3:
                    with st.expander("全カテゴリを表示"):
                        for idx, row in stats['categories'].iterrows():
                            st.markdown(
                                f"• {row['category']}: {row['count']}件")

        except Exception as e:
            st.error(f"情報パネル表示エラー: {str(e)}")

    def render_detail_panel_content(self, selected_id: int, selected_data: dict):
        """詳細パネルの内容を描画（レスポンシブ対応）"""
        device_type = st.session_state.get('device_type', 'desktop')

        st.markdown("---")
        st.markdown("### 📋 占い師詳細情報")

        # 基本情報カード（レスポンシブ対応）
        card_padding = "15px" if device_type == 'mobile' else "25px"
        font_size_main = "22px" if device_type == 'mobile' else "26px"
        font_size_content = "14px" if device_type == 'mobile' else "16px"

        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #e8f5e8 0%, #f0f8ff 100%);
            padding: {card_padding};
            border-radius: 12px;
            border: 3px solid {config.PRIMARY_COLOR};
            margin: 15px 0;
            box-shadow: 0 6px 12px rgba(139, 79, 159, 0.2);
        ">
            <h2 style="color: {config.PRIMARY_COLOR}; margin-top: 0; font-size: {font_size_main};">
                🔮 {selected_data['name']}
            </h2>
            <hr style="margin: 15px 0; opacity: 0.3;">
            <p style="margin: 10px 0; font-size: {font_size_content};"><strong>🎴 占術:</strong> {selected_data.get('category', '未設定')}</p>
            <p style="margin: 10px 0; font-size: {font_size_content};"><strong>✨ 特徴:</strong> {selected_data.get('description', '説明なし')}</p>
            <p style="margin: 8px 0; font-size: 12px; color: #666;"><strong>👤 投稿者:</strong> {selected_data.get('submitted_by', '不明')}</p>
        </div>
        """, unsafe_allow_html=True)

        # 連絡先情報（レスポンシブ対応）
        st.markdown("#### 📞 連絡先・住所情報")

        if device_type == 'mobile':
            # モバイルでは縦並び
            self._show_mobile_contact_info(selected_data)
        else:
            # PC・タブレットでは横並び
            self._show_desktop_contact_info(selected_data)

        # ナビゲーションボタン（レスポンシブ対応）
        self._show_responsive_navigation_buttons(selected_data)

        # アクションボタン（レスポンシブ対応）
        self._show_responsive_action_buttons(selected_id, device_type)

    def _show_mobile_contact_info(self, selected_data: dict):
        """モバイル用の連絡先情報表示"""
        contact = selected_data.get('contact')
        website = selected_data.get('website')
        zipcode = selected_data.get('zipcode')
        address = selected_data.get('address')

        # 電話番号
        if contact:
            phone_clean = re.sub(r'[^\d]', '', contact)
            st.markdown(f"""
            <div style="padding: 15px; background: #f0f8ff; border-radius: 8px; border-left: 4px solid {config.PRIMARY_COLOR}; margin: 8px 0;">
                📞 <strong>電話:</strong><br>
                <a href="tel:{phone_clean}" style="color: {config.PRIMARY_COLOR}; font-size: 20px; text-decoration: none; display: block; padding: 8px 0; min-height: 44px; line-height: 28px;">{contact}</a>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("📞 電話番号未登録")

        # ウェブサイト
        if website:
            st.markdown(f"""
            <div style="padding: 15px; background: #f0f8ff; border-radius: 8px; border-left: 4px solid {config.PRIMARY_COLOR}; margin: 8px 0;">
                🌐 <strong>ウェブサイト:</strong><br>
                <a href="{website}" target="_blank" style="color: {config.PRIMARY_COLOR}; font-size: 18px; text-decoration: none; display: block; padding: 8px 0; min-height: 44px; line-height: 28px;">サイトを見る ↗</a>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("🌐 ウェブサイト未登録")

        # 住所情報
        if zipcode or address:
            address_parts = []
            if zipcode:
                address_parts.append(f"〒{zipcode}")
            if address:
                address_parts.append(address)
            full_address = " ".join(address_parts)

            st.markdown(f"""
            <div style="padding: 15px; background: #f5f5f5; border-radius: 8px; border-left: 4px solid {config.PRIMARY_COLOR}; margin: 8px 0;">
                📍 <strong>住所:</strong><br>
                <span style="font-size: 16px; line-height: 1.5;">{full_address}</span>
            </div>
            """, unsafe_allow_html=True)

    def _show_desktop_contact_info(self, selected_data: dict):
        """PC・タブレット用の連絡先情報表示"""
        contact_col1, contact_col2 = st.columns(2)

        with contact_col1:
            contact = selected_data.get('contact')
            if contact:
                phone_clean = re.sub(r'[^\d]', '', contact)
                st.markdown(f"""
                <div style="padding: 15px; background: #f0f8ff; border-radius: 8px; border-left: 4px solid {config.PRIMARY_COLOR};">
                    📞 <strong>電話:</strong><br>
                    <a href="tel:{phone_clean}" style="color: {config.PRIMARY_COLOR}; font-size: 18px; text-decoration: none;">{contact}</a>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("📞 電話番号未登録")

        with contact_col2:
            website = selected_data.get('website')
            if website:
                st.markdown(f"""
                <div style="padding: 15px; background: #f0f8ff; border-radius: 8px; border-left: 4px solid {config.PRIMARY_COLOR};">
                    🌐 <strong>ウェブサイト:</strong><br>
                    <a href="{website}" target="_blank" style="color: {config.PRIMARY_COLOR}; font-size: 18px; text-decoration: none;">サイトを見る ↗</a>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("🌐 ウェブサイト未登録")

        # 住所情報
        zipcode = selected_data.get('zipcode')
        address = selected_data.get('address')
        if zipcode or address:
            address_parts = []
            if zipcode:
                address_parts.append(f"〒{zipcode}")
            if address:
                address_parts.append(address)
            full_address = " ".join(address_parts)

            st.markdown(f"""
            <div style="padding: 15px; background: #f5f5f5; border-radius: 8px; border-left: 4px solid {config.PRIMARY_COLOR}; margin-bottom: 15px;">
                📍 <strong>住所:</strong><br>
                <span style="font-size: 16px;">{full_address}</span>
            </div>
            """, unsafe_allow_html=True)

    def _show_responsive_navigation_buttons(self, selected_data: dict):
        """レスポンシブ対応のナビゲーションボタン"""
        device_type = st.session_state.get('device_type', 'desktop')

        st.markdown("#### 🧭 他のマップアプリでナビ")
        st.caption("お好みのマップアプリで道案内を開始できます")

        # 座標取得
        lat = selected_data['latitude']
        lng = selected_data['longitude']

        # ナビゲーションリンクを生成
        nav_links = self._generate_navigation_links(
            lat, lng, selected_data['name'])

        if device_type == 'mobile':
            # モバイルでは縦並び
            st.markdown(f"""
            <a href="{nav_links['google']}" target="_blank" style="text-decoration: none;">
                <div style="
                    background: linear-gradient(45deg, #4285F4, #34A853);
                    color: white;
                    padding: 16px;
                    border-radius: 8px;
                    text-align: center;
                    margin: 8px 0;
                    cursor: pointer;
                    transition: transform 0.2s;
                    min-height: 44px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                ">
                    🗺️ <strong>Google Maps</strong><br>
                    <small>道案内を開始</small>
                </div>
            </a>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <a href="{nav_links['yahoo']}" target="_blank" style="text-decoration: none;">
                <div style="
                    background: linear-gradient(45deg, #FF0033, #FF6B00);
                    color: white;
                    padding: 16px;
                    border-radius: 8px;
                    text-align: center;
                    margin: 8px 0;
                    cursor: pointer;
                    transition: transform 0.2s;
                    min-height: 44px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                ">
                    🗾 <strong>Yahoo! Map</strong><br>
                    <small>ヤフー地図で表示</small>
                </div>
            </a>
            """, unsafe_allow_html=True)
        else:
            # PC・タブレットでは横並び
            nav_col1, nav_col2 = st.columns(2)

            with nav_col1:
                st.markdown(f"""
                <a href="{nav_links['google']}" target="_blank" style="text-decoration: none;">
                    <div style="
                        background: linear-gradient(45deg, #4285F4, #34A853);
                        color: white;
                        padding: 12px;
                        border-radius: 8px;
                        text-align: center;
                        margin: 5px 0;
                        cursor: pointer;
                        transition: transform 0.2s;
                    ">
                        🗺️ <strong>Google Maps</strong><br>
                        <small>道案内を開始</small>
                    </div>
                </a>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <a href="{nav_links['yahoo']}" target="_blank" style="text-decoration: none;">
                    <div style="
                        background: linear-gradient(45deg, #FF0033, #FF6B00);
                        color: white;
                        padding: 12px;
                        border-radius: 8px;
                        text-align: center;
                        margin: 5px 0;
                        cursor: pointer;
                        transition: transform 0.2s;
                    ">
                        🗾 <strong>Yahoo! Map</strong><br>
                        <small>ヤフー地図で表示</small>
                    </div>
                </a>
                """, unsafe_allow_html=True)

            with nav_col2:
                st.markdown(f"""
                <a href="{nav_links['apple']}" target="_blank" style="text-decoration: none;">
                    <div style="
                        background: linear-gradient(45deg, #007AFF, #5AC8FA);
                        color: white;
                        padding: 12px;
                        border-radius: 8px;
                        text-align: center;
                        margin: 5px 0;
                        cursor: pointer;
                        transition: transform 0.2s;
                    ">
                        🍎 <strong>Apple Maps</strong><br>
                        <small>iPhoneで開く</small>
                    </div>
                </a>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <a href="{nav_links['waze']}" target="_blank" style="text-decoration: none;">
                    <div style="
                        background: linear-gradient(45deg, #318CE7, #00C7F7);
                        color: white;
                        padding: 12px;
                        border-radius: 8px;
                        text-align: center;
                        margin: 5px 0;
                        cursor: pointer;
                        transition: transform 0.2s;
                    ">
                        🚗 <strong>Waze</strong><br>
                        <small>渋滞回避ルート</small>
                    </div>
                </a>
                """, unsafe_allow_html=True)

    def _show_responsive_action_buttons(self, selected_id: int, device_type: str):
        """レスポンシブ対応のアクションボタン"""
        st.markdown("#### 🎯 アクション・ナビゲーション")

        if device_type == 'mobile':
            # モバイルでは縦並び
            if st.button(
                "🗺️ 地図で強調表示",
                key=f"highlight_{selected_id}",
                use_container_width=True,
                type="primary"
            ):
                st.session_state.highlight_id = selected_id
                st.rerun()

            if st.button(
                "✖ 詳細パネルを閉じる",
                key=f"close_{selected_id}",
                type="secondary",
                use_container_width=True
            ):
                st.session_state.selected_fortuneteller = None
                st.session_state.highlight_id = None
                st.session_state.detail_refresh_flag = False
                if 'detail_placeholder' in st.session_state:
                    st.session_state.detail_placeholder.empty()
                st.rerun()
        else:
            # PC・タブレットでは横並び
            action_col1, action_col2 = st.columns(2)

            with action_col1:
                if st.button(
                    "🗺️ 地図で強調表示",
                    key=f"highlight_{selected_id}",
                    use_container_width=True
                ):
                    st.session_state.highlight_id = selected_id
                    st.rerun()

            with action_col2:
                if st.button(
                    "✖ 詳細パネルを閉じる",
                    key=f"close_{selected_id}",
                    type="secondary",
                    use_container_width=True
                ):
                    st.session_state.selected_fortuneteller = None
                    st.session_state.highlight_id = None
                    st.session_state.detail_refresh_flag = False
                    if 'detail_placeholder' in st.session_state:
                        st.session_state.detail_placeholder.empty()
                    st.rerun()

    def _generate_navigation_links(self, lat: float, lng: float, name: str) -> dict:
        """各種マップアプリのナビゲーションリンクを生成"""
        import urllib.parse

        # 名前をURLエンコード
        encoded_name = urllib.parse.quote(name)

        # 各マップアプリのリンクを生成
        links = {
            'google': f"https://maps.google.com/maps?q={lat},{lng}({encoded_name})",
            'apple': f"https://maps.apple.com/?q={lat},{lng}&t=m",
            'yahoo': f"https://map.yahoo.co.jp/place?lat={lat}&lon={lng}&zoom=16&maptype=basic",
            'waze': f"https://waze.com/ul?ll={lat},{lng}&navigate=yes"
        }

        return links

    def show_detail_panel(self, selected_id: int):
        """詳細パネル表示 - レスポンシブ対応版"""
        try:
            # データを最新取得
            selected_data = self.db.get_fortuneteller_by_id(selected_id)

            if selected_data:
                # st.empty()を使った強制再描画
                if 'detail_placeholder' not in st.session_state:
                    st.session_state.detail_placeholder = st.empty()

                # プレースホルダーを完全にクリア
                st.session_state.detail_placeholder.empty()

                # 0.1秒待機（確実なクリア）
                time.sleep(0.1)

                # 新しい内容で再描画
                with st.session_state.detail_placeholder.container():
                    self.render_detail_panel_content(
                        selected_id, selected_data)

                # フラグをリセット
                st.session_state.detail_refresh_flag = False

            else:
                st.error(f"⚠ ID {selected_id} のデータが見つかりません")
                st.session_state.selected_fortuneteller = None

        except Exception as e:
            st.error(f"⚠ 詳細パネル表示エラー: {str(e)}")
            st.exception(e)

    def run(self):
        """アプリケーション実行（レスポンシブ対応）"""
        try:
            # ページ設定（レスポンシブ対応）
            UIManager.setup_page_config()

            # ヘッダー非表示（新規追加）
            hide_streamlit_style()

            # デバイス検出
            self._detect_device_type()

            # レスポンシブ対応ヘッダー表示
            UIManager.show_header()

            # 画面遷移処理
            if st.session_state.show_admin:
                self.admin_page.show()
                if st.button("🗺️ 地図に戻る"):
                    st.session_state.show_admin = False
                    st.rerun()

            elif st.session_state.show_submission_form:
                self.submission_form.show()

            elif st.session_state.show_work_request:
                self.work_request_form.show()

            else:
                # メイン画面（レスポンシブ対応）
                device_type = st.session_state.get('device_type', 'desktop')

                if device_type == 'mobile':
                    # モバイルレイアウト（縦並び）
                    self._show_mobile_layout()
                else:
                    # PC・タブレットレイアウト（横並び）
                    self._show_desktop_layout()

        except Exception as e:
            st.error(f"⚠ アプリケーション実行エラー: {str(e)}")
            st.exception(e)

    def _show_mobile_layout(self):
        """モバイル用レイアウト"""
        st.markdown("### 🗺️ 占い師マップ")

        # 地図表示（モバイル最適化）
        fortunetellers_df = self.db.get_fortunetellers()
        map_obj = MapManager.create_map(
            fortunetellers_df,
            highlight_id=st.session_state.highlight_id,
            selected_id=st.session_state.selected_fortuneteller
        )

        map_key = f"map_{st.session_state.selected_fortuneteller}_mobile"
        mobile_map_height = 300

        # 地図表示（モバイル用高さ）
        map_data = st_folium(
            map_obj,
            width=None,
            height=mobile_map_height,
            returned_objects=["last_object_clicked", "last_clicked"],
            key=map_key
        )

        # 地図クリック処理
        self._handle_map_interaction(map_data, fortunetellers_df)

        # 詳細パネル表示（モバイル対応）
        if st.session_state.get('selected_fortuneteller'):
            st.markdown("---")
            self.show_detail_panel(st.session_state.selected_fortuneteller)

        # 情報パネル（モバイル対応）
        st.markdown("---")
        self.show_responsive_info_panel()

        # 管理者ログインボタン（モバイル対応）
        st.markdown("---")
        if st.button("👨‍💼 管理者ログイン", key="admin_login_mobile", use_container_width=True):
            st.session_state.show_admin = True
            st.rerun()

    def _show_desktop_layout(self):
        """PC・タブレット用レイアウト（メニューを左側に配置）"""
        main_col1, main_col2 = st.columns([3, 7])

        with main_col1:
            self.show_responsive_info_panel()
            st.markdown("---")
            if st.button("👨‍💼 管理者ログイン", key="admin_login_desktop"):
                st.session_state.show_admin = True
                st.rerun()

        with main_col2:
            st.markdown("### 🗺️ 占い師マップ")

            # 地図表示
            fortunetellers_df = self.db.get_fortunetellers()
            map_obj = MapManager.create_map(
                fortunetellers_df,
                highlight_id=st.session_state.highlight_id,
                selected_id=st.session_state.selected_fortuneteller
            )

            map_key = f"map_{st.session_state.selected_fortuneteller}_desktop"
            desktop_map_height = self._get_responsive_map_height()

            # 地図表示
            map_data = st_folium(
                map_obj,
                width=None,
                height=desktop_map_height,
                returned_objects=["last_object_clicked", "last_clicked"],
                key=map_key
            )

            # 地図クリック処理
            self._handle_map_interaction(map_data, fortunetellers_df)

            # 詳細パネル表示
            if st.session_state.get('selected_fortuneteller'):
                self.show_detail_panel(st.session_state.selected_fortuneteller)

    def _handle_map_interaction(self, map_data, fortunetellers_df):
        """地図クリック処理（共通）"""
        clicked_fortuneteller_id = None

        if map_data:
            # last_object_clicked を確認（座標の場合）
            if map_data.get('last_object_clicked'):
                obj_clicked = map_data['last_object_clicked']

                # 座標データの場合
                if isinstance(obj_clicked, dict) and 'lat' in obj_clicked and 'lng' in obj_clicked:
                    clicked_lat = obj_clicked['lat']
                    clicked_lng = obj_clicked['lng']
                    clicked_fortuneteller_id = self.find_closest_fortuneteller(
                        clicked_lat, clicked_lng, fortunetellers_df
                    )

                # ポップアップデータの場合（従来通り）
                elif isinstance(obj_clicked, dict) and 'popup' in obj_clicked:
                    popup_content = obj_clicked['popup']
                    match = re.search(r'ID: (\d+)', popup_content)
                    if match:
                        clicked_fortuneteller_id = int(match.group(1))

            # last_clicked をバックアップとして使用
            if not clicked_fortuneteller_id and map_data.get('last_clicked'):
                clicked_coords = map_data['last_clicked']
                if clicked_coords and isinstance(clicked_coords, dict):
                    clicked_lat = clicked_coords.get('lat')
                    clicked_lng = clicked_coords.get('lng')
                    if clicked_lat and clicked_lng:
                        clicked_fortuneteller_id = self.find_closest_fortuneteller(
                            clicked_lat, clicked_lng, fortunetellers_df
                        )

        # 詳細パネル表示処理
        if clicked_fortuneteller_id:
            current_selected = st.session_state.get('selected_fortuneteller')
            if current_selected != clicked_fortuneteller_id:
                self.force_update_detail_panel(clicked_fortuneteller_id)

        # ハイライトクリア
        if st.session_state.highlight_id:
            st.session_state.highlight_id = None


# アプリケーション起動
if __name__ == "__main__":
    try:
        app = FortunetellerMapApp()
        app.run()
    except Exception as e:
        st.error(f"⚠ 起動エラー: {str(e)}")
        st.exception(e)
