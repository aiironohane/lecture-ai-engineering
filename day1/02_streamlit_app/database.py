# database.py
import sqlite3
import pandas as pd
from datetime import datetime
import streamlit as st
from config import DB_FILE
# from metrics import calculate_metrics # metricsを計算するために必要

# --- スキーマ定義 ---
TABLE_NAME = "asr_history"
SCHEMA = f'''
CREATE TABLE IF NOT EXISTS asr_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    audio_file TEXT,
    transcript TEXT,
    response_time REAL
)
'''

# --- データベース初期化 ---
def init_db():
    """データベースとテーブルを初期化する"""
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(SCHEMA)
        conn.commit()
        conn.close()
        print(f"Database '{DB_FILE}' initialized successfully.")
    except Exception as e:
        st.error(f"データベースの初期化に失敗しました: {e}")
        raise e # エラーを再発生させてアプリの起動を止めるか、適切に処理する

def save_to_db(audio_file, transcript, response_time):
    """音声ファイルの文字起こし結果をデータベースに保存する"""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute(f'''
        INSERT INTO {TABLE_NAME} (timestamp, audio_file, transcript, response_time)
        VALUES (?, ?, ?, ?)
        ''', (timestamp, audio_file, transcript, response_time))
        conn.commit()
        print("ASRデータ保存完了！")
    except sqlite3.Error as e:
        st.error(f"データベースへの保存中にエラーが発生しました: {e}")
    finally:
        if conn:
            conn.close()

def get_transcription_history():
    """文字起こし履歴を取得する"""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT * FROM asr_history ORDER BY timestamp DESC", conn)
        return df
    except sqlite3.Error as e:
        st.error(f"履歴の取得中にエラーが発生しました: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

def get_db_count():
    """データベース内のレコード数を取得する"""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        count = c.fetchone()[0]
        return count
    except sqlite3.Error as e:
        st.error(f"レコード数の取得中にエラーが発生しました: {e}")
        return 0
    finally:
        if conn:
            conn.close()

def clear_db():
    """データベースの全レコードを削除する"""
    conn = None
    confirmed = st.session_state.get("confirm_clear", False)

    if not confirmed:
        st.warning("本当にすべてのデータを削除しますか？もう一度「データベースをクリア」ボタンを押すと削除が実行されます。")
        st.session_state.confirm_clear = True
        return False # 削除は実行されなかった

    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(f"DELETE FROM {TABLE_NAME}")
        conn.commit()
        st.success("データベースが正常にクリアされました。")
        st.session_state.confirm_clear = False # 確認状態をリセット
        return True # 削除成功
    except sqlite3.Error as e:
        st.error(f"データベースのクリア中にエラーが発生しました: {e}")
        st.session_state.confirm_clear = False # エラー時もリセット
        return False # 削除失敗
    finally:
        if conn:
            conn.close()