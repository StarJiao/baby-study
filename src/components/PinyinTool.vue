<script lang="ts" setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { Home, Ear, Pencil, Play, Volume2, Star, ThumbsUp, Heart, Check, X, XCircle, PartyPopper } from 'lucide-vue-next'
import { type Syllable, syllables } from '../data/syllables'
import { charWordMap } from '../data/wordMap'

const emit = defineEmits<{
  'back-to-lobby': []
}>()

// ===================== 数据定义 =====================

interface ListenOption {
  pinyin: string
  isCorrect: boolean
}

interface ListenQuestion {
  syllable: Syllable
  options: ListenOption[]
}

interface SpellQuestion {
  syllable: Syllable
  initialOptions: string[]
  finalOptions: string[]
  toneOptions: number[]
}

interface IdentifyOption {
  label: string
  value: string
}

interface IdentifyQuestion {
  syllable: Syllable
  type: 'initial' | 'final' | 'mixed'
  options: IdentifyOption[]
  correctValue: string
}

interface GameHistory {
  question: string
  correctAnswer: string
  userAnswer: string
  isCorrect: boolean
}

const allInitials = [...new Set(syllables.map(s => s.initial))].filter(Boolean)
const allFinals = [...new Set(syllables.map(s => s.final))].filter(Boolean)
const tones = [1, 2, 3, 4]
const toneMarks: Record<number, string> = { 0: '˙', 1: 'ˉ', 2: 'ˊ', 3: 'ˇ', 4: 'ˋ' }
const toneLabels: Record<number, string> = { 0: '轻声', 1: '第一声', 2: '第二声', 3: '第三声', 4: '第四声' }

// ===================== 音频播放 =====================

// 预生成音频路径映射
const getWordAudio = (word: string) => `/audio/${word}.mp3`

const praiseAudios = [
  '/audio/praise_太棒了.mp3', '/audio/praise_你真厉害.mp3', '/audio/praise_非常好.mp3',
  '/audio/praise_超级棒.mp3', '/audio/praise_哇太厉害了.mp3', '/audio/praise_好样的.mp3',
  '/audio/praise_真聪明.mp3', '/audio/praise_完美.mp3', '/audio/praise_厉害极了.mp3',
  '/audio/praise_真棒.mp3',
]

const encourageAudios = [
  '/audio/encourage_再想想哦.mp3', '/audio/encourage_再试试.mp3',
  '/audio/encourage_仔细听听.mp3',
]

const resultAudios: Record<string, string> = {
  excellent: '/audio/result_太棒了，你超级厉害.mp3',
  good: '/audio/result_做得不错，继续加油.mp3',
  keepGoing: '/audio/result_再接再厉哦.mp3',
}

let currentAudio: HTMLAudioElement | null = null

const playAudio = (src: string): Promise<void> => {
  return new Promise((resolve) => {
    stopAudio()
    const audio = new Audio(src)
    currentAudio = audio
    audio.onended = () => {
      if (currentAudio === audio) currentAudio = null
      resolve()
    }
    audio.onerror = () => {
      console.warn(`Audio load failed: ${src}`)
      if (currentAudio === audio) currentAudio = null
      resolve()
    }
    audio.play().catch(() => resolve())
  })
}

const stopAudio = () => {
  if (currentAudio) {
    currentAudio.pause()
    currentAudio.currentTime = 0
    currentAudio = null
  }
}

const speakWord = (word: string) => {
  playAudio(getWordAudio(word))
}

const getWordGroupAudio = (word: string) => `/audio/word/${word}.mp3`

const hasGroupWord = (word: string): boolean => {
  return !!charWordMap[word]
}

const speakGroupWord = (word: string) => {
  const groupWord = charWordMap[word]
  if (groupWord) {
    playAudio(getWordGroupAudio(word))
  } else {
    // 无组词数据时，回退播放该字单字音频，避免按钮点击无反应
    playAudio(`/audio/word/${word}.mp3`)
  }
}

const randomPraiseAudio = () => {
  return praiseAudios[Math.floor(Math.random() * praiseAudios.length)]
}

const randomEncourageAudio = () => {
  return encourageAudios[Math.floor(Math.random() * encourageAudios.length)]
}

// ===================== 游戏状态 =====================

const page = ref<'select' | 'listen' | 'spell' | 'identify'>('select')

// 听音辨音状态
const listenState = ref<'setup' | 'playing' | 'result'>('setup')
const listenQuestions = ref<ListenQuestion[]>([])
const listenIndex = ref(0)
const listenSelected = ref<number | null>(null)
const listenIsCorrect = ref<boolean | null>(null)
const listenHistory = ref<GameHistory[]>([])
const listenQuestionCount = ref(10)
const listenType = ref<'pinyin' | 'initial' | 'final' | 'mixed'>('pinyin')
const listenSoundCard = ref<HTMLElement | null>(null)
const listenFirstCorrect = ref<Set<number>>(new Set())
const listenUserFirstAnswers = ref<Record<number, string>>({})
const listenFeedbackPending = ref(false)

// 拼读闯关状态
const spellState = ref<'setup' | 'playing' | 'result'>('setup')
const spellQuestions = ref<SpellQuestion[]>([])
const spellIndex = ref(0)
const spellInitial = ref<string | null>(null)
const spellFinal = ref<string | null>(null)
const spellTone = ref<number | null>(null)
const spellIsCorrect = ref<boolean | null>(null)
const spellHistory = ref<GameHistory[]>([])
const spellQuestionCount = ref(10)

// 认音识字状态
const identifyState = ref<'setup' | 'playing' | 'result'>('setup')
const identifyType = ref<'initial' | 'final' | 'mixed'>('initial')
const identifyQuestions = ref<IdentifyQuestion[]>([])
const identifyIndex = ref(0)
const identifySelected = ref<number | null>(null)
const identifyIsCorrect = ref<boolean | null>(null)
const identifyHistory = ref<GameHistory[]>([])
const identifyQuestionCount = ref(10)
const identifySoundCard = ref<HTMLElement | null>(null)
const identifyFirstCorrect = ref<Set<number>>(new Set())
const identifyUserFirstAnswers = ref<Record<number, string>>({})
const identifyFeedbackPending = ref(false)

// 激励动画
const showStar = ref(false)
const showThumbUp = ref(false)
const showHeart = ref(false)
const animKey = ref(0)

// ===================== 工具函数 =====================

const randomPick = <T>(arr: T[], count: number): T[] => {
  const shuffled = [...arr].sort(() => Math.random() - 0.5)
  return shuffled.slice(0, count)
}

// iPad Safari 会在触摸按钮后保留焦点/悬停状态；反馈结束后显式释放。
const releaseAnswerFocus = (answerButton: HTMLElement | null) => {
  answerButton?.blur()
  const activeElement = document.activeElement
  if (
    activeElement instanceof HTMLElement &&
    (
      activeElement.classList.contains('listen-option') ||
      activeElement.classList.contains('identify-option')
    )
  ) {
    activeElement.blur()
  }
}

const playCorrectSound = () => {
  try {
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
    const notes = [784, 880, 988, 1047]
    notes.forEach((freq, i) => {
      const oscillator = audioContext.createOscillator()
      const gainNode = audioContext.createGain()
      oscillator.connect(gainNode)
      gainNode.connect(audioContext.destination)
      oscillator.frequency.setValueAtTime(freq, audioContext.currentTime + i * 0.08)
      oscillator.type = 'sine'
      gainNode.gain.setValueAtTime(0.15, audioContext.currentTime + i * 0.08)
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + i * 0.08 + 0.15)
      oscillator.start(audioContext.currentTime + i * 0.08)
      oscillator.stop(audioContext.currentTime + i * 0.08 + 0.15)
    })
  } catch (e) { /* ignore */ }
}

