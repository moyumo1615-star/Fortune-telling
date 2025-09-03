"""
設定ファイル
アプリケーション全体で使用する設定値を管理
スマホ・タブレット対応版
"""
import os

# データベース設定
DATABASE_PATH = "fortuneteller.db"

# 管理者設定（本番対応）
# 環境変数からパスワードを取得、なければデフォルト値
DEFAULT_ADMIN_PASSWORD = "admin123"  # 初回起動時のデフォルトパスワード

# 地図設定
DEFAULT_CENTER_LAT = 35.6762  # 東京の緯度
DEFAULT_CENTER_LON = 139.6503  # 東京の経度
DEFAULT_ZOOM_LEVEL = 6
DETAIL_ZOOM_LEVEL = 14

# レスポンシブデザイン設定（新規追加）
MOBILE_BREAKPOINT = 768   # モバイル判定の幅（px）
TABLET_BREAKPOINT = 1024  # タブレット判定の幅（px）

# 占いカテゴリ
FORTUNE_CATEGORIES = [
    "タロット",
    "手相",
    "占星術",
    "四柱推命",
    "姓名判断",
    "風水",
    "水晶玉",
    "霊視",
    "数秘術",
    "易経",
    "ルーン",
    "その他"
]

# デフォルトお知らせ
DEFAULT_ANNOUNCEMENTS = [
    "🌟 新機能：詳細パネルで電話・ウェブサイトにアクセス可能",
    "🔮 占い師情報を募集中！",
    "✨ 口コミ機能を近日公開予定",
    "📱 スマホ・タブレットでも快適にご利用いただけます"
]

# デフォルトメールアドレス
DEFAULT_CONTACT_EMAIL = "admin@fortune-teller-map.com"

# UIカラー設定
PRIMARY_COLOR = "#8b4f9f"  # 紫色（占いのイメージカラー）

# ページ設定
PAGE_TITLE = "占いマップ"
PAGE_ICON = "🔮"

# セキュリティ設定
PASSWORD_MIN_LENGTH = 8  # パスワード最小文字数
PASSWORD_HISTORY_LIMIT = 5  # 過去のパスワード履歴保存数

