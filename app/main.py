from typing import Dict, List

import streamlit as st
from openai import OpenAI

from .auth import authenticate
from .config import get_settings
from .database import init_db, log_chat_message


def _ensure_session_state() -> None:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "loaded" not in st.session_state:
        st.session_state.loaded = True


def _render_login() -> None:
    st.title("DiaLab Chat")
    st.write("研究室向け GPT チャットシステム")

    with st.form("login"):
        username = st.text_input("ユーザー名")
        password = st.text_input("パスワード", type="password")
        submitted = st.form_submit_button("ログイン")

    if submitted:
        user = authenticate(username, password)
        if user:
            st.session_state.authenticated = True
            st.session_state.user = {"id": user["id"], "username": user["username"]}
            st.session_state.messages = [
                {"role": "assistant", "content": "こんにちは、どのようにお手伝いできますか？"}
            ]
            st.success(f"{user['username']} としてログインしました")
            st.experimental_rerun()
        else:
            st.error("ユーザー名またはパスワードが正しくありません")


def _render_chat(client: OpenAI, model_name: str) -> None:
    user = st.session_state.user

    st.sidebar.header("ユーザー情報")
    st.sidebar.write(f"👤 {user['username']}")
    st.sidebar.write(f"利用モデル: `{model_name}`")

    if st.sidebar.button("ログアウト", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key in {"authenticated", "user", "messages"}:
                del st.session_state[key]
        st.experimental_rerun()

    st.title("DiaLab Chat")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("メッセージを入力してください"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        log_chat_message(
            user_id=user["id"],
            role="user",
            content=prompt,
            model=model_name,
            input_tokens=None,
            output_tokens=None,
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("... 応答を生成しています ...")
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=_build_messages(st.session_state.messages),
                )
                assistant_message = response.choices[0].message.content
                message_placeholder.markdown(assistant_message)

                input_tokens = getattr(response.usage, "prompt_tokens", None)
                output_tokens = getattr(response.usage, "completion_tokens", None)
                st.session_state.messages.append({"role": "assistant", "content": assistant_message})
                log_chat_message(
                    user_id=user["id"],
                    role="assistant",
                    content=assistant_message,
                    model=model_name,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                )
            except Exception as exc:
                message_placeholder.markdown("エラーが発生しました。詳細はサーバーログを確認してください。")
                st.error(str(exc))


def _build_messages(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    system_message = {
        "role": "system",
        "content": "You are a helpful assistant for a research laboratory.",
    }
    return [system_message] + messages


def run() -> None:
    st.set_page_config(page_title="DiaLab Chat", page_icon="💬", layout="wide")

    init_db()
    settings = get_settings()
    client = OpenAI(api_key=settings.openai_api_key)
    model_name = settings.openai_model

    _ensure_session_state()

    if not st.session_state.authenticated:
        _render_login()
    else:
        _render_chat(client, model_name)


if __name__ == "__main__":
    run()