const playWrongSound = () => {
  try {
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
    const notes = [330, 294]
    notes.forEach((freq, i) => {
      const oscillator = audioContext.createOscillator()
      const gainNode = audioContext.createGain()
      oscillator.connect(gainNode)
      gainNode.connect(audioContext.destination)
      oscillator.frequency.setValueAtTime(freq, audioContext.currentTime + i * 0.15)
      oscillator.type = 'sine'
      gainNode.gain.setValueAtTime(0.12, audioContext.currentTime + i * 0.15)
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + i * 0.15 + 0.2)
      oscillator.start(audioContext.currentTime + i * 0.15)
      oscillator.stop(audioContext.currentTime + i * 0.15 + 0.2)
    })
  } catch (e) { /* ignore */ }
}

const triggerCorrectAnimation = () => {
  const animType = Math.floor(Math.random() * 3)
  showStar.value = animType === 0
  showThumbUp.value = animType === 1
  showHeart.value = animType === 2
  animKey.value++
  setTimeout(() => {
    showStar.value = false
    showThumbUp.value = false
    showHeart.value = false
  }, 1000)
  const randomPraise = randomPraiseAudio()
  playAudio(randomPraise)
}

// ===================== 听音辨音 =====================

const generateListenDistractors = (correct: Syllable, count: number): ListenOption[] => {
  const pool = new Set<string>()
  const strategies = [
    // 同声母不同韵母
    () => {
      const candidates = syllables.filter(s => s.initial === correct.initial && s.final !== correct.final)
      if (candidates.length > 0) pool.add(randomPick(candidates, 1)[0].pinyin)
    },
    // 同韵母不同声母
    () => {
      const candidates = syllables.filter(s => s.final === correct.final && s.initial !== correct.initial)
      if (candidates.length > 0) pool.add(randomPick(candidates, 1)[0].pinyin)
    },
    // 同拼法不同声调
    () => {
      const candidates = syllables.filter(s => s.initial === correct.initial && s.final === correct.final && s.tone !== correct.tone)
      if (candidates.length > 0) pool.add(randomPick(candidates, 1)[0].pinyin)
    },
    // 完全不同
    () => {
      const candidates = syllables.filter(s => s.initial !== correct.initial && s.final !== correct.final)
      if (candidates.length > 0) pool.add(randomPick(candidates, 1)[0].pinyin)
    },
  ]

  while (pool.size < count) {
    const strategy = strategies[Math.floor(Math.random() * strategies.length)]
    strategy()
  }

  return Array.from(pool).slice(0, count).map(p => ({ pinyin: p, isCorrect: false }))
}

const startListenGame = () => {
  if (listenType.value === 'pinyin') {
    const picks = randomPick(syllables, listenQuestionCount.value)
    listenQuestions.value = picks.map(s => {
      const distractors = generateListenDistractors(s, 3)
      const options = [...distractors, { pinyin: s.pinyin, isCorrect: true }]
        .sort(() => Math.random() - 0.5)
      return { syllable: s, options }
    })
    listenIndex.value = 0
    listenSelected.value = null
    listenIsCorrect.value = null
    listenHistory.value = []
    listenFirstCorrect.value = new Set()
    listenUserFirstAnswers.value = {}
    listenFeedbackPending.value = false
    listenState.value = 'playing'
    setTimeout(() => speakWord(listenQuestions.value[0].syllable.word), 400)
  } else {
    // 声母/韵母/混合模式 — 复用认音识字逻辑
    identifyType.value = listenType.value
    identifyQuestionCount.value = listenQuestionCount.value
    startIdentifyGame()
    listenState.value = 'playing'
  }
}

const handleListenSelect = (optionIndex: number, event: MouseEvent) => {
  if (listenFeedbackPending.value) return

  const q = listenQuestions.value[listenIndex.value]
  const option = q.options[optionIndex]
  const correct = option.isCorrect
  const answerButton = event.currentTarget as HTMLElement | null

  listenFeedbackPending.value = true
  listenSelected.value = optionIndex
  listenIsCorrect.value = correct

  const idx = listenIndex.value

  if (correct) {
    // 记录首次是否正确
    if (!(idx in listenUserFirstAnswers.value)) {
      listenFirstCorrect.value.add(idx)
      listenUserFirstAnswers.value[idx] = option.pinyin
    }
    // 记录最终答对的记录
    listenHistory.value.push({
      question: q.syllable.word,
      correctAnswer: q.syllable.pinyin,
      userAnswer: option.pinyin,
      isCorrect: true,
    })

    playCorrectSound()
    triggerCorrectAnimation()

    setTimeout(() => {
      releaseAnswerFocus(answerButton)
      listenSelected.value = null
      listenIsCorrect.value = null
      listenFeedbackPending.value = false
      if (listenIndex.value < listenQuestions.value.length - 1) {
        listenIndex.value++
        setTimeout(() => speakWord(listenQuestions.value[listenIndex.value].syllable.word), 300)
      } else {
        listenState.value = 'result'
      }
    }, 1500)
  } else {
    // 记录首次错误答案
    if (!(idx in listenUserFirstAnswers.value)) {
      listenUserFirstAnswers.value[idx] = option.pinyin
    }

    playWrongSound()
    const randomMsg = randomEncourageAudio()
    playAudio(randomMsg)

    // 错误后重置选中状态，允许重试，并自动重播发音
    setTimeout(() => {
      releaseAnswerFocus(answerButton)
      listenSelected.value = null
      listenIsCorrect.value = null
      listenFeedbackPending.value = false
      speakWord(q.syllable.word)
    }, 1200)
  }
}

const listenCorrectCount = computed(() => {
  if (listenType.value === 'pinyin') {
    return listenFirstCorrect.value.size
  }
  return identifyFirstCorrect.value.size
})
const listenAccuracy = computed(() => {
  const total = listenType.value === 'pinyin' ? listenQuestions.value.length : identifyQuestions.value.length
  if (total === 0) return 0
  const correct = listenType.value === 'pinyin' ? listenFirstCorrect.value.size : identifyFirstCorrect.value.size
  return Math.round((correct / total) * 100)
})
const listenModeTotal = computed(() => {
  return listenType.value === 'pinyin' ? listenQuestions.value.length : identifyQuestions.value.length
})

// ===================== 拼读闯关 =====================

const generateSpellOptions = (correct: string, pool: string[], count: number): string[] => {
  const others = pool.filter(s => s !== correct)
  const picks = randomPick(others, count - 1)
  return [...picks, correct].sort(() => Math.random() - 0.5)
}

const startSpellGame = () => {
  const picks = randomPick(syllables.filter(s => s.initial !== '' && s.final !== ''), spellQuestionCount.value)
  spellQuestions.value = picks.map(s => ({
    syllable: s,
    initialOptions: generateSpellOptions(s.initial, allInitials.filter(init =>
      syllables.some(sy => sy.initial === init)
    ), 4),
    finalOptions: generateSpellOptions(s.final, allFinals.filter(fin =>
      syllables.some(sy => sy.initial === s.initial && sy.final === fin)
    ), 4),
    toneOptions: [0, 1, 2, 3, 4],
  }))
  spellIndex.value = 0
  spellInitial.value = null
  spellFinal.value = null
  spellTone.value = null
  spellIsCorrect.value = null
  spellHistory.value = []
  spellState.value = 'playing'
}

