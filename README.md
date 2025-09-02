# 🔮 占い師マップアプリ

日本全国の占い師を地図で探せるWebアプリケーションです。

## ✨ 主な機能

- 🗺️ **インタラクティブ地図**: 占い師の位置をマップで表示
- 🔍 **検索・フィルター**: 占術カテゴリや地域での絞り込み
- ➕ **新規登録**: 占い師情報の投稿システム
- 👨‍💼 **管理者機能**: 投稿の承認・削除・管理
- 💼 **お仕事依頼**: 占い師への依頼システム
- 📊 **統計機能**: 登録状況の可視化

## 🎴 対応占術カテゴリ

- タロット
- 手相
- 占星術
- 四柱推命
- 姓名判断
- 風水
- 水晶玉
- 霊視
- 数秘術
- 易経
- ルーン
- その他

## 🚀 技術スタック

- **フレームワーク**: Streamlit
- **地図表示**: Folium + Streamlit-Folium
- **データベース**: SQLite
- **デプロイ**: Streamlit Cloud
- **言語**: Python 3.10+

## 📁 プロジェクト構成

```
fortune-teller-map/
├── app.py                 # メインアプリケーション
├── config.py             # 設定ファイル
├── database.py           # データベース管理
├── requirements.txt      # 依存関係
├── README.md            # このファイル
├── models/
│   ├── __init__.py
│   └── fortuneteller.py  # データモデル
├── pages/
│   ├── __init__.py
│   ├── admin.py         # 管理者画面
│   ├── submission.py    # 投稿フォーム
│   └── work_request.py  # お仕事依頼
└── ui/
    ├── __init__.py
    ├── components.py    # UI共通コンポーネント
    └── map_manager.py   # 地図管理
```

## 🛠️ ローカル実行方法

1. **リポジトリクローン**
   ```bash
   git clone https://github.com/your-username/fortune-teller-map.git
   cd fortune-teller-map
   ```

2. **依存関係インストール**
   ```bash
   pip install -r requirements.txt
   ```

3. **アプリケーション起動**
   ```bash
   streamlit run app.py
   ```

4. **ブラウザでアクセス**
   ```
   http://localhost:8501
   ```

## 🌐 デプロイ

このアプリはStreamlit Cloudで簡単にデプロイできます：

1. GitHubリポジトリを作成
2. Streamlit Cloudでアカウント作成
3. リポジトリを連携してデプロイ

## 🔐 管理者機能

デフォルト管理者パスワード: `admin123`
（初回ログイン後に必ず変更してください）

## 📝 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🤝 コントリビューション

プルリクエストや課題報告を歓迎します！

---

**開発者**: あなたの名前
**最終更新**: 2024年12月