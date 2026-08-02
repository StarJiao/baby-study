#!/usr/bin/env python3
"""生成鼓励语和结果语的新音频文件"""
import asyncio
import os
import edge_tts
from pydub import AudioSegment

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
AUDIO_DIR = os.path.join(BASE_DIR, "public", "audio")
VOICE = "zh-CN-XiaoxiaoNeural"
RATE = "-10%"
PITCH = "+5Hz"
PAD_MS = 300

# 需要新生成的文件
TEXTS = [
    ("encourage_再试试", "再试试"),
    ("result_再接再厉哦", "再接再厉哦"),
]


async def generate_one(filename: str, text: str):
    path = os.path.join(AUDIO_DIR, f"{filename}.mp3")
    if os.path.exists(path):
        print(f"  已存在，跳过: {filename}.mp3")
        return
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
    tmp_path = path + ".tmp.mp3"
    await communicate.save(tmp_path)
    audio = AudioSegment.from_mp3(tmp_path)
    silence = AudioSegment.silent(duration=PAD_MS)
    padded = silence + audio + silence
    padded.export(path, format="mp3", bitrate="128k")
    os.remove(tmp_path)
    print(f"  生成完成: {filename}.mp3")


async def main():
    os.makedirs(AUDIO_DIR, exist_ok=True)
    print("生成鼓励/结果音频...\n")
    for filename, text in TEXTS:
        await generate_one(filename, text)
    print("\n完成！")


if __name__ == "__main__":
    asyncio.run(main())
