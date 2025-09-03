"""
占い師投稿フォーム（デスクトップ固定版）
新規占い師情報の投稿を管理
"""
import streamlit as st
import folium
from streamlit_folium import st_folium
import config
import requests
import re


class SubmissionForm:
    """投稿フォームクラス（デスクトップ固定版）"""

    def __init__(self, db):
        self.db = db

    def show(self):
        """投稿フォーム表示（デスクトップ固定版）"""
        st.markdown("---")
        st.subheader("🔮 新規占い師を登録")

        # セッション状態の初期化
        self._init_session_state()

        # 地図表示（デスクトップ固定）
        self._show_map()

        # フォームセクション（デスクトップ固定）
        self._show_form_section()

        # 閉じるボタン
        self._show_close_section()

    def _init_session_state(self):
        """セッション状態の初期化"""
        if 'submission_click_lat' not in st.session_state:
            st.session_state.submission_click_lat = None
        if 'submission_click_lng' not in st.session_state:
            st.session_state.submission_click_lng = None
        if 'auto_address' not in st.session_state:
            st.session_state.auto_address = ""

    def _show_map(self):
        """地図表示（デスクトップ固定版）"""
        # ★★★ 位置情報取得ボタン（デスクトップ固定） ★★★
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("📍 位置情報を取得", key="get_location_desktop", type="primary"):
                self._get_current_location()

        st.info("📍 地図をクリックして占い師の位置を指定してください")

        # 現在の選択状態
        has_location = (st.session_state.submission_click_lat is not None and
                        st.session_state.submission_click_lng is not None)

        # 地図の中心とズームを決定
        if has_location:
            center_lat = st.session_state.submission_click_lat
            center_lng = st.session_state.submission_click_lng
            zoom_level = 14
        else:
            center_lat = config.DEFAULT_CENTER_LAT
            center_lng = config.DEFAULT_CENTER_LON
            zoom_level = 10

        # 地図作成
        submission_map = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=zoom_level,
            tiles='OpenStreetMap'
        )

        # マーカー追加（位置が選択されている場合）
        if has_location:
            folium.Marker(
                [st.session_state.submission_click_lat,
                 st.session_state.submission_click_lng],
                popup=folium.Popup(
                    f"""
                    <div style="font-family: sans-serif; width: 220px;">
                        <h4 style="color: {config.PRIMARY_COLOR}; margin: 5px 0;">📍 選択された位置</h4>
                        <p style="margin: 5px 0;"><strong>緯度:</strong> {st.session_state.submission_click_lat:.6f}</p>
                        <p style="margin: 5px 0;"><strong>経度:</strong> {st.session_state.submission_click_lng:.6f}</p>
                        <p style="font-size: 12px; color: #666; margin-top: 8px;">✅ この位置で占い師を登録します</p>
                    </div>
                    """,
                    max_width=250
                ),
                tooltip="占い師登録位置",
                icon=folium.Icon(
                    color='red',
                    icon='star',
                    prefix='fa'
                )
            ).add_to(submission_map)

        # 地図表示（デスクトップサイズ固定）
        map_data = st_folium(
            submission_map,
            width=None,
            height=400,  # デスクトップサイズ固定
            returned_objects=["last_clicked"],
            key="submission_map_desktop"
        )

        # 地図クリック処理
        self._process_map_click(map_data, has_location)

        # 位置情報の表示
        self._show_location_status(has_location)

        # リセットボタン（デスクトップ固定）
        if has_location:
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                if st.button("🔄 位置をリセット", type="secondary"):
                    self._reset_location()

    def _reset_location(self):
        """位置情報のリセット"""
        st.session_state.submission_click_lat = None
        st.session_state.submission_click_lng = None
        st.session_state.auto_address = ""
        st.success("✅ 位置をリセットしました")
        st.rerun()

    def _get_current_location(self):
        """位置情報取得処理（改良版）"""
        st.info("📍 位置情報を取得中...")

        # より強化されたJavaScriptコード
        st.markdown("""
        <script>
        function getCurrentLocationForSubmission() {
            if (!navigator.geolocation) {
                alert('このブラウザは位置情報に対応していません');
                return;
            }
            
            const options = {
                enableHighAccuracy: true,
                timeout: 15000,
                maximumAge: 300000
            };
            
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    const accuracy = Math.round(position.coords.accuracy);
                    
                    // 成功メッセージを表示
                    const message = `位置情報を取得しました！\n緯度: ${lat.toFixed(6)}\n経度: ${lng.toFixed(6)}\n精度: 約${accuracy}m\n\n地図上でクリックして微調整できます。`;
                    alert(message);
                    
                    // 位置情報をStreamlitに送信
                    window.parent.postMessage({
                        type: 'geolocation_success',
                        latitude: lat,
                        longitude: lng,
                        accuracy: accuracy
                    }, '*');
                },
                function(error) {
                    let message = '位置情報の取得に失敗しました:\n';
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            message += '位置情報の使用が拒否されました。\nブラウザの設定で許可してください。';
                            break;
                        case error.POSITION_UNAVAILABLE:
                            message += '位置情報を取得できませんでした。\nGPSやWi-Fiの接続を確認してください。';
                            break;
                        case error.TIMEOUT:
                            message += '位置情報の取得がタイムアウトしました。\n再度お試しください。';
                            break;
                        default:
                            message += '不明なエラーが発生しました。';
                            break;
                    }
                    alert(message);
                },
                options
            );
        }
        
        // 即座に実行
        getCurrentLocationForSubmission();
        </script>
        """, unsafe_allow_html=True)

    def _process_map_click(self, map_data, current_has_location):
        """地図クリック処理"""
        if map_data.get('last_clicked') is not None:
            clicked_lat = map_data['last_clicked']['lat']
            clicked_lng = map_data['last_clicked']['lng']

            # 新しいクリックかどうかを判定
            is_new_click = (
                st.session_state.submission_click_lat is None or
                st.session_state.submission_click_lng is None or
                abs(clicked_lat - st.session_state.submission_click_lat) > 0.0001 or
                abs(clicked_lng - st.session_state.submission_click_lng) > 0.0001
            )

            if is_new_click:
                # セッション状態を更新
                st.session_state.submission_click_lat = clicked_lat
                st.session_state.submission_click_lng = clicked_lng

                # 少し待ってから画面更新
                import time
                time.sleep(0.5)
                st.rerun()

    def _show_location_status(self, has_location):
        """位置情報ステータス表示"""
        if has_location:
            st.success(
                f"📍 選択済み位置: 緯度 {st.session_state.submission_click_lat:.6f}, 経度 {st.session_state.submission_click_lng:.6f}")
        else:
            st.warning("⚠️ 地図をクリックまたは位置情報を取得して位置を指定してください")

    def _show_form_section(self):
        """フォームセクション表示（デスクトップ固定版）"""
        has_location = (st.session_state.submission_click_lat is not None and
                        st.session_state.submission_click_lng is not None)

        with st.form("submission_form"):
            st.markdown("### 📝 占い師情報を入力してください")

            # 基本情報（デスクトップレイアウト）
            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("占い師名 *", placeholder="例：渋谷占い館")
                category = st.selectbox("占いの種類", config.FORTUNE_CATEGORIES)
                contact = st.text_input("電話番号", placeholder="例：03-1234-5678")

            with col2:
                website = st.text_input(
                    "ウェブサイト", placeholder="例：https://example.com")
                submitted_by = st.text_input("投稿者名", placeholder="匿名可")

            # 住所情報（デスクトップレイアウト）
            zipcode, address = self._show_address_section()

            # 詳細説明
            description = st.text_area(
                "詳細説明",
                placeholder="占い師の特徴や得意分野を教えてください",
                height=100
            )

            st.markdown("---")

            # 位置確認
            st.markdown("#### 📍 登録位置の確認")
            if has_location:
                st.info(
                    f"📍 登録予定位置: 緯度 {st.session_state.submission_click_lat:.6f}, 経度 {st.session_state.submission_click_lng:.6f}")
            else:
                st.error("⚠️ まず地図上で位置を指定または位置情報を取得してください")

            # 送信ボタンと処理
            submitted = st.form_submit_button(
                "🔮 登録する", type="primary", use_container_width=True)

            if submitted:
                self._handle_form_submission(
                    name, category, contact, website, submitted_by,
                    description, zipcode, address, has_location
                )

    def _show_address_section(self):
        """住所入力セクション（デスクトップレイアウト）"""
        st.markdown("#### 📍 住所情報（任意）")

        address_col1, address_col2 = st.columns([2, 3])

        with address_col1:
            zipcode = st.text_input(
                "郵便番号",
                placeholder="例：1000001 または 100-0001"
            )

        with address_col2:
            address = st.text_input(
                "住所",
                value=st.session_state.auto_address,
                placeholder="例：東京都渋谷区神宮前1-1-1"
            )

        # 郵便番号検索ボタン
        if st.form_submit_button("📮 郵便番号から住所を取得", type="secondary"):
            if zipcode:
                with st.spinner("住所を検索中..."):
                    auto_address = self._search_address_from_zipcode(zipcode)
                    if auto_address:
                        st.session_state.auto_address = auto_address
                        st.success(f"✅ 住所を取得: {auto_address}")
                        st.rerun()
                    else:
                        st.error("❌ 住所が見つかりませんでした。郵便番号をご確認ください。")
            else:
                st.warning("⚠️ 郵便番号を入力してください")

        return zipcode, address

    def _handle_form_submission(self, name, category, contact, website,
                                submitted_by, description, zipcode, address, has_location):
        """フォーム送信処理"""
        # 入力チェック
        if not name:
            st.error("❌ 占い師名は必須項目です。")
            return

        if not has_location:
            st.error("❌ 地図上で位置を指定または位置情報を取得してください。")
            return

        # 座標の妥当性チェック
        if not self._validate_coordinates(
            st.session_state.submission_click_lat,
            st.session_state.submission_click_lng
        ):
            st.error("❌ 位置情報が不正です。")
            return

        # 郵便番号の形式チェック
        if zipcode and not self._validate_zipcode(zipcode):
            st.error("❌ 郵便番号の形式が正しくありません。7桁の数字または「123-4567」形式で入力してください。")
            return

        # データ作成
        fortuneteller_data = {
            'name': name.strip(),
            'latitude': st.session_state.submission_click_lat,
            'longitude': st.session_state.submission_click_lng,
            'description': description.strip(),
            'contact': contact.strip(),
            'website': website.strip() if website else None,
            'category': category,
            'submitted_by': submitted_by.strip() if submitted_by else "匿名",
            'zipcode': zipcode.strip() if zipcode else None,
            'address': address.strip() if address else None
        }

        # 保存処理
        try:
            if self.db.save_fortuneteller(fortuneteller_data):
                st.success("✅ 登録完了！管理者の承認をお待ちください。")
                st.balloons()  # お祝いアニメーション

                # 成功時のクリーンアップ
                self._clear_session_state()
                st.session_state.show_submission_form = False
                st.rerun()
            else:
                st.error("❌ 保存に失敗しました。もう一度お試しください。")
        except Exception as e:
            st.error(f"❌ エラーが発生しました: {str(e)}")

    def _show_close_section(self):
        """閉じるボタンセクション"""
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("✖ 閉じる", type="secondary", use_container_width=True):
                self._clear_session_state()
                st.session_state.show_submission_form = False
                st.rerun()

    def _clear_session_state(self):
        """セッション状態のクリア"""
        st.session_state.auto_address = ""
        st.session_state.submission_click_lat = None
        st.session_state.submission_click_lng = None

    def _search_address_from_zipcode(self, zipcode: str) -> str:
        """郵便番号から住所を検索（zipcloud API使用）"""
        try:
            # 郵便番号の正規化（ハイフンを除去）
            clean_zipcode = re.sub(r'[^\d]', '', zipcode)

            # zipcloud APIを呼び出し
            api_url = f"https://zipcloud.ibsnet.co.jp/api/search?zipcode={clean_zipcode}"
            response = requests.get(api_url, timeout=10)

            if response.status_code == 200:
                data = response.json()

                if data.get('status') == 200 and data.get('results'):
                    result = data['results'][0]
                    address = f"{result['address1']}{result['address2']}{result['address3']}"
                    return address

            return None

        except Exception as e:
            st.error(f"住所検索エラー: {str(e)}")
            return None

    def _validate_zipcode(self, zipcode: str) -> bool:
        """郵便番号の形式チェック（日本の郵便番号形式）"""
        pattern = r'^(\d{7}|\d{3}-\d{4})$'
        return bool(re.match(pattern, zipcode.strip()))

    def _validate_coordinates(self, lat: float, lng: float) -> bool:
        """座標の妥当性検証"""
        if lat is None or lng is None:
            return False
        return -90 <= lat <= 90 and -180 <= lng <= 180
