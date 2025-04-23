# app.py
import streamlit as st
import ui                   # UIモジュール
import llm                  # LLMモジュール
import database             # データベースモジュール
import torch
from transformers import pipeline
from config import MODEL_NAME
from huggingface_hub import HfFolder

# --- アプリケーション設定 ---
st.set_page_config(page_title="Whisper ASR", layout="wide")

# データベースの初期化（テーブルが存在しない場合、作成）
database.init_db()

# ASRモデルのロード（キャッシュを利用）
# モデルをキャッシュして再利用
@st.cache_resource
def load_model():
    """ASRモデルをロードする"""
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        st.info(f"Using device: {device}") # 使用デバイスを表示
        pipe = pipeline("automatic-speech-recognition", 
                        model=MODEL_NAME,
                        device=device)
        st.success(f"モデル '{MODEL_NAME}' の読み込みに成功しました。")
        return pipe
    except Exception as e:
        st.error(f"モデル '{MODEL_NAME}' の読み込みに失敗しました: {e}")
        st.error("GPUメモリ不足の可能性があります。不要なプロセスを終了するか、より小さいモデルの使用を検討してください。")
        return None
pipe = llm.load_model()

# --- Streamlit アプリケーション ---
st.title("Whisper translate speech")
st.write("Whisperモデルを使用した音声文字おこしアプリです。")
st.markdown("---")


# --- セッション状態初期化 ---
if 'page' not in st.session_state:
    st.session_state.page = "音声文字おこし"


# --- サイドバー ---
st.sidebar.title("ナビゲーション")
page = st.sidebar.radio(
    "ページ選択",
    ["音声文字おこし", "履歴閲覧", "サンプルデータ管理"],
    index=["音声文字おこし", "履歴閲覧", "サンプルデータ管理"].index(st.session_state.page),
    key="page_selector"
)
st.session_state.page = page  # 状態更新


# --- メイン表示 ---
if st.session_state.page == "音声文字おこし":
    if pipe:
        ui.display_transcription_page(pipe)
    else:
        st.error("モデルの読み込みに失敗しました。")
elif st.session_state.page == "履歴閲覧":
    ui.display_transcription_history()
elif st.session_state.page == "サンプルデータ管理":
    ui.display_data_page()


# --- フッターなど（任意） ---
st.sidebar.markdown("---")
st.sidebar.info("開発者: [Akimoto Aoba]")