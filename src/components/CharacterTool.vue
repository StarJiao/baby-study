<script lang="ts" setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { Home, ArrowLeft, ArrowRight, Shuffle, Volume2 } from 'lucide-vue-next'
import { type Syllable, syllables } from '../data/syllables'
import { charWordMap } from '../data/wordMap'

const emit = defineEmits<{
  'back-to-lobby': []
}>()

// ==================== 数据 ====================

// 前 100 高频汉字（清华大学字频统计）
const TOP_100_CHARS = '的一国在人了有中是年大和业不为发会工经上地市要个产这出行作生家以成到日民来我部对进多全建他公开们场展时理新方主企资实学报制政济用同于法高长现本月定化加动合品重关机分力自外者区能设后就等体下万元社过前面'

// 构建音节查找表
const syllableMap: Record<string, Syllable> = {}
syllables.forEach(s => { syllableMap[s.word] = s })

// 前 100 中能在 syllables 中找到的汉字
const sourceList = computed(() => {
  return TOP_100_CHARS.split('').filter(c => syllableMap[c])
})

// 随机开关（默认开）
const randomMode = ref(true)

// 随机打乱后的列表
const shuffledList = computed(() => {
  const arr = [...sourceList.value]
  if (randomMode.value) {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]]
    }
  }
  return arr
})

type Mode = 'flashcard' | 'wordcards'
const mode = ref<Mode>('flashcard')
const modes: { id: Mode; label: string }[] = [
  { id: 'flashcard', label: '汉字闪卡' },
  { id: 'wordcards', label: '组词卡片' },
]

// ==================== 字卡状态 ====================
const cardIndex = ref(0)
const currentChar = computed(() => shuffledList.value[cardIndex.value] || '一')
const currentSyllable = computed(() => syllableMap[currentChar.value])
const currentWord = computed(() => charWordMap[currentChar.value] || '')

const goPrev = () => {
  if (cardIndex.value > 0) {
    cardIndex.value--
    speakChar() // 在用户手势内立即发音，避免被浏览器自动播放策略拦截
  }
}
const goNext = () => {
  if (cardIndex.value < shuffledList.value.length - 1) {
    cardIndex.value++
    speakChar()
  }
}

// 从组词卡片跳转到对应字卡
const jumpToChar = (char: string) => {
  const idx = shuffledList.value.indexOf(char)
  if (idx >= 0) {
    cardIndex.value = idx
    mode.value = 'flashcard'
    speakChar()
  }
}

// 键盘翻页
const handleKey = (e: KeyboardEvent) => {
  if (mode.value !== 'flashcard') return
  if (e.key === 'ArrowLeft') goPrev()
  else if (e.key === 'ArrowRight') goNext()
}

// 触屏滑动
const touchStartX = ref(0)
const onTouchStart = (e: TouchEvent) => {
  touchStartX.value = e.touches[0].clientX
}
const onTouchEnd = (e: TouchEvent) => {
  const dx = e.changedTouches[0].clientX - touchStartX.value
  if (dx > 60) goPrev()
  else if (dx < -60) goNext()
}

// ==================== 音频播放 ====================
let currentAudio: HTMLAudioElement | null = null

const stopAudio = () => {
  if (currentAudio) { currentAudio.pause(); currentAudio = null }
}

const speakText = (text: string) => {
  stopAudio()
  const path = `/audio/${text}.mp3`
  const audio = new Audio(path)
  currentAudio = audio
  audio.play().catch(() => {})
}

const speakChar = () => {
  const c = currentChar.value
  speakText(c)
}

const speakGroupWord = () => {
  // 组词音频资源按单字存放于 /audio/word/ 下，朗读当前汉字单字音频
  const c = currentChar.value
  if (c) speakText(`word/${c}`)
}

// ==================== 笔顺动画（内嵌于字卡，自动循环） ====================
const strokeContainer = ref<HTMLDivElement>()
let writerInstance: any = null
let hanziWriterLoaded = false

