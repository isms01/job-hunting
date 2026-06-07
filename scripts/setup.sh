#!/bin/bash
# scripts/setup.sh
# 初回セットアップ: uv のインストール、仮想環境構築、実行権限付与

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "🔧 job-hunting セットアップ開始..."
echo ""

# 1. Homebrew の確認
if ! command -v brew &>/dev/null; then
    echo "❌ Homebrew が見つかりません。先にインストールしてください: https://brew.sh"
        exit 1
        fi
        echo "✅ Homebrew: OK"

        # 2. sox のインストール（録音用）
        if ! command -v rec &>/dev/null; then
            echo "📦 sox をインストール中..."
                brew install sox
                else
                    echo "✅ sox: OK"
                    fi

                    # 3. uv のインストール
                    if ! command -v uv &>/dev/null; then
                        echo "📦 uv をインストール中..."
                            brew install uv
                            else
                                echo "✅ uv: OK"
                                fi

                                # 4. 仮想環境構築 + mlx-whisper インストール
                                echo "🐍 Python 仮想環境を構築中 (uv sync)..."
                                cd "$REPO_ROOT"
                                uv sync
                                echo "✅ 仮想環境: OK"

                                # 5. スクリプトに実行権限を付与
                                chmod +x "$REPO_ROOT/scripts/record_and_transcribe.sh"
                                echo "✅ 実行権限: OK"

                                echo ""
                                echo "🎉 セットアップ完了！"
                                echo ""
                                echo "次のコマンドで録音を開始できます:"
                                echo "  ./scripts/record_and_transcribe.sh"
                                
