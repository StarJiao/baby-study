<script lang="ts" setup>
import { ref, computed, watch } from 'vue'
import { Play, X, Check, XCircle, Star, ThumbsUp, Heart, Home, ChevronRight } from 'lucide-vue-next'

interface Question {
  id: number
  expression: string
  answer: number
}

interface QuestionHistory {
  question: Question
  userAnswer: number | null
  isCorrect: boolean
}

const emit = defineEmits<{
  'back-to-lobby': []
}>()

const difficulties = [
  { value: 1, label: '10以内加减' },
  { value: 2, label: '10以内连加连减混合' },
  { value: 3, label: '20以内无需借位进位' },
  { value: 4, label: '20以内需要借位进位' }
]

const questionCountOptions = [5, 10, 15, 20, 30, 50]

const selectedDifficulty = ref(1)
const questionCount = ref(10)
const answerInput = ref<HTMLInputElement | null>(null)
const questions = ref<Question[]>([])
const currentIndex = ref(0)
const userAnswer = ref<number | ''>('')
const correctCount = ref(0)
const isStarted = ref(false)
const isFinished = ref(false)
const isCorrect = ref<boolean | null>(null)
const history = ref<QuestionHistory[]>([])
const showHistorySheet = ref(false)

// 动画状态
const showStar = ref(false)
const showThumbUp = ref(false)
const showHeart = ref(false)

const currentQuestion = computed(() => questions.value[currentIndex.value])
const progress = computed(() => `${currentIndex.value + 1}/${questions.value.length}`)

// 播放正确音效 - 可爱的小星星音效
const playCorrectSound = () => {
  try {
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
    // 叮叮叮~ 星星音效
    const notes = [784, 880, 988, 1047] // G5, A5, B5, C6
    
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
  } catch (e) {
    console.log('Audio not supported')
  }
}

// 播放错误音效 - 柔和的再来一次
const playWrongSound = () => {
  try {
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
    // 低沉的提示音
    const notes = [330, 294] // E4, D4
    
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
  } catch (e) {
    console.log('Audio not supported')
  }
}

// 触发视觉激励
const triggerCorrectAnimation = () => {
  // 随机选择一种动画
  const animType = Math.floor(Math.random() * 3)
  if (animType === 0) {
    showStar.value = true
    setTimeout(() => showStar.value = false, 1000)
  } else if (animType === 1) {
    showThumbUp.value = true
    setTimeout(() => showThumbUp.value = false, 1000)
  } else {
    showHeart.value = true
    setTimeout(() => showHeart.value = false, 1000)
  }
}

// 结束游戏，返回难度选择页面
const finishGame = () => {
  isStarted.value = false
  isFinished.value = false
  questions.value = []
  currentIndex.value = 0
  history.value = []
  showHistorySheet.value = false
}

const startGame = () => {
  questions.value = generateQuestions(selectedDifficulty.value, questionCount.value)
  currentIndex.value = 0
  correctCount.value = 0
  isStarted.value = true
  isFinished.value = false
  userAnswer.value = ''
  isCorrect.value = null
  history.value = []
  showHistorySheet.value = false

  // 自动聚焦到输入框
  setTimeout(() => {
    answerInput.value?.focus()
  }, 100)
}

// 题目生成逻辑（从 Go 后端移植）
const generateQuestions = (difficulty: number, count: number): Question[] => {
  const generated = new Set<string>()
  const result: Question[] = []

  while (result.length < count) {
    const q = generateSingleQuestion(difficulty)
    if (!generated.has(q.expression)) {
      generated.add(q.expression)
      result.push({ id: result.length + 1, expression: q.expression, answer: q.answer })
    }
  }

  return result
}

const generateSingleQuestion = (difficulty: number): { expression: string, answer: number } => {
  switch (difficulty) {
    case 1: return generateLevel1()
    case 2: return generateLevel2()
    case 3: return generateLevel3()
    case 4: return generateLevel4()
    default: return generateLevel1()
  }
}