const allSpellSelected = computed(() =>
  spellInitial.value !== null && spellFinal.value !== null && spellTone.value !== null
)

const submitSpellAnswer = () => {
  if (!allSpellSelected.value || spellIsCorrect.value !== null) return

  const q = spellQuestions.value[spellIndex.value].syllable
  const correct =
    spellInitial.value === q.initial &&
    spellFinal.value === q.final &&
    spellTone.value === q.tone

  spellIsCorrect.value = correct

  const userPinyin = (spellInitial.value ?? '') + (spellFinal.value ?? '') + (
    spellTone.value ? ['','ā','á','ǎ','à'][spellTone.value] : ''
  )

  spellHistory.value.push({
    question: q.word,
    correctAnswer: q.pinyin,
    userAnswer: userPinyin || q.initial + q.final,
    isCorrect: correct,
  })

  if (correct) {
    playCorrectSound()
    triggerCorrectAnimation()
    // 正确：延迟后进入下一题
    setTimeout(() => {
      spellInitial.value = null
      spellFinal.value = null
      spellTone.value = null
      spellIsCorrect.value = null
      if (spellIndex.value < spellQuestions.value.length - 1) {
        spellIndex.value++
      } else {
        spellState.value = 'result'
      }
    }, 1500)
  } else {
    playWrongSound()
    const randomMsg = randomEncourageAudio()
    playAudio(randomMsg)
    // 错误：短暂显示错误后重置，让用户重新选择
    setTimeout(() => {
      spellInitial.value = null
      spellFinal.value = null
      spellTone.value = null
      spellIsCorrect.value = null
    }, 1200)
  }
}

const spellCorrectCount = computed(() => spellHistory.value.filter(h => h.isCorrect).length)
const spellAccuracy = computed(() => {
  if (spellHistory.value.length === 0) return 0
  return Math.round((spellCorrectCount.value / spellHistory.value.length) * 100)
})

// ===================== 认音识字 =====================

const identifyTypeLabels: Record<string, string> = {
  initial: '声母',
  final: '韵母',
  mixed: '混合',
}

const generateIdentifyDistractors = (
  correctValue: string,
  pool: string[],
  count: number
): string[] => {
  const others = pool.filter(v => v !== correctValue)
  const shuffled = [...others].sort(() => Math.random() - 0.5)
  return shuffled.slice(0, count)
}

const startIdentifyGame = () => {
  const type = identifyType.value

  // 根据题型过滤掉对应部分为空的音节
  let pool = syllables
  if (type === 'initial') {
    pool = syllables.filter(s => s.initial !== '')
  } else if (type === 'final') {
    pool = syllables.filter(s => s.final !== '')
  }

  const picks = randomPick(pool, identifyQuestionCount.value)

  identifyQuestions.value = picks.map(s => {
    const qType = type === 'mixed'
      ? (() => {
          // 避开空值：没有声母就不选 initial，没有韵母就不选 final
          const av: ('initial' | 'final' | 'mixed')[] = ['mixed']
          if (s.initial !== '') av.push('initial')
          if (s.final !== '') av.push('final')
          return av[Math.floor(Math.random() * av.length)]
        })()
      : type

    let correctValue: string
    let optionPool: string[]
    let labelMap: (v: string) => string

    if (qType === 'initial') {
      correctValue = s.initial
      optionPool = allInitials
      labelMap = v => v
    } else if (qType === 'final') {
      correctValue = s.final
      optionPool = allFinals
      labelMap = v => v
    } else {
      // 混合 — 避开空值，选非空的组件
      if (s.initial !== '' && (s.final === '' || Math.random() < 0.5)) {
        correctValue = s.initial
        optionPool = allInitials
        labelMap = v => v
      } else {
        correctValue = s.final
        optionPool = allFinals
        labelMap = v => v
      }
    }

    const distractors = generateIdentifyDistractors(correctValue, optionPool, 3)
    const rawOptions = [...distractors, correctValue].sort(() => Math.random() - 0.5)
    const options: IdentifyOption[] = rawOptions.map(v => ({
      label: labelMap(v),
      value: v,
    }))

    // 记录此题的实际题型
    const effectiveType = qType === 'mixed' ? correctValue === s.initial ? 'initial' : 'final' : qType
    return { syllable: s, type: effectiveType as 'initial' | 'final' | 'mixed', options, correctValue }
  })

  identifyIndex.value = 0
  identifySelected.value = null
  identifyIsCorrect.value = null
  identifyHistory.value = []
  identifyFirstCorrect.value = new Set()
  identifyUserFirstAnswers.value = {}
  identifyFeedbackPending.value = false
  identifyState.value = 'playing'

  // 自动播放第一题
  setTimeout(() => speakWord(identifyQuestions.value[0].syllable.word), 400)
}

const handleIdentifySelect = (optionIndex: number, event: MouseEvent) => {
  if (identifyFeedbackPending.value) return

  const q = identifyQuestions.value[identifyIndex.value]
  const option = q.options[optionIndex]
  const correct = option.value === q.correctValue
  const answerButton = event.currentTarget as HTMLElement | null

  identifyFeedbackPending.value = true
  identifySelected.value = optionIndex
  identifyIsCorrect.value = correct

  const idx = identifyIndex.value

  if (correct) {
    // 记录首次是否正确
    if (!(idx in identifyUserFirstAnswers.value)) {
      identifyFirstCorrect.value.add(idx)
      identifyUserFirstAnswers.value[idx] = option.value
    }
    identifyHistory.value.push({
      question: q.syllable.word,
      correctAnswer: q.correctValue,
      userAnswer: option.value,
      isCorrect: true,
    })

    playCorrectSound()
    triggerCorrectAnimation()

    setTimeout(() => {
      releaseAnswerFocus(answerButton)
      identifySelected.value = null
      identifyIsCorrect.value = null
      identifyFeedbackPending.value = false
      if (identifyIndex.value < identifyQuestions.value.length - 1) {
        identifyIndex.value++
        setTimeout(() => speakWord(identifyQuestions.value[identifyIndex.value].syllable.word), 300)
      } else {
        listenState.value = 'result'
      }
    }, 1500)
  } else {
    // 记录首次错误答案
    if (!(idx in identifyUserFirstAnswers.value)) {
      identifyUserFirstAnswers.value[idx] = option.value
    }

    playWrongSound()
    const randomMsg = randomEncourageAudio()
    playAudio(randomMsg)

    // 错误后重置选中状态，允许重试，并自动重播发音
    setTimeout(() => {
      releaseAnswerFocus(answerButton)
      identifySelected.value = null
      identifyIsCorrect.value = null
      identifyFeedbackPending.value = false
      speakWord(q.syllable.word)
    }, 1200)
  }
}

const identifyCorrectCount = computed(() => identifyHistory.value.filter(h => h.isCorrect).length)
const identifyAccuracy = computed(() => {
  if (identifyHistory.value.length === 0) return 0
  return Math.round((identifyCorrectCount.value / identifyHistory.value.length) * 100)
})

// 结果页语音
watch(listenState, (s) => {
  if (s === 'result') {
    setTimeout(() => {
      const acc = listenAccuracy.value
      if (acc >= 90) playAudio(resultAudios.excellent)
      else if (acc >= 70) playAudio(resultAudios.good)
      else playAudio(resultAudios.keepGoing)
    }, 500)
  }
})

