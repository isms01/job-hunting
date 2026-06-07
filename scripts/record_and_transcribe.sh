#!/bin/bash
# scripts/record_and_transcribe.sh
# 音声を録音してWhisper (mlx) で文字起こしし、input/dictations/ に保存する

set -e

DATE=$(date +%Y%m%d_%H%M%S)
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DICTATIONS_DIR="$REPO_ROOT/input/dictations"
AUDIO_FILE="/tmp/dictation_$DATE.wav"
OUTPUT_FILE="$DICTATIONS_DIR/dictation_$DATE.md"

mkdir -p "$DICTATIONS_DIR"

echo "🎙️  録音開始... Enterで停止"
rec -r 16000 -c 1 -b 16 "$AUDIO_FILE" &
REC_PID=$!
read -r
kill $REC_PID
wait $REC_PID 2>/dev/null || true

echo "📝 文字起こし中 (whisper-mlx / large-v3)..."
python3 - <<EOF
import mlx_whisper, os

result = mlx_whisper.transcribe(
    "$AUDIO_FILE",
        path_or_hf_repo="mlx-community/whisper-large-v3-mlx",
            language="ja"
            )
            text = result["text"].strip()

            os.makedirs("$DICTATIONS_DIR", exist_ok=True)
            with open("$OUTPUT_FILE", "w") as f:
                f.write("# Dictation $DATE\n\n")
                    f.write(text + "\n")
                    EOF

                    echo ""
                    echo "✅ 保存完了: $OUTPUT_FILE"
                    echo ""
                    cat "$OUTPUT_FILE"
                    echo ""

                    cd "$REPO_ROOT"
                    git add "$OUTPUT_FILE"
                    echo "💡 内容を確認後: git commit -m 'add dictation $DATE'"
                    
