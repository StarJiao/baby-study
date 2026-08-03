<script lang="ts" setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { Home, ArrowLeft, ArrowRight, Shuffle, Volume2 } from 'lucide-vue-next'
import { type LetterEntry, letters } from '../data/letters'

const emit = defineEmits<{
  'back-to-lobby': []
}>()

// ==================== 数据 ====================
const sourceList = computed<LetterEntry[]>(() => letters)

// 随机开关（默认关，按 A→Z 顺序）
const randomMode = ref(false)

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
  { id: 'flashcard', label: '字母闪卡' },
  { id: 'wordcards', label: '单词卡片' },
]

// ==================== 字卡状态 ====================
const cardIndex = ref(0)
const currentEntry = computed(() => shuffledList.value[cardIndex.value] || sourceList.value[0])
const currentWords = computed(() => currentEntry.value.words)

const goPrev = () => {
  if (cardIndex.value > 0) {
    cardIndex.value--
    speakLetter() // 在用户手势内立即发音，避免被浏览器自动播放策略拦截
  }
}
const goNext = () => {
  if (cardIndex.value < shuffledList.value.length - 1) {
    cardIndex.value++
    speakLetter()
  }
}

// 从单词卡片跳转到对应字母卡
const jumpToLetter = (entry: LetterEntry) => {
  const idx = shuffledList.value.indexOf(entry)
  if (idx >= 0) {
    cardIndex.value = idx
    mode.value = 'flashcard'
    speakLetter()
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
// 英语音频存放于 /audio/en/ 下，字母与单词各自一个 mp3
let currentAudio: HTMLAudioElement | null = null

import { audioUrl } from '../audioConfig'

const stopAudio = () => {
  if (currentAudio) { currentAudio.pause(); currentAudio = null }
}

const speakText = (text: string) => {
  stopAudio()
  const audio = new Audio(audioUrl(`en/${text}.mp3`))
  currentAudio = audio
  audio.play().catch(() => {})
}

const speakLetter = () => {
  speakText(currentEntry.value.letter)
}

const speakWord = (word: string) => {
  speakText(word)
}

// ==================== 切换模式时管理事件 ====================
watch(mode, (m) => {
  if (m === 'flashcard') {
    document.addEventListener('keydown', handleKey)
    nextTick(() => speakLetter())
  } else {
    document.removeEventListener('keydown', handleKey)
  }
})

onMounted(() => {
  document.addEventListener('keydown', handleKey)
  // 进入页面时朗读当前字母（来自大厅的点击属于用户手势，可正常自动播放）
  nextTick(() => speakLetter())
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKey)
})
</script>

<template>
  <div class="en-tool">
    <!-- 顶栏 — 与其他模块对齐：左上标题 + 右上返回大厅 -->
    <header class="en-header">
      <div class="en-header-left">
        <h1 class="en-title">英语学习</h1>
      </div>
      <button class="en-home-btn" @click="emit('back-to-lobby')">
        <Home :size="18" /> 返回大厅
      </button>
    </header>

    <!-- 模式切换 -->
    <nav class="en-tabs">
      <button
        v-for="m in modes" :key="m.id"
        class="en-tab"
        :class="{ active: mode === m.id }"
        @click="mode = m.id"
      >{{ m.label }}</button>
    </nav>

    <!-- ============== 字母闪卡 ============== -->
    <section v-if="mode === 'flashcard'" class="en-flashcard-section">
      <!-- 顶部工具条：随机展示开关 -->
      <div class="fc-toolbar">
        <label class="random-toggle">
          <input type="checkbox" v-model="randomMode" />
          <Shuffle :size="16" />
          <span>随机展示</span>
        </label>
      </div>

      <!-- 卡片区：上一/下一按钮左右分布 -->
      <div class="fc-nav-row">
        <button class="fc-nav-btn side" @click="goPrev" :disabled="cardIndex === 0" aria-label="上一个">
          <ArrowLeft :size="22" />
        </button>

        <div class="flashcard-container">
          <div
            class="flashcard"
            @click="speakLetter"
            @touchstart="onTouchStart"
            @touchend="onTouchEnd"
          >
            <div class="fc-letter-pair">
              <span class="fc-upper">{{ currentEntry.letter }}</span>
              <span class="fc-lower">{{ currentEntry.lower }}</span>
            </div>
            <div class="fc-emoji">{{ currentEntry.emoji }}</div>
            <div class="fc-speaker-hint">
              <Volume2 :size="16" /> 点击发音
            </div>
          </div>

          <!-- 配套单词：每个单词配 emoji 卡通图 + 中文，点击朗读 -->
          <div class="fc-words">
            <div
              v-for="w in currentWords"
              :key="w.word"
              class="fc-word-pill"
              @click="speakWord(w.word)"
            >
              <span class="fc-word-emoji">{{ w.emoji }}</span>
              <span class="fc-word-text">{{ w.word }}</span>
              <span class="fc-word-cn">{{ w.cn }}</span>
              <Volume2 :size="13" class="fc-word-speaker" />
            </div>
          </div>
        </div>

        <button class="fc-nav-btn side" @click="goNext" :disabled="cardIndex >= shuffledList.length - 1" aria-label="下一个">
          <ArrowRight :size="22" />
        </button>
      </div>
    </section>

    <!-- ============== 单词卡片（按字母浏览） ============== -->
    <section v-if="mode === 'wordcards'" class="en-words-section">
      <div class="wordcards-grid">
        <div
          v-for="entry in sourceList" :key="entry.letter"
          class="wordcard"
          @click="jumpToLetter(entry)"
        >
          <div class="wc-letter">{{ entry.letter }}</div>
          <div class="wc-emoji">{{ entry.emoji }}</div>
          <div class="wc-words">
            <span v-for="w in entry.words" :key="w.word" class="wc-word-chip">
              {{ w.emoji }} {{ w.word }}
            </span>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.en-tool {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 16px 40px;
}

/* 顶栏 — 与其他模块对齐 */
.en-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.en-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}
.en-title {
  font-size: 24px;
  color: #2c3e50;
  font-weight: 700;
  margin: 0;
}
.en-home-btn {
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
.en-home-btn:hover { background: #e0e0e0; }

/* 模式标签 */
.en-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  border-bottom: 2px solid #ebeef5;
  padding-bottom: 0;
}
.en-tab {
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
.en-tab:hover { color: #3498db; }
.en-tab.active {
  color: #3498db;
  border-bottom-color: #3498db;
  font-weight: 600;
}

/* ========== 字母闪卡 ========== */
.en-flashcard-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

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
.flashcard {
  width: 300px;
  min-height: 300px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
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
.fc-letter-pair {
  display: flex;
  align-items: baseline;
  gap: 10px;
}
.fc-upper {
  font-size: 96px;
  font-weight: 700;
  color: #2c3e50;
  line-height: 1.1;
  font-family: 'Georgia', 'Times New Roman', serif;
}
.fc-lower {
  font-size: 56px;
  font-weight: 600;
  color: #3498db;
  line-height: 1.1;
  font-family: 'Georgia', 'Times New Roman', serif;
}
.fc-emoji {
  font-size: 72px;
  line-height: 1.2;
  margin: 8px 0 4px;
  filter: drop-shadow(0 4px 8px rgba(0,0,0,0.12));
}
.fc-speaker-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 8px;
  font-size: 13px;
  color: #b0b7c3;
}

/* 配套单词 */
.fc-words {
  margin-top: 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
  max-width: 320px;
}
.fc-word-pill {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  background: #f5f7fa;
  border: 1px solid #ebeef5;
  border-radius: 14px;
  font-size: 17px;
  color: #303133;
  cursor: pointer;
  transition: background 0.15s;
}
.fc-word-pill:hover { background: #e8f4fd; }
.fc-word-emoji { font-size: 26px; flex-shrink: 0; }
.fc-word-text {
  font-weight: 600;
  flex: 1;
  text-align: left;
  font-family: 'Georgia', 'Times New Roman', serif;
}
.fc-word-cn { color: #909399; font-size: 14px; flex-shrink: 0; }
.fc-word-speaker { color: #3498db; flex-shrink: 0; }

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

/* ========== 单词卡片 ========== */
.en-words-section {
  padding-top: 8px;
}
.wordcards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
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
.wc-letter {
  font-size: 38px;
  font-weight: 700;
  color: #2c3e50;
  font-family: 'Georgia', 'Times New Roman', serif;
}
.wc-emoji {
  font-size: 36px;
  margin: 4px 0;
}
.wc-words {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 6px;
}
.wc-word-chip {
  font-size: 13px;
  color: #606266;
}

/* ========== 响应式 ========== */
@media (max-width: 768px) {
  .en-header { flex-wrap: wrap; gap: 8px; }
  .fc-upper { font-size: 72px; }
  .fc-lower { font-size: 44px; }
  .fc-emoji { font-size: 56px; }
  .flashcard { min-height: 260px; padding: 28px 16px 18px; }
  .en-tab { padding: 8px 14px; font-size: 14px; }
  .wordcards-grid { grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); }
  .wc-letter { font-size: 30px; }
}
@media (max-width: 480px) {
  .fc-upper { font-size: 56px; }
  .fc-nav-row { gap: 10px; }
  .fc-nav-btn.side { width: 46px; height: 46px; }
  .wordcards-grid { grid-template-columns: repeat(auto-fill, minmax(90px, 1fr)); }
}
</style>
