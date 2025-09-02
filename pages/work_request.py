"""
お仕事依頼フォーム
占い師への仕事依頼を管理
"""
import streamlit as st
import re
import config


class WorkRequestForm:
    """お仕事依頼フォームクラス"""

    def __init__(self, db):
        self.db = db

    def show(self):
        """お仕事依頼フォーム表示"""
        st.markdown("---")
        st.subheader("💼 お仕事のご依頼")

        contact_email = self.db.get_setting(
            'contact_email') or config.DEFAULT_CONTACT_EMAIL

        st.info("占い師の出張依頼、イベント出演、取材などのご依頼を承ります。")

        with st.form("work_request_form"):
            col1, col2 = st.columns(2)

            with col1:
                client_name = st.text_input("お名前 *")
                client_email = st.text_input("メールアドレス *")

            with col2:
                subject = st.text_input("件名 *")

            content = st.text_area("依頼内容 *", height=200)

            submitted = st.form_submit_button("📧 送信する", type="primary")

            if submitted:
                if all([client_name, client_email, subject, content]):
                    if self._validate_email(client_email):
                        if self.db.save_work_request(subject, content, client_name, client_email):
                            st.success(f"✅ お仕事依頼を受け付けました。")
                            st.session_state.show_work_request = False
                            st.rerun()
                        else:
                            st.error("送信に失敗しました")
                    else:
                        st.error("正しいメールアドレスを入力してください")
                else:
                    st.error("すべての必須項目を入力してください")

        # 閉じるボタン
        if st.button("✖ 閉じる"):
            st.session_state.show_work_request = False
            st.rerun()

    def _validate_email(self, email: str) -> bool:
        """メールアドレスの簡易バリデーション"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
