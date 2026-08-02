#!/usr/bin/env python3
"""生成英语学习模块的音频文件（字母 + 单词），存放于 public/audio/en/

依赖：
    pip install edge-tts pydub

用法：
    python scripts/generate_english_audio.py
"""

import asyncio
import os
import sys
from typing import List

try:
    import edge_tts
    from pydub import AudioSegment
except ImportError as e:
    print("缺少依赖，请先运行： pip install edge-tts pydub")
    sys.exit(1)

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
AUDIO_DIR = os.path.join(BASE_DIR, "public", "audio", "en")

# 美式儿童友好女声
VOICE = "en-US-JennyNeural"
RATE = "-8%"
PITCH = "+3Hz"
PAD_MS = 300

# 26 个字母 + 每个字母配套的 3 个单词
# 与 src/data/letters.ts 保持同步
LETTER_WORDS = {
    "A": ["apple", "ant", "airplane"],
    "B": ["ball", "banana", "bear"],
    "C": ["cat", "car", "cake"],
    "D": ["dog", "duck", "door"],
    "E": ["elephant", "egg", "eye"],
    "F": ["fish", "flower", "frog"],
    "G": ["goat", "grape", "gift"],
    "H": ["house", "horse", "hand"],
    "I": ["ice", "ice cream", "igloo"],
    "J": ["juice", "jam", "jump"],
    "K": ["kite", "key", "king"],
    "L": ["lion", "leaf", "lamp"],
    "M": ["moon", "monkey", "milk"],
    "N": ["nose", "nest", "night"],
    "O": ["octopus", "orange", "owl"],
    "P": ["pig", "penguin", "pizza"],
    "Q": ["queen", "question", "quilt"],
    "R": ["rabbit", "rainbow", "robot"],
    "S": ["sun", "star", "snake"],
    "T": ["tree", "tiger", "train"],
    "U": ["umbrella", "unicorn", "up"],
    "V": ["violin", "van", "vegetable"],
    "W": ["water", "whale", "watch"],
    "X": ["xylophone", "box", "fox"],
    "Y": ["yellow", "yak", "yo-yo"],
    "Z": ["zebra", "zoo", "zero"],
}

# 待生成文本列表：字母（大写）与单词
TASKS: List[str] = []
for letter, words in LETTER_WORDS.items():
    TASKS.append(letter)
    TASKS.extend(words)


async def generate_audio(text: str, path: str):
    if os.path.exists(path):
        return
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
    tmp_path = path + ".tmp.mp3"
    await communicate.save(tmp_path)
    audio = AudioSegment.from_mp3(tmp_path)
    silence = AudioSegment.silent(duration=PAD_MS)
    padded = silence + audio + silence
    padded.export(path, format="mp3", bitrate="128k")
    os.remove(tmp_path)


async def main():
    os.makedirs(AUDIO_DIR, exist_ok=True)
    print(f"共 {len(TASKS)} 个待生成音频（26 字母 + {len(TASKS) - 26} 单词）\n")

    sem = asyncio.Semaphore(8)

    async def process(text: str, i: int):
        async with sem:
            path = os.path.join(AUDIO_DIR, f"{text}.mp3")
            await generate_audio(text, path)
            if (i + 1) % 20 == 0 or i == len(TASKS) - 1:
                print(f"  进度: {i + 1}/{len(TASKS)}")

    tasks = [process(t, i) for i, t in enumerate(TASKS)]
    await asyncio.gather(*tasks)

    print(f"\n✅ 完成！音频文件 → {AUDIO_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