const loadHanziWriter = (): Promise<any> => {
  return new Promise((resolve) => {
    if (hanziWriterLoaded && (window as any).HanziWriter) {
      resolve((window as any).HanziWriter)
      return
    }
    const script = document.createElement('script')
    script.src = 'https://cdn.jsdelivr.net/npm/hanzi-writer@2.2/dist/hanzi-writer.min.js'
    script.onload = () => {
      hanziWriterLoaded = true
      resolve((window as any).HanziWriter)
    }
    script.onerror = () => resolve(null)
    document.head.appendChild(script)
  })
}

const createWriter = async (char: string) => {
  if (!strokeContainer.value) return
  const HW = await loadHanziWriter()
  if (!HW) return

  // 销毁旧的
  if (writerInstance) {
    strokeContainer.value.innerHTML = ''
    writerInstance = null
  }

  const dim = Math.min(strokeContainer.value.clientWidth, 280)

  writerInstance = HW.create(strokeContainer.value, char, {
    width: dim,
    height: dim,
    padding: 5,
    strokeAnimationSpeed: 1,
    delayBetweenStrokes: 400,
    delayBetweenLoops: 1200,
    strokeColor: '#2c3e50',
    radicalColor: '#e74c3c',
    highlightColor: '#3498db',
    outlineColor: '#ddd',
    drawingColor: '#3498db',
    charDataLoader: HW.CharDataLoader,
    onLoadCharDataSuccess: () => {},
    onLoadCharDataError: (err: any) => {
      console.warn(`无法加载"${char}"的笔顺数据:`, err)
    },
  })
}

const strokeChar = computed(() => currentChar.value)

// 切换汉字时重新创建并自动循环播放，并朗读当前字
watch([strokeChar, mode], async ([char, m]) => {
  if (m !== 'flashcard') return
  await nextTick()
  // 短暂延迟确保 DOM 已渲染
  await new Promise(r => setTimeout(r, 100))
  await createWriter(char)
  if (writerInstance) {
    try {
      writerInstance.loopCharacterAnimation()
    } catch {
      writerInstance.animateCharacter()
    }
  }
  // 注意：切换汉字的朗读已在上一个/下一个/滑动等用户手势中同步触发，
  // 此处不再调用 speakChar，以免因异步延迟被浏览器自动播放策略拦截或重复播放。
})

// ==================== 切换模式时管理事件 ====================
watch(mode, (m) => {
  if (m === 'flashcard') {
    document.addEventListener('keydown', handleKey)
    // 进入闪卡tab时朗读当前字
    nextTick(() => speakChar())
  } else {
    document.removeEventListener('keydown', handleKey)
  }
})

onMounted(() => {
  document.addEventListener('keydown', handleKey)
  // 进入页面时朗读当前汉字（来自大厅的点击属于用户手势，可正常自动播放）
  nextTick(() => speakChar())
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKey)
})
</script>