watch(spellState, (s) => {
  if (s === 'result') {
    setTimeout(() => {
      const acc = spellAccuracy.value
      if (acc >= 90) playAudio(resultAudios.excellent)
      else if (acc >= 70) playAudio(resultAudios.good)
      else playAudio(resultAudios.keepGoing)
    }, 500)
  }
})

const questionCountOptions = [5, 10, 15, 20]

// 测量小喇叭(.sound-card)的真实高度，赋给 --spk-h，
// 使「词」按钮成为边长等于小喇叭高度的正方形
function measureSpeakerHeight() {
  const el = document.querySelector<HTMLElement>('.pinyin-tool .sound-card')
  if (el) document.documentElement.style.setProperty('--spk-h', `${el.offsetHeight}px`)
}

// 状态切换 / 题目刷新后，DOM 重新渲染时重新测量
watch([page, listenType, listenIndex, listenState, identifyType, identifyIndex, identifyState, spellIndex, spellState], () => {
  nextTick(() => requestAnimationFrame(measureSpeakerHeight))
})

onMounted(() => {
  measureSpeakerHeight()
  window.addEventListener('resize', measureSpeakerHeight)
  // 字体/音频加载可能导致高度变化，稍后再测一次
  requestAnimationFrame(measureSpeakerHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', measureSpeakerHeight)
})
</script>

<template>
  <div class="pinyin-tool">

    <!-- ==================== 模式选择 ==================== -->
    <div v-if="page === 'select'" class="mode-select">
      <div class="setup-header">
        <h1 class="panel-title">拼音学习</h1>
        <button class="btn-home" @click="emit('back-to-lobby')">
          <Home :size="16" /> 返回大厅
        </button>
      </div>

      <div class="mode-grid">
        <button class="mode-card" @click="page = 'listen'">
          <div class="mode-icon">
            <Ear :size="40" color="#3498db" />
          </div>
          <h2 class="mode-name">听音辨音</h2>
          <p class="mode-desc">听读音，选正确的拼音</p>
        </button>
        <button class="mode-card" @click="page = 'spell'">
          <div class="mode-icon">
            <Pencil :size="40" color="#e67e22" />
          </div>
          <h2 class="mode-name">拼读闯关</h2>
          <p class="mode-desc">选声母、韵母和声调</p>
        </button>

      </div>
    </div>

    <!-- ==================== 听音辨音 ==================== -->
    <template v-else-if="page === 'listen'">

      <!-- 难度选择 -->
      <div v-if="listenState === 'setup'" class="setup-panel">
        <div class="setup-header">
          <div class="header-left-side">
            <button class="btn-back" @click="page = 'select'">
              ← 返回
            </button>
            <h2 class="panel-title">听音辨音</h2>
          </div>
          <button class="btn-home" @click="emit('back-to-lobby')">
            <Home :size="16" /> 返回大厅
          </button>
        </div>

        <div class="mode-info">
          <Volume2 :size="20" color="#3498db" />
          <span>听读音，选择正确的拼音。考察听力和拼读能力！</span>
        </div>

        <div class="form-group">
          <label class="label">题型</label>
          <div class="option-buttons">
            <button
              class="option-btn"
              :class="{ active: listenType === 'pinyin' }"
              @click="listenType = 'pinyin'"
            >拼音</button>
            <button
              class="option-btn"
              :class="{ active: listenType === 'initial' }"
              @click="listenType = 'initial'"
            >声母</button>
            <button
              class="option-btn"
              :class="{ active: listenType === 'final' }"
              @click="listenType = 'final'"
            >韵母</button>
            <button
              class="option-btn"
              :class="{ active: listenType === 'mixed' }"
              @click="listenType = 'mixed'"
            >混合</button>
          </div>
        </div>

        <div class="form-group">
          <label class="label">题目数量</label>
          <div class="option-buttons">
            <button
              v-for="cnt in questionCountOptions" :key="cnt"
              class="option-btn"
              :class="{ active: listenQuestionCount === cnt }"
              @click="listenQuestionCount = cnt"
            >{{ cnt }}题</button>
          </div>
        </div>

        <div class="form-group">
          <label class="label">覆盖范围</label>
          <p class="range-hint">包含所有声母和韵母组合，随机出题</p>
        </div>

        <button class="btn btn-primary" @click="startListenGame">
          <Play :size="18" /> 开始练习
        </button>
      </div>

      <!-- 答题中 -->
      <div v-else-if="listenState === 'playing'" class="game-container">
        <div class="game-header">
          <span class="progress">
            <template v-if="listenType === 'pinyin'">{{ listenIndex + 1 }} / {{ listenQuestions.length }}</template>
            <template v-else>{{ identifyIndex + 1 }} / {{ identifyQuestions.length }}</template>
          </span>
          <span class="badge">听音辨音</span>
          <button class="btn-exit" @click="listenState = 'setup'">
            <X :size="16" /> 退出
          </button>
        </div>

        <!-- 激励动画 -->
        <div class="incentive-area">
          <div v-if="showStar" class="anim-pop" :key="'star-' + animKey">
            <Star :size="60" fill="#FFD700" color="#FFD700" />
          </div>
          <div v-if="showThumbUp" class="anim-pop" :key="'thumb-' + animKey">
            <ThumbsUp :size="60" color="#FF6B6B" />
          </div>
          <div v-if="showHeart" class="anim-pop" :key="'heart-' + animKey">
            <Heart :size="60" fill="#FF6B6B" color="#FF6B6B" />
          </div>
        </div>

        <!-- 拼音模式：发音 + 选项 -->
        <template v-if="listenType === 'pinyin'">
          <!-- 发音区域 -->
          <div class="sound-card-row">
            <div ref="listenSoundCard" tabindex="0" class="sound-card" @click="speakWord(listenQuestions[listenIndex].syllable.word)">
              <Volume2 :size="36" color="#3498db" />
              <span class="pinyin-word-text">{{ listenQuestions[listenIndex].syllable.word }}</span>
            </div>
            <button class="word-group-btn" @click.stop="speakGroupWord(listenQuestions[listenIndex].syllable.word)" :title="hasGroupWord(listenQuestions[listenIndex].syllable.word) ? '听组词' : '暂无组词'">词</button>
          </div>

          <!-- 选项 -->
          <div class="listen-options" :class="{ 'show-result': listenSelected !== null }">
            <button
              v-for="(opt, i) in listenQuestions[listenIndex].options"
              :key="i"
              class="listen-option"
              :class="{
                selected: listenSelected === i,
                correct: listenSelected !== null && listenIsCorrect === true && opt.isCorrect,
                wrong: listenSelected === i && !opt.isCorrect,
              }"
              :disabled="listenFeedbackPending"
              @click="handleListenSelect(i, $event)"
            >
              <span class="pinyin-text">{{ opt.pinyin }}</span>
              <Check v-if="listenSelected !== null && listenIsCorrect === true && opt.isCorrect" :size="20" class="opt-mark" />
              <X v-else-if="listenSelected === i && !opt.isCorrect" :size="20" class="opt-mark" />
            </button>
          </div>

          <div class="score-display">
            正确：{{ listenFirstCorrect.size }} / {{ listenIndex }}
          </div>
        </template>

        <!-- 声母/韵母/混合模式 -->
        <template v-else>
          <div class="identify-prompt">
            <span class="identify-type-badge">{{ identifyTypeLabels[identifyQuestions[identifyIndex].type] }}</span>
            <span class="identify-hint">这个发音的{{ identifyTypeLabels[identifyQuestions[identifyIndex].type] }}是什么？</span>
          </div>

          <div class="sound-card-row">
            <div ref="identifySoundCard" tabindex="0" class="sound-card identify-sound-card" @click="speakWord(identifyQuestions[identifyIndex].syllable.word)">
              <Volume2 :size="36" color="#8e44ad" />
              <span class="identify-word-text">{{ identifyQuestions[identifyIndex].syllable.word }}</span>
            </div>
            <button class="word-group-btn purple" @click.stop="speakGroupWord(identifyQuestions[identifyIndex].syllable.word)" :title="hasGroupWord(identifyQuestions[identifyIndex].syllable.word) ? '听组词' : '暂无组词'">词</button>
          </div>

          <div class="identify-options" :class="{ 'show-result': identifySelected !== null }">
            <button
              v-for="(opt, i) in identifyQuestions[identifyIndex].options"
              :key="i"
              class="identify-option"
              :class="{
                selected: identifySelected === i,
                correct: identifySelected !== null && identifyIsCorrect === true && opt.value === identifyQuestions[identifyIndex].correctValue,
                wrong: identifySelected === i && opt.value !== identifyQuestions[identifyIndex].correctValue,
              }"
              :disabled="identifyFeedbackPending"
              @click="handleIdentifySelect(i, $event)"
            >
              <span class="identify-label">{{ opt.label }}</span>
              <Check v-if="identifySelected !== null && identifyIsCorrect === true && opt.value === identifyQuestions[identifyIndex].correctValue" :size="24" class="opt-mark" />
              <X v-else-if="identifySelected === i && opt.value !== identifyQuestions[identifyIndex].correctValue" :size="24" class="opt-mark" />
            </button>
          </div>

          <div class="score-display">
            正确：{{ identifyFirstCorrect.size }} / {{ identifyIndex }}
          </div>
        </template>
      </div>

      <!-- 结算 -->
      <div v-else class="result-panel">
        <div class="decorations">
          <span v-for="i in 8" :key="i" class="deco" :class="'dec-' + i">
            <Star v-if="i % 2 === 0" :size="18" fill="#FFD700" color="#FFD700" />
            <PartyPopper v-else :size="16" color="#FF9F43" />
          </span>
        </div>

        <h2 class="result-title">
          <span v-if="listenAccuracy >= 90">🎉 太棒了！🎉</span>
          <span v-else-if="listenAccuracy >= 70">💪 做得不错！💪</span>
          <span v-else>🌟 再接再厉！🌟</span>
        </h2>

        <div class="result-card" :class="{
          'card-excellent': listenAccuracy >= 90,
          'card-good': listenAccuracy >= 70 && listenAccuracy < 90,
          'card-normal': listenAccuracy < 70
        }">
          <div class="accuracy-circle" :class="{
            excellent: listenAccuracy >= 90,
            good: listenAccuracy >= 70 && listenAccuracy < 90,
            normal: listenAccuracy < 70
          }">{{ listenAccuracy }}</div>

          <div class="result-stats">
            <div class="stat-item">
              <Check :size="20" color="#3498db" />
              <span class="stat-label">正确</span>
              <span class="stat-value correct-text">{{ listenCorrectCount }}</span>
            </div>
            <div class="stat-item">
              <XCircle :size="20" color="#f56c6c" />
              <span class="stat-label">错误</span>
              <span class="stat-value wrong-text">{{ listenModeTotal - listenCorrectCount }}</span>
            </div>
          </div>
        </div>

        <!-- 答题记录（自动展示） -->
        <div class="history-list">
          <template v-if="listenType === 'pinyin'">
            <div
              v-for="(q, i) in listenQuestions"
              :key="i"
              class="history-item"
              :class="{ correct: listenFirstCorrect.has(i), wrong: !listenFirstCorrect.has(i) }"
              @click="speakWord(q.syllable.word)"
            >
              <span class="history-index">{{ i + 1 }}</span>
              <span class="history-word">{{ q.syllable.word }}</span>
              <span class="history-expr">{{ q.syllable.pinyin }}</span>
              <span v-if="!listenFirstCorrect.has(i)" class="history-user">你选的：{{ listenUserFirstAnswers[i] }}</span>
              <Volume2 :size="14" class="history-speaker" />
              <Check v-if="listenFirstCorrect.has(i)" :size="16" class="icon-correct" />
              <XCircle v-else :size="16" class="icon-wrong" />
            </div>
          </template>
          <template v-else>
            <div
              v-for="(q, i) in identifyQuestions"
              :key="i"
              class="history-item"
              :class="{ correct: identifyFirstCorrect.has(i), wrong: !identifyFirstCorrect.has(i) }"
              @click="speakWord(q.syllable.word)"
            >
              <span class="history-index">{{ i + 1 }}</span>
              <span class="history-word">{{ q.syllable.word }}</span>
              <span class="history-expr">{{ q.correctValue }}</span>
              <span v-if="!identifyFirstCorrect.has(i)" class="history-user">你选的：{{ identifyUserFirstAnswers[i] }}</span>
              <Volume2 :size="14" class="history-speaker" />
              <Check v-if="identifyFirstCorrect.has(i)" :size="16" class="icon-correct" />
              <XCircle v-else :size="16" class="icon-wrong" />
            </div>
          </template>
        </div>

        <div class="result-buttons">
          <button class="btn btn-primary btn-restart" @click="startListenGame">
            <Play :size="20" /> 再玩一次
          </button>
          <button class="btn btn-back-lobby" @click="emit('back-to-lobby')">
            <Home :size="20" /> 返回大厅
          </button>
        </div>
      </div>
    </template>

    <!-- ==================== 拼读闯关 ==================== -->
    <template v-else-if="page === 'spell'">

      <!-- 难度选择 -->
      <div v-if="spellState === 'setup'" class="setup-panel">
        <div class="setup-header">
          <div class="header-left-side">
            <button class="btn-back" @click="page = 'select'">
              ← 返回
            </button>
            <h2 class="panel-title">拼读闯关</h2>
          </div>
          <button class="btn-home" @click="emit('back-to-lobby')">
            <Home :size="16" /> 返回大厅
          </button>
        </div>

        <div class="mode-info">
          <Pencil :size="20" color="#e67e22" />
          <span>看汉字，选出声母、韵母和声调，拼出正确拼音！</span>
        </div>

        <div class="form-group">
          <label class="label">题目数量</label>
          <div class="option-buttons">
            <button
              v-for="cnt in questionCountOptions" :key="cnt"
              class="option-btn"
              :class="{ active: spellQuestionCount === cnt }"
              @click="spellQuestionCount = cnt"
            >{{ cnt }}题</button>
          </div>
        </div>

        <button class="btn btn-primary" @click="startSpellGame">
          <Play :size="18" /> 开始闯关
        </button>
      </div>

      <!-- 答题中 -->
      <div v-else-if="spellState === 'playing'" class="game-container">
        <div class="game-header">
          <span class="progress">{{ spellIndex + 1 }} / {{ spellQuestions.length }}</span>
          <span class="badge" style="background:#fef3e2;color:#e67e22;">拼读闯关</span>
          <button class="btn-exit" @click="spellState = 'setup'">
            <X :size="16" /> 退出
          </button>
        </div>

        <!-- 激励动画 -->
        <div class="incentive-area">
          <div v-if="showStar" class="anim-pop" :key="'s2-' + animKey">
            <Star :size="60" fill="#FFD700" color="#FFD700" />
          </div>
          <div v-if="showThumbUp" class="anim-pop" :key="'t2-' + animKey">
            <ThumbsUp :size="60" color="#FF6B6B" />
          </div>
          <div v-if="showHeart" class="anim-pop" :key="'h2-' + animKey">
            <Heart :size="60" fill="#FF6B6B" color="#FF6B6B" />
          </div>
        </div>

        <!-- 题目展示（小喇叭直接复用听音辨音样式） -->
        <div class="sound-card-row spell-question-card" :class="{ 'spell-correct': spellIsCorrect === true, 'spell-wrong': spellIsCorrect === false }">
          <div class="sound-card" @click="speakWord(spellQuestions[spellIndex].syllable.word)">
            <Volume2 :size="36" color="#3498db" />
            <span class="pinyin-word-text">{{ spellQuestions[spellIndex].syllable.word }}</span>
          </div>
          <button class="word-group-btn" @click.stop="speakGroupWord(spellQuestions[spellIndex].syllable.word)" :title="hasGroupWord(spellQuestions[spellIndex].syllable.word) ? '听组词' : '暂无组词'">词</button>
        </div>

        <!-- 声母选择 -->
        <div class="spell-section">
          <h3 class="spell-section-title">选择声母</h3>
          <div class="spell-options">
            <button
              v-for="opt in spellQuestions[spellIndex].initialOptions"
              :key="opt"
              class="spell-opt"
              :class="{
                selected: spellInitial === opt,
                'correct-reveal': spellIsCorrect === true && opt === spellQuestions[spellIndex].syllable.initial,
                'wrong-reveal': spellIsCorrect === false && spellInitial === opt && opt !== spellQuestions[spellIndex].syllable.initial,
              }"
              :disabled="spellIsCorrect === true"
              @click="spellInitial = opt"
            >{{ opt }}</button>
          </div>
        </div>

        <!-- 韵母选择 -->
        <div class="spell-section">
          <h3 class="spell-section-title">选择韵母</h3>
          <div class="spell-options">
            <button
              v-for="opt in spellQuestions[spellIndex].finalOptions"
              :key="opt"
              class="spell-opt"
              :class="{
                selected: spellFinal === opt,
                'correct-reveal': spellIsCorrect === true && opt === spellQuestions[spellIndex].syllable.final,
                'wrong-reveal': spellIsCorrect === false && spellFinal === opt && opt !== spellQuestions[spellIndex].syllable.final,
              }"
              :disabled="spellIsCorrect === true"
              @click="spellFinal = opt"
            >{{ opt }}</button>
          </div>
        </div>

        <!-- 声调选择 -->
        <div class="spell-section">
          <h3 class="spell-section-title">选择声调</h3>
          <div class="spell-options tone-options">
            <button
              v-for="t in spellQuestions[spellIndex].toneOptions"
              :key="t"
              class="spell-opt tone-opt"
              :class="{
                selected: spellTone === t,
                'correct-reveal': spellIsCorrect === true && t === spellQuestions[spellIndex].syllable.tone,
                'wrong-reveal': spellIsCorrect === false && spellTone === t && t !== spellQuestions[spellIndex].syllable.tone,
              }"
              :disabled="spellIsCorrect === true"
              @click="spellTone = t"
            >
              <span class="tone-mark">{{ toneMarks[t] }}</span>
              <span class="tone-label">{{ toneLabels[t] }}</span>
            </button>
          </div>
        </div>

        <!-- 提交按钮 -->
        <button
          class="btn btn-submit"
          :class="{ disabled: !allSpellSelected || spellIsCorrect === true }"
          :disabled="!allSpellSelected || spellIsCorrect === true"
          @click="submitSpellAnswer"
        >
          提交答案
        </button>

        <div class="score-display">
          正确：{{ spellCorrectCount }} / {{ spellIndex }}
        </div>
      </div>

      <!-- 结算 -->
      <div v-else class="result-panel">
        <div class="decorations">
          <span v-for="i in 8" :key="i" class="deco" :class="'dec-' + i">
            <Star v-if="i % 2 === 0" :size="18" fill="#FFD700" color="#FFD700" />
            <PartyPopper v-else :size="16" color="#FF9F43" />
          </span>
        </div>

        <h2 class="result-title">
          <span v-if="spellAccuracy >= 90">🎉 太棒了！🎉</span>
          <span v-else-if="spellAccuracy >= 70">💪 做得不错！💪</span>
          <span v-else>🌟 再接再厉！🌟</span>
        </h2>

        <div class="result-card" :class="{
          'card-excellent': spellAccuracy >= 90,
          'card-good': spellAccuracy >= 70 && spellAccuracy < 90,
          'card-normal': spellAccuracy < 70
        }">
          <div class="accuracy-circle" :class="{
            excellent: spellAccuracy >= 90,
            good: spellAccuracy >= 70 && spellAccuracy < 90,
            normal: spellAccuracy < 70
          }">{{ spellAccuracy }}</div>

          <div class="result-stats">
            <div class="stat-item">
              <Check :size="20" color="#3498db" />
              <span class="stat-label">正确</span>
              <span class="stat-value correct-text">{{ spellCorrectCount }}</span>
            </div>
            <div class="stat-item">
              <XCircle :size="20" color="#f56c6c" />
              <span class="stat-label">错误</span>
              <span class="stat-value wrong-text">{{ spellHistory.length - spellCorrectCount }}</span>
            </div>
          </div>
        </div>

        <div class="history-list spell-history-list">
          <h3 class="history-heading">答题记录</h3>
          <div
            v-for="(item, i) in spellHistory"
            :key="i"
            class="history-item"
            :class="{ correct: item.isCorrect, wrong: !item.isCorrect }"
            @click="speakWord(item.question)"
          >
            <span class="history-index">{{ i + 1 }}</span>
            <span class="history-word">{{ item.question }}</span>
            <span class="history-expr">{{ item.correctAnswer }}</span>
            <span v-if="!item.isCorrect" class="history-user">你答：{{ item.userAnswer }}</span>
            <Volume2 :size="14" class="history-speaker" />
            <Check v-if="item.isCorrect" :size="16" class="icon-correct" />
            <XCircle v-else :size="16" class="icon-wrong" />
          </div>
        </div>

        <div class="result-buttons">
          <button class="btn btn-primary btn-restart" @click="startSpellGame">
            <Play :size="20" /> 再玩一次
          </button>
          <button class="btn btn-back-lobby" @click="emit('back-to-lobby')">
            <Home :size="20" /> 返回大厅
          </button>
        </div>
      </div>
    </template>

  </div>
