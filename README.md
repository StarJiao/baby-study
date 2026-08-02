# 儿童学习 App（Vue 3 + TypeScript）

一个面向低龄儿童的趣味学习 Web 应用，包含**计算练习、拼音学习、汉字初识**三大功能模块，并预留「英语学习」入口。采用 Vue 3 `<script setup>` + Vite + TypeScript 构建，UI 风格统一、色彩明快、交互以「点击大按钮 + 语音朗读」为主，适配触屏与键盘操作。

---

## 技术栈

- **框架**：Vue 3（`<script setup>` SFC）
- **语言**：TypeScript（`vue-tsc` 类型检查）
- **构建**：Vite（`base: './'`，产物可静态部署到任意子路径）
- **图标**：[lucide-vue-next](https://lucide.dev/)（线性图标）
- **笔顺动画**：[hanzi-writer](https://hanziwriter.org/)（通过 CDN 动态加载 `hanzi-writer.min.js`）
- **语音合成（离线生成）**：Python 脚本调用 `edge-tts` + `pypinyin` + `pydub` 预生成 `public/audio/**.mp3`，运行时用 `<audio>` 播放，避免依赖浏览器在线 TTS

---

## 目录结构

```
study/
├── index.html                 # 应用入口 HTML
├── vite.config.ts             # Vite 配置（base:'./'）
├── tsconfig*.json             # TypeScript 配置
├── package.json               # 依赖与脚本
│
├── public/
│   └── audio/                 # 预生成的语音音频（由脚本生成，勿手改）
│       ├── *.mp3              # 单字/词语/鼓励语等音频
│       └── word/              # 单字音频：word/<汉字>.mp3（如 word/头.mp3）
│
├── scripts/                   # 数据 & 音频生成脚本（Python，需 edge-tts 等依赖）
│   ├── generate_audio.py      # 生成常用汉字音节数据(src/data/syllables.ts) + 音频
│   ├── build_word_map.py      # 构建 汉字→组词 映射(wordMap.ts) + 组词音频
│   └── generate_encourage_result.py  # 生成鼓励语/结果语音频
│
└── src/
    ├── main.ts                # 应用挂载入口
    ├── App.vue                # 根组件：大厅/各功能页切换（keep-alive 缓存）
    ├── style.css              # 全局样式（含 CSS 变量、通用类 .btn 等）
    ├── components/
    │   ├── GameLobby.vue      # 功能大厅：模块卡片网格 + 返回主页
    │   ├── CalculationTool.vue# 计算练习：加减法运算
    │   ├── PinyinTool.vue     # 拼音学习：听音辨音 / 拼读闯关 / 认音识字
    │   ├── CharacterTool.vue  # 汉字初识：字卡闪卡 + 笔顺动画 + 组词
    │   └── ToolSidebar.vue    # （保留组件，当前未在大厅路由中使用）
    │
    └── data/
        ├── syllables.ts       # 常用汉字音节数据（自动生成，勿手改）
        └── wordMap.ts         # 汉字→组词 映射（手工维护的主数据）
```

> ⚠️ `src/data/syllables.ts` 由 `scripts/generate_audio.py` 自动生成，**不要直接编辑**；如需增删汉字请改脚本后重新生成。`wordMap.ts` 为手工维护数据，可直接编辑补词。

---

## 路由与页面切换

- `App.vue` 用 `currentView` ref 在「大厅(`GameLobby`)」与各功能组件间切换。
- 各功能组件通过 `emit('back')` 返回大厅。
- 功能组件用 `<keep-alive>` 包裹，离开页面时保留状态（再次进入不重置）。
- 进入某功能页时该组件**重新挂载**（每次进入都是新实例）。

---

## 各模块说明

### 1. GameLobby（功能大厅）
- 模块卡片网格，每张卡片含：图标、名称、描述。
- 模块配置 `modules` 数组：`{ id, name, icon, desc, enabled }`。
  - `icon` 可以是 lucide 组件，或是字面量字符串 `'A'`（英语模块用大写字幕 A 渲染）。
  - `enabled:false` 的模块置灰、不可进入（如英语学习）。
- 当前模块：计算练习、拼音学习、汉字初识（已启用）；英语学习（即将上线）。

### 2. CalculationTool（计算练习）
- 加减法运算练习，大号数字与按钮，结果语音反馈。

### 3. PinyinTool（拼音学习）
三种游戏模式（内部 `mode`：`listen` 听音辨音 / `spell` 拼读闯关 / `identify` 认音识字）：
- **听音辨音**：播放音频，从候选拼音中选出正确读音。
- **拼读闯关**：看汉字，拼出完整拼音（声母/韵母/声调选择）。
- **认音识字**：看拼音/听音，从候选汉字中选字。
- 「词」按钮：点击朗读该字组词；若组词音频缺失则**回退播放单字音频** `/audio/word/<字>.mp3`，保证按钮始终可点可听。

### 4. CharacterTool（汉字初识）
- **字卡闪卡**：固定 300×300 卡片，拼音在字上方、汉字居中、右下角小喇叭提示朗读。
- **左右导航**：上一张 / 下一张（含键盘 ← →），与「卡片 + 组词」整体垂直居中并列。
- **组词展示**：附在卡片下方，点击朗读单字音频。
- **笔顺动画**：`hanzi-writer` 渲染，自动循环播放；点击卡片重播。
- **随机展示**：工具栏右上角独立一行按钮，随机打乱展示顺序。
- **自动发音**：进入页面（onMounted）、上/下一张、滑动切换、组词跳转时，均在用户手势内同步调用 `speakChar()`，规避浏览器自动播放策略拦截。

---

## 数据说明

### `syllables.ts`
```ts
interface Syllable {
  word: string    // 汉字
  pinyin: string  // 完整拼音（含声调）
  initial: string // 声母（零声母为空串 ''，如「有」= ∅ + iu，属正常拼音教学表示）
  final: string   // 韵母
  tone: number    // 声调 1-4，0 为轻声
}
```
> 说明：`initial` 为零声母（空串）是**正确**的拼音教学表示（y/w 为半元音，非真声母），界面已不再展示「声母+韵母」徽标，避免误解。

### `wordMap.ts`
```ts
export const charWordMap: Record<string, string>  // 汉字 -> 一个常见双字词
```
- 作为组词朗读与拼音工具中「词」按钮的数据来源。
- 已覆盖 `syllables.ts` 全部汉字；新增汉字时务必同步在此补词，否则该字组词按钮仅能回退朗读单字。

### 音频文件约定
- 单字音频：`public/audio/word/<汉字>.mp3`
- 其它提示音/鼓励语：`public/audio/<名称>.mp3`（如 `encourage_再试试.mp3`、`result_再接再厉哦.mp3`）

---

## 常用脚本

```bash
npm install          # 安装前端依赖
npm run dev          # 本地开发（Vite）
npm run build        # 类型检查 + 生产构建（vue-tsc && vite build）
npm run preview      # 预览构建产物

# 数据/音频生成（需 Python 环境，安装 edge-tts pypinyin pydub）
python scripts/generate_audio.py          # 重新生成 syllables.ts 与单字音频
python scripts/build_word_map.py          # 重新生成 wordMap.ts 与组词音频
python scripts/generate_encourage_result.py
```

---

## UI 风格偏好（后续开发请遵循）

以下为该项目的视觉与交互约定，新增/调整界面时应保持一致：

### 整体基调
- **儿童向、明快亲和**：圆角卡片、轻柔阴影、大字号、高对比度主色。
- 主色蓝 `#3498db`，禁用/置灰态 `#909399`，深色文字 `#2c3e50`。
- 通用按钮使用全局 `.btn` 类（见 `src/style.css`），避免各自写一套样式。

### 布局
- 功能页**顶部统一页头**：左侧标题文字（无图标前缀），右侧「返回大厅」按钮；标题与返回按钮垂直居中对齐。
  - 例：`CharacterTool` 的 `.ct-header` / `.ct-header-left` / `.ct-title`；`PinyinTool` 的 `.panel-title`。
- 内容区水平/垂直居中，卡片尺寸**固定**（不随内容拉伸），如闪卡 `300×300`。
- 工具栏（如「随机展示」）独占一行置于内容区右上角，与下方卡片区在视觉上分层。

### 图标
- 统一使用 `lucide-vue-next` 线性图标。
- 大厅模块图标要**贴合功能语义**：
  - 汉字初识 → 钢笔/书写类（`PenLine`）
  - 拼音学习 → 文字/拼音类（`Type`）
  - 英语学习 → 字幕字母 `A`（字面量渲染，衬线大写）
  - 计算练习 → 计算器（`Calculator`）
- 不再使用「声母+韵母」徽标与「声调」徽标（已移除以简化卡片）。

### 交互与音频
- 朗读必须在**用户手势内同步触发**（点击/按键/滑动的处理函数里直接调用），不要放在 `await`/定时器之后的 watcher 中，否则会被浏览器自动播放策略拦截。
- 进入功能页时（onMounted）即朗读首个内容。
- 音频缺失时**优雅降级**（如组词缺失回退到单字音频），保证按钮始终可点。
- 导航按钮与内容「整体」垂直居中、并列排布，而非各自对齐。
- 支持键盘操作（如闪卡 ← → 翻页）与触屏滑动。

### 数据一致性
- 新增汉字到 `syllables.ts` 时，同步在 `wordMap.ts` 补组词。
- 组词尽量避免多音字声调冲突（如「头发」的「发 fà」与音节表 `fā` 冲突，已改用「头脑」）。
