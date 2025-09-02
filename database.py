"""
データベース管理モジュール
SQLiteを使用した占い師データの管理
削除機能・パスワード管理機能追加版
"""
import sqlite3
import pandas as pd
from typing import Optional, Dict, Any, List
from datetime import datetime
import config
import hashlib
import secrets
import os

# Fortunetellerクラスを直接インポートではなく、条件付きインポートに変更


def get_fortuneteller_model():
    """Fortunetellerモデルを取得（循環インポート回避）"""
    from models.fortuneteller import Fortuneteller
    return Fortuneteller


class DatabaseManager:
    """データベース管理クラス（削除機能・パスワード管理追加版）"""

    def __init__(self):
        """初期化"""
        self.db_path = config.DATABASE_PATH
        self._init_database()
        self._upgrade_database()  # 新しい列を追加
        self._init_admin_password()  # 管理者パスワード初期化
        self._insert_sample_data()

    def _init_database(self):
        """データベース初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 占い師テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fortunetellers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                description TEXT,
                contact TEXT,
                website TEXT,
                category TEXT,
                status TEXT DEFAULT 'pending',
                submitted_by TEXT DEFAULT '匿名',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approved_by TEXT,
                approved_at TIMESTAMP,
                zipcode TEXT,
                address TEXT,
                deleted_at TIMESTAMP,
                deleted_by TEXT
            )
        """)

        # お仕事依頼テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS work_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                content TEXT NOT NULL,
                client_name TEXT NOT NULL,
                client_email TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP,
                deleted_by TEXT
            )
        """)

        # 設定テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 管理者パスワードテーブル（新規追加）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)

        # パスワード履歴テーブル（新規追加）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS password_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 削除ログテーブル（新規追加）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deletion_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL,
                record_id INTEGER NOT NULL,
                record_data TEXT NOT NULL,
                deleted_by TEXT NOT NULL,
                deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reason TEXT
            )
        """)

        conn.commit()
        conn.close()

    def _upgrade_database(self):
        """データベースのアップグレード（既存テーブルに新しい列を追加）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # fortunetellersテーブルの列を確認・追加
        cursor.execute("PRAGMA table_info(fortunetellers)")
        columns = [column[1] for column in cursor.fetchall()]

        new_columns = {
            'zipcode': 'TEXT',
            'address': 'TEXT',
            'deleted_at': 'TIMESTAMP',
            'deleted_by': 'TEXT'
        }

        for column_name, column_type in new_columns.items():
            if column_name not in columns:
                cursor.execute(
                    f"ALTER TABLE fortunetellers ADD COLUMN {column_name} {column_type}")
                print(f"✅ {column_name}列を追加しました")

        # work_requestsテーブルの列を確認・追加
        cursor.execute("PRAGMA table_info(work_requests)")
        work_columns = [column[1] for column in cursor.fetchall()]

        work_new_columns = {
            'deleted_at': 'TIMESTAMP',
            'deleted_by': 'TEXT'
        }

        for column_name, column_type in work_new_columns.items():
            if column_name not in work_columns:
                cursor.execute(
                    f"ALTER TABLE work_requests ADD COLUMN {column_name} {column_type}")
                print(f"✅ work_requests.{column_name}列を追加しました")

        conn.commit()
        conn.close()

    def _init_admin_password(self):
        """管理者パスワードの初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 既存のアクティブなパスワードがあるかチェック
        cursor.execute(
            "SELECT COUNT(*) FROM admin_passwords WHERE is_active = 1")
        count = cursor.fetchone()[0]

        # アクティブなパスワードがない場合、デフォルトパスワードを設定
        if count == 0:
            password_hash, salt = self._hash_password(
                config.DEFAULT_ADMIN_PASSWORD)
            cursor.execute("""
                INSERT INTO admin_passwords (password_hash, salt, is_active)
                VALUES (?, ?, 1)
            """, (password_hash, salt))
            print("✅ デフォルト管理者パスワードを設定しました")

        conn.commit()
        conn.close()

    def _hash_password(self, password: str) -> tuple:
        """パスワードをハッシュ化"""
        salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256', password.encode(), salt.encode(), 100000)
        return password_hash.hex(), salt

    def _verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """パスワードを検証"""
        password_hash = hashlib.pbkdf2_hmac(
            'sha256', password.encode(), salt.encode(), 100000)
        return password_hash.hex() == stored_hash

    def verify_admin_password(self, password: str) -> bool:
        """管理者パスワードを検証"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT password_hash, salt FROM admin_passwords 
            WHERE is_active = 1 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        result = cursor.fetchone()
        conn.close()

        if result:
            stored_hash, salt = result
            return self._verify_password(password, stored_hash, salt)
        return False

    def change_admin_password(self, current_password: str, new_password: str) -> dict:
        """管理者パスワードを変更"""
        try:
            # 現在のパスワードを検証
            if not self.verify_admin_password(current_password):
                return {'success': False, 'error': '現在のパスワードが間違っています'}

            # 新しいパスワードの妥当性チェック
            if len(new_password) < config.PASSWORD_MIN_LENGTH:
                return {'success': False, 'error': f'パスワードは{config.PASSWORD_MIN_LENGTH}文字以上にしてください'}

            # 過去のパスワードと重複チェック
            if self._is_password_used_before(new_password):
                return {'success': False, 'error': '過去に使用したパスワードは使用できません'}

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 現在のパスワードを無効化
            cursor.execute(
                "UPDATE admin_passwords SET is_active = 0 WHERE is_active = 1")

            # 新しいパスワードをハッシュ化して保存
            password_hash, salt = self._hash_password(new_password)
            cursor.execute("""
                INSERT INTO admin_passwords (password_hash, salt, is_active)
                VALUES (?, ?, 1)
            """, (password_hash, salt))

            # パスワード履歴に追加
            cursor.execute("""
                INSERT INTO password_history (password_hash)
                VALUES (?)
            """, (password_hash,))

            # 古いパスワード履歴を削除（最新N件のみ保持）
            cursor.execute("""
                DELETE FROM password_history 
                WHERE id NOT IN (
                    SELECT id FROM password_history 
                    ORDER BY created_at DESC 
                    LIMIT ?
                )
            """, (config.PASSWORD_HISTORY_LIMIT,))

            conn.commit()
            conn.close()

            return {'success': True, 'message': 'パスワードを変更しました'}

        except Exception as e:
            return {'success': False, 'error': f'パスワード変更エラー: {str(e)}'}

    def _is_password_used_before(self, password: str) -> bool:
        """パスワードが過去に使用されたかチェック"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT password_hash FROM password_history ORDER BY created_at DESC")
        password_histories = cursor.fetchall()
        conn.close()

        # 仮のソルトでハッシュ化（履歴比較用）
        temp_salt = "temp_salt_for_comparison"
        new_hash = hashlib.pbkdf2_hmac(
            'sha256', password.encode(), temp_salt.encode(), 100000).hex()

        for (stored_hash,) in password_histories:
            # 実際の比較では同じソルトを使用する必要があるため、
            # ここでは簡易的な実装
            if stored_hash == new_hash:
                return True

        return False

    def _insert_sample_data(self):
        """サンプルデータ挿入"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # データが空の場合のみサンプルを挿入
        cursor.execute(
            "SELECT COUNT(*) FROM fortunetellers WHERE deleted_at IS NULL")
        count = cursor.fetchone()[0]

        if count == 0:
            sample_data = [
                ("東京占い館", 35.6762, 139.6503, "タロット", "タロットカードと西洋占星術が得意",
                 "03-1234-5678", "https://example.com", "approved", "1000001", "東京都千代田区千代田"),
                ("渋谷占いの部屋", 35.6580, 139.7016, "手相",
                 "手相占いの専門家", "03-2345-6789", None, "approved", "1500001", "東京都渋谷区神宮前"),
                ("新宿スピリチュアル", 35.6896, 139.6921, "霊視", "霊視とオーラ診断",
                 "03-3456-7890", "https://example2.com", "approved", "1600001", "東京都新宿区西新宿"),
                ("池袋占いサロン", 35.7295, 139.7109, "占星術",
                 "西洋占星術と数秘術", "03-4567-8901", None, "approved", "1700001", "東京都豊島区南池袋"),
                ("品川占い処", 35.6285, 139.7387, "四柱推命",
                 "四柱推命の専門家", "03-5678-9012", None, "approved", "1400001", "東京都品川区北品川")
            ]

            for name, lat, lon, category, desc, contact, website, status, zipcode, address in sample_data:
                cursor.execute("""
                    INSERT INTO fortunetellers 
                    (name, latitude, longitude, category, description, contact, website, status, submitted_by, approved_by, approved_at, zipcode, address)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?)
                """, (name, lat, lon, category, desc, contact, website, status, "システム", "システム", zipcode, address))

        conn.commit()
        conn.close()

    def get_fortunetellers(self, status: str = "approved", include_deleted: bool = False) -> pd.DataFrame:
        """占い師一覧取得（削除対応版）"""
        conn = sqlite3.connect(self.db_path)

        # 削除されたレコードの扱い
        deleted_condition = "" if include_deleted else "AND deleted_at IS NULL"

        if status == "all":
            query = f"SELECT * FROM fortunetellers WHERE 1=1 {deleted_condition} ORDER BY created_at DESC"
        else:
            query = f"SELECT * FROM fortunetellers WHERE status = '{status}' {deleted_condition} ORDER BY created_at DESC"

        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def get_fortuneteller_by_id(self, fortuneteller_id: int, include_deleted: bool = False) -> Optional[Dict[str, Any]]:
        """IDから占い師情報を取得（削除対応版）"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 削除されたレコードの扱い
        deleted_condition = "" if include_deleted else "AND deleted_at IS NULL"

        cursor.execute(f"""
            SELECT * FROM fortunetellers 
            WHERE id = ? {deleted_condition}
        """, (fortuneteller_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def delete_fortuneteller(self, fortuneteller_id: int, deleted_by: str, reason: str = "") -> bool:
        """占い師情報を削除（論理削除）"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 削除前にデータを取得
            cursor.execute(
                "SELECT * FROM fortunetellers WHERE id = ? AND deleted_at IS NULL", (fortuneteller_id,))
            fortuneteller_data = cursor.fetchone()

            if not fortuneteller_data:
                conn.close()
                print(f"削除対象が見つかりません: ID {fortuneteller_id}")
                return False

            # 論理削除実行
            cursor.execute("""
                UPDATE fortunetellers 
                SET deleted_at = CURRENT_TIMESTAMP, deleted_by = ?
                WHERE id = ? AND deleted_at IS NULL
            """, (deleted_by, fortuneteller_id))

            # 削除が実行されたか確認
            if cursor.rowcount == 0:
                conn.close()
                print(f"削除対象が見つからないか、既に削除済み: ID {fortuneteller_id}")
                return False

            # 削除ログを記録
            import json
            cursor.execute("""
                INSERT INTO deletion_logs (table_name, record_id, record_data, deleted_by, reason)
                VALUES (?, ?, ?, ?, ?)
            """, ("fortunetellers", fortuneteller_id, json.dumps(dict(fortuneteller_data), ensure_ascii=False), deleted_by, reason))

            conn.commit()
            conn.close()

            print(
                f"✅ 占い師を削除しました: ID {fortuneteller_id}, Name: {fortuneteller_data['name']}")
            return True

        except Exception as e:
            print(f"❌ 削除エラー: {e}")
            import traceback
            traceback.print_exc()
            return False

    def restore_fortuneteller(self, fortuneteller_id: int) -> bool:
        """占い師情報を復元"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE fortunetellers 
                SET deleted_at = NULL, deleted_by = NULL
                WHERE id = ? AND deleted_at IS NOT NULL
            """, (fortuneteller_id,))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"復元エラー: {e}")
            return False

    def get_deleted_fortunetellers(self) -> pd.DataFrame:
        """削除された占い師一覧を取得"""
        conn = sqlite3.connect(self.db_path)
        query = "SELECT * FROM fortunetellers WHERE deleted_at IS NOT NULL ORDER BY deleted_at DESC"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def delete_work_request(self, request_id: int, deleted_by: str, reason: str = "") -> bool:
        """お仕事依頼を削除（論理削除）"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 削除前にデータを取得
            cursor.execute(
                "SELECT * FROM work_requests WHERE id = ? AND deleted_at IS NULL", (request_id,))
            request_data = cursor.fetchone()

            if not request_data:
                conn.close()
                print(f"削除対象が見つかりません: ID {request_id}")
                return False

            # 論理削除実行
            cursor.execute("""
                UPDATE work_requests 
                SET deleted_at = CURRENT_TIMESTAMP, deleted_by = ?
                WHERE id = ? AND deleted_at IS NULL
            """, (deleted_by, request_id))

            # 削除が実行されたか確認
            if cursor.rowcount == 0:
                conn.close()
                print(f"削除対象が見つからないか、既に削除済み: ID {request_id}")
                return False

            # 削除ログを記録
            import json
            cursor.execute("""
                INSERT INTO deletion_logs (table_name, record_id, record_data, deleted_by, reason)
                VALUES (?, ?, ?, ?, ?)
            """, ("work_requests", request_id, json.dumps(dict(request_data), ensure_ascii=False), deleted_by, reason))

            conn.commit()
            conn.close()

            print(
                f"✅ お仕事依頼を削除しました: ID {request_id}, Subject: {request_data['subject']}")
            return True

        except Exception as e:
            print(f"❌ お仕事依頼削除エラー: {e}")
            import traceback
            traceback.print_exc()
            return False

    def save_fortuneteller(self, fortuneteller_data: Dict[str, Any]) -> bool:
        """占い師情報を保存（辞書形式で受け取り）"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO fortunetellers 
                (name, latitude, longitude, description, contact, website, category, status, submitted_by, zipcode, address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fortuneteller_data.get('name'),
                fortuneteller_data.get('latitude'),
                fortuneteller_data.get('longitude'),
                fortuneteller_data.get('description'),
                fortuneteller_data.get('contact'),
                fortuneteller_data.get('website'),
                fortuneteller_data.get('category'),
                'pending',
                fortuneteller_data.get('submitted_by', '匿名'),
                fortuneteller_data.get('zipcode'),
                fortuneteller_data.get('address')
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"保存エラー: {e}")
            return False

    def update_status(self, fortuneteller_id: int, status: str, approved_by: str) -> bool:
        """ステータス更新"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if status == "approved":
                cursor.execute("""
                    UPDATE fortunetellers 
                    SET status = ?, approved_by = ?, approved_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND deleted_at IS NULL
                """, (status, approved_by, fortuneteller_id))
            else:
                cursor.execute("""
                    UPDATE fortunetellers 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND deleted_at IS NULL
                """, (status, fortuneteller_id))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"更新エラー: {e}")
            return False

    def save_work_request(self, subject: str, content: str, client_name: str, client_email: str) -> bool:
        """お仕事依頼を保存"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO work_requests (subject, content, client_name, client_email)
                VALUES (?, ?, ?, ?)
            """, (subject, content, client_name, client_email))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"保存エラー: {e}")
            return False

    def get_work_requests(self, include_deleted: bool = False) -> pd.DataFrame:
        """お仕事依頼一覧取得（削除対応版）"""
        conn = sqlite3.connect(self.db_path)
        deleted_condition = "" if include_deleted else "WHERE deleted_at IS NULL"
        query = f"SELECT * FROM work_requests {deleted_condition} ORDER BY created_at DESC"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def get_setting(self, key: str) -> Optional[str]:
        """設定値取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        result = cursor.fetchone()
        conn.close()

        if result:
            return result[0]
        return None

    def update_setting(self, key: str, value: str) -> bool:
        """設定値更新"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, value))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"設定更新エラー: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """統計情報取得（削除対応版）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # ステータス別件数
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN status = 'approved' AND deleted_at IS NULL THEN 1 END) as approved,
                COUNT(CASE WHEN status = 'pending' AND deleted_at IS NULL THEN 1 END) as pending,
                COUNT(CASE WHEN status = 'rejected' AND deleted_at IS NULL THEN 1 END) as rejected,
                COUNT(CASE WHEN deleted_at IS NOT NULL THEN 1 END) as deleted
            FROM fortunetellers
        """)

        counts = cursor.fetchone()

        # カテゴリ別件数
        categories_df = pd.read_sql_query("""
            SELECT category, COUNT(*) as count
            FROM fortunetellers
            WHERE status = 'approved' AND deleted_at IS NULL
            GROUP BY category
            ORDER BY count DESC
        """, conn)

        conn.close()

        return {
            'approved': counts[0] or 0,
            'pending': counts[1] or 0,
            'rejected': counts[2] or 0,
            'deleted': counts[3] or 0,
            'categories': categories_df
        }

    def permanently_delete_fortunetellers(self, fortuneteller_ids: list, deleted_by: str) -> dict:
        """占い師情報を完全削除（物理削除）"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            deleted_count = 0
            deleted_names = []
            errors = []

            for fortuneteller_id in fortuneteller_ids:
                try:
                    # 削除前にデータを取得（削除済みのもののみ）
                    cursor.execute("""
                        SELECT * FROM fortunetellers 
                        WHERE id = ? AND deleted_at IS NOT NULL
                    """, (fortuneteller_id,))

                    fortuneteller_data = cursor.fetchone()

                    if fortuneteller_data:
                        # 完全削除ログを記録
                        import json
                        cursor.execute("""
                            INSERT INTO deletion_logs (table_name, record_id, record_data, deleted_by, reason)
                            VALUES (?, ?, ?, ?, ?)
                        """, ("fortunetellers_permanent", fortuneteller_id,
                              json.dumps(dict(fortuneteller_data),
                                         ensure_ascii=False),
                              deleted_by, "完全削除"))

                        # 物理削除実行
                        cursor.execute(
                            "DELETE FROM fortunetellers WHERE id = ?", (fortuneteller_id,))

                        if cursor.rowcount > 0:
                            deleted_count += 1
                            deleted_names.append(fortuneteller_data['name'])
                            print(
                                f"✅ 完全削除: ID {fortuneteller_id}, Name: {fortuneteller_data['name']}")
                        else:
                            errors.append(f"ID {fortuneteller_id}: 削除に失敗")
                    else:
                        errors.append(
                            f"ID {fortuneteller_id}: 削除済みデータが見つかりません")

                except Exception as e:
                    errors.append(f"ID {fortuneteller_id}: {str(e)}")
                    print(f"❌ 完全削除エラー (ID: {fortuneteller_id}): {e}")

            conn.commit()
            conn.close()

            return {
                'success': deleted_count > 0,
                'deleted_count': deleted_count,
                'deleted_names': deleted_names,
                'errors': errors,
                'total_requested': len(fortuneteller_ids)
            }

        except Exception as e:
            print(f"❌ 完全削除処理エラー: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'deleted_count': 0,
                'deleted_names': [],
                'errors': [f"システムエラー: {str(e)}"],
                'total_requested': len(fortuneteller_ids)
            }

    def permanently_delete_work_requests(self, request_ids: list, deleted_by: str) -> dict:
        """お仕事依頼を完全削除（物理削除）"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            deleted_count = 0
            deleted_subjects = []
            errors = []

            for request_id in request_ids:
                try:
                    # 削除前にデータを取得（削除済みのもののみ）
                    cursor.execute("""
                        SELECT * FROM work_requests 
                        WHERE id = ? AND deleted_at IS NOT NULL
                    """, (request_id,))

                    request_data = cursor.fetchone()

                    if request_data:
                        # 完全削除ログを記録
                        import json
                        cursor.execute("""
                            INSERT INTO deletion_logs (table_name, record_id, record_data, deleted_by, reason)
                            VALUES (?, ?, ?, ?, ?)
                        """, ("work_requests_permanent", request_id,
                              json.dumps(dict(request_data),
                                         ensure_ascii=False),
                              deleted_by, "完全削除"))

                        # 物理削除実行
                        cursor.execute(
                            "DELETE FROM work_requests WHERE id = ?", (request_id,))

                        if cursor.rowcount > 0:
                            deleted_count += 1
                            deleted_subjects.append(request_data['subject'])
                            print(
                                f"✅ 依頼完全削除: ID {request_id}, Subject: {request_data['subject']}")
                        else:
                            errors.append(f"ID {request_id}: 削除に失敗")
                    else:
                        errors.append(f"ID {request_id}: 削除済みデータが見つかりません")

                except Exception as e:
                    errors.append(f"ID {request_id}: {str(e)}")
                    print(f"❌ 依頼完全削除エラー (ID: {request_id}): {e}")

            conn.commit()
            conn.close()

            return {
                'success': deleted_count > 0,
                'deleted_count': deleted_count,
                'deleted_subjects': deleted_subjects,
                'errors': errors,
                'total_requested': len(request_ids)
            }

        except Exception as e:
            print(f"❌ 依頼完全削除処理エラー: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'deleted_count': 0,
                'deleted_subjects': [],
                'errors': [f"システムエラー: {str(e)}"],
                'total_requested': len(request_ids)
            }

    def get_deletion_logs(self, limit: int = 50) -> pd.DataFrame:
        """削除ログ一覧を取得"""
        conn = sqlite3.connect(self.db_path)
        query = f"SELECT * FROM deletion_logs ORDER BY deleted_at DESC LIMIT {limit}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
