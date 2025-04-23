# ui.py
import streamlit as st
import pandas as pd
import time
from database import save_to_db, get_db_count, clear_db
from database import get_transcription_history
from llm import transcribe_audio
# from data import create_sample_evaluation_data
# from metrics import get_metrics_descriptions


def display_transcription_page(pipe):
    st.subheader("音声ファイルをアップロードしてください（.wav 推奨）")
    uploaded_file = st.file_uploader("音声ファイル", type=["wav", "mp3", "m4a"])

    if uploaded_file is not None:
        with st.spinner("文字起こし中..."):
            # ファイル保存（temp用など）
            audio_path = f"/tmp/{uploaded_file.name}"
            with open(audio_path, "wb") as f:
                f.write(uploaded_file.read())

            transcript, response_time = transcribe_audio(pipe, audio_path)
            st.success("文字起こし完了！")
            st.markdown(f"**文字起こし結果:**\n\n{transcript}")
            st.info(f"処理時間: {response_time:.2f}秒")

            # 保存ボタン
            if st.button("この結果を保存"):
                save_to_db(uploaded_file.name, transcript, response_time)
                st.success("結果を保存しました！")


# --- 履歴閲覧ページのUI ---
def display_transcription_history():
    st.subheader("文字起こし履歴")

    history_df = get_transcription_history()

    if history_df.empty:
        st.info("まだ履歴がありません。")
        return

    st.dataframe(history_df, use_container_width=True)





# --- サンプルデータ管理ページのUI ---
def display_data_page():
    """サンプルデータ管理ページのUIを表示する"""
    st.subheader("サンプル評価データの管理")
    count = get_db_count()
    st.write(f"現在のデータベースには {count} 件のレコードがあります。")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("サンプルデータを追加", key="create_samples"):
            create_sample_evaluation_data()
            st.rerun() # 件数表示を更新

    with col2:
        # 確認ステップ付きのクリアボタン
        if st.button("データベースをクリア", key="clear_db_button"):
            if clear_db(): # clear_db内で確認と実行を行う
                st.rerun() # クリア後に件数表示を更新