# レスポンシブデザイン用CSSテンプレート（重要：この部分が追加されました）
RESPONSIVE_CSS = """
<style>
/* 基本設定 - 余白を大幅削減 */
.main {{ 
    padding: 0 !important; 
    margin: 0 !important;
}}
.block-container {{
    padding: 0.5rem !important;
    max-width: 100%;
    margin-top: 0 !important;
    padding-top: 0.5rem !important;
}}

/* ヘッダー余白削減 */
h1 {{
    color: {primary_color};
    font-size: 28px !important;
    margin-bottom: 5px !important;
    margin-top: 0 !important;
    padding-top: 0 !important;
}}

/* ★★★ ボタン共通 - 全て紫色に強制統一（最強版）★★★ */
div[data-testid="stButton"] > button,
.stButton > button,
.stButton button,
button[kind="primary"],
button[kind="secondary"],
button[data-testid="baseButton-primary"],
button[data-testid="baseButton-secondary"],
.element-container button,
.main button,
button,
input[type="submit"],
.st-emotion-cache-1x8cf1d > button,
.st-emotion-cache-19ih6ej > button,
.st-emotion-cache-12fmjuu > button,
.st-emotion-cache-5rimss > button,
[data-baseweb="button"],
[role="button"] {{
    background-color: {primary_color} !important;
    background: linear-gradient(45deg, {primary_color}, #a855f7) !important;
    color: white !important;
    border: 2px solid {primary_color} !important;
    border-radius: 10px !important;
    width: 100% !important;
    padding: 0.6rem 1rem !important;
    font-weight: 600 !important;
    font-size: 16px !important;
    cursor: pointer !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    margin: 4px 0 !important;
    min-height: 44px !important;
    box-shadow: 0 4px 8px rgba(139, 79, 159, 0.25) !important;
    text-decoration: none !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}}

/* ホバー効果 - 紫色統一 */
div[data-testid="stButton"] > button:hover,
.stButton > button:hover,
.stButton button:hover,
button[kind="primary"]:hover,
button[kind="secondary"]:hover,
button[data-testid="baseButton-primary"]:hover,
button[data-testid="baseButton-secondary"]:hover,
.element-container button:hover,
.main button:hover,
button:hover,
input[type="submit"]:hover,
.st-emotion-cache-1x8cf1d > button:hover,
.st-emotion-cache-19ih6ej > button:hover,
.st-emotion-cache-12fmjuu > button:hover,
.st-emotion-cache-5rimss > button:hover,
[data-baseweb="button"]:hover,
[role="button"]:hover {{
    background-color: #6a3d7a !important;
    background: linear-gradient(45deg, #6a3d7a, #7c3aed) !important;
    border-color: #6a3d7a !important;
    color: white !important;
    box-shadow: 0 8px 16px rgba(139, 79, 159, 0.4) !important;
    transform: translateY(-2px) scale(1.02) !important;
}}

/* フォーカス効果 - 紫色統一 */
div[data-testid="stButton"] > button:focus,
.stButton > button:focus,
.stButton button:focus,
button:focus,
[data-baseweb="button"]:focus,
[role="button"]:focus {{
    background-color: #6a3d7a !important;
    border-color: #6a3d7a !important;
    color: white !important;
    box-shadow: 0 0 0 3px rgba(139, 79, 159, 0.5) !important;
    outline: none !important;
}}

/* アクティブ効果 - 紫色統一 */
div[data-testid="stButton"] > button:active,
.stButton > button:active,
.stButton button:active,
button:active {{
    transform: translateY(0px) scale(0.98) !important;
    box-shadow: 0 2px 4px rgba(139, 79, 159, 0.3) !important;
}}

/* プライマリボタン特別指定 */
div[data-testid="stButton"] > button[kind="primary"],
button[kind="primary"] {{
    background: linear-gradient(135deg, {primary_color}, #a855f7) !important;
    border: 2px solid {primary_color} !important;
    color: white !important;
    font-weight: bold !important;
    box-shadow: 0 6px 12px rgba(139, 79, 159, 0.3) !important;
}}

/* セカンダリボタンも紫色に統一 */
div[data-testid="stButton"] > button[kind="secondary"],
button[kind="secondary"] {{
    background: linear-gradient(45deg, {primary_color}, #9333ea) !important;
    border: 2px solid {primary_color} !important;
    color: white !important;
}}

/* 詳細パネル */
.detail-panel {{
    background: linear-gradient(135deg, #f5ebff 0%, #ffffff 100%);
    padding: 20px;
    border-radius: 10px;
    border: 2px solid {primary_color};
    margin-top: 10px;
}}

/* リンク */
.clickable-link {{
    color: {primary_color};
    text-decoration: none;
    font-weight: bold;
}}
.clickable-link:hover {{
    text-decoration: underline;
}}

/* アクションボタン専用クラス */
.action-button,
.purple-action-button {{
    background: linear-gradient(135deg, {primary_color} 0%, #a855f7 50%, #c084fc 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    font-weight: bold !important;
    font-size: 18px !important;
    cursor: pointer !important;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    width: 100% !important;
    margin: 12px 0 !important;
    min-height: 54px !important;
    box-shadow: 0 10px 20px rgba(139, 79, 159, 0.35) !important;
    text-decoration: none !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    position: relative !important;
    overflow: hidden !important;
}}

.action-button::before,
.purple-action-button::before {{
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    transition: left 0.5s;
}}

.action-button:hover::before,
.purple-action-button:hover::before {{
    left: 100%;
}}

.action-button:hover,
.purple-action-button:hover {{
    background: linear-gradient(135deg, #6a3d7a 0%, #7c3aed 50%, #a855f7 100%) !important;
    box-shadow: 0 15px 25px rgba(139, 79, 159, 0.5) !important;
    transform: translateY(-4px) scale(1.05) !important;
}}

.action-button:active,
.purple-action-button:active {{
    transform: translateY(-1px) scale(1.02) !important;
    box-shadow: 0 5px 10px rgba(139, 79, 159, 0.4) !important;
}}

/* タブレット対応 (768px〜1024px) */
@media screen and (min-width: 768px) and (max-width: 1024px) {{
    .block-container {{
        padding: 0.5rem !important;
        padding-top: 0.5rem !important;
    }}
    
    h1 {{
        font-size: 24px !important;
        margin-bottom: 5px !important;
        margin-top: 0 !important;
    }}
    
    /* 地図の高さを調整 */
    .folium-map {{
        height: 400px !important;
    }}
    
    /* ボタンを少し小さく - でも紫色統一 */
    div[data-testid="stButton"] > button,
    .stButton > button,
    button {{
        padding: 0.5rem 1rem !important;
        font-size: 15px !important;
        background-color: {primary_color} !important;
        color: white !important;
        min-height: 42px !important;
    }}
    
    /* フォームの列幅調整 */
    .row-widget.stHorizontal {{
        flex-wrap: wrap;
    }}
}}

/* スマートフォン対応 (〜768px) */
@media screen and (max-width: 767px) {{
    /* 全体のパディング調整 - さらに削減 */
    .block-container {{
        padding: 0.25rem !important;
        padding-top: 0.25rem !important;
        margin-top: 0 !important;
    }}
    
    /* ヘッダーサイズ調整 */
    h1 {{
        font-size: 20px !important;
        text-align: center;
        margin-bottom: 5px !important;
        margin-top: 0 !important;
        padding-top: 0 !important;
    }}
    
    h2 {{
        font-size: 18px !important;
        margin-top: 5px !important;
        margin-bottom: 5px !important;
    }}
    
    h3 {{
        font-size: 16px !important;
        margin-top: 5px !important;
        margin-bottom: 5px !important;
    }}
    
    /* 地図の高さを小さく */
    .folium-map {{
        height: 300px !important;
    }}
    
    /* ボタンをフル幅に - 紫色強制統一 */
    div[data-testid="stButton"] > button,
    .stButton > button,
    .stButton button,
    button,
    [data-baseweb="button"],
    [role="button"] {{
        width: 100% !important;
        padding: 0.75rem !important;
        font-size: 16px !important;
        margin-bottom: 10px !important;
        min-height: 50px !important;
        background-color: {primary_color} !important;
        background: linear-gradient(45deg, {primary_color}, #a855f7) !important;
        color: white !important;
        border: 2px solid {primary_color} !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }}
    
    /* モバイル専用アクションボタン */
    .action-button,
    .purple-action-button {{
        padding: 18px 16px !important;
        font-size: 18px !important;
        min-height: 56px !important;
        margin: 14px 0 !important;
        border-radius: 14px !important;
    }}
    
    /* 列レイアウトを縦並びに */
    .row-widget.stHorizontal {{
        flex-direction: column !important;
    }}
    
    .row-widget.stHorizontal > div {{
        width: 100% !important;
        margin-bottom: 10px;
    }}
    
    /* 入力フィールドの調整 */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea,
    .stSelectbox>div>div>select {{
        font-size: 16px;
        padding: 12px;
    }}
    
    /* メトリクスを小さく */
    [data-testid="metric-container"] {{
        padding: 8px;
        margin: 4px 0;
    }}
    
    /* 詳細パネルの調整 */
    .detail-panel {{
        padding: 15px;
        margin: 10px 0;
    }}
    
    /* エキスパンダーの調整 */
    .streamlit-expanderHeader {{
        font-size: 14px !important;
    }}
    
    /* フォームの間隔調整 */
    .stForm {{
        padding: 15px;
    }}
    
    /* ナビゲーションボタンの調整 - 紫色統一 */
    .nav-button {{
        padding: 12px !important;
        margin: 4px 0 !important;
        font-size: 14px !important;
        background-color: {primary_color} !important;
        color: white !important;
        min-height: 48px !important;
    }}
}}

/* 極小画面対応 (〜480px) */
@media screen and (max-width: 480px) {{
    .block-container {{
        padding: 0.125rem !important;
        padding-top: 0.125rem !important;
        margin-top: 0 !important;
    }}
    
    h1 {{
        font-size: 18px !important;
        margin-bottom: 3px !important;
        margin-top: 0 !important;
    }}
    
    .folium-map {{
        height: 250px !important;
    }}
    
    div[data-testid="stButton"] > button,
    .stButton > button,
    button {{
        padding: 0.75rem !important;
        font-size: 15px !important;
        background-color: {primary_color} !important;
        color: white !important;
        min-height: 48px !important;
    }}
    
    .detail-panel {{
        padding: 10px;
    }}
    
    /* テーブルをスクロール可能に */
    .dataframe {{
        font-size: 12px;
        overflow-x: auto;
    }}
    
    /* アクションボタンをさらに大きく */
    .action-button,
    .purple-action-button {{
        padding: 20px 16px !important;
        font-size: 17px !important;
        min-height: 60px !important;
        margin: 16px 0 !important;
    }}
}}

/* タッチデバイス対応 */
@media (hover: none) and (pointer: coarse) {{
    /* タッチ用のボタンサイズ - 紫色統一 */
    div[data-testid="stButton"] > button,
    .stButton > button,
    button,
    [data-baseweb="button"],
    [role="button"] {{
        min-height: 48px !important;
        min-width: 48px !important;
        background-color: {primary_color} !important;
        color: white !important;
        padding: 12px !important;
        font-size: 16px !important;
    }}
    
    /* タップ領域の拡大 */
    .clickable-link {{
        padding: 12px;
        display: inline-block;
        min-height: 48px;
        line-height: 24px;
    }}
    
    /* フォーカス状態の改善 */
    div[data-testid="stButton"] > button:focus,
    .stButton > button:focus,
    button:focus {{
        outline: 3px solid {primary_color};
        outline-offset: 2px;
    }}
    
    /* タッチ専用アクションボタン */
    .action-button,
    .purple-action-button {{
        min-height: 56px !important;
        padding: 16px 20px !important;
        font-size: 18px !important;
        margin: 12px 0 !important;
    }}
}}

/* 横向き対応（スマホを横にした場合） */
@media screen and (max-width: 896px) and (orientation: landscape) {{
    .folium-map {{
        height: 200px !important;
    }}
    
    .block-container {{
        padding: 0.25rem !important;
        padding-top: 0.25rem !important;
    }}
    
    div[data-testid="stButton"] > button,
    .stButton > button,
    button {{
        background-color: {primary_color} !important;
        color: white !important;
    }}
}}

/* ダークモード対応（システム設定に応じて） */
@media (prefers-color-scheme: dark) {{
    .detail-panel {{
        background: linear-gradient(135deg, #2d1b3d 0%, #1a1a1a 100%);
        color: #ffffff;
        border-color: #8b4f9f;
    }}
    
    .clickable-link {{
        color: #a855f7;
    }}
    
    /* ダークモードでもボタンは紫色統一 */
    div[data-testid="stButton"] > button,
    .stButton > button,
    button {{
        background-color: {primary_color} !important;
        color: white !important;
    }}
}}

/* 印刷時の最適化 */
@media print {{
    .stButton,
    .stTextInput,
    .stSelectbox {{
        display: none !important;
    }}
    
    .folium-map {{
        height: 400px !important;
    }}
    
    /* 印刷時はボタンを非表示 */
    div[data-testid="stButton"],
    .action-button,
    .purple-action-button {{
        display: none !important;
    }}
}}

/* 高コントラスト対応 */
@media (prefers-contrast: high) {{
    div[data-testid="stButton"] > button,
    .stButton > button,
    button,
    .action-button,
    .purple-action-button {{
        border-width: 3px !important;
        font-weight: bold !important;
        background-color: {primary_color} !important;
        color: white !important;
    }}
}}

/* アニメーション無効化対応 */
@media (prefers-reduced-motion: reduce) {{
    div[data-testid="stButton"] > button,
    .stButton > button,
    button,
    .action-button,
    .purple-action-button {{
        transition: none !important;
        transform: none !important;
    }}
    
    .action-button::before,
    .purple-action-button::before {{
        display: none !important;
    }}
}}
</style>
"""
