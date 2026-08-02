#!/usr/bin/env python3
"""构建后校验：检查数据里引用到的音频文件是否都已生成。

校验范围（与 generate_audio.py / fill_missing_word_audio.py / generate_english_audio.py 对应）：
  1. 汉字单字音频   public/audio/{char}.mp3            <- src/data/syllables.ts
  2. 汉字组词音频   public/audio/word/{char}.mp3       <- src/data/wordMap.ts
  3. 英语字母/单词  public/audio/en/{name}.mp3          <- src/data/letters.ts

若有缺失，打印清单并以非零退出码结束（使 npm run build 失败）。
依赖：仅标准库。
用法：python scripts/check_audio.py
"""
import os
import re
import sys

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
AUDIO_ROOT = os.path.join(BASE_DIR, "public", "audio")
SRC_DIR = os.path.join(BASE_DIR, "src", "data")


def read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def missing(base_dir: str, names: list[str]) -> list[str]:
    existing = set(os.listdir(base_dir)) if os.path.isdir(base_dir) else set()
    return [n for n in names if f"{n}.mp3" not in existing]


problems: list[tuple[str, list[str]]] = []

# 1. 汉字单字音频
syllables_txt = read(os.path.join(SRC_DIR, "syllables.ts"))
chars = re.findall(r'word:\s*"([^"]+)"', syllables_txt)
m = missing(AUDIO_ROOT, chars)
if m:
    problems.append(("汉字单字音频 public/audio/{char}.mp3", m))

# 2. 组词音频
wordmap_txt = read(os.path.join(SRC_DIR, "wordMap.ts"))
words = [c for c, _ in re.findall(r'"([^"]+)":\s*"([^"]+)"', wordmap_txt)]
m = missing(os.path.join(AUDIO_ROOT, "word"), words)
if m:
    problems.append(("组词音频 public/audio/word/{char}.mp3", m))

# 3. 英语音频（字母 + 单词）
letters_txt = read(os.path.join(SRC_DIR, "letters.ts"))
en_letters = re.findall(r"letter:\s*'([A-Z])'", letters_txt)
en_words = re.findall(r"word:\s*'([^']+)'", letters_txt)
en_names = en_letters + en_words
m = missing(os.path.join(AUDIO_ROOT, "en"), en_names)
if m:
    problems.append(("英语音频 public/audio/en/{name}.mp3", m))

if not problems:
    print("✅ 音频校验通过：所有数据引用的音频文件均已生成。")
    sys.exit(0)

total = sum(len(m) for _, m in problems)
print(f"❌ 音频校验失败：共缺失 {total} 个音频文件\n")
for label, ms in problems:
    print(f"  [{label}] 缺失 {len(ms)} 个，例如：{', '.join(ms[:10])}")
print("\n修复方式（按需运行）：")
print("  汉字单字： python scripts/generate_audio.py")
print("  组词音频： python scripts/fill_missing_word_audio.py")
print("  英语音频： python scripts/generate_english_audio.py")
sys.exit(1)
