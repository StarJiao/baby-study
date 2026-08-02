// 英语学习数据 —— 26 个字母 + 每个字母配套常见单词（具象名词为主，面向低龄儿童）
// emoji 作为离线卡通插图；音频由 scripts/generate_english_audio.py 生成到 public/audio/en/

export interface EnglishWord {
  word: string        // 英文单词
  emoji: string       // 卡通插图（系统 emoji，无需额外资源）
  cn: string          // 中文释义
}

export interface LetterEntry {
  letter: string      // 大写字母 A-Z
  lower: string       // 小写字母 a-z
  emoji: string       // 该字母代表性 emoji（与首词呼应）
  words: EnglishWord[] // 配套常见词
}

export const letters: LetterEntry[] = [
  {
    letter: 'A', lower: 'a', emoji: '🍎',
    words: [
      { word: 'apple', emoji: '🍎', cn: '苹果' },
      { word: 'ant', emoji: '🐜', cn: '蚂蚁' },
      { word: 'airplane', emoji: '✈️', cn: '飞机' },
    ],
  },
  {
    letter: 'B', lower: 'b', emoji: '🏀',
    words: [
      { word: 'ball', emoji: '⚽', cn: '球' },
      { word: 'banana', emoji: '🍌', cn: '香蕉' },
      { word: 'bear', emoji: '🐻', cn: '熊' },
    ],
  },
  {
    letter: 'C', lower: 'c', emoji: '🐱',
    words: [
      { word: 'cat', emoji: '🐱', cn: '猫' },
      { word: 'car', emoji: '🚗', cn: '汽车' },
      { word: 'cake', emoji: '🍰', cn: '蛋糕' },
    ],
  },
  {
    letter: 'D', lower: 'd', emoji: '🐶',
    words: [
      { word: 'dog', emoji: '🐶', cn: '狗' },
      { word: 'duck', emoji: '🦆', cn: '鸭子' },
      { word: 'door', emoji: '🚪', cn: '门' },
    ],
  },
  {
    letter: 'E', lower: 'e', emoji: '🐘',
    words: [
      { word: 'elephant', emoji: '🐘', cn: '大象' },
      { word: 'egg', emoji: '🥚', cn: '鸡蛋' },
      { word: 'eye', emoji: '👁️', cn: '眼睛' },
    ],
  },
  {
    letter: 'F', lower: 'f', emoji: '🐸',
    words: [
      { word: 'fish', emoji: '🐟', cn: '鱼' },
      { word: 'flower', emoji: '🌸', cn: '花' },
      { word: 'frog', emoji: '🐸', cn: '青蛙' },
    ],
  },
  {
    letter: 'G', lower: 'g', emoji: '🍇',
    words: [
      { word: 'goat', emoji: '🐐', cn: '山羊' },
      { word: 'grape', emoji: '🍇', cn: '葡萄' },
      { word: 'gift', emoji: '🎁', cn: '礼物' },
    ],
  },
  {
    letter: 'H', lower: 'h', emoji: '🏠',
    words: [
      { word: 'house', emoji: '🏠', cn: '房子' },
      { word: 'horse', emoji: '🐴', cn: '马' },
      { word: 'hand', emoji: '✋', cn: '手' },
    ],
  },
  {
    letter: 'I', lower: 'i', emoji: '🍦',
    words: [
      { word: 'ice', emoji: '🧊', cn: '冰' },
      { word: 'ice cream', emoji: '🍦', cn: '冰淇淋' },
      { word: 'igloo', emoji: '🛖', cn: '冰屋' },
    ],
  },
  {
    letter: 'J', lower: 'j', emoji: '🤹',
    words: [
      { word: 'juice', emoji: '🧃', cn: '果汁' },
      { word: 'jam', emoji: '🍯', cn: '果酱' },
      { word: 'jump', emoji: '🤸', cn: '跳' },
    ],
  },
  {
    letter: 'K', lower: 'k', emoji: '🔑',
    words: [
      { word: 'kite', emoji: '🪁', cn: '风筝' },
      { word: 'key', emoji: '🔑', cn: '钥匙' },
      { word: 'king', emoji: '🤴', cn: '国王' },
    ],
  },
  {
    letter: 'L', lower: 'l', emoji: '🦁',
    words: [
      { word: 'lion', emoji: '🦁', cn: '狮子' },
      { word: 'leaf', emoji: '🍃', cn: '树叶' },
      { word: 'lamp', emoji: '💡', cn: '台灯' },
    ],
  },
  {
    letter: 'M', lower: 'm', emoji: '🌙',
    words: [
      { word: 'moon', emoji: '🌙', cn: '月亮' },
      { word: 'monkey', emoji: '🐵', cn: '猴子' },
      { word: 'milk', emoji: '🥛', cn: '牛奶' },
    ],
  },
  {
    letter: 'N', lower: 'n', emoji: '🪺',
    words: [
      { word: 'nose', emoji: '👃', cn: '鼻子' },
      { word: 'nest', emoji: '🪺', cn: '鸟巢' },
      { word: 'night', emoji: '🌌', cn: '夜晚' },
    ],
  },
  {
    letter: 'O', lower: 'o', emoji: '🐙',
    words: [
      { word: 'octopus', emoji: '🐙', cn: '章鱼' },
      { word: 'orange', emoji: '🍊', cn: '橘子' },
      { word: 'owl', emoji: '🦉', cn: '猫头鹰' },
    ],
  },
  {
    letter: 'P', lower: 'p', emoji: '🐧',
    words: [
      { word: 'pig', emoji: '🐷', cn: '猪' },
      { word: 'penguin', emoji: '🐧', cn: '企鹅' },
      { word: 'pizza', emoji: '🍕', cn: '披萨' },
    ],
  },
  {
    letter: 'Q', lower: 'q', emoji: '👑',
    words: [
      { word: 'queen', emoji: '👑', cn: '女王' },
      { word: 'question', emoji: '❓', cn: '问题' },
      { word: 'quilt', emoji: '🛏️', cn: '被子' },
    ],
  },
  {
    letter: 'R', lower: 'r', emoji: '🌈',
    words: [
      { word: 'rabbit', emoji: '🐰', cn: '兔子' },
      { word: 'rainbow', emoji: '🌈', cn: '彩虹' },
      { word: 'robot', emoji: '🤖', cn: '机器人' },
    ],
  },
  {
    letter: 'S', lower: 's', emoji: '⭐',
    words: [
      { word: 'sun', emoji: '☀️', cn: '太阳' },
      { word: 'star', emoji: '⭐', cn: '星星' },
      { word: 'snake', emoji: '🐍', cn: '蛇' },
    ],
  },
  {
    letter: 'T', lower: 't', emoji: '🌳',
    words: [
      { word: 'tree', emoji: '🌳', cn: '树' },
      { word: 'tiger', emoji: '🐯', cn: '老虎' },
      { word: 'train', emoji: '🚂', cn: '火车' },
    ],
  },
  {
    letter: 'U', lower: 'u', emoji: '☂️',
    words: [
      { word: 'umbrella', emoji: '☂️', cn: '雨伞' },
      { word: 'unicorn', emoji: '🦄', cn: '独角兽' },
      { word: 'up', emoji: '⬆️', cn: '向上' },
    ],
  },
  {
    letter: 'V', lower: 'v', emoji: '🎻',
    words: [
      { word: 'violin', emoji: '🎻', cn: '小提琴' },
      { word: 'van', emoji: '🚐', cn: '面包车' },
      { word: 'vegetable', emoji: '🥦', cn: '蔬菜' },
    ],
  },
  {
    letter: 'W', lower: 'w', emoji: '🐋',
    words: [
      { word: 'water', emoji: '💧', cn: '水' },
      { word: 'whale', emoji: '🐋', cn: '鲸鱼' },
      { word: 'watch', emoji: '⌚', cn: '手表' },
    ],
  },
  {
    letter: 'X', lower: 'x', emoji: '🎶',
    words: [
      { word: 'xylophone', emoji: '🎼', cn: '木琴' },
      { word: 'box', emoji: '📦', cn: '盒子' },
      { word: 'fox', emoji: '🦊', cn: '狐狸' },
    ],
  },
  {
    letter: 'Y', lower: 'y', emoji: '🪀',
    words: [
      { word: 'yellow', emoji: '💛', cn: '黄色' },
      { word: 'yak', emoji: '🐃', cn: '牦牛' },
      { word: 'yo-yo', emoji: '🪀', cn: '悠悠球' },
    ],
  },
  {
    letter: 'Z', lower: 'z', emoji: '🦁',
    words: [
      { word: 'zebra', emoji: '🦓', cn: '斑马' },
      { word: 'zoo', emoji: '🦁', cn: '动物园' },
      { word: 'zero', emoji: '0️⃣', cn: '零' },
    ],
  },
]
