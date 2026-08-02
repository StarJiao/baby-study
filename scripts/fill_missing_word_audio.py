#!/usr/bin/env python3
"""补齐缺失的汉字组词音频：基于现有 src/data/wordMap.ts，
只生成 public/audio/word/ 中缺失的 {char}.mp3。
已存在的文件会被跳过，不会重复生成。

依赖：pip install edge-tts pydub
用法：python scripts/fill_missing_word_audio.py
"""
import asyncio
import os
import re
import sys

try:
    import edge_tts
    from pydub import AudioSegment
except ImportError:
    print("缺少依赖，请先运行： pip install edge-tts pydub")
    sys.exit(1)

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
WORD_MAP_FILE = os.path.join(BASE_DIR, "src", "data", "wordMap.ts")
AUDIO_DIR = os.path.join(BASE_DIR, "public", "audio", "word")
VOICE = "zh-CN-XiaoxiaoNeural"
PAD_MS = 300


def parse_word_map():
    with open(WORD_MAP_FILE, encoding="utf-8") as f:
        text = f.read()
    return re.findall(r'"([^"]+)":\s*"([^"]+)"', text)


async def generate_one(char: str, word: str, path: str):
    communicate = edge_tts.Communicate(word, VOICE)
    tmp = path + ".tmp.mp3"
    await communicate.save(tmp)
    audio = AudioSegment.from_mp3(tmp)
    silence = AudioSegment.silent(duration=PAD_MS)
    (silence + audio + silence).export(path, format="mp3", bitrate="128k")
    os.remove(tmp)


async def main():
    os.makedirs(AUDIO_DIR, exist_ok=True)
    pairs = parse_word_map()
    existing = set(os.listdir(AUDIO_DIR))

    # 找出缺失项，并对每个失败项做有限次重试，避免瞬时网络错误留下缺口
    MAX_RETRY = 3
    missing = [(c, w) for c, w in pairs if f"{c}.mp3" not in existing]
    print(f"词映射总条数: {len(pairs)}，已存在音频: {len(existing)}，待补齐: {len(missing)}")

    if not missing:
        print("✅ 没有缺失，无需生成。")
        return

    sem = asyncio.Semaphore(8)

    async def process(char: str, word: str, i: int):
        async with sem:
            path = os.path.join(AUDIO_DIR, f"{char}.mp3")
            last_err = None
            for attempt in range(1, MAX_RETRY + 1):
                try:
                    await generate_one(char, word, path)
                    break
                except Exception as e:
                    last_err = e
                    if attempt < MAX_RETRY:
                        await asyncio.sleep(1.5 * attempt)
            else:
                print(f"  ⚠️ 最终失败: {char}->{word} ({last_err})")
                return
            if (i + 1) % 50 == 0 or i == len(missing) - 1:
                print(f"  进度: {i + 1}/{len(missing)}")

    await asyncio.gather(*(process(c, w, i) for i, (c, w) in enumerate(missing)))
    print(f"\n✅ 补齐完成！音频目录：{AUDIO_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