<template>
  <div class="char-tool">
    <!-- 顶栏 — 与其他模块对齐：左上标题 + 右上返回大厅 -->
    <header class="ct-header">
      <div class="ct-header-left">
        <h1 class="ct-title">汉字初识</h1>
      </div>
      <button class="ct-home-btn" @click="emit('back-to-lobby')">
        <Home :size="18" /> 返回大厅
      </button>
    </header>

    <!-- 模式切换 -->
    <nav class="ct-tabs">
      <button
        v-for="m in modes" :key="m.id"
        class="ct-tab"
        :class="{ active: mode === m.id }"
        @click="mode = m.id"
      >{{ m.label }}</button>
    </nav>

    <!-- ============== 汉字闪卡（内含笔顺动画） ============== -->
    <section v-if="mode === 'flashcard'" class="ct-flashcard-section">
      <!-- 顶部工具条：随机展示按钮置于右上角，单独占一行 -->
      <div class="fc-toolbar">
        <label class="random-toggle">
          <input type="checkbox" v-model="randomMode" />
          <Shuffle :size="16" />
          <span>随机展示</span>
        </label>
      </div>

      <!-- 卡片区：上一/下一按钮左右分布，与卡片对齐并上下居中；卡片固定大小居中 -->
      <div class="fc-nav-row">
        <button class="fc-nav-btn side" @click="goPrev" :disabled="cardIndex === 0" aria-label="上一个">
          <ArrowLeft :size="22" />
        </button>

        <div class="flashcard-container">
          <div
            class="flashcard"
            @click="speakChar"
            @touchstart="onTouchStart"
            @touchend="onTouchEnd"
          >
            <div class="fc-pinyin">{{ currentSyllable?.pinyin || '' }}</div>
            <div class="fc-char">{{ currentChar }}</div>
            <div class="fc-speaker-hint">
              <Volume2 :size="16" /> 点击发音
            </div>
          </div>

          <!-- 组词：贴近字卡，与字卡同处一个上下居中组合 -->
          <div class="fc-word-block" v-if="currentWord" @click="speakGroupWord">
            <span class="fc-word-label">组词：</span>{{ currentWord }}
            <Volume2 :size="14" class="fc-word-speaker" />
          </div>
          <div class="fc-word-block fc-word-empty" v-else>点击上方卡片发音</div>

          <!-- 笔顺动画区 -->
          <div ref="strokeContainer" class="stroke-canvas"></div>
        </div>

        <button class="fc-nav-btn side" @click="goNext" :disabled="cardIndex >= shuffledList.length - 1" aria-label="下一个">
          <ArrowRight :size="22" />
        </button>
      </div>
    </section>

    <!-- ============== 组词卡片 ============== -->
    <section v-if="mode === 'wordcards'" class="ct-words-section">
      <div class="wordcards-grid">
        <div
          v-for="c in sourceList" :key="c"
          class="wordcard"
          @click="jumpToChar(c)"
        >
          <div class="wc-char">{{ c }}</div>
          <div class="wc-pinyin">{{ syllableMap[c]?.pinyin || '' }}</div>
          <div class="wc-word" v-if="charWordMap[c]">{{ charWordMap[c] }}</div>
          <div class="wc-word" v-else style="color:#ccc">—</div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.char-tool {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 16px 40px;
}

