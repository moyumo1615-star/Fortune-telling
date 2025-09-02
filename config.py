"""
設定ファイル
アプリケーション全体で使用する設定値を管理
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
    "✨ 口コミ機能を近日公開予定"
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
