#!/usr/bin/env python3
"""构建汉字→常见词映射，并生成组词音频"""
import asyncio
import json
import os
import re
from typing import Optional
import edge_tts
from pydub import AudioSegment

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
DATA_FILE = os.path.join(BASE_DIR, "src", "data", "syllables.ts")
OUT_TS = os.path.join(BASE_DIR, "src", "data", "wordMap.ts")
AUDIO_DIR = os.path.join(BASE_DIR, "public", "audio", "word")
VOICE = "zh-CN-XiaoxiaoNeural"
PAD_MS = 300  # 前后留白

# ── 预置常见双字词（按字索引） ──────────────────────────
# jieba 词典能覆盖大部分，但有些独字（如语助、姓氏）需要手动补全
MANUAL_MAP: dict[str, str] = {
    "大": "大人", "小": "小孩", "人": "人们", "天": "天空",
    "地": "土地", "水": "水果", "火": "火车", "风": "风筝",
    "日": "日期", "月": "月亮", "花": "花朵", "草": "草地",
    "树": "树木", "山": "高山", "石": "石头", "土": "泥土",
    "河": "河流", "海": "大海", "雨": "下雨", "雪": "雪花",
    "云": "白云", "星": "星星", "马": "马上", "牛": "牛奶",
    "羊": "山羊", "鸟": "小鸟", "鱼": "小鱼", "虫": "虫子",
    "狗": "小狗", "猫": "小猫", "虎": "老虎", "龙": "龙门",
    "蛇": "小蛇", "兔": "兔子", "猴": "猴子", "鸡": "鸡蛋",
    "鸭": "鸭子", "鹅": "白鹅", "猪": "小猪", "象": "大象",
    "熊": "小熊", "狼": "野狼", "鼠": "老鼠", "蛙": "青蛙",
    "手": "小手", "脚": "脚步", "头": "头发", "眼": "眼睛",
    "耳": "耳朵", "鼻": "鼻子", "口": "开口", "牙": "牙齿",
    "舌": "舌头", "脸": "笑脸", "腿": "小腿", "肚": "肚子",
    "爸": "爸爸", "妈": "妈妈", "哥": "哥哥", "弟": "弟弟",
    "姐": "姐姐", "妹": "妹妹", "爷": "爷爷", "奶": "奶奶",
    "儿": "儿子", "女": "女儿", "朋": "朋友", "友": "友善",
    "书": "书本", "笔": "铅笔", "纸": "纸张", "课": "上课",
    "学": "学习", "校": "学校", "班": "班级", "教": "教育",
    "字": "汉字", "读": "读书", "写": "写字", "算": "计算",
    "画": "画画", "唱": "唱歌", "跳": "跳舞", "跑": "跑步",
    "走": "走路", "坐": "坐下", "站": "站立", "看": "看见",
    "听": "听见", "说": "说话", "笑": "微笑", "哭": "哭了",
    "吃": "吃饭", "喝": "喝水", "睡": "睡觉", "起": "起床",
    "玩": "玩耍", "来": "回来", "去": "出去", "回": "回家",
    "开": "开门", "关": "关门", "上": "上午", "下": "下午",
    "左": "左边", "右": "右边", "前": "前面", "后": "后面",
    "里": "里面", "外": "外面", "春": "春天", "夏": "夏天",
    "秋": "秋天", "冬": "冬天", "热": "热水", "冷": "冷风",
    "高": "高大", "低": "低头", "长": "长大", "短": "短小",
    "快": "赶快", "慢": "慢慢", "多": "多少", "少": "少年",
    "大": "大人", "好": "好人", "新": "新年", "旧": "旧书",
    "红": "红色", "黄": "黄色", "蓝": "蓝天", "绿": "绿叶",
    "白": "白色", "黑": "黑夜", "一": "一步", "二": "二月",
    "三": "三个", "四": "四季", "五": "五月", "六": "六个",
    "七": "七月", "八": "八月", "九": "九月", "十": "十个",
    "百": "百姓", "千": "千万", "万": "万一", "这": "这个",
    "那": "那个", "哪": "哪里", "谁": "谁家", "什": "什么",
    "么": "什么", "怎": "怎么", "都": "都有", "很": "很好",
    "也": "也是", "还": "还是", "就": "就是", "会": "开会",
    "在": "现在", "有": "没有", "是": "是的", "不": "不是",
    "没": "没有", "了": "好了", "着": "着迷", "过": "过去",
    "的": "目的", "地": "地点", "得": "得到", "和": "和平",
    "与": "与其", "为": "为了", "以": "以后", "被": "被打",
    "把": "把握", "从": "从前", "对": "对方", "向": "方向",
    "到": "到达", "让": "让开", "给": "送给", "用": "有用",
    "情": "心情", "感": "感情", "想": "想法", "爱": "爱心",
    "喜": "喜欢", "乐": "快乐", "安": "安全", "美": "美丽",
    "光": "阳光", "明": "明天", "亮": "明亮", "声": "声音",
    "音": "音乐", "话": "说话", "文": "文字", "语": "语言",
    "国": "国家", "家": "大家", "城": "城市", "路": "马路",
    "车": "汽车", "船": "小船", "门": "大门", "屋": "屋子",
    "桌": "桌子", "椅": "椅子", "床": "起床", "灯": "灯光",
    "衣": "衣服", "鞋": "鞋子", "帽": "帽子", "包": "书包",
    "于": "于是",
    # ── 补充前 100 高频字中缺失的组词 ──
    "中": "中间", "年": "新年", "业": "作业", "工": "工人",
    "经": "经过", "市": "城市", "要": "需要", "产": "生产",
    "出": "出来", "行": "行走", "生": "生活", "成": "成长",
    "民": "人民", "我": "我们", "部": "部分", "进": "进步",
    "全": "全部", "建": "建设", "他": "他们", "公": "公园",
    "们": "我们", "场": "广场", "展": "展开", "时": "时间",
    "理": "道理", "方": "地方", "主": "主人", "实": "真实",
    "报": "报纸", "制": "制作", "政": "政治", "济": "经济",
    "同": "同学", "法": "方法", "现": "现在", "本": "书本",
    "定": "一定", "动": "动作", "合": "合作", "品": "作品",
    "重": "重要", "机": "机会", "分": "分开", "力": "力气",
    "自": "自己", "者": "记者", "能": "能力", "设": "设计",
    "等": "等待", "体": "身体", "社": "社会", "面": "前面",
}