// Level 1: 10以内加减
const generateLevel1 = (): { expression: string, answer: number } => {
  const isAdd = Math.random() < 0.5
  if (isAdd) {
    const a = Math.floor(Math.random() * 9) + 1
    const b = Math.floor(Math.random() * (9 - a)) + 1
    return { expression: `${a} + ${b}`, answer: a + b }
  }
  const a = Math.floor(Math.random() * 9) + 1
  const b = Math.floor(Math.random() * (a - 1)) + 1
  return { expression: `${a} - ${b}`, answer: a - b }
}

// Level 2: 10以内连加连减混合
const generateLevel2 = (): { expression: string, answer: number } => {
  while (true) {
    const a = Math.floor(Math.random() * 9) + 1
    const b = Math.floor(Math.random() * 9) + 1
    const c = Math.floor(Math.random() * 9) + 1
    const op1 = Math.random() < 0.5 ? '+' : '-'
    const op2 = Math.random() < 0.5 ? '+' : '-'

    const step1 = op1 === '+' ? a + b : a - b
    if (step1 < 1 || step1 >= 10) continue

    const result = op2 === '+' ? step1 + c : step1 - c
    if (result < 1 || result >= 10) continue

    return { expression: `${a} ${op1} ${b} ${op2} ${c}`, answer: result }
  }
}

// Level 3: 20以内无需进位、无需借位
const generateLevel3 = (): { expression: string, answer: number } => {
  const isAdd = Math.random() < 0.5
  if (isAdd) {
    while (true) {
      const a = Math.floor(Math.random() * 20) + 1
      const b = Math.floor(Math.random() * 20) + 1
      if ((a >= 11 || b >= 11) && (a % 10) + (b % 10) < 10 && a + b <= 20 && a + b >= 1) {
        return { expression: `${a} + ${b}`, answer: a + b }
      }
    }
  }
  while (true) {
    const a = Math.floor(Math.random() * 20) + 1
    const b = Math.floor(Math.random() * 20) + 1
    if ((a >= 11 || b >= 11) && a > b && a % 10 >= b % 10) {
      return { expression: `${a} - ${b}`, answer: a - b }
    }
  }
}

// Level 4: 20以内需要进位、需要借位
const generateLevel4 = (): { expression: string, answer: number } => {
  const isAdd = Math.random() < 0.5
  if (isAdd) {
    while (true) {
      const a = Math.floor(Math.random() * 20) + 1
      const b = Math.floor(Math.random() * 20) + 1
      if ((a >= 11 || b >= 11) && (a % 10) + (b % 10) >= 10 && a + b <= 20) {
        return { expression: `${a} + ${b}`, answer: a + b }
      }
    }
  }
  while (true) {
    const a = Math.floor(Math.random() * 20) + 1
    const b = Math.floor(Math.random() * 20) + 1
    if ((a >= 11 || b >= 11) && a > b && a % 10 < b % 10) {
      return { expression: `${a} - ${b}`, answer: a - b }
    }
  }
}

const submitAnswer = () => {
  if (
    isCorrect.value !== null ||
    userAnswer.value === '' ||
    userAnswer.value === null ||
    userAnswer.value === undefined
  ) return
  
  const answer = Number(userAnswer.value)
  const correct = answer === currentQuestion.value.answer

  // 每道题只记录第一次作答，重试答对不改变正确率或历史记录。
  const isFirstAttempt = !history.value.some(
    item => item.question.id === currentQuestion.value.id
  )
  if (isFirstAttempt) {
    history.value.push({
      question: { ...currentQuestion.value },
      userAnswer: answer,
      isCorrect: correct
    })
    if (correct) {
      correctCount.value++
    }
  }
  
  if (correct) {
    isCorrect.value = true
    playCorrectSound()
    triggerCorrectAnimation()

    // 正确：延迟后进入下一题
    setTimeout(() => {
      isCorrect.value = null

      if (currentIndex.value < questions.value.length - 1) {
        currentIndex.value++
        userAnswer.value = ''
        setTimeout(() => {
          answerInput.value?.focus()
        }, 100)
      } else {
        isFinished.value = true
      }
    }, 1000)
  } else {
    isCorrect.value = false
    playWrongSound()

    // 错误：短暂显示错误后重置，让用户重新作答
    setTimeout(() => {
      isCorrect.value = null
      userAnswer.value = ''
      setTimeout(() => {
        answerInput.value?.focus()
      }, 100)
    }, 1200)
  }
}