/* 顶栏 — 与其他模块对齐 */
.ct-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.ct-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}
.ct-title {
  font-size: 24px;
  color: #2c3e50;
  font-weight: 700;
  margin: 0;
}
.ct-home-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #f0f0f0;
  border: 1px solid #dcdfe6;
  border-radius: 10px;
  font-size: 14px;
  color: #606266;
  cursor: pointer;
  font-family: inherit;
  flex-shrink: 0;
  transition: background 0.15s;
}
.ct-home-btn:hover { background: #e0e0e0; }

/* 模式标签 */
.ct-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  border-bottom: 2px solid #ebeef5;
  padding-bottom: 0;
}
.ct-tab {
  padding: 10px 20px;
  font-size: 15px;
  border: none;
  background: transparent;
  color: #909399;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.2s;
  font-family: inherit;
}
.ct-tab:hover { color: #3498db; }
.ct-tab.active {
  color: #3498db;
  border-bottom-color: #3498db;
  font-weight: 600;
}

/* ========== 汉字闪卡（含笔顺） ========== */
.ct-flashcard-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 顶部工具栏：随机展示按钮置于右上角，单独占一行高度 */
.fc-toolbar {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  width: 100%;
  min-height: 44px;
  margin-bottom: 16px;
}

.flashcard-container {
  width: 100%;
  max-width: 360px;
  display: flex;
  flex-direction: column;
  align-items: center;
}
/* 卡片固定大小并居中 */
.flashcard {
  width: 300px;
  height: 300px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: #fff;
  border: 2px solid #ebeef5;
  border-radius: 24px;
  padding: 24px 20px;
  text-align: center;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  transition: all 0.3s;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}
.flashcard:active {
  transform: scale(0.97);
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}
.fc-char {
  font-size: 96px;
  font-weight: 700;
  color: #2c3e50;
  line-height: 1.2;
}
.fc-pinyin {
  font-size: 28px;
  color: #3498db;
  margin: 8px 0;
  font-family: 'Georgia', serif;
}
.fc-tone-row {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin: 8px 0 12px;
}
.fc-tone-badge {
  background: #e8f4fd;
  color: #3498db;
  font-size: 13px;
  padding: 4px 12px;
  border-radius: 20px;
}
/* 组词：贴近字卡，与字卡同处一个上下居中组合 */
.fc-word-block {
  margin-top: 16px;
  max-width: 100%;
  padding: 10px 22px;
  background: #f5f7fa;
  border: 1px solid #ebeef5;
  border-radius: 14px;
  font-size: 20px;
  color: #303133;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: background 0.15s;
}
.fc-word-block:hover { background: #e8f4fd; }
.fc-word-empty {
  cursor: default;
  color: #b0b7c3;
  background: transparent;
  border-style: dashed;
}
.fc-word-empty:hover { background: transparent; }
.fc-word-label { color: #909399; font-size: 15px; }
.fc-word-speaker { color: #3498db; flex-shrink: 0; }
.fc-speaker-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 12px;
  font-size: 13px;
  color: #b0b7c3;
}

/* 笔顺动画区 */
.stroke-canvas {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
  margin-top: 16px;
}

.fc-nav-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  width: 100%;
}
.fc-nav-btn.side {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  padding: 0;
  border: 1px solid #dcdfe6;
  border-radius: 50%;
  background: #fff;
  color: #3498db;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.2s;
  flex-shrink: 0;
}
.fc-nav-btn.side:hover:not(:disabled) {
  background: #3498db;
  color: #fff;
  border-color: #3498db;
}
.fc-nav-btn.side:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

/* 随机开关 */
.random-toggle {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 8px 16px;
  background: #f5f7fa;
  border-radius: 20px;
  font-size: 14px;
  color: #606266;
  cursor: pointer;
  user-select: none;
  transition: background 0.15s;
}
.random-toggle:hover { background: #e8f4fd; }
.random-toggle input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: #3498db;
  cursor: pointer;
}

/* ========== 组词卡片 ========== */
.ct-words-section {
  padding-top: 8px;
}
.wordcards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
  gap: 12px;
}
.wordcard {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 16px;
  padding: 16px 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  -webkit-tap-highlight-color: transparent;
}
.wordcard:hover {
  border-color: #3498db;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52,152,219,0.15);
}
.wordcard:active { transform: scale(0.96); }
.wc-char {
  font-size: 32px;
  font-weight: 700;
  color: #2c3e50;
}
.wc-pinyin {
  font-size: 14px;
  color: #3498db;
  font-family: 'Georgia', serif;
  margin: 4px 0;
}
.wc-word {
  font-size: 13px;
  color: #909399;
  margin-top: 2px;
}

/* ========== 响应式 ========== */
@media (max-width: 768px) {
  .ct-header { flex-wrap: wrap; gap: 8px; }
  .fc-char { font-size: 72px; }
  .fc-pinyin { font-size: 22px; }
  .flashcard { padding: 28px 16px 18px; }
  .ct-tab { padding: 8px 14px; font-size: 14px; }
  .wordcards-grid { grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); }
  .wc-char { font-size: 26px; }
}
@media (max-width: 480px) {
  .fc-char { font-size: 56px; }
  .fc-nav-row { gap: 10px; }
  .fc-nav-btn.side { width: 46px; height: 46px; }
  .wordcards-grid { grid-template-columns: repeat(auto-fill, minmax(80px, 1fr)); }
}
</style>
