"""
UI共通コンポーネント
ヘッダー、詳細パネルなどの共通UI要素を管理
スマホ・タブレット対応版（エラー対応）
"""
import streamlit as st
import re
from typing import Dict
import config


class UIManager:
    """UI表示を管理するクラス（レスポンシブ対応・エラー対応版）"""

    @staticmethod
    def setup_page_config():
        """ページ設定（レスポンシブ対応・エラー対応）"""
        st.set_page_config(
            page_title=config.PAGE_TITLE,
            page_icon=config.PAGE_ICON,
            layout="wide",
            initial_sidebar_state="collapsed",
            # モバイル対応のメタタグ追加
            menu_items={
                'Get Help': None,
                'Report a bug': None,
                'About': f"{config.PAGE_TITLE} - スマホ・PC対応の占いマップ"
            }
        )

        # レスポンシブCSS適用（エラー対応）
        UIManager._apply_responsive_css()

    @staticmethod
    def _apply_responsive_css():
        """レスポンシブCSSの適用（エラー対応版）"""
        try:
            # config.pyからRESPONSIVE_CSSを取得
            if hasattr(config, 'RESPONSIVE_CSS'):
                responsive_css = config.RESPONSIVE_CSS.format(
                    primary_color=config.PRIMARY_COLOR
                )
                st.markdown(responsive_css, unsafe_allow_html=True)
            else:
                # RESPONSIVE_CSSが存在しない場合のフォールバック
                UIManager._apply_fallback_css()
        except Exception as e:
            # エラーが発生した場合もフォールバック
            print(f"CSS適用エラー: {e}")
            UIManager._apply_fallback_css()

        # 追加のモバイル最適化用メタタグ
        st.markdown("""
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="default">
        <meta name="format-detection" content="telephone=no">
        """, unsafe_allow_html=True)

    @staticmethod
    def _apply_fallback_css():
        """フォールバック用のシンプルなCSS"""
        fallback_css = f"""
        <style>
        /* 基本設定 */
        .main {{ padding: 0; }}
        .block-container {{
            padding: 0.5rem;
            max-width: 100%;
            margin-top: 0 !important;
        }}

        /* ヘッダー */
        h1 {{
            color: {config.PRIMARY_COLOR};
            font-size: 28px !important;
            margin-bottom: 5px !important;
            margin-top: 0 !important;
        }}

        /* ボタン共通 - 全て紫色統一 */
        .stButton>button {{
            background-color: {config.PRIMARY_COLOR} !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
            padding: 0.5rem 1rem !important;
            font-weight: 500 !important;
        }}
        .stButton>button:hover {{
            background-color: #6a3d7a !important;
            border-color: #6a3d7a !important;
            color: white !important;
        }}

        /* 詳細パネル */
        .detail-panel {{
            background: linear-gradient(135deg, #f5ebff 0%, #ffffff 100%);
            padding: 20px;
            border-radius: 10px;
            border: 2px solid {config.PRIMARY_COLOR};
            margin-top: 10px;
        }}

        /* リンク */
        .clickable-link {{
            color: {config.PRIMARY_COLOR};
            text-decoration: none;
            font-weight: bold;
        }}
        .clickable-link:hover {{
            text-decoration: underline;
        }}

        /* スマートフォン対応 */
        @media screen and (max-width: 767px) {{
            .block-container {{
                padding: 0.25rem;
                margin-top: 0 !important;
            }}
            
            h1 {{
                font-size: 20px !important;
                text-align: center;
                margin-bottom: 5px !important;
                margin-top: 0 !important;
            }}
            
            .stButton>button {{
                width: 100% !important;
                padding: 0.6rem !important;
                font-size: 16px !important;
                margin-bottom: 8px !important;
                min-height: 44px !important;
                background-color: {config.PRIMARY_COLOR} !important;
                color: white !important;
            }}
            
            .detail-panel {{
                padding: 15px;
                margin: 10px 0;
            }}
            
            .clickable-link {{
                padding: 8px;
                display: inline-block;
                min-height: 44px;
                line-height: 28px;
            }}
        }}

        /* タブレット対応 */
        @media screen and (min-width: 768px) and (max-width: 1024px) {{
            .block-container {{
                padding: 0.5rem;
                margin-top: 0 !important;
            }}
            
            h1 {{
                font-size: 24px !important;
                margin-bottom: 5px !important;
                margin-top: 0 !important;
            }}
            
            .stButton>button {{
                padding: 0.4rem 0.8rem !important;
                font-size: 14px !important;
                background-color: {config.PRIMARY_COLOR} !important;
                color: white !important;
            }}
        }}
        </style>
        """
        st.markdown(fallback_css, unsafe_allow_html=True)

    @staticmethod
    def show_header():
        """ヘッダー表示（重複削除版） - タイトルを表示しない"""
        # モバイル判定用のJavaScript
        UIManager._inject_device_detection()

        # タイトルは削除（重複のため）
        # デバイス判定のJavaScriptのみ実行

    @staticmethod
    def _inject_device_detection():
        """デバイス判定用のJavaScriptを注入（エラー対応版）"""
        try:
            st.markdown("""
            <script>
            function detectDevice() {
                const width = window.innerWidth;
                const isMobile = width <= 767;
                const isTablet = width >= 768 && width <= 1024;
                
                // body要素にクラスを追加
                document.body.classList.remove('mobile', 'tablet', 'desktop');
                if (isMobile) {
                    document.body.classList.add('mobile');
                } else if (isTablet) {
                    document.body.classList.add('tablet');
                } else {
                    document.body.classList.add('desktop');
                }
            }
            
            // 初回実行
            detectDevice();
            
            // リサイズ時に再実行
            window.addEventListener('resize', detectDevice);
            </script>
            """, unsafe_allow_html=True)
        except Exception as e:
            print(f"JavaScript注入エラー: {e}")

    @staticmethod
    def _handle_navigation_to_submission():
        """占い師登録への遷移処理"""
        st.session_state.show_work_request = False
        st.session_state.show_admin = False
        st.session_state.selected_fortuneteller = None
        st.session_state.highlight_id = None
        st.session_state.show_submission_form = True
        st.rerun()

    @staticmethod
    def _handle_navigation_to_work_request():
        """お仕事依頼への遷移処理"""
        st.session_state.show_submission_form = False
        st.session_state.show_admin = False
        st.session_state.selected_fortuneteller = None
        st.session_state.highlight_id = None
        st.session_state.show_work_request = True
        st.rerun()

    @staticmethod
    def show_responsive_info_panel():
        """レスポンシブ対応の情報パネル（不明表示完全削除版）"""
        st.markdown("### 📊 サイト情報")

        # **メトリクス表示を完全に削除** - 不明な表示を一切しない
        try:
            from database import DatabaseManager
            db = DatabaseManager()
            stats = db.get_statistics()

            # シンプルな文字表示のみ（メトリクスボックスは使用しない）
            st.write(f"**登録占い師数**: {stats['approved']}件")

        except Exception as e:
            st.error(f"統計情報の読み込みエラー: {e}")
            st.write("**登録占い師数**: 読み込み中...")

        # 新着情報を安全に表示
        try:
            UIManager._show_responsive_news()
        except Exception as e:
            st.error(f"新着情報表示エラー: {e}")
            st.markdown("### 🆕 新着情報")
            st.info("新着情報の読み込みに失敗しました")

        # お知らせを安全に表示
        try:
            UIManager._show_responsive_announcements()
        except Exception as e:
            st.error(f"お知らせ表示エラー: {e}")
            st.markdown("### 📰 お知らせ")
            st.info("お知らせの読み込みに失敗しました")

        # ★★★ アクションボタンを確実に表示（重複削除版） ★★★
        st.markdown("---")
        st.markdown("### 🎯 アクション")

        # 強制的にボタンスタイルを適用
        st.markdown(f"""
        <style>
        /* すべてのボタンを強制的に紫色に */
        div[data-testid="stButton"] > button {{
            background-color: {config.PRIMARY_COLOR} !important;
            color: white !important;
            border: 1px solid {config.PRIMARY_COLOR} !important;
            border-radius: 8px !important;
            width: 100% !important;
            padding: 0.6rem !important;
            font-weight: 500 !important;
        }}
        
        div[data-testid="stButton"] > button:hover {{
            background-color: #6a3d7a !important;
            border-color: #6a3d7a !important;
            color: white !important;
        }}
        
        div[data-testid="stButton"] > button:focus {{
            background-color: #6a3d7a !important;
            border-color: #6a3d7a !important;
            color: white !important;
            box-shadow: 0 0 0 2px rgba(139, 79, 159, 0.5) !important;
        }}
        </style>
        """, unsafe_allow_html=True)

        try:
            # 占い師登録ボタン（実際に機能するStreamlitボタンのみ）
            if st.button(
                "🔮 占い師登録",
                key="sidebar_submit_main",
                use_container_width=True,
                help="新しい占い師情報を登録します"
            ):
                UIManager._handle_navigation_to_submission()

            # お仕事依頼ボタン（実際に機能するStreamlitボタンのみ）
            if st.button(
                "💼 お仕事のご依頼",
                key="sidebar_work_main",
                use_container_width=True,
                help="占い師への仕事依頼を送信します"
            ):
                UIManager._handle_navigation_to_work_request()

        except Exception as e:
            st.error(f"アクションボタン表示エラー: {str(e)}")

        # カテゴリ統計を安全に表示
        try:
            UIManager._show_responsive_categories()
        except Exception as e:
            st.error(f"カテゴリ統計表示エラー: {e}")
            st.markdown("### 🎴 占術カテゴリ")
            st.info("カテゴリ統計の読み込みに失敗しました")

        # 管理者ログインを確実に表示（紫色統一）
        st.markdown("---")
        try:
            if st.button(
                "👨‍💼 管理者ログイン",
                key="sidebar_admin_main",
                use_container_width=True,
                help="管理者画面にアクセスします"
            ):
                UIManager._handle_navigation_to_admin()
        except Exception as e:
            st.error(f"管理者ログイン表示エラー: {e}")

    @staticmethod
    def _show_responsive_news():
        """レスポンシブ対応の新着情報（エラー対応版）"""
        st.markdown("### 🆕 新着情報")
        st.caption("クリックで詳細パネル表示")

        try:
            from database import DatabaseManager
            db = DatabaseManager()
            recent_df = db.get_fortunetellers("approved")

            if not recent_df.empty:
                recent_df = recent_df.head(5)

                for idx, row in recent_df.iterrows():
                    current_selected = st.session_state.get(
                        'selected_fortuneteller')
                    is_selected = (current_selected == row['id'])

                    button_key = f"info_{row['id']}_{idx}_responsive"
                    button_text = f"{'✅' if is_selected else '🔮'} {row['name']}"

                    # カテゴリ表示
                    category_display = row.get('category', '未設定')

                    if st.button(
                        f"{button_text} - {category_display}",
                        key=button_key,
                        use_container_width=True,
                        type="primary" if is_selected else "secondary"
                    ):
                        UIManager._handle_fortuneteller_selection(row['id'])
            else:
                st.info("新着情報がありません")
        except Exception as e:
            st.warning(f"新着情報の読み込み中にエラーが発生しました: {str(e)}")

    @staticmethod
    def _show_responsive_announcements():
        """レスポンシブ対応のお知らせ（エラー対応版）"""
        st.markdown("### 📰 お知らせ")

        try:
            from database import DatabaseManager
            db = DatabaseManager()
            announcements_json = db.get_setting('announcements')

            if announcements_json:
                try:
                    import json
                    announcements = json.loads(announcements_json)

                    for announcement in announcements:
                        st.markdown(f"• {announcement}")

                except json.JSONDecodeError:
                    st.warning("お知らせの読み込みエラー")
                    # デフォルトのお知らせ表示
                    for announcement in config.DEFAULT_ANNOUNCEMENTS:
                        st.markdown(f"• {announcement}")
            else:
                # デフォルトのお知らせ
                for announcement in config.DEFAULT_ANNOUNCEMENTS:
                    st.markdown(f"• {announcement}")

        except Exception as e:
            st.warning(f"お知らせの読み込み中にエラーが発生しました: {str(e)}")
            # 最後のフォールバック
            st.markdown("• システムからのお知らせを読み込み中...")

    @staticmethod
    def _handle_navigation_to_admin():
        """管理者画面への遷移処理"""
        st.session_state.show_submission_form = False
        st.session_state.show_work_request = False
        st.session_state.selected_fortuneteller = None
        st.session_state.highlight_id = None
        st.session_state.show_admin = True
        st.rerun()

    @staticmethod
    def _show_responsive_categories():
        """レスポンシブ対応のカテゴリ統計（エラー対応版）"""
        st.markdown("### 🎴 占術カテゴリ")

        try:
            from database import DatabaseManager
            db = DatabaseManager()
            stats = db.get_statistics()

            if not stats['categories'].empty:
                for idx, row in stats['categories'].iterrows():
                    st.markdown(f"• {row['category']}: {row['count']}件")
            else:
                st.info("カテゴリ統計を準備中...")
        except Exception as e:
            st.warning(f"カテゴリ統計の読み込み中にエラーが発生しました: {str(e)}")

    @staticmethod
    def _handle_fortuneteller_selection(fortuneteller_id):
        """占い師選択時の処理（エラー対応版）"""
        try:
            st.session_state.selected_fortuneteller = fortuneteller_id
            st.session_state.highlight_id = fortuneteller_id
            st.session_state.detail_refresh_flag = True
            st.session_state.last_render_time = __import__('time').time()
            st.rerun()
        except Exception as e:
            st.error(f"占い師選択エラー: {e}")
            print(f"占い師選択処理エラー: {e}")

    @staticmethod
    def show_responsive_detail_panel(fortuneteller: Dict):
        """レスポンシブ対応の詳細パネル（エラー対応版）"""
        try:
            st.markdown("### 📋 占い師詳細情報")

            with st.container():
                # モバイル対応の詳細カード
                st.markdown(f"""
                <div class="detail-panel responsive-detail">
                    <h3 style="color: {config.PRIMARY_COLOR}; margin-top: 0;">🔮 {fortuneteller['name']}</h3>
                    <hr style="margin: 15px 0;">
                    <p style="margin: 8px 0;"><b>🎴 占術:</b> {fortuneteller.get('category', '未設定')}</p>
                    <p style="margin: 8px 0;"><b>✨ 特徴:</b> {fortuneteller.get('description', '説明なし')}</p>
                </div>
                """, unsafe_allow_html=True)

                # 連絡先情報（モバイル対応）
                UIManager._show_responsive_contact_info(fortuneteller)

                # アクションボタン（モバイル対応）
                UIManager._show_responsive_action_buttons(fortuneteller)
        except Exception as e:
            st.error(f"詳細パネル表示エラー: {e}")
            # エラー時の簡易表示
            st.markdown("### 📋 占い師情報")
            st.write(f"**名前**: {fortuneteller.get('name', '不明')}")
            st.write(f"**カテゴリ**: {fortuneteller.get('category', '未設定')}")

    @staticmethod
    def _show_responsive_contact_info(fortuneteller: Dict):
        """レスポンシブ対応の連絡先情報（エラー対応版）"""
        try:
            st.markdown("#### 📞 連絡先情報")

            contact_col1, contact_col2 = st.columns([1, 1])

            with contact_col1:
                if fortuneteller.get('contact'):
                    phone = fortuneteller['contact']
                    phone_clean = re.sub(r'[^\d]', '', phone)
                    st.markdown(f"""
                    <div class="contact-info">
                        <p><b>📞 電話:</b><br>
                        <a href="tel:{phone_clean}" class="clickable-link" 
                           style="font-size: 16px; display: block; padding: 8px 0;">
                           {phone}
                        </a></p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("📞 電話番号未登録")

            with contact_col2:
                if fortuneteller.get('website'):
                    st.markdown(f"""
                    <div class="contact-info">
                        <p><b>🌐 サイト:</b><br>
                        <a href="{fortuneteller['website']}" target="_blank" class="clickable-link"
                           style="font-size: 16px; display: block; padding: 8px 0;">
                           サイトを見る ↗
                        </a></p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("🌐 ウェブサイト未登録")
        except Exception as e:
            st.error(f"連絡先情報表示エラー: {e}")

    @staticmethod
    def _show_responsive_action_buttons(fortuneteller):
        """レスポンシブ対応のアクションボタン（詳細パネル用）"""
        # この関数は詳細パネル表示時に使用される
        pass

    @staticmethod
    def show_geolocation_component():
        """現在地取得コンポーネントを表示"""
        st.markdown("""
        <div id="geolocation-container" style="margin: 15px 0;">
            <button id="get-location-btn" onclick="getCurrentLocation()" 
                    style="
                        background: linear-gradient(45deg, #28a745, #20c997);
                        color: white;
                        border: none;
                        padding: 12px 20px;
                        border-radius: 8px;
                        font-size: 16px;
                        cursor: pointer;
                        transition: all 0.3s ease;
                        min-height: 44px;
                        width: 100%;
                        margin-bottom: 10px;
                    ">
                📍 現在地を取得して登録
            </button>
            <div id="location-status" style="margin-top: 10px; font-size: 14px;"></div>
        </div>

        <script>
        function getCurrentLocation() {
            const statusDiv = document.getElementById('location-status');
            const btn = document.getElementById('get-location-btn');
            
            // ボタンを無効化
            btn.disabled = true;
            btn.innerHTML = '📍 位置情報を取得中...';
            btn.style.background = '#6c757d';
            
            statusDiv.innerHTML = '<div style="color: #007bff;">🔄 位置情報を取得しています...</div>';
            
            if (!navigator.geolocation) {
                statusDiv.innerHTML = '<div style="color: #dc3545;">❌ お使いのブラウザは位置情報に対応していません</div>';
                resetButton();
                return;
            }
            
            const options = {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 600000
            };
            
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    const accuracy = position.coords.accuracy;
                    
                    // Streamlitのセッション状態に位置情報を保存
                    window.parent.postMessage({
                        type: 'geolocation_success',
                        latitude: lat,
                        longitude: lng,
                        accuracy: accuracy
                    }, '*');
                    
                    statusDiv.innerHTML = 
                        '<div style="color: #28a745;">✅ 現在地を取得しました！</div>' +
                        '<div style="color: #6c757d; font-size: 12px;">緯度: ' + lat.toFixed(6) + ', 経度: ' + lng.toFixed(6) + '</div>' +
                        '<div style="color: #6c757d; font-size: 12px;">精度: 約' + Math.round(accuracy) + 'm</div>';
                    
                    resetButton();
                },
                function(error) {
                    let errorMessage = '';
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            errorMessage = '❌ 位置情報の使用が拒否されました。ブラウザの設定で許可してください。';
                            break;
                        case error.POSITION_UNAVAILABLE:
                            errorMessage = '❌ 位置情報を取得できませんでした。';
                            break;
                        case error.TIMEOUT:
                            errorMessage = '❌ 位置情報の取得がタイムアウトしました。';
                            break;
                        default:
                            errorMessage = '❌ 位置情報の取得に失敗しました。';
                            break;
                    }
                    
                    statusDiv.innerHTML = '<div style="color: #dc3545;">' + errorMessage + '</div>';
                    
                    // Streamlitにエラーを通知
                    window.parent.postMessage({
                        type: 'geolocation_error',
                        error: errorMessage
                    }, '*');
                    
                    resetButton();
                },
                options
            );
        }
        
        function resetButton() {
            const btn = document.getElementById('get-location-btn');
            btn.disabled = false;
            btn.innerHTML = '📍 現在地を取得して登録';
            btn.style.background = 'linear-gradient(45deg, #28a745, #20c997)';
        }
        
        // メッセージリスナー（Streamlit側からの応答を受信）
        window.addEventListener('message', function(event) {
            if (event.data.type === 'reset_geolocation') {
                const statusDiv = document.getElementById('location-status');
                statusDiv.innerHTML = '';
                resetButton();
            }
        });
        </script>
        """, unsafe_allow_html=True)

    @staticmethod
    def show_geolocation_instructions():
        """現在地取得の説明を表示"""
        st.info("""
        **📍 現在地登録について**
        
        • 現在地ボタンをクリックすると、お使いのデバイスの位置情報を取得します
        • 初回利用時は、ブラウザから位置情報の使用許可を求められます
        • 取得した位置は地図上で確認・調整できます
        • WiFiや GPS の電波状況により精度が変わります
        • 位置情報はお客様のプライバシーを尊重し、適切に管理されます
        """)

        st.warning("""
        **⚠️ ご注意**
        
        • 位置情報機能を利用するには、ブラウザの許可が必要です
        • HTTPSサイトでのみ動作します（ローカルでは制限あり）
        • 屋内や電波の悪い場所では精度が低下する場合があります
        """)

    @staticmethod
    def handle_geolocation_message():
        """位置情報取得結果のJavaScript通信を処理"""
        # JavaScriptからの位置情報メッセージを処理するためのリスナー
        st.markdown("""
        <script>
        // Streamlitセッション状態との連携
        window.addEventListener('message', function(event) {
            if (event.data.type === 'geolocation_success') {
                // Streamlitのコールバック関数があれば呼び出し
                if (window.streamlitGeolocationCallback) {
                    window.streamlitGeolocationCallback(event.data);
                }
            }
        });
        </script>
        """, unsafe_allow_html=True)