// 退出当前练习
const exitGame = () => {
  isStarted.value = false
  isFinished.value = false
  questions.value = []
  currentIndex.value = 0
  correctCount.value = 0
  userAnswer.value = ''
  isCorrect.value = null
  history.value = []
  showHistorySheet.value = false
}

const restartGame = () => {
  isStarted.value = false
  isFinished.value = false
  questions.value = []
  currentIndex.value = 0
  correctCount.value = 0
  userAnswer.value = ''
  isCorrect.value = null
  history.value = []
  showHistorySheet.value = false
}

const accuracy = computed(() => {
  if (questions.value.length === 0) return 0
  return Math.round((correctCount.value / questions.value.length) * 100)
})

watch(isFinished, (finished) => {
  if (finished) {
    showHistorySheet.value = true
  }
})

</script>

<template>
  <div class="calculation-tool">
    <!-- 开始游戏前 -->
    <div v-if="!isStarted" class="setup-panel">
      <div class="setup-header">
        <h2 class="panel-title">计算练习</h2>
        <button class="btn-home" @click="emit('back-to-lobby')">
          <Home :size="16" /> 返回大厅
        </button>
      </div>
      
      <div class="form-group">
        <label class="label">选择难度</label>
        <div class="option-buttons">
          <button
            v-for="diff in difficulties"
            :key="diff.value"
            class="option-btn"
            :class="{ active: selectedDifficulty === diff.value }"
            @click="selectedDifficulty = diff.value"
          >
            {{ diff.label }}
          </button>
        </div>
      </div>
      
      <div class="form-group">
        <label class="label">题目数量</label>
        <div class="option-buttons">
          <button
            v-for="count in questionCountOptions"
            :key="count"
            class="option-btn"
            :class="{ active: questionCount === count }"
            @click="questionCount = count"
          >
            {{ count }}题
          </button>
        </div>
      </div>
      
      <button class="btn btn-primary" @click="startGame">
        <Play :size="18" />
        开始练习
      </button>
    </div>

    <!-- 答题中 -->
    <div v-else-if="!isFinished" class="game-container">
      <div class="game-header">
        <span class="progress">{{ progress }}</span>
        <span class="badge">{{ difficulties[selectedDifficulty - 1].label }}</span>
        <button class="btn-exit" @click="exitGame">
          <X :size="16" /> 退出
        </button>
      </div>
      
      <!-- 激励动画 -->
      <div class="incentive-area">
        <div v-if="showStar" class="anim-pop">
          <Star :size="60" fill="#FFD700" color="#FFD700" />
        </div>
        <div v-if="showThumbUp" class="anim-pop">
          <ThumbsUp :size="60" color="#FF6B6B" />
        </div>
        <div v-if="showHeart" class="anim-pop">
          <Heart :size="60" fill="#FF6B6B" color="#FF6B6B" />
        </div>
      </div>
      
      <div class="question-card" :class="{ correct: isCorrect === true, wrong: isCorrect === false }">
        <div class="question-number">第 {{ currentIndex + 1 }} 题</div>
        <div class="question-expression">
          {{ currentQuestion?.expression }} <span class="equals">= ?</span>
        </div>
      </div>
      
      <div class="answer-section">
        <input
          ref="answerInput"
          v-model="userAnswer"
          type="number"
          class="answer-input"
          placeholder="请输入答案"
          @keyup.enter="submitAnswer"
          :disabled="isCorrect !== null"
        />
        <button class="btn btn-primary btn-submit-answer" @click="submitAnswer" :disabled="isCorrect !== null">
          提交
        </button>
      </div>
      
      <div class="score-display">
        正确：{{ correctCount }} / {{ history.length }}
      </div>
    </div>

    <!-- 游戏结束 -->
    <div v-else class="result-panel">
      <h2 class="result-title">练习结果</h2>
      
      <div class="result-card" :class="{ 'card-excellent': accuracy >= 90, 'card-good': accuracy >= 70 && accuracy < 90, 'card-normal': accuracy < 70 }">
        <div class="accuracy-circle" :class="{ excellent: accuracy >= 90, good: accuracy >= 70 && accuracy < 90, normal: accuracy < 70 }">
          {{ accuracy }}
        </div>
        
        <div class="result-stats">
          <div class="stat-item">
            <Check :size="20" color="#67c23a" />
            <span class="stat-label">正确</span>
            <span class="stat-value correct-text">{{ correctCount }}</span>
          </div>
          <div class="stat-item">
            <XCircle :size="20" color="#f56c6c" />
            <span class="stat-label">错误</span>
            <span class="stat-value wrong-text">{{ questions.length - correctCount }}</span>
          </div>
          <div class="stat-item">
            <Star :size="20" color="#909399" />
            <span class="stat-label">总计</span>
            <span class="stat-value">{{ questions.length }}</span>
          </div>
        </div>

        <div class="history-entry" @click="showHistorySheet = true">
          <span>查看答题记录</span>
          <ChevronRight :size="18" />
        </div>
      </div>
      
      <div class="result-buttons">
        <button class="btn btn-primary btn-restart" @click="startGame">
          <Play :size="20" />
          再玩一次
        </button>
        <button class="btn btn-secondary btn-finish" @click="finishGame(); emit('back-to-lobby')">
          <Home :size="20" />
          返回大厅
        </button>
      </div>
    </div>

    <!-- 答题记录半弹层 -->
    <Teleport to="body">
      <div v-if="showHistorySheet" class="sheet-overlay" @click.self="showHistorySheet = false">
        <div class="sheet-panel">
          <div class="sheet-header">
            <h3 class="sheet-title">答题记录</h3>
            <button class="sheet-close" @click="showHistorySheet = false">
              <X :size="20" />
            </button>
          </div>
          <div class="sheet-body">
            <div class="history-list">
              <div 
                v-for="(item, index) in history" 
                :key="index"
                class="history-item"
                :class="{ correct: item.isCorrect, wrong: !item.isCorrect }"
              >
                <span class="history-index">{{ index + 1 }}</span>
                <span class="history-expr">{{ item.question.expression }}</span>
                <span class="history-eq">=</span>
                <span class="history-answer" :class="{ 'answer-wrong': !item.isCorrect }">
                  {{ item.userAnswer }}
                </span>
                <span v-if="!item.isCorrect" class="history-correct-answer">
                  正确：{{ item.question.answer }}
                </span>
                <Check v-if="item.isCorrect" :size="16" class="icon-correct" />
                <XCircle v-else :size="16" class="icon-wrong" />
              </div>
              <div v-if="history.length === 0" class="history-empty">暂无记录</div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.calculation-tool {
  max-width: 700px;
  margin: 0 auto;
}

