#!/usr/bin/env python3
"""生成 500 个常用汉字的拼音数据和音频文件"""

import asyncio
import json
import os
import re
from typing import Optional
import edge_tts
from pypinyin import pinyin, Style

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
AUDIO_DIR = os.path.join(BASE_DIR, "public", "audio")
DATA_FILE = os.path.join(BASE_DIR, "src", "data", "syllables.ts")
VOICE = "zh-CN-XiaoxiaoNeural"
RATE = "-10%"
PITCH = "+5Hz"

# 现代汉语 ~500 个最常用汉字（按频率排序，覆盖 ~78% 日常使用）
COMMON_CHARS = list(
    "的是一了不在有人这我他她它来们说上下去出得和那还要里到为着时也能自"
    "过大用对所动然起行面样分其生子以家成天可想法经年当种前水回开都两"
    "多力如学高实把重做已从些心但又战事者之关进小公老己定而体理气明机"
    "好知同等手现道长意看量相外物全头将十向新政变正没文地主或无问部日"
    "点并比第法提制度五系见性眼安只马被光产教军使工极此各次本样合路"
    "给记话经场及最山门流做看面内很海月原住位建走品运题计习数"
    "管吃通强结外处改真风思表花任老反平三台色代意见但体文解"
    "心部间关说石至式五方百边级角利要拉打示认特指导林题"
    "活入目口手眼常白同如业又家叫代件干记少高车张无气"
    "展受最政头字万斯圆器收引路听处太织任品保安火完金况步"
    "南教变团报即基求离候省府速号装克更度青矿背统会科"
    "性新身表情取明生中直机象世言尔两争电星门半照写接连孩究治决极具"
    "张市府队省消志界必般难先才准算管精社什且任基续红投激识达容存专反较"
    "效式切造苦约观非领段众运德美格易空民算今团总品克历原卫要百"
    "整希单司连引科解消复此示员史厂响类许苏容院列级状夜型跟建育"
    "花歌满状望坚晚落试近领布群故速亚德似排讲研版温设低感母"
    "办选况按技病制找革获历图改青委各显终热著普统传黄织"
    "宝笑答随请养装视足兵义斗素验善坚助句备准负么师怕吸洋验"
    "洲查娘故环树努升续按印姐罗苦疑般米织修范买江某继奇层急"
    "乡营坚试供洲即球额杀钢黑顶轴源异余免块布武况刻谋属针饭降"
    "愿拿脑章汽换演评承职请雨土精止复维鼓属优河措防旧脱律业食"
    "虽读越承构散背静具监站播终验般值预需细适济属庆量秋"
    "创叶输右显草未枪述距板独李功退序责亮男露招味纪唯充保圆谓"
    "若疑银角坚玉坐曾跑赶朗优章角养汽队响弹升盘答形共排富初坚尊"
)

# 高频口语字 + 覆盖面补充
EXTRA_CHARS = list(
    "啊哦嗯嗨哎呀吧呢啦嘛哇呵咦呜嘿吼啧嘀咚咔嚓嘶咕喵哼咿哐砰唰哗"
    "桌椅师同爸妈哥姐姐弟妹吃玩画唱跳跑游泳洗澡睡觉"
    "红黄蓝绿黑白大小高矮胖瘦长短粗细冷热"
    "甜酸苦辣咸香臭好坏真假美丑新旧快慢远近左右"
    "春夏秋冬风雨雪晴阴雷电云冰雾霜露早晚午深夜"
    "村城镇街巷弄路桥楼房屋厅堂廊阁院园亭台塔"
    "金银铜铁锡铅锌锰硫磷碳氮氧氢氦氖氩硅钙钾钠镁铝"
    "笔墨纸砚书画琴棋歌舞诗词曲赋对联谜语"
    "男女老少幼童婴孩足首颈肩臂腿脚趾肝肺肾胃肠脑心"
    "叶根茎花果种籽芽苗树森林草竹梅兰菊莲荷桃杏梨"
    "江海河湖溪泉池潭浪潮波涛瀑布川"
    "风雨雷电雪霜雾霾冰雹露彩霞虹"
    "猫狗鸡鸭鹅猪牛羊马兔蛇鼠龙虎狮象鹰燕鸽"
    "酸甜苦辣咸淡鲜麻酥脆软硬黏滑粗糙"
    "东西南北中前后左右里外上下旁"
    "酸甜苦辣咸淡鲜香臭味觉"
)