def get_manual_word(char):
    return MANUAL_MAP.get(char)


# ── 从源代码解析音节汉字 ─────────────────────────────
def parse_syllables():
    with open(DATA_FILE, encoding="utf-8") as f:
        text = f.read()
    # 匹配 { word: "X", ... pinyin: "Y" ... }
    items = re.findall(
        r'\{[^}]*word:\s*"([^"]+)"[^}]*pinyin:\s*"([^"]+)"[^}]*\}',
        text,
    )
    return items


# ── 生成词映射 TS 文件 ────────────────────────────────
def build_word_map():
    items = parse_syllables()
    word_map: dict[str, str] = {}

    print(f"解析到 {len(items)} 个音节条目")

    for word, pinyin_str in items:
        if word in word_map:
            continue
        manual = get_manual_word(word)
        if manual:
            word_map[word] = manual
        else:
            # 回退：双写（如 鸟→小鸟）
            word_map[word] = f"小{word}" if len(word) == 1 else word

    # 补全 MANUAL_MAP 中可能遗漏的字
    for ch, wrd in MANUAL_MAP.items():
        if ch not in word_map:
            word_map[ch] = wrd

    # 生成 TS 文件
    lines = ["// 自动生成 — 汉字 → 常见组词（用于点击「词」发音）"]
    lines.append("export const charWordMap: Record<string, string> = {")
    for ch, wrd in sorted(word_map.items(), key=lambda x: x[0]):
        lines.append(f'  "{ch}": "{wrd}",')
    lines.append("};")
    lines.append("")

    os.makedirs(os.path.dirname(OUT_TS), exist_ok=True)
    with open(OUT_TS, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"词映射已写入 {OUT_TS}（{len(word_map)} 条）")
    return word_map


# ── 生成组词音频 ──────────────────────────────────────
async def generate_word_audio(word_map: dict[str, str]):
    os.makedirs(AUDIO_DIR, exist_ok=True)
    total = len(word_map)
    print(f"\n开始生成组词音频（共 {total} 个）...")

    for i, (char, group_word) in enumerate(word_map.items()):
        path = os.path.join(AUDIO_DIR, f"{char}.mp3")
        if os.path.exists(path):
            if (i + 1) % 100 == 0:
                print(f"  进度: {i+1}/{total}")
            continue

        communicate = edge_tts.Communicate(group_word, VOICE)
        tmp = path + ".tmp.mp3"
        await communicate.save(tmp)
        audio = AudioSegment.from_mp3(tmp)
        silence = AudioSegment.silent(duration=PAD_MS)
        padded = silence + audio + silence
        padded.export(path, format="mp3", bitrate="128k")
        os.remove(tmp)

        if (i + 1) % 50 == 0:
            print(f"  进度: {i+1}/{total}")

    print(f"\n组词音频完成！已生成到 {AUDIO_DIR}/")


# ── main ─────────────────────────────────────────────
async def main():
    word_map = build_word_map()
    await generate_word_audio(word_map)
    print("全部完成！")


if __name__ == "__main__":
    asyncio.run(main())