.panel-title {
  font-size: 28px;
  color: #2c3e50;
  text-align: center;
}

.setup-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
}

.setup-header .panel-title {
  margin-bottom: 0;
}

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
}

.btn-home:hover {
  background: #e8f4fd;
  border-color: #3498db;
}

.form-group {
  margin-bottom: 24px;
}

.label {
  display: block;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 12px;
  text-align: left;
}

.select, .input {
  width: 100%;
  padding: 12px 16px;
  font-size: 16px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  outline: none;
  transition: border-color 0.2s;
}

.select:focus, .input:focus {
  border-color: #3498db;
}

.option-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-start;
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
}

.option-btn:hover {
  border-color: #3498db;
  color: #3498db;
}

.option-btn.active {
  background: #3498db;
  border-color: #3498db;
  color: #fff;
}

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
}

.btn-primary {
  width: 100%;
  background: #3498db;
  color: #fff;
}

.btn-primary:hover {
  background: #2980b9;
}

.btn-primary:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

/* Game Container */
.game-container {
  position: relative;
}

.game-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

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
}

.btn-exit:hover {
  background: #fef0f0;
  color: #f56c6c;
  border-color: #f56c6c;
}

.progress {
  color: #909399;
  font-size: 14px;
}

.question-card {
  background: #fff;
  border-radius: 16px;
  padding: 40px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
  transition: all 0.3s;
}

