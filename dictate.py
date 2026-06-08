#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "mlx-whisper",
#   "sounddevice",
#   "numpy",
#   "soundfile",
#   "scipy",
# ]
# ///
"""
音声録音 → Whisper large-v3 (MLX) 文字起こし → input/dictations/ 保存
M1 Mac 最適化: mlx-whisper を使用

実行方法:
    uv run dictate.py
"""

import argparse
import datetime
import os
import queue
import sys

import mlx_whisper
import numpy as np
import scipy.signal as signal
import sounddevice as sd
import soundfile as sf

# ---- 設定 ----------------------------------------------------------------
MODEL_ID = "mlx-community/whisper-large-v3-mlx"
SAMPLE_RATE = 16000          # Whisper が要求するサンプルレート
CHANNELS = 1
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "input", "dictations")
# --------------------------------------------------------------------------


def record_until_enter(sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """Enter キーを押すまで録音し、音声データ (float32) を返す。"""
    audio_queue: queue.Queue = queue.Queue()

    def callback(indata, frames, time_info, status):
        if status:
            print(f"[warn] {status}", file=sys.stderr)
        audio_queue.put(indata.copy())

    print("録音を開始します。終了するには Enter キーを押してください...", flush=True)
    stream = sd.InputStream(
        samplerate=sample_rate,
        channels=CHANNELS,
        dtype="float32",
        callback=callback,
    )
    stream.start()

    input()  # Enter 待ち

    stream.stop()
    stream.close()

    chunks = []
    while not audio_queue.empty():
        chunks.append(audio_queue.get())

    if not chunks:
        print("音声データが空です。マイクを確認してください。", file=sys.stderr)
        sys.exit(1)

    audio = np.concatenate(chunks, axis=0).flatten()
    duration = len(audio) / sample_rate
    print(f"録音完了: {duration:.1f} 秒")
    return audio


def transcribe(audio: np.ndarray) -> str:
    """mlx-whisper で文字起こしし、テキストを返す。"""
    print(f"文字起こし中 (モデル: {MODEL_ID}) ...")
    result = mlx_whisper.transcribe(
        audio,
        path_or_hf_repo=MODEL_ID,
        language="ja",
        verbose=False,
    )
    return result["text"].strip()


def save_text(text: str) -> str:
    """日付時刻ファイル名で output_dir に保存し、ファイルパスを返す。"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(OUTPUT_DIR, f"{timestamp}.txt")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    return filepath


def main():
    parser = argparse.ArgumentParser(description="音声ディクテーション → テキスト保存")
    parser.add_argument(
        "--file", "-f",
        metavar="AUDIO_FILE",
        help="録音済みの音声ファイルを文字起こしする場合に指定 (WAV/MP3 等)",
    )
    args = parser.parse_args()

    if args.file:
        # ファイルモード: 既存音声を文字起こし
        audio, sr = sf.read(args.file, dtype="float32")
        if audio.ndim > 1:
            audio = audio.mean(axis=1)  # ステレオ → モノラル
        if sr != SAMPLE_RATE:
            # 簡易リサンプル (精度が必要なら librosa.resample を使うこと)
            audio = signal.resample(audio, int(len(audio) * SAMPLE_RATE / sr))
    else:
        # マイク録音モード
        audio = record_until_enter()

    text = transcribe(audio)

    if not text:
        print("文字起こし結果が空でした。")
        sys.exit(1)

    filepath = save_text(text)
    print(f"\n--- 文字起こし結果 ---\n{text}\n")
    print(f"保存先: {filepath}")


if __name__ == "__main__":
    main()
