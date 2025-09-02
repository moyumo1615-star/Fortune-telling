"""
管理者画面
占い師の承認、削除、サイト設定、パスワード変更、統計情報などを管理
削除機能・パスワード変更機能追加版
"""
import streamlit as st
import json
import config
import pandas as pd
from datetime import datetime


class AdminPage:
    """管理者ページクラス（削除機能・パスワード変更追加版）"""

    def __init__(self, db):
        self.db = db

    def show(self):
        """管理者パネル表示"""
        st.header("👨‍💼 管理者パネル")

        # 認証チェック
        if not st.session_state.get('admin_authenticated', False):
            self._show_login()
            return

        # ログアウトボタン
        col1, col2 = st.columns([6, 1])
        with col2:
            if st.button("🚪 ログアウト"):
                st.session_state.admin_authenticated = False
                st.rerun()

        # タブ表示
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
            ["📋 承認待ち", "✅ 承認済み", "🗑️ 削除済み", "⚙️ サイト設定",
                "💼 お仕事依頼", "📊 統計", "🔐 パスワード変更"]
        )

        with tab1:
            self._show_pending_submissions()

        with tab2:
            self._show_approved_submissions()

        with tab3:
            self._show_deleted_submissions()

        with tab4:
            self._show_site_settings()

        with tab5:
            self._show_work_requests()

        with tab6:
            self._show_statistics()

        with tab7:
            self._show_password_change()

    def _show_login(self):
        """ログイン画面"""
        st.markdown("### 🔐 管理者ログイン")

        password = st.text_input(
            "管理者パスワード", type="password", key="admin_login_password")

        if st.button("🔓 ログイン", type="primary"):
            if self.db.verify_admin_password(password):
                st.session_state.admin_authenticated = True
                st.success("✅ ログインしました")
                st.rerun()
            else:
                st.error("❌ パスワードが間違っています")

    def _show_pending_submissions(self):
        """承認待ち表示（削除ボタン追加版）"""
        st.subheader("📋 承認待ち一覧")

        # 削除確認状態をチェック
        delete_confirm_key = "delete_confirm_pending"
        if st.session_state.get(delete_confirm_key):
            self._handle_delete_confirmation(delete_confirm_key)
            return

        pending_df = self.db.get_fortunetellers("pending")
        if not pending_df.empty:
            for idx, row in pending_df.iterrows():
                with st.expander(f"🔮 {row['name']} (ID: {row['id']})"):
                    self._show_fortuneteller_details(row)

                    # アクションボタン
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("✅ 承認", key=f"approve_{row['id']}"):
                            if self.db.update_status(row['id'], "approved", "管理者"):
                                st.success("✅ 承認しました")
                                st.rerun()
                    with col2:
                        if st.button("❌ 却下", key=f"reject_{row['id']}"):
                            if self.db.update_status(row['id'], "rejected", "管理者"):
                                st.warning("❌ 却下しました")
                                st.rerun()
                    with col3:
                        if st.button("🗑️ 削除", key=f"delete_pending_{row['id']}", type="secondary"):
                            # 削除確認状態を設定
                            st.session_state[delete_confirm_key] = {
                                'id': row['id'],
                                'name': row['name'],
                                'tab': 'pending'
                            }
                            st.rerun()
        else:
            st.info("📝 承認待ちの投稿はありません")

    def _show_approved_submissions(self):
        """承認済み一覧表示（削除ボタン付き）"""
        st.subheader("✅ 承認済み一覧")

        # 削除確認状態をチェック
        delete_confirm_key = "delete_confirm_approved"
        if st.session_state.get(delete_confirm_key):
            self._handle_delete_confirmation(delete_confirm_key)
            return

        approved_df = self.db.get_fortunetellers("approved")
        if not approved_df.empty:
            # 検索フィルター
            col1, col2 = st.columns([3, 1])
            with col1:
                search_term = st.text_input(
                    "🔍 検索（名前・カテゴリ・住所）", key="approved_search")
            with col2:
                category_filter = st.selectbox(
                    "カテゴリフィルター", ["すべて"] + config.FORTUNE_CATEGORIES, key="approved_category")

            # フィルター適用
            filtered_df = approved_df
            if search_term:
                filtered_df = filtered_df[
                    filtered_df['name'].str.contains(search_term, na=False) |
                    filtered_df['category'].str.contains(search_term, na=False) |
                    filtered_df['address'].str.contains(search_term, na=False)
                ]
            if category_filter != "すべて":
                filtered_df = filtered_df[filtered_df['category']
                                          == category_filter]

            st.markdown(
                f"**表示件数: {len(filtered_df)}件 / 全{len(approved_df)}件**")

            for idx, row in filtered_df.iterrows():
                with st.expander(f"✅ {row['name']} (ID: {row['id']}) - {row.get('category', '未設定')}"):
                    self._show_fortuneteller_details(row)

                    # 承認情報
                    st.markdown("**📋 承認情報**")
                    st.write(f"承認者: {row.get('approved_by', '不明')}")
                    st.write(f"承認日時: {row.get('approved_at', '不明')}")

                    # 削除ボタン
                    col1, col2 = st.columns([4, 1])
                    with col2:
                        if st.button("🗑️ 削除", key=f"delete_approved_{row['id']}", type="secondary"):
                            # 削除確認状態を設定
                            st.session_state[delete_confirm_key] = {
                                'id': row['id'],
                                'name': row['name'],
                                'tab': 'approved'
                            }
                            st.rerun()
        else:
            st.info("✅ 承認済みの投稿はありません")

    def _show_deleted_submissions(self):
        """削除済み一覧表示（完全なDOM競合回避版）"""
        st.subheader("🗑️ 削除済み一覧")

        # 完全削除確認状態をチェック
        permanent_delete_key = "permanent_delete_confirm"
        if st.session_state.get(permanent_delete_key):
            self._handle_permanent_delete_confirmation(permanent_delete_key)
            return

        deleted_df = self.db.get_deleted_fortunetellers()
        if not deleted_df.empty:
            st.warning(f"⚠️ 削除済みレコード: {len(deleted_df)}件")

            # チェックボックス用のセッション状態を初期化
            if 'selected_for_permanent_delete' not in st.session_state:
                st.session_state.selected_for_permanent_delete = set()

            # 無効なIDを削除
            valid_ids = set(deleted_df['id'].tolist())
            st.session_state.selected_for_permanent_delete = st.session_state.selected_for_permanent_delete.intersection(
                valid_ids)

            # 現在の選択件数を計算
            selected_count = len(
                st.session_state.selected_for_permanent_delete)

            # 全選択/全解除ボタン（エラー回避版）
            col1, col2, col3, col4 = st.columns([2, 2, 3, 3])

            with col1:
                if st.button("☑️ 全選択", key="select_all_deleted"):
                    try:
                        st.session_state.selected_for_permanent_delete = set(
                            deleted_df['id'].tolist())
                        st.success(f"✅ {len(deleted_df)}件を選択しました")
                        import time
                        time.sleep(0.5)  # DOM競合回避のため短い待機
                        st.rerun()
                    except Exception as e:
                        st.error(f"全選択でエラーが発生しました: {str(e)}")
                        st.session_state.selected_for_permanent_delete = set()

            with col2:
                if st.button("☐ 全解除", key="deselect_all_deleted"):
                    try:
                        st.session_state.selected_for_permanent_delete = set()
                        st.info("✅ 選択を解除しました")
                        import time
                        time.sleep(0.5)  # DOM競合回避のため短い待機
                        st.rerun()
                    except Exception as e:
                        st.error(f"全解除でエラーが発生しました: {str(e)}")
                        st.session_state.selected_for_permanent_delete = set()

            with col3:
                if selected_count > 0:
                    if st.button(f"💀 完全削除 ({selected_count}件)", key="permanent_delete_selected", type="primary"):
                        try:
                            selected_ids = list(
                                st.session_state.selected_for_permanent_delete)
                            selected_names = []
                            for row_id in selected_ids:
                                row = deleted_df[deleted_df['id'] == row_id]
                                if not row.empty:
                                    selected_names.append(row.iloc[0]['name'])

                            st.session_state[permanent_delete_key] = {
                                'ids': selected_ids,
                                'names': selected_names,
                                'count': selected_count
                            }
                            import time
                            time.sleep(0.5)  # DOM競合回避のため短い待機
                            st.rerun()
                        except Exception as e:
                            st.error(f"完全削除の準備でエラーが発生しました: {str(e)}")
                            # エラー時はセッション状態をリセット
                            if permanent_delete_key in st.session_state:
                                del st.session_state[permanent_delete_key]
                else:
                    st.button("💀 完全削除 (0件)",
                              key="permanent_delete_disabled", disabled=True)

            with col4:
                st.info(f"選択中: {selected_count}件")

            # 危険性の警告
            if selected_count > 0:
                st.error("⚠️ **完全削除警告**: 選択されたデータは完全に削除され、復元できません！")

            st.markdown("---")
            st.markdown("### 📋 削除済みアイテム一覧")

            # フォームを使用して安全なチェックボックス処理を実現
            with st.form("permanent_delete_selection_form", clear_on_submit=False):
                st.markdown("**💡 ヒント**: チェックボックスを変更した後、「選択を更新」ボタンをクリックしてください")

                # 一時的な選択状態を保持
                temp_selection = set()

                for idx, row in deleted_df.iterrows():
                    # 現在の選択状態
                    is_currently_selected = row['id'] in st.session_state.selected_for_permanent_delete

                    # チェックボックス（フォーム内で安全）
                    checkbox_key = f"temp_checkbox_{row['id']}"
                    checkbox_value = st.checkbox(
                        f"🗑️ {row['name']} (ID: {row['id']}) - 削除日時: {row['deleted_at'][:19]}",
                        value=is_currently_selected,
                        key=checkbox_key
                    )

                    if checkbox_value:
                        temp_selection.add(row['id'])

                # 選択を更新ボタン
                col_update, col_info = st.columns([2, 3])
                with col_update:
                    update_selection = st.form_submit_button(
                        "🔄 選択を更新", type="secondary")

                with col_info:
                    temp_count = len(temp_selection)
                    st.info(f"新しい選択: {temp_count}件")

                # フォーム送信時に選択を更新（エラー回避版）
                if update_selection:
                    try:
                        old_count = len(
                            st.session_state.selected_for_permanent_delete)
                        st.session_state.selected_for_permanent_delete = temp_selection
                        new_count = len(temp_selection)

                        st.success(f"✅ 選択を更新しました: {old_count}件 → {new_count}件")

                        # セッション状態の整合性を確認
                        if not isinstance(st.session_state.selected_for_permanent_delete, set):
                            st.session_state.selected_for_permanent_delete = set(
                                temp_selection)

                        import time
                        time.sleep(0.5)  # DOM競合回避のため短い待機
                        st.rerun()

                    except Exception as e:
                        st.error(f"選択の更新でエラーが発生しました: {str(e)}")
                        # エラー時は安全な状態にリセット
                        try:
                            st.session_state.selected_for_permanent_delete = set()
                            st.warning("選択状態をリセットしました。再度選択してください。")
                        except:
                            pass  # リセットに失敗してもスルー

            # 詳細表示（静的なexpander）
            st.markdown("---")
            st.markdown("### 🔍 詳細情報")

            for idx, row in deleted_df.iterrows():
                is_selected = row['id'] in st.session_state.selected_for_permanent_delete

                # 静的なexpander（DOM競合を回避）
                with st.expander(f"{'✅ [選択済み] ' if is_selected else '🗑️ '}{row['name']} (ID: {row['id']})"):
                    if is_selected:
                        st.error("⚠️ この項目は完全削除の対象として選択されています")

                    self._show_fortuneteller_details(row)

                    # 削除情報
                    st.markdown("**🗑️ 削除情報**")
                    st.write(f"削除者: {row.get('deleted_by', '不明')}")
                    st.write(f"削除日時: {row.get('deleted_at', '不明')}")

                    # 個別復元ボタン（エラー回避版）
                    if not is_selected:
                        if st.button("♻️ 復元", key=f"restore_{row['id']}_safe", type="secondary"):
                            try:
                                if self.db.restore_fortuneteller(row['id']):
                                    st.success("♻️ 復元しました")
                                    # 選択状態からも除外（安全に）
                                    try:
                                        st.session_state.selected_for_permanent_delete.discard(
                                            row['id'])
                                    except:
                                        st.session_state.selected_for_permanent_delete = set()

                                    import time
                                    time.sleep(0.5)  # DOM競合回避のため短い待機
                                    st.rerun()
                                else:
                                    st.error("❌ 復元に失敗しました")
                            except Exception as e:
                                st.error(f"復元処理でエラーが発生しました: {str(e)}")
                                # エラー時も選択状態をクリア
                                try:
                                    st.session_state.selected_for_permanent_delete.discard(
                                        row['id'])
                                except:
                                    st.session_state.selected_for_permanent_delete = set()
                    else:
                        st.info("復元ボタンは選択解除後に表示されます")

        else:
            st.info("🗑️ 削除済みの投稿はありません")

        # 削除ログ表示
        with st.expander("📜 削除ログを表示"):
            try:
                logs_df = self.db.get_deletion_logs(20)
                if not logs_df.empty:
                    st.markdown("**最近の削除・完全削除ログ**")
                    for idx, log in logs_df.iterrows():
                        if "permanent" in str(log['table_name']):
                            st.error(
                                f"💀 完全削除: {log['table_name']} ID:{log['record_id']} by {log['deleted_by']} ({log['deleted_at']})")
                        else:
                            st.info(
                                f"🗑️ 論理削除: {log['table_name']} ID:{log['record_id']} by {log['deleted_by']} ({log['deleted_at']})")
                else:
                    st.info("削除ログはありません")
            except Exception as e:
                st.warning(f"削除ログの読み込みでエラーが発生しました: {str(e)}")

    def _handle_permanent_delete_confirmation(self, confirm_key: str):
        """完全削除確認ダイアログ処理（キャンセルエラー修正版）"""
        delete_info = st.session_state.get(confirm_key)
        if not delete_info:
            # 削除情報がない場合は安全に戻る
            if confirm_key in st.session_state:
                del st.session_state[confirm_key]
            st.rerun()
            return

        selected_ids = delete_info.get('ids', [])
        selected_names = delete_info.get('names', [])
        count = delete_info.get('count', 0)

        # データ整合性チェック
        if not selected_ids or count <= 0:
            st.error("⚠️ 削除対象が見つかりません。削除済み一覧に戻ります。")
            if confirm_key in st.session_state:
                del st.session_state[confirm_key]
            st.rerun()
            return

        st.error("🚨 **完全削除の最終確認**")
        st.markdown(f"**対象件数**: {count}件")
        st.markdown("**対象アイテム**:")
        for i, name in enumerate(selected_names[:5]):  # 最初の5件のみ表示
            if i < len(selected_ids):
                st.write(f"• {name} (ID: {selected_ids[i]})")
        if len(selected_names) > 5:
            st.write(f"• ...他{len(selected_names) - 5}件")

        st.error("⚠️ **危険**: この操作は取り消すことができません！データは完全に失われます！")

        # 確認チェックボックス
        confirm_understand = st.checkbox(
            "上記の警告を理解し、完全削除を実行することに同意します", key=f"permanent_delete_understand_{confirm_key}")

        # 削除理由入力
        delete_reason = st.text_area(
            "完全削除の理由（必須）",
            key=f"permanent_delete_reason_{confirm_key}",
            placeholder="例：データ保護規制への対応、容量削減、個人情報削除要請への対応"
        )

        col1, col2 = st.columns(2)
        with col1:
            delete_enabled = confirm_understand and delete_reason.strip()
            if st.button(
                f"💀 完全削除を実行 ({count}件)",
                key=f"execute_permanent_delete_{confirm_key}",
                type="primary",
                disabled=not delete_enabled
            ):
                if delete_enabled:
                    # 完全削除実行
                    with st.spinner("完全削除を実行中..."):
                        try:
                            result = self.db.permanently_delete_fortunetellers(
                                selected_ids, "管理者")

                            if result['success']:
                                st.success(
                                    f"✅ {result['deleted_count']}件を完全削除しました")
                                if result['deleted_names']:
                                    st.info("削除されたアイテム: " + ", ".join(result['deleted_names'][:3]) +
                                            (f"...他{len(result['deleted_names'])-3}件" if len(result['deleted_names']) > 3 else ""))

                                if result['errors']:
                                    st.warning(
                                        f"⚠️ {len(result['errors'])}件でエラーが発生:")
                                    for error in result['errors'][:3]:
                                        st.write(f"• {error}")
                            else:
                                st.error("❌ 完全削除に失敗しました")
                                if result['errors']:
                                    for error in result['errors']:
                                        st.error(f"• {error}")

                        except Exception as e:
                            st.error(f"❌ 完全削除処理中にエラーが発生しました: {str(e)}")

                    # 確認状態と選択状態を安全にクリア
                    try:
                        if confirm_key in st.session_state:
                            del st.session_state[confirm_key]
                        if 'selected_for_permanent_delete' in st.session_state:
                            st.session_state.selected_for_permanent_delete = set()
                        if 'checkbox_changes' in st.session_state:
                            st.session_state.checkbox_changes = {}
                    except Exception as e:
                        st.warning(
                            f"セッション状態のクリア中にエラーが発生しましたが、処理は継続します: {str(e)}")

                    # 少し待ってからリロード
                    import time
                    time.sleep(1)
                    st.rerun()

        with col2:
            if st.button("❌ キャンセル", key=f"cancel_permanent_delete_{confirm_key}"):
                try:
                    # 確認状態を安全にクリア（選択状態は保持）
                    if confirm_key in st.session_state:
                        del st.session_state[confirm_key]

                    # セッション状態の整合性チェック
                    if 'selected_for_permanent_delete' not in st.session_state:
                        st.session_state.selected_for_permanent_delete = set()

                    # チェックボックス変更フラグも初期化
                    if 'checkbox_changes' not in st.session_state:
                        st.session_state.checkbox_changes = {}

                    st.info("✅ 完全削除をキャンセルしました")

                    # 安全な方法で画面を更新
                    import time
                    time.sleep(0.5)  # 短い待機でDOM操作競合を回避
                    st.rerun()

                except Exception as e:
                    # エラーが発生した場合も安全に処理を継続
                    st.warning(f"キャンセル処理中にエラーが発生しましたが、操作はキャンセルされました: {str(e)}")

                    # 強制的にセッション状態をクリア
                    try:
                        if confirm_key in st.session_state:
                            del st.session_state[confirm_key]
                        st.session_state.selected_for_permanent_delete = set()
                        st.session_state.checkbox_changes = {}
                    except:
                        pass  # エラーが発生してもスルー

                    # 強制リロード
                    st.rerun()

    def _show_fortuneteller_details(self, row):
        """占い師詳細情報表示（共通関数）"""
        # 基本情報
        st.write(f"**🎴 カテゴリ**: {row.get('category', '未設定')}")
        st.write(f"**📝 説明**: {row.get('description', '説明なし')}")
        st.write(f"**📞 連絡先**: {row.get('contact', '未登録')}")
        st.write(f"**👤 投稿者**: {row.get('submitted_by', '不明')}")
        st.write(f"**📅 投稿日時**: {row['created_at']}")

        # 住所情報
        if row.get('zipcode') or row.get('address'):
            st.markdown("**📍 住所情報**")
            if row.get('zipcode'):
                st.write(f"  📮 郵便番号: {row['zipcode']}")
            if row.get('address'):
                st.write(f"  🏠 住所: {row['address']}")

        # ウェブサイト情報
        if row.get('website'):
            st.write(f"**🌐 ウェブサイト**: {row['website']}")

        # 位置情報
        st.write(
            f"**📍 位置**: 緯度 {row['latitude']:.6f}, 経度 {row['longitude']:.6f}")

    def _handle_delete_confirmation(self, confirm_key: str):
        """削除確認ダイアログ処理（改良版）"""
        delete_info = st.session_state.get(confirm_key)
        if not delete_info:
            return

        fortuneteller_id = delete_info['id']
        name = delete_info['name']
        tab = delete_info['tab']

        st.error(f"⚠️ **削除確認**: {name} (ID: {fortuneteller_id})")
        st.warning("この操作は取り消すことができますが、一時的に非表示になります。")

        # 削除理由入力
        delete_reason = st.text_input(
            "削除理由（任意）",
            key=f"delete_reason_{fortuneteller_id}_{confirm_key}",
            placeholder="例：重複登録、不適切な内容"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"🗑️ 確実に削除", key=f"confirm_delete_{fortuneteller_id}_{confirm_key}", type="primary"):
                try:
                    if self.db.delete_fortuneteller(fortuneteller_id, "管理者", delete_reason):
                        st.success(f"✅ {name} を削除しました")
                        # 削除確認状態をクリア
                        del st.session_state[confirm_key]
                        # 少し待ってからリロード
                        import time
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("❌ 削除に失敗しました")
                except Exception as e:
                    st.error(f"❌ 削除エラー: {str(e)}")

        with col2:
            if st.button("❌ キャンセル", key=f"cancel_delete_{fortuneteller_id}_{confirm_key}"):
                # 削除確認状態をクリア
                del st.session_state[confirm_key]
                st.info("✅ 削除をキャンセルしました")
                st.rerun()

    def _show_site_settings(self):
        """サイト設定"""
        st.subheader("⚙️ サイト設定")

        # お知らせ編集
        st.markdown("### 📰 お知らせの編集")
        announcements_json = self.db.get_setting('announcements')

        try:
            announcements = json.loads(
                announcements_json) if announcements_json else config.DEFAULT_ANNOUNCEMENTS
        except (json.JSONDecodeError, TypeError):
            announcements = config.DEFAULT_ANNOUNCEMENTS

        # 既存のお知らせ編集
        new_announcements = []
        for i, announcement in enumerate(announcements):
            col1, col2 = st.columns([4, 1])
            with col1:
                edited = st.text_input(
                    f"お知らせ {i+1}", value=announcement, key=f"ann_{i}")
                if edited:
                    new_announcements.append(edited)
            with col2:
                if st.button("🗑️", key=f"delete_ann_{i}", help="このお知らせを削除"):
                    announcements.pop(i)
                    self.db.update_setting('announcements', json.dumps(
                        announcements, ensure_ascii=False))
                    st.rerun()

        # 新しいお知らせ追加
        col1, col2 = st.columns([4, 1])
        with col1:
            new_announcement = st.text_input("新しいお知らせを追加")
        with col2:
            if st.button("➕ 追加") and new_announcement:
                announcements.append(new_announcement)
                self.db.update_setting('announcements', json.dumps(
                    announcements, ensure_ascii=False))
                st.success("追加しました")
                st.rerun()

        if st.button("💾 お知らせ保存"):
            self.db.update_setting('announcements', json.dumps(
                new_announcements, ensure_ascii=False))
            st.success("✅ お知らせを保存しました")
            st.rerun()

        # メール設定
        st.markdown("### 📧 メール設定")
        current_email = self.db.get_setting(
            'contact_email') or config.DEFAULT_CONTACT_EMAIL
        new_email = st.text_input("送信先メールアドレス", value=current_email)

        if st.button("💾 メール保存"):
            self.db.update_setting('contact_email', new_email)
            st.success("✅ メールアドレスを保存しました")

    def _show_work_requests(self):
        """お仕事依頼一覧（フォームベース削除システム版）"""
        st.subheader("💼 お仕事依頼一覧")

        try:
            requests_df = self.db.get_work_requests()
            if not requests_df.empty:
                st.info(f"📧 受信件数: {len(requests_df)}件")

                # フォームベースの削除システム
                with st.form("work_request_management_form", clear_on_submit=False):
                    st.markdown("### 📋 依頼一覧と削除操作")
                    st.markdown(
                        "**💡 ヒント**: 削除したい依頼のチェックボックスを選択して、削除ボタンをクリックしてください")

                    # 削除対象を選択
                    selected_for_deletion = []

                    for idx, row in requests_df.iterrows():
                        # チェックボックスで削除対象を選択
                        delete_this = st.checkbox(
                            f"📧 {row['subject']} - {row['client_name']} ({row['created_at'][:19]})",
                            key=f"delete_work_request_{row['id']}",
                            value=False
                        )

                        if delete_this:
                            selected_for_deletion.append(row['id'])

                        # 詳細を展開可能な形で表示
                        with st.expander(f"📝 詳細: {row['subject']} (ID: {row['id']})"):
                            st.write(f"**👤 依頼者**: {row['client_name']}")
                            st.write(f"**📧 メール**: {row['client_email']}")
                            st.write(f"**📝 内容**:")
                            st.text_area(
                                "", value=row['content'], height=100, disabled=True, key=f"content_display_{row['id']}")
                            st.write(f"**📅 受信日時**: {row['created_at']}")

                    # 削除実行セクション
                    st.markdown("---")
                    st.markdown("### 🗑️ 削除実行")

                    if selected_for_deletion:
                        st.warning(
                            f"⚠️ 選択された {len(selected_for_deletion)}件の依頼が削除されます")

                        # 削除理由入力
                        delete_reason = st.text_input(
                            "削除理由（必須）",
                            placeholder="例：対応完了、スパム、重複依頼",
                            key="work_delete_reason_form"
                        )

                        # 削除実行ボタン
                        col1, col2 = st.columns(2)
                        with col1:
                            delete_submitted = st.form_submit_button(
                                f"🗑️ 選択した {len(selected_for_deletion)}件を削除",
                                type="primary"
                            )
                        with col2:
                            cancel_submitted = st.form_submit_button(
                                "❌ 選択をクリア")
                    else:
                        st.info("削除する依頼を選択してください")
                        delete_submitted = False
                        cancel_submitted = st.form_submit_button("🔄 表示を更新")

                # フォーム送信処理
                if 'delete_submitted' in locals() and delete_submitted:
                    if selected_for_deletion and delete_reason.strip():
                        # 削除実行
                        success_count = 0
                        error_count = 0
                        deleted_subjects = []

                        for request_id in selected_for_deletion:
                            try:
                                # 削除対象の情報を取得
                                row = requests_df[requests_df['id']
                                                  == request_id]
                                if not row.empty:
                                    subject = row.iloc[0]['subject']
                                    if self.db.delete_work_request(request_id, "管理者", delete_reason):
                                        success_count += 1
                                        deleted_subjects.append(subject)
                                    else:
                                        error_count += 1
                            except Exception as e:
                                error_count += 1
                                st.error(f"ID {request_id} の削除でエラー: {str(e)}")

                        # 結果表示
                        if success_count > 0:
                            st.success(f"✅ {success_count}件の依頼を削除しました")
                            if deleted_subjects:
                                st.info("削除された依頼: " + ", ".join(deleted_subjects[:3]) +
                                        (f"...他{len(deleted_subjects)-3}件" if len(deleted_subjects) > 3 else ""))

                        if error_count > 0:
                            st.error(f"❌ {error_count}件の削除に失敗しました")

                        # 画面を安全に更新
                        import time
                        time.sleep(1)
                        st.rerun()

                    elif selected_for_deletion and not delete_reason.strip():
                        st.error("❌ 削除理由を入力してください")

                if 'cancel_submitted' in locals() and cancel_submitted:
                    st.info("✅ 表示を更新しました")
                    st.rerun()

            else:
                st.info("💼 お仕事依頼はありません")
        except Exception as e:
            st.error(f"❌ 依頼一覧の取得エラー: {str(e)}")

    def _show_statistics(self):
        """統計表示（削除件数追加版）"""
        st.subheader("📊 統計情報")

        try:
            stats = self.db.get_statistics()

            # メトリクス表示
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("✅ 承認済み", f"{stats['approved']}件", delta="公開中")
            with col2:
                st.metric("📋 承認待ち", f"{stats['pending']}件", delta="審査中")
            with col3:
                st.metric("❌ 却下", f"{stats['rejected']}件")
            with col4:
                st.metric("🗑️ 削除済み", f"{stats['deleted']}件", delta="非表示")

            # カテゴリ別グラフ
            if not stats['categories'].empty:
                st.markdown("### 🎴 占術カテゴリ別件数")
                st.bar_chart(stats['categories'].set_index('category'))

            # 詳細統計
            with st.expander("📈 詳細統計"):
                total_records = stats['approved'] + stats['pending'] + \
                    stats['rejected'] + stats['deleted']
                if total_records > 0:
                    st.write(f"**全体登録数**: {total_records}件")
                    st.write(
                        f"**公開率**: {stats['approved']/total_records*100:.1f}%")
                    st.write(
                        f"**削除率**: {stats['deleted']/total_records*100:.1f}%")

                # 最近の活動
                recent_df = self.db.get_fortunetellers("all")
                if not recent_df.empty:
                    recent_counts = recent_df['created_at'].str[:10].value_counts().head(
                        7)
                    st.markdown("**📅 最近7日間の登録件数**")
                    st.bar_chart(recent_counts)

        except Exception as e:
            st.error(f"❌ 統計情報の取得エラー: {str(e)}")

    def _show_password_change(self):
        """パスワード変更画面"""
        st.subheader("🔐 管理者パスワード変更")

        st.warning("⚠️ **セキュリティ重要**: パスワードは定期的に変更してください")

        # パスワード変更成功フラグをチェック
        if st.session_state.get('password_changed_success', False):
            st.success("✅ パスワードを変更しました")
            st.info("🔄 セキュリティのため、再ログインしてください")

            # 再ログインボタン（フォーム外で配置）
            if st.button("🚪 再ログイン画面へ", type="primary"):
                st.session_state.admin_authenticated = False
                st.session_state.password_changed_success = False
                st.rerun()
            return

        with st.form("password_change_form"):
            st.markdown("### 📝 パスワード変更フォーム")

            current_password = st.text_input("🔑 現在のパスワード", type="password")
            new_password = st.text_input("🆕 新しいパスワード", type="password")
            confirm_password = st.text_input("🔄 新しいパスワード（確認）", type="password")

            st.markdown("**パスワード要件:**")
            st.markdown(f"• {config.PASSWORD_MIN_LENGTH}文字以上")
            st.markdown("• 英数字と記号を含むことを推奨")
            st.markdown("• 過去に使用したパスワードは使用不可")

            submitted = st.form_submit_button("🔐 パスワード変更", type="primary")

            if submitted:
                # バリデーション
                if not all([current_password, new_password, confirm_password]):
                    st.error("❌ すべての項目を入力してください")
                elif new_password != confirm_password:
                    st.error("❌ 新しいパスワードが一致しません")
                elif len(new_password) < config.PASSWORD_MIN_LENGTH:
                    st.error(
                        f"❌ パスワードは{config.PASSWORD_MIN_LENGTH}文字以上にしてください")
                else:
                    # パスワード変更実行
                    result = self.db.change_admin_password(
                        current_password, new_password)

                    if result['success']:
                        st.session_state.password_changed_success = True
                        st.rerun()
                    else:
                        st.error(f"❌ {result['error']}")

        # パスワードセキュリティのヒント
        with st.expander("💡 セキュリティのヒント"):
            st.markdown("""
            **強力なパスワードの作成方法:**
            • 大文字・小文字・数字・記号を組み合わせる
            • 辞書にない単語を使用する
            • 定期的に変更する（3-6ヶ月ごと）
            • 他のサービスと同じパスワードを使わない
            
            **例**: `MyApp2025!Secure#`
            """)
