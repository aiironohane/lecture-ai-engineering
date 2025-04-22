# ASR.py
import os
import torch
from transformers import pipeline
import streamlit as st
import time
from config import MODEL_NAME
from huggingface_hub import login

# モデルをキャッシュして再利用
@st.cache_resource
def load_model():
    """ASRモデルをロードする"""
    try:

        # アクセストークンを保存
        hf_token = st.secrets["huggingface"]["token"]
        
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

def transcribe_audio(pipe, audio_path):
    """音声ファイルをWhisperで文字起こしする"""
    if pipe is None:
        return "モデルがロードされていないため、文字起こしできません。", 0

    try:
        start_time = time.time()
        result = pipe(audio_path)
        end_time = time.time()
        return result["text"], end_time - start_time
    except Exception as e:
        st.error(f"音声処理中にエラーが発生しました: {e}")
        return f"エラーが発生しました: {str(e)}", 0