.question-card.correct {
  background: #f0f9eb;
  border: 2px solid #67c23a;
}

.question-card.wrong {
  background: #fef0f0;
  border: 2px solid #f56c6c;
}

.question-number {
  color: #909399;
  font-size: 14px;
  margin-bottom: 16px;
}

.question-expression {
  font-size: 56px;
  font-weight: 700;
  color: #2c3e50;
  letter-spacing: 4px;
}

.question-expression .equals {
  font-size: 36px;
  font-weight: 500;
  color: #909399;
  margin-left: 8px;
}

.answer-section {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.answer-input {
  flex: 1;
  padding: 16px;
  font-size: 24px;
  text-align: center;
  border: 2px solid #dcdfe6;
  border-radius: 12px;
  outline: none;
}

.answer-input:focus {
  border-color: #3498db;
}

.btn-submit-answer {
  flex: 0 0 auto;
  padding: 16px 32px;
  width: auto;
}

.score-display {
  text-align: center;
  color: #606266;
  font-size: 14px;
  margin-top: 16px;
}

/* 结果页 - 查看记录入口 */
.history-entry {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 12px;
  margin-top: 20px;
  font-size: 14px;
  color: #909399;
  cursor: pointer;
  transition: color 0.2s;
}
.history-entry:hover {
  color: #3498db;
}

/* 半弹层 */
.sheet-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}
.sheet-panel {
  width: 100%;
  max-width: 600px;
  max-height: 70vh;
  background: #fff;
  border-radius: 20px 20px 0 0;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease-out;
}
@keyframes slideUp {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}
.sheet-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
  flex-shrink: 0;
}
.sheet-title {
  font-size: 18px;
  color: #2c3e50;
  margin: 0;
}
.sheet-close {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  color: #606266;
  transition: all 0.2s;
}
.sheet-close:hover {
  background: #e8eaed;
  color: #f56c6c;
}
.sheet-body {
  padding: 16px 24px;
  overflow-y: auto;
  flex: 1;
}

/* History List (reused in sheet) */
.history-list {
  max-height: 100%;
}

.history-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  background: #f5f7fa;
  transition: all 0.2s;
  gap: 10px;
}

.history-item.correct {
  background: #f0f9eb;
}

.history-item.wrong {
  background: #fef0f0;
}

.history-index {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border-radius: 50%;
  font-size: 12px;
  color: #909399;
  flex-shrink: 0;
}

.history-expr {
  flex: 1;
  font-size: 14px;
  color: #2c3e50;
}

.history-eq {
  color: #909399;
  font-size: 14px;
}

.history-answer {
  font-weight: 600;
  font-size: 14px;
  color: #3498db;
  min-width: 24px;
  text-align: center;
}

.history-answer.answer-wrong {
  color: #f56c6c;
}

.history-correct-answer {
  color: #67c23a;
  font-size: 13px;
  white-space: nowrap;
}

.icon-correct {
  color: #67c23a;
  flex-shrink: 0;
}

.icon-wrong {
  color: #f56c6c;
  flex-shrink: 0;
}

.history-empty {
  text-align: center;
  color: #909399;
  padding: 20px;
  font-size: 14px;
}

/* 激励动画 */
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

.result-panel {
  position: relative;
}

.result-title {
  font-size: 32px;
  color: #2c3e50;
  margin-bottom: 24px;
  text-align: center;
}

.result-card {
  background: #fff;
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
  transition: all 0.3s;
}