</template>

<style scoped>
.pinyin-tool {
  max-width: 700px;
  margin: 0 auto;
}

/* ==================== 公共 ==================== */
.setup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
}

.header-left-side {
  display: flex;
  align-items: center;
  gap: 16px;
}

.panel-title {
  font-size: 28px;
  color: #2c3e50;
  text-align: center;
}

.setup-header .panel-title {
  margin: 0;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  font-size: 14px;
  background: #f5f7fa;
  color: #606266;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-back:hover { background: #e8f4fd; border-color: #3498db; color: #3498db; }

.btn-home {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 8px 14px;
  font-size: 14px;
  background: #f5f7fa;
  color: #3498db;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}
.btn-home:hover { background: #e8f4fd; border-color: #3498db; }

.form-group { margin-bottom: 24px; }
.label {
  display: block;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 12px;
}
.range-hint {
  font-size: 14px;
  color: #909399;
}
.option-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.option-btn {
  padding: 10px 16px;
  font-size: 14px;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  color: #606266;
  font-family: inherit;
}
.option-btn:hover { border-color: #3498db; color: #3498db; }
.option-btn.active { background: #3498db; border-color: #3498db; color: #fff; }

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 500;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}
.btn-primary {
  width: 100%;
  background: #3498db;
  color: #fff;
}
.btn-primary:hover { background: #2980b9; }

/* 模式选择页 */
.mode-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px;
  background: #e8f4fd;
  border-radius: 12px;
  margin-bottom: 24px;
  font-size: 14px;
  color: #2c3e50;
}
.mode-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 40px;
}
.mode-card {
  background: #fff;
  border: 2px solid #ebeef5;
  border-radius: 20px;
  padding: 32px 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  font-family: inherit;
}
.mode-card:hover {
  border-color: #3498db;
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(52, 152, 219, 0.15);
}
.mode-icon {
  width: 68px;
  height: 68px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 50%;
}
.mode-name { font-size: 18px; color: #2c3e50; font-weight: 600; }
.mode-desc { font-size: 13px; color: #909399; line-height: 1.4; }

/* 游戏区域 */
.game-container {
  position: relative;
}
.game-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.progress { color: #909399; font-size: 14px; }
.badge {
  background: #e8f4fd;
  color: #3498db;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 14px;
}
.btn-exit {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  font-size: 14px;
  background: #f5f7fa;
  color: #606266;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}
.btn-exit:hover { background: #fef0f0; color: #f56c6c; border-color: #f56c6c; }

.incentive-area {
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.anim-pop {
  animation: popIn 0.5s ease-out;
}
@keyframes popIn {
  0% { transform: scale(0); opacity: 0; }
  50% { transform: scale(1.3); }
  100% { transform: scale(1); opacity: 1; }
}

.score-display {
  text-align: center;
  color: #606266;
  font-size: 14px;
  margin-top: 16px;
}

/* 听音辨音 — 发音区域（与"词"按钮并列，等高等宽对齐） */
.sound-card-row {
  display: flex;
  align-items: stretch;
  gap: 12px;
  margin-bottom: 24px;
}
.sound-card {
  flex: 1;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-evenly;
  gap: 8px;
  padding: 24px;
  background: #f0f7ff;
  border: 2px dashed #3498db;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s;
}
.sound-card:hover {
  background: #e0efff;
  transform: scale(1.02);
}
.pinyin-word-text {
  font-size: 36px;
  font-weight: 700;
  color: #2c3e50 !important;
}

/* 听音辨音 — 选项 */
.listen-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.listen-option {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: #fff;
  border: 2px solid #ebeef5;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
}
.listen-option.selected { border-color: #3498db; }
.listen-option.correct {
  border-color: #3498db;
  background: #e8f4fd;
}
.listen-option.wrong {
  border-color: #f56c6c;
  background: #fef0f0;
}
.listen-option:disabled {
  opacity: 1;
  cursor: default;
}
.listen-option:disabled.correct {
  border-color: #3498db;
  background: #e8f4fd;
}
.listen-option:disabled.wrong {
  border-color: #f56c6c;
  background: #fef0f0;
}
.listen-option:focus-visible {
  outline: 3px solid rgba(52, 152, 219, 0.35);
  outline-offset: 2px;
}
.pinyin-text {
  font-size: 32px;
  font-weight: 700;
  color: #2c3e50;
}
.opt-mark {
  position: absolute;
  top: 8px;
  right: 8px;
}

/* 拼读闯关 题目卡片（移除多余嵌套，直接复用 sound-card-row） */
.spell-question-card {
  margin-bottom: 24px;
  transition: all 0.3s;
}
.spell-question-card.spell-correct .sound-card { border-color: #3498db; background: #e8f4fd; }
.spell-question-card.spell-wrong .sound-card { border-color: #f56c6c; background: #fef0f0; }


/* 听组词"词"方形按钮：边长 = 兄弟小喇叭(.sound-card)高度（由 JS 写入 --spk-h），真正正方形 */
.word-group-btn {
  flex: 0 0 auto;
  align-self: center;
  width: var(--spk-h, 80px);
  height: var(--spk-h, 80px);
  border: 2px solid #3498db;
  border-radius: 16px;
  background: #ebf5fc;
  color: #3498db;
  font-size: 26px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
  padding: 0;
  font-family: inherit;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
}
.word-group-btn:hover {
  background: #3498db;
  color: #fff;
  transform: scale(1.04);
}
.word-group-btn:active {
  transform: scale(0.94);
}
.word-group-btn.purple {
  border-color: #8e44ad;
  background: #f5effb;
  color: #8e44ad;
}
.word-group-btn.purple:hover {
  background: #8e44ad;
  color: #fff;
}
/* 无组词数据的降级样式 */
.word-group-btn.disabled,
.word-group-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
  transform: none !important;
}
.word-group-btn.disabled:hover,
.word-group-btn:disabled:hover {
  background: #ebf5fc;
  color: #3498db;
  transform: none;
}
.word-group-btn.purple.disabled:hover,
.word-group-btn.purple:disabled:hover {
  background: #f5effb;
  color: #8e44ad;
}

/* 拼读选项区 */
.spell-section { margin-bottom: 16px; }
.spell-section-title {
  font-size: 15px;
  color: #606266;
  margin-bottom: 10px;
}
.spell-options {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
}
.spell-opt {
  padding: 12px;
  font-size: 22px;
  font-weight: 600;
  background: #fff;
  border: 2px solid #ebeef5;
  border-radius: 10px;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  color: #2c3e50;
  font-family: inherit;
  -webkit-transform: translateZ(0);
  -webkit-backface-visibility: hidden;
  -webkit-appearance: none;
  appearance: none;
}
.spell-opt:not(:disabled):hover { border-color: #e67e22; background: #fef9f2; }
.spell-opt.selected { border-color: #e67e22; background: #fef3e2; }
.spell-opt.correct-reveal { border-color: #67c23a; background: #f0f9eb; color: #67c23a; }
.spell-opt.wrong-reveal { border-color: #f56c6c; background: #fef0f0; color: #f56c6c; }
.spell-opt:disabled {
  background: #fff;
  cursor: default;
}

.tone-options {
  grid-template-columns: repeat(5, 1fr);
}
.tone-opt {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 14px 8px;
}
.tone-mark {
  font-size: 28px;
  line-height: 1;
  color: inherit;
}
.tone-label {
  font-size: 12px;
  color: #909399;
}

.btn-submit {
  width: 100%;
  margin-top: 20px;
  padding: 14px;
  font-size: 18px;
  background: #e67e22;
  color: #fff;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-family: inherit;
  font-weight: 600;
  transition: all 0.2s;
}
.btn-submit:hover:not(:disabled) { background: #d35400; }
.btn-submit.disabled, .btn-submit:disabled { background: #bdc3c7; cursor: not-allowed; }

/* ==================== 认音识字 ==================== */

.identify-prompt {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 16px;
}
.identify-type-badge {
  background: #f5effb;
  color: #8e44ad;
  padding: 4px 14px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
}
.identify-hint {
  font-size: 16px;
  color: #606266;
}

.identify-sound-card {
  border-color: #8e44ad;
  background: #f5effb;
}
.identify-sound-card:hover {
  background: #ede1f6;
}
.identify-word-text {
  font-size: 36px;
  font-weight: 700;
  color: #6c3483 !important;
}

.identify-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.identify-option {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 24px;
  background: #fff;
  border: 3px solid #ebeef5;
  border-radius: 20px;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s, transform 0.2s, box-shadow 0.2s;
  font-family: inherit;
  -webkit-transform: translateZ(0);
  -webkit-backface-visibility: hidden;
  -webkit-appearance: none;
  appearance: none;
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
}
.identify-option.selected { border-color: #8e44ad; }
.identify-option.correct {
  border-color: #3498db;
  background: #e8f4fd;
}
.identify-option.wrong {
  border-color: #f56c6c;
  background: #fef0f0;
}
.identify-option:disabled {
  opacity: 1;
  background: #fff;
  cursor: default;
}
.identify-option:disabled.correct {
  border-color: #3498db;
  background: #e8f4fd;
}
.identify-option:disabled.wrong {
  border-color: #f56c6c;
  background: #fef0f0;
}
.identify-option:focus-visible {
  outline: 3px solid rgba(142, 68, 173, 0.3);
  outline-offset: 2px;
}

@media (hover: hover) and (pointer: fine) {
  .listen-option:not(:disabled):hover {
    border-color: #3498db;
    background: #f0f7ff;
  }

  .identify-option:not(:disabled):hover {
    border-color: #8e44ad;
    background: #faf5ff;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(142, 68, 173, 0.15);
  }
}
.identify-label {
  font-size: 48px;
  font-weight: 800;
  color: #2c3e50;
  letter-spacing: 2px;
}

/* ==================== 结算页 ==================== */
.result-panel { position: relative; overflow: hidden; }
.decorations { position: absolute; top: 0; left: 0; right: 0; bottom: 0; pointer-events: none; }
.deco { position: absolute; animation: twinkle 2s ease-in-out infinite; }
.dec-1 { top: 5%; left: 5%; animation-delay: 0s; }
.dec-2 { top: 10%; right: 8%; animation-delay: 0.2s; }
.dec-3 { top: 25%; left: 3%; animation-delay: 0.4s; }
.dec-4 { top: 35%; right: 5%; animation-delay: 0.6s; }
.dec-5 { top: 50%; left: 8%; animation-delay: 0.8s; }
.dec-6 { top: 60%; right: 3%; animation-delay: 1s; }
.dec-7 { top: 75%; left: 5%; animation-delay: 1.2s; }
.dec-8 { top: 85%; right: 8%; animation-delay: 1.4s; }
@keyframes twinkle {
  0%, 100% { opacity: 0.6; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.2); }
}

.result-title {
  font-size: 32px;
  color: #2c3e50;
  margin-bottom: 24px;
  text-align: center;
  animation: bounceIn 0.6s ease-out;
}
@keyframes bounceIn {
  0% { transform: scale(0.5); opacity: 0; }
  60% { transform: scale(1.1); }
  100% { transform: scale(1); opacity: 1; }
}

.result-card {
  background: #fff;
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  margin-bottom: 24px;
  transition: all 0.3s;
}
.result-card.card-excellent { background: linear-gradient(135deg,#fff9e6 0%,#fff 100%); border: 3px solid #FFD700; }
.result-card.card-good { background: linear-gradient(135deg,#f0f9eb 0%,#fff 100%); border: 3px solid #67c23a; }
.result-card.card-normal { background: linear-gradient(135deg,#fef0f0 0%,#fff 100%); border: 3px solid #E6A23C; }

.accuracy-circle {
  width: 120px; height: 120px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  font-weight: 800;
  margin: 0 auto 24px;
  background: linear-gradient(135deg,#f5f7fa 0%,#e4e7eb 100%);
  border: 4px solid #909399;
  color: #909399;
}
.accuracy-circle.excellent { background: linear-gradient(135deg,#fff9e6 0%,#ffe066 100%); border-color:#FFD700; color:#d48806; box-shadow:0 8px 30px rgba(255,215,0,0.4); }
.accuracy-circle.good { background: linear-gradient(135deg,#f0f9eb 0%,#b3e19d 100%); border-color:#67c23a; color:#529b2e; box-shadow:0 8px 30px rgba(103,194,58,0.4); }
.accuracy-circle.normal { background: linear-gradient(135deg,#fef0f0 0%,#fab6b6 100%); border-color:#E6A23C; color:#cf9236; box-shadow:0 8px 30px rgba(230,162,60,0.4); }

.result-stats {
  display: flex;
  justify-content: center;
  gap: 40px;
}
.stat-item { text-align: center; display: flex; flex-direction: column; align-items: center; gap: 4px; }
.stat-label { color: #909399; font-size: 14px; }
.stat-value { font-size: 28px; font-weight: 700; color: #2c3e50; }

.result-buttons {
  display: flex;
  gap: 16px;
  max-width: 400px;
  margin: 0 auto;
}
.btn-restart {
  flex: 1;
  padding: 16px;
  font-size: 18px;
  border-radius: 30px;
  box-shadow: 0 4px 15px rgba(52,152,219,0.4);
  justify-content: center;
}
.btn-restart:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(52,152,219,0.5); }
.btn-back-lobby {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  font-size: 18px;
  background: linear-gradient(135deg,#67c23a 0%,#85ce61 100%);
  color: #fff;
  border: none;
  border-radius: 30px;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(103,194,58,0.4);
  transition: all 0.3s;
  font-family: inherit;
}
.btn-back-lobby:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(103,194,58,0.5); }

/* 答题记录列表（结果页自动展示） */
.history-list {
  margin: 20px 0 24px;
  padding: 16px;
  background: #fafafa;
  border-radius: 12px;
}
.history-heading {
  margin: 0 0 12px;
  color: #2c3e50;
  font-size: 16px;
  text-align: left;
}
.history-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  background: #f5f7fa;
  gap: 10px;
  cursor: pointer;
  transition: background 0.15s;
}
.history-item:last-child { margin-bottom: 0; }
.history-item:hover { background: #e8eaed; }
.history-item.correct { background: #e8f4fd; }
.history-item.correct:hover { background: #d6eafa; }
.history-item.wrong { background: #fef0f0; }
.history-item.wrong:hover { background: #fde2e2; }
.history-speaker {
  color: #3498db;
  flex-shrink: 0;
  margin-left: auto;
  opacity: 0.6;
  transition: opacity 0.15s;
}
.history-item:hover .history-speaker { opacity: 1; }
.history-index {
  width: 24px; height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border-radius: 50%;
  font-size: 12px;
  color: #909399;
  flex-shrink: 0;
}
.history-word {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  flex-shrink: 0;
  min-width: 32px;
  text-align: center;
}
.history-expr {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}
.history-user {
  font-size: 13px;
  color: #f56c6c;
  flex-shrink: 0;
}
.icon-correct { color: #3498db; flex-shrink: 0; }
.icon-wrong { color: #f56c6c; flex-shrink: 0; }

/* 移动端 */
@media (max-width: 768px) {
  .panel-title { font-size: 24px; }
  .mode-grid { grid-template-columns: 1fr 1fr; }
  .setup-header { flex-wrap: wrap; gap: 12px; }
  .header-left-side { width: 100%; justify-content: space-between; }
  .btn-home { font-size: 12px; padding: 6px 10px; }

  .listen-options { grid-template-columns: 1fr 1fr; gap: 10px; }
  .spell-opt { font-size: 15px; padding: 10px 6px; }
  .tone-mark { font-size: 22px; }
  .pinyin-text { font-size: 26px; }
  .listen-option { padding: 16px; }

  .spell-options { grid-template-columns: repeat(5, 1fr); }
  .tone-options { grid-template-columns: repeat(5, 1fr); }

  .result-title { font-size: 26px; }
  .result-card { padding: 20px; }
  .result-stats { gap: 20px; }
  .result-buttons { flex-direction: column; }

  .identify-options { grid-template-columns: 1fr 1fr; gap: 10px; }
  .identify-option { padding: 24px 16px; }
  .identify-label { font-size: 36px; }
}
</style>