ALL_CHARS = list(dict.fromkeys(COMMON_CHARS + EXTRA_CHARS))  # 去重


def split_pinyin(py_tone: str, py_num: str) -> Optional[dict]:
    """将拼音拆分为 声母+韵母+声调"""
    if not py_tone or not py_num:
        return None

    # 提取声调数字
    tone_match = re.search(r"(\d)$", py_num)
    tone = int(tone_match.group(1)) if tone_match else 0
    bare = re.sub(r"\d$", "", py_num)  # 去掉数字的拼音

    # 零声母字
    zero_initial_map = {
        "a": "a", "o": "o", "e": "e",
        "ai": "ai", "ei": "ei", "ao": "ao", "ou": "ou",
        "an": "an", "en": "en", "ang": "ang", "eng": "eng", "ong": "ong",
        "er": "er",
        "yi": "i", "ya": "ia", "ye": "ie", "yao": "iao",
        "you": "iu", "yan": "ian", "yin": "in", "yang": "iang", "ying": "ing",
        "yong": "iong",
        "wu": "u", "wa": "ua", "wo": "uo", "wai": "uai", "wei": "ui",
        "wan": "uan", "wen": "un", "wang": "uang", "weng": "ueng",
        "yu": "ü", "yue": "üe", "yuan": "üan", "yun": "ün",
    }

    if bare in zero_initial_map:
        return {"initial": "", "final": zero_initial_map[bare], "tone": tone}

    # 有声母
    initials_list = [
        "zh", "ch", "sh",  # 翘舌
        "b", "p", "m", "f", "d", "t", "n", "l",
        "g", "k", "h", "j", "q", "x",
        "z", "c", "s", "r", "y", "w",
    ]
    for init in sorted(initials_list, key=len, reverse=True):
        if bare.startswith(init):
            return {"initial": init, "final": bare[len(init):], "tone": tone}

    return None


async def generate_audio(word: str, path: str):
    """生成单个音频文件"""
    if os.path.exists(path):
        return
    communicate = edge_tts.Communicate(word, VOICE, rate=RATE, pitch=PITCH)
    await communicate.save(path)


async def main():
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

    syllables = []
    errors = []

    print(f"共 {len(ALL_CHARS)} 个待处理汉字\n")

    # 先用 pypinyin 批量获取拼音
    words = ALL_CHARS
    tones = pinyin(words, style=Style.TONE)      # 带声调，如 bā
    nums = pinyin(words, style=Style.TONE3)      # 带数字，如 ba1

    print("开始生成音频...")
    sem = asyncio.Semaphore(8)  # 并发限制

    async def process_one(i: int):
        async with sem:
            word = words[i]
            py_tone = tones[i][0]
            py_num = nums[i][0]

            parsed = split_pinyin(py_tone, py_num)
            if not parsed:
                errors.append(f"无法解析: {word} ({py_tone}/{py_num})")
                return

            syllables.append({
                "word": word,
                "pinyin": py_tone,
                "initial": parsed["initial"],
                "final": parsed["final"],
                "tone": parsed["tone"],
            })

            # 生成音频
            path = os.path.join(AUDIO_DIR, f"{word}.mp3")
            await generate_audio(word, path)
            if (i + 1) % 50 == 0 or i == len(words) - 1:
                print(f"  进度: {i + 1}/{len(words)}")

    tasks = [process_one(i) for i in range(len(words))]
    await asyncio.gather(*tasks)

    # 写入 TypeScript 数据文件
    ts_lines = [
        "// 自动生成 —— 常用汉字音节数据",
        "// 运行 scripts/generate_audio.py 重新生成",
        "",
        "export interface Syllable {",
        "  word: string",
        "  pinyin: string",
        "  initial: string",
        "  final: string",
        "  tone: number",
        "}",
        "",
        f"export const syllables: Syllable[] = {json.dumps(syllables, ensure_ascii=False, indent=2)}",
        "",
    ]
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(ts_lines))

    print(f"\n✅ 完成！")
    print(f"   音节数据: {len(syllables)} 个 → {DATA_FILE}")
    print(f"   音频文件: {len(syllables)} 个 → {AUDIO_DIR}/")
    if errors:
        print(f"   ⚠️  解析失败 {len(errors)} 个:")
        for e in errors:
            print(f"      {e}")


if __name__ == "__main__":
    asyncio.run(main())