.result-card.card-excellent {
  background: linear-gradient(135deg, #fff9e6 0%, #fff 100%);
  border: 3px solid #FFD700;
}

.result-card.card-good {
  background: linear-gradient(135deg, #f0f9eb 0%, #fff 100%);
  border: 3px solid #67c23a;
}

.result-card.card-normal {
  background: linear-gradient(135deg, #fef0f0 0%, #fff 100%);
  border: 3px solid #E6A23C;
}

.result-stats {
  display: flex;
  justify-content: center;
  gap: 40px;
}

.stat-item {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-label {
  display: block;
  color: #909399;
  font-size: 14px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
}

.btn-restart {
  padding: 16px 40px;
  font-size: 18px;
  border-radius: 30px;
  box-shadow: 0 4px 15px rgba(52, 152, 219, 0.4);
  flex: 1;
  justify-content: center;
}

.btn-restart:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(52, 152, 219, 0.5);
}

.result-buttons {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
}

.btn-secondary {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  color: white;
  border: none;
  padding: 16px 40px;
  font-size: 18px;
  border-radius: 30px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 15px rgba(103, 194, 58, 0.4);
  transition: all 0.3s ease;
  flex: 1;
  justify-content: center;
}

.btn-secondary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(103, 194, 58, 0.5);
}

/* 分数圆圈 */
.accuracy-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  font-weight: 800;
  margin: 0 auto 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7eb 100%);
  border: 4px solid #909399;
  color: #909399;
  transition: all 0.3s ease;
}

.accuracy-circle.excellent {
  background: linear-gradient(135deg, #fff9e6 0%, #ffe066 100%);
  border-color: #FFD700;
  color: #d48806;
  box-shadow: 0 8px 30px rgba(255, 215, 0, 0.4);
}

.accuracy-circle.good {
  background: linear-gradient(135deg, #f0f9eb 0%, #b3e19d 100%);
  border-color: #67c23a;
  color: #529b2e;
  box-shadow: 0 8px 30px rgba(103, 194, 58, 0.4);
}

.accuracy-circle.normal {
  background: linear-gradient(135deg, #fef0f0 0%, #fab6b6 100%);
  border-color: #E6A23C;
  color: #cf9236;
  box-shadow: 0 8px 30px rgba(230, 162, 60, 0.4);
}

/* ========== 移动端适配 ========== */
@media (max-width: 768px) {
  /* 设置面板 */
  .panel-title {
    font-size: 24px;
    margin-bottom: 24px;
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  .label {
    font-size: 14px;
    margin-bottom: 8px;
  }
  
  .option-btn {
    padding: 10px 14px;
    font-size: 13px;
    flex: 1 1 calc(50% - 5px);
    text-align: center;
    justify-content: center;
  }
  
  .btn {
    padding: 14px 20px;
    font-size: 16px;
  }
  
  /* 游戏面板 */
  .game-container {
    flex-direction: column;
    gap: 16px;
  }
  
  .game-header {
    margin-bottom: 16px;
    flex-wrap: wrap;
    gap: 8px;
  }

  .badge {
    font-size: 12px;
    padding: 5px 10px;
  }
  
  .btn-exit {
    font-size: 12px;
    padding: 5px 10px;
  }
  
  .progress {
    font-size: 13px;
  }
  
  .question-card {
    padding: 24px 16px;
    border-radius: 12px;
    margin-bottom: 16px;
  }
  
  .question-number {
    font-size: 13px;
    margin-bottom: 12px;
  }
  
  .question-expression {
    font-size: 40px;
    letter-spacing: 2px;
  }
  
  .question-expression .equals {
    font-size: 28px;
  }
  
  .answer-section {
    flex-direction: column;
    gap: 12px;
    margin-bottom: 16px;
  }
  
  .answer-input {
    padding: 14px;
    font-size: 20px;
    text-align: center;
  }
  
  .btn-primary {
    padding: 14px;
  }
  
  .score-display {
    font-size: 13px;
  }
  
  /* 结果面板 */
  .result-panel {
    padding: 0 8px;
  }
  
  .result-title {
    font-size: 26px;
    margin-bottom: 24px;
  }
  
  .result-card {
    padding: 24px 16px;
    border-radius: 12px;
    margin-bottom: 20px;
  }

  .result-stats {
    gap: 20px;
  }
  
  .stat-label {
    font-size: 13px;
  }
  
  .stat-value {
    font-size: 20px;
  }
  
}

/* 更小屏幕 */
@media (max-width: 480px) {
  .question-expression {
    font-size: 32px;
    letter-spacing: 1px;
  }
  
  .question-expression .equals {
    font-size: 24px;
  }
  
  .option-btn {
    padding: 8px 12px;
    font-size: 12px;
  }
}
</style>
