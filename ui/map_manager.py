"""
地図管理クラス - カテゴリ別アイコン付きクラスタリング機能（紫色統一版）
各占術カテゴリごとに最適なアイコンを表示、色は紫色で統一
"""
import folium
from folium.plugins import MarkerCluster
import pandas as pd
from typing import Optional
import config


class MapManager:
    """地図表示を管理するクラス（カテゴリ別アイコン・紫色統一版）"""

    # 占術カテゴリ別アイコンマッピング
    CATEGORY_ICONS = {
        "タロット": "address-card",      # 🎴 カード（タロットカード）
        "手相": "hand-paper",           # ✋ 手のひら
        "占星術": "sun",                # ☀️ 太陽・星座
        "四柱推命": "yin-yang",          # ☯️ 陰陽マーク
        "姓名判断": "file-text",         # 📄 文書・名前
        "風水": "compass",              # 🧭 コンパス・方位
        "水晶玉": "gem",                # 💎 宝石・水晶
        "霊視": "eye",                  # 👁️ 目・透視
        "数秘術": "calculator",         # 🔢 計算機・数字
        "易経": "book",                 # 📖 本・古典
        "ルーン": "magic",              # 🪄 魔法杖・古代文字
        "その他": "question-circle"     # ❓ 未分類
    }

    @staticmethod
    def create_map(fortunetellers_df: pd.DataFrame,
                   highlight_id: Optional[int] = None,
                   selected_id: Optional[int] = None) -> folium.Map:
        """地図を作成（カテゴリ別アイコン・紫色統一版）"""
        center_lat = config.DEFAULT_CENTER_LAT
        center_lon = config.DEFAULT_CENTER_LON
        zoom_level = config.DEFAULT_ZOOM_LEVEL

        # ハイライトまたは選択された占い師がある場合、その位置を中心にする
        if (highlight_id or selected_id) and not fortunetellers_df.empty:
            target_id = selected_id if selected_id else highlight_id
            target_row = fortunetellers_df[fortunetellers_df['id'] == target_id]
            if not target_row.empty:
                center_lat = target_row.iloc[0]['latitude']
                center_lon = target_row.iloc[0]['longitude']
                zoom_level = config.DETAIL_ZOOM_LEVEL

        # 地図を作成
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom_level,
            tiles='OpenStreetMap'
        )

        if not fortunetellers_df.empty:
            # 占いテーマのクラスター設定（紫色統一）
            marker_cluster = MarkerCluster(
                name='占い師クラスター',
                overlay=True,
                control=True,
                icon_create_function="""
                function(cluster) {
                    var childCount = cluster.getChildCount();
                    var c = ' marker-cluster-';
                    if (childCount < 10) {
                        c += 'small';
                    } else if (childCount < 100) {
                        c += 'medium';
                    } else {
                        c += 'large';
                    }
                    
                    return new L.DivIcon({ 
                        html: '<div><span>🔮<br>' + childCount + '</span></div>', 
                        className: 'marker-cluster' + c, 
                        iconSize: new L.Point(50, 50),
                        iconAnchor: [25, 25]
                    });
                }
                """,
                options={
                    'showCoverageOnHover': True,
                    'zoomToBoundsOnClick': True,
                    'spiderfyOnMaxZoom': True,
                    'removeOutsideVisibleBounds': True,
                    'disableClusteringAtZoom': 15  # ズーム15以上では個別マーカー表示
                }
            )

            # 特別なマーカー（選択・ハイライト）は個別に追加
            special_ids = set()
            if selected_id:
                special_ids.add(selected_id)
            if highlight_id:
                special_ids.add(highlight_id)

            # 通常マーカーをクラスターに追加
            for idx, row in fortunetellers_df.iterrows():
                if row['id'] in special_ids:
                    continue  # 特別なマーカーは後で個別に追加

                # 通常マーカーの作成（紫色統一）
                marker = MapManager._create_normal_marker(row)
                marker_cluster.add_child(marker)

            # クラスターを地図に追加
            marker_cluster.add_to(m)

            # 特別なマーカー（選択・ハイライト）を個別に追加
            for idx, row in fortunetellers_df.iterrows():
                if row['id'] in special_ids:
                    special_marker = MapManager._create_special_marker(
                        row, selected_id, highlight_id
                    )
                    special_marker.add_to(m)

        # 占いテーマのクラスタースタイルを追加
        MapManager._add_fortune_cluster_style(m)

        return m

    @staticmethod
    def _get_icon_for_category(category: str):
        """カテゴリに応じたアイコンを取得"""
        return MapManager.CATEGORY_ICONS.get(category, "question-circle")

    @staticmethod
    def _create_normal_marker(row):
        """通常マーカーを作成（紫色統一・カテゴリ別アイコン）"""
        # カテゴリに応じたアイコンを取得
        icon_symbol = MapManager._get_icon_for_category(
            row.get('category', 'その他'))

        # ツールチップ（ホバー時）
        tooltip_html = MapManager._create_tooltip_html(row)

        # ポップアップ（クリック時）
        popup_html = MapManager._create_popup_html(row)

        marker = folium.Marker(
            [row['latitude'], row['longitude']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=folium.Tooltip(tooltip_html, permanent=False, sticky=True),
            icon=folium.Icon(
                color='purple',  # 紫色で統一
                icon=icon_symbol,
                prefix='fa'
            )
        )

        return marker

    @staticmethod
    def _create_special_marker(row, selected_id, highlight_id):
        """特別なマーカー（選択・ハイライト）を作成"""
        # カテゴリに応じたアイコンを取得
        icon_symbol = MapManager._get_icon_for_category(
            row.get('category', 'その他'))

        # アイコンの色設定（紫色ベース）
        if selected_id and row['id'] == selected_id:
            icon_color = 'green'        # 選択時は緑色
        elif highlight_id and row['id'] == highlight_id:
            icon_color = 'red'          # ハイライト時は赤色
        else:
            icon_color = 'purple'       # 通常は紫色

        # ツールチップ（ホバー時）
        tooltip_html = MapManager._create_tooltip_html(row)

        # ポップアップ（クリック時）
        popup_html = MapManager._create_popup_html(row)

        marker = folium.Marker(
            [row['latitude'], row['longitude']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=folium.Tooltip(tooltip_html, permanent=False, sticky=True),
            icon=folium.Icon(
                color=icon_color,
                icon=icon_symbol,
                prefix='fa'
            )
        )

        return marker

    @staticmethod
    def _add_fortune_cluster_style(m):
        """占いテーマのクラスタースタイルを追加（紫色統一）"""
        cluster_style = """
        <style>
        .marker-cluster-small {
            background-color: rgba(139, 79, 159, 0.7);
            border: 3px solid rgba(186, 85, 211, 0.8);
        }
        .marker-cluster-small div {
            background-color: rgba(139, 79, 159, 0.8);
            color: white;
            font-weight: bold;
        }
        
        .marker-cluster-medium {
            background-color: rgba(139, 79, 159, 0.8);
            border: 3px solid rgba(186, 85, 211, 0.9);
        }
        .marker-cluster-medium div {
            background-color: rgba(139, 79, 159, 0.9);
            color: white;
            font-weight: bold;
        }
        
        .marker-cluster-large {
            background-color: rgba(139, 79, 159, 1.0);
            border: 3px solid rgba(186, 85, 211, 1.0);
        }
        .marker-cluster-large div {
            background-color: rgba(139, 79, 159, 1.0);
            color: white;
            font-weight: bold;
        }
        
        .marker-cluster {
            background-clip: padding-box;
            border-radius: 25px;
            box-shadow: 0 3px 8px rgba(139, 79, 159, 0.5);
        }
        .marker-cluster div {
            width: 40px;
            height: 40px;
            margin-left: 5px;
            margin-top: 5px;
            text-align: center;
            border-radius: 20px;
            font: 11px "Helvetica Neue", Arial, Helvetica, sans-serif;
            line-height: 1.2;
        }
        .marker-cluster span {
            line-height: 1.2;
            color: #fff;
            font-weight: bold;
            display: block;
            padding-top: 3px;
        }
        </style>
        """

        m.get_root().html.add_child(folium.Element(cluster_style))

    @staticmethod
    def _create_tooltip_html(row) -> str:
        """ツールチップHTML作成（占いテーマ・紫色統一・住所対応）"""
        description = row.get('description', '説明なし')
        contact = row.get('contact', '連絡先なし')
        category = row.get('category', '未設定')
        address = row.get('address', '')

        # カテゴリに応じた絵文字
        category_emoji = {
            "タロット": "🎴",
            "手相": "✋",
            "占星術": "⭐",
            "四柱推命": "☯️",
            "姓名判断": "📝",
            "風水": "🧭",
            "水晶玉": "🔮",
            "霊視": "👁️",
            "数秘術": "🔢",
            "易経": "📖",
            "ルーン": "🗿",
            "その他": "❓"
        }.get(category, "🔮")

        # 住所情報がある場合は表示
        address_html = ""
        if address:
            address_display = address[:30] + \
                '...' if len(address) > 30 else address
            address_html = f"""
            <div style="font-size: 11px; margin-top: 5px; color: #c8e6c9;">
                📍 {address_display}
            </div>
            """

        return f"""
        <div style="
            background-color: rgba(139, 79, 159, 0.95);
            color: white;
            padding: 12px;
            border-radius: 10px;
            font-family: sans-serif;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            min-width: 220px;
        ">
            <div style="font-size: 17px; font-weight: bold; margin-bottom: 8px;">
                {category_emoji} {row['name']}
            </div>
            <div style="font-size: 14px; margin-bottom: 5px;">
                <b>占術:</b> {category}
            </div>
            <div style="font-size: 13px; line-height: 1.4; margin-bottom: 6px;">
                {description[:50]}{'...' if len(description) > 50 else ''}
            </div>
            <div style="font-size: 12px; margin-top: 8px; color: #ffeb3b;">
                📞 {contact}
            </div>
            {address_html}
            <hr style="margin: 8px 0; opacity: 0.3;">
            <div style="font-size: 11px; color: #e0e0e0;">
                クリックで詳細パネル表示
            </div>
        </div>
        """

    @staticmethod
    def _create_popup_html(row) -> str:
        """ポップアップHTML作成（占いテーマ・紫色統一・住所対応・ナビ機能付き）"""
        description = row.get('description', '説明なし')
        contact = row.get('contact', '連絡先なし')
        submitted_by = row.get('submitted_by', '不明')
        category = row.get('category', '未設定')
        zipcode = row.get('zipcode', '')
        address = row.get('address', '')

        # 座標取得
        lat = row['latitude']
        lng = row['longitude']

        # カテゴリに応じた絵文字
        category_emoji = {
            "タロット": "🎴",
            "手相": "✋",
            "占星術": "⭐",
            "四柱推命": "☯️",
            "姓名判断": "📝",
            "風水": "🧭",
            "水晶玉": "🔮",
            "霊視": "👁️",
            "数秘術": "🔢",
            "易経": "📖",
            "ルーン": "🗿",
            "その他": "❓"
        }.get(category, "🔮")

        # 住所情報がある場合は表示
        address_html = ""
        if zipcode or address:
            address_parts = []
            if zipcode:
                address_parts.append(f"〒{zipcode}")
            if address:
                address_parts.append(address)
            address_display = " ".join(address_parts)
            address_html = f'<p style="margin: 6px 0;"><b>住所:</b> {address_display}</p>'

        # ナビゲーションリンク生成
        import urllib.parse
        encoded_name = urllib.parse.quote(row['name'])
        google_link = f"https://maps.google.com/maps?q={lat},{lng}({encoded_name})"
        yahoo_link = f"https://map.yahoo.co.jp/place?lat={lat}&lon={lng}&zoom=16&maptype=basic"

        return f"""
        <div style="width: 320px; font-family: sans-serif;">
            <h4 style="color: {config.PRIMARY_COLOR}; margin: 8px 0;">{category_emoji} {row['name']}</h4>
            <hr style="margin: 8px 0;">
            <p style="margin: 6px 0;"><b>占術:</b> {category}</p>
            <p style="margin: 6px 0;"><b>特徴:</b> {description}</p>
            <p style="margin: 6px 0;"><b>連絡先:</b> {contact}</p>
            {address_html}
            
            <!-- ナビボタン追加 -->
            <div style="margin: 10px 0; text-align: center;">
                <p style="margin: 5px 0; font-size: 13px; font-weight: bold; color: {config.PRIMARY_COLOR};">🧭 ナビで道案内</p>
                <div style="display: flex; gap: 8px; justify-content: center;">
                    <a href="{google_link}" target="_blank" style="
                        background: #4285F4; color: white; padding: 6px 10px; 
                        border-radius: 4px; text-decoration: none; font-size: 11px; flex: 1; text-align: center;
                    ">Google Maps</a>
                    <a href="{yahoo_link}" target="_blank" style="
                        background: #FF0033; color: white; padding: 6px 10px; 
                        border-radius: 4px; text-decoration: none; font-size: 11px; flex: 1; text-align: center;
                    ">Yahoo! Map</a>
                </div>
            </div>
            
            <p style="margin: 6px 0; font-size: 12px; color: #666;">
                ID: {row['id']} | 投稿者: {submitted_by}
            </p>
            <hr style="margin: 8px 0;">
            <p style="font-size: 12px; color: {config.PRIMARY_COLOR};">
                下の詳細パネルで電話やウェブサイトにアクセスできます
            </p>
        </div>
        """
