<script lang="ts" setup>
import { ref, computed } from 'vue'
import { Play, RotateCcw, X, Check, XCircle, Star, ThumbsUp, Heart, Music, PartyPopper } from 'lucide-vue-next'

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
const isReviewing = ref(false)
const reviewIndex = ref(-1)

// 动画状态
const showStar = ref(false)
const showThumbUp = ref(false)
const showHeart = ref(false)

// 检测是否为移动端
const isMobile = ref(window.innerWidth <= 768)
if (typeof window !== 'undefined') {
  window.addEventListener('resize', () => {
    isMobile.value = window.innerWidth <= 768
  })
}

const currentQuestion = computed(() => questions.value[currentIndex.value])
const progress = computed(() => `${currentIndex.value + 1}/${questions.value.length}`)

// 语音激励
const praiseMessages = [
  '太棒了！', '你真厉害！', '非常好！', '超级棒！', '哇，太厉害了！',
  '好样的！', '真聪明！', '完美！', '厉害极了！', '真棒！'
]

const tryAgainMessages = [
  '再想想哦~', '没关系，再试一次！', '加油，你可以的！', '仔细算一算~'
]

const speak = (text: string) => {
  try {
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.rate = 0.9
    utterance.pitch = 1.2
    utterance.lang = 'zh-CN'
    speechSynthesis.speak(utterance)
  } catch (e) {
    console.log('Speech not supported')
  }
}

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
  
  // 随机语音激励
  const randomPraise = praiseMessages[Math.floor(Math.random() * praiseMessages.length)]
  speak(randomPraise)
}

declare const window: any
declare const go: any

const startGame = async () => {
  if (window.go) {
    const result = await window.go.main.App.GenerateQuestions(selectedDifficulty.value, questionCount.value)
    questions.value = result.map((q: any, index: number) => ({
      id: index + 1,
      expression: q.Expression,
      answer: q.Answer
    }))
  } else {
    // 开发环境模拟数据
    questions.value = generateMockQuestions(selectedDifficulty.value, questionCount.value)
  }
  currentIndex.value = 0
  correctCount.value = 0
  isStarted.value = true
  isFinished.value = false
  userAnswer.value = ''
  isCorrect.value = null
  history.value = []
  
  // 自动聚焦到输入框
  setTimeout(() => {
    answerInput.value?.focus()
  }, 100)
}

const generateMockQuestions = (difficulty: number, count: number): Question[] => {
  const result: Question[] = []
  const maxNum = difficulty === 1 ? 10 : difficulty === 2 ? 10 : 20
  for (let i = 0; i < count; i++) {
    const a = Math.floor(Math.random() * maxNum)
    const b = Math.floor(Math.random() * (maxNum - 1)) + 1
    const isAdd = Math.random() > 0.5
    const expr = isAdd ? `${a} + ${b}` : `${Math.max(a, b)} - ${Math.min(a, b)}`
    const ans = isAdd ? a + b : Math.abs(a - b)
    result.push({ id: i + 1, expression: expr, answer: ans })
  }
  return result
}

const submitAnswer = async () => {
  if (userAnswer.value === '' || userAnswer.value === null || userAnswer.value === undefined) return
  
  const answer = Number(userAnswer.value)
  const correct = answer === currentQuestion.value.answer
  
  // 如果在回溯状态，更新原有记录；否则新增
  if (isReviewing.value) {
    const oldRecord = history.value[reviewIndex.value]
    const wasCorrect = oldRecord ? oldRecord.isCorrect : false
    
    // 更新记录
    history.value[reviewIndex.value] = {
      question: { ...currentQuestion.value },
      userAnswer: answer,
      isCorrect: correct
    }
    
    // 调整正确计数：如果之前是对的现在错了则减一，如果之前是错的现在对了则加一
    if (wasCorrect && !correct) {
      correctCount.value--
    } else if (!wasCorrect && correct) {
      correctCount.value++
    }
    
    isReviewing.value = false
    reviewIndex.value = -1
  } else {
    // 记录历史
    history.value.push({
      question: { ...currentQuestion.value },
      userAnswer: answer,
      isCorrect: correct
    })
    // 新增时正确则计数加一
    if (correct) {
      correctCount.value++
    }
  }
  
  if (correct) {
    isCorrect.value = true
    playCorrectSound()
    triggerCorrectAnimation()
  } else {
    isCorrect.value = false
    playWrongSound()
    // 柔和的鼓励
    const randomMsg = tryAgainMessages[Math.floor(Math.random() * tryAgainMessages.length)]
    speak(randomMsg)
  }
  
  setTimeout(() => {
    isCorrect.value = null
    
    // 如果是回溯状态订正，答题后停留在当前题目
    if (isReviewing.value) {
      isReviewing.value = false
      reviewIndex.value = -1
      userAnswer.value = ''
      // 保持在当前题目
      setTimeout(() => {
        answerInput.value?.focus()
      }, 100)
      return
    }
    
    // 正常答题流程
    if (currentIndex.value < questions.value.length - 1) {
      currentIndex.value++
      userAnswer.value = ''
      // 自动聚焦到输入框
      setTimeout(() => {
        answerInput.value?.focus()
      }, 100)
    } else {
      isFinished.value = true
    }
  }, 1000)
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
}

// 回溯到指定历史题目
const goToHistory = (index: number) => {
  if (isCorrect.value !== null) return // 等待动画完成
  isReviewing.value = true
  reviewIndex.value = index
  currentIndex.value = index
  userAnswer.value = ''
}

const accuracy = computed(() => {
  if (questions.value.length === 0) return 0
  return Math.round((correctCount.value / questions.value.length) * 100)
})

// 监听游戏结束，播放总结语音
import { watch } from 'vue'
watch(isFinished, (finished) => {
  if (finished) {
    setTimeout(() => {
      if (accuracy.value >= 90) {
        speak('太棒了！你超级厉害！')
      } else if (accuracy.value >= 70) {
        speak('做得不错！继续加油！')
      } else {
        speak('没关系，再接再厉！你可以的！')
      }
    }, 500)
  }
})

// 移动端倒序显示历史记录
const reversedHistory = computed(() => {
  return [...history.value].reverse()
})
</script>

<template>
  <div class="calculation-tool">
    <!-- 开始游戏前 -->
    <div v-if="!isStarted" class="setup-panel">
      <h2 class="panel-title">计算练习</h2>
      
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
      <div class="game-panel">
        <div class="game-header">
          <div class="header-left">
            <span class="difficulty-badge">{{ difficulties[selectedDifficulty - 1].label }}</span>
            <button class="btn-exit" @click="exitGame" title="退出练习">
              <X :size="16" />
              退出
            </button>
          </div>
          <span class="progress">{{ progress }}</span>
        </div>
        
        <!-- 激励动画 -->
        <div class="激励机制">
          <div v-if="showStar" class="anim-star">
            <Star :size="60" fill="#FFD700" color="#FFD700" />
            <Star :size="40" fill="#FFD700" color="#FFD700" class="star2" />
            <Star :size="30" fill="#FFD700" color="#FFD700" class="star3" />
          </div>
          <div v-if="showThumbUp" class="anim-thumbup">
            <ThumbsUp :size="60" color="#FF6B6B" />
          </div>
          <div v-if="showHeart" class="anim-heart">
            <Heart :size="60" fill="#FF6B6B" color="#FF6B6B" />
          </div>
        </div>
        
        <div class="question-card" :class="{ correct: isCorrect === true, wrong: isCorrect === false }">
          <div class="question-number">第 {{ currentIndex + 1 }} 题</div>
          <div class="question-expression">{{ currentQuestion?.expression }} = ?</div>
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
          <button class="btn btn-primary" @click="submitAnswer" :disabled="isCorrect !== null">
            提交
          </button>
        </div>
        
        <div class="score-display">
          正确: {{ correctCount }} / {{ currentIndex }}
        </div>
      </div>
      
      <!-- 右侧历史记录 -->
      <div class="history-panel">
        <h3 class="history-title">答题记录</h3>
        <div class="history-list">
          <!-- 桌面端：正序 -->
          <template v-if="!isMobile">
            <div 
              v-for="(item, index) in history" 
              :key="index"
              class="history-item"
              :class="{ correct: item.isCorrect, wrong: !item.isCorrect, clickable: isCorrect === null }"
              @click="goToHistory(index)"
            >
              <span class="history-index">{{ index + 1 }}</span>
              <span class="history-expr">{{ item.question.expression }}</span>
              <Check v-if="item.isCorrect" :size="16" class="icon-correct" />
              <XCircle v-else :size="16" class="icon-wrong" />
            </div>
          </template>
          <!-- 移动端：倒序 -->
          <template v-else>
            <div 
              v-for="(item, index) in reversedHistory" 
              :key="index"
              class="history-item"
              :class="{ correct: item.isCorrect, wrong: !item.isCorrect, clickable: isCorrect === null }"
              @click="goToHistory(history.length - 1 - index)"
            >
              <span class="history-index">{{ history.length - index }}</span>
              <span class="history-expr">{{ item.question.expression }}</span>
              <Check v-if="item.isCorrect" :size="16" class="icon-correct" />
              <XCircle v-else :size="16" class="icon-wrong" />
            </div>
          </template>
          <div v-if="history.length === 0" class="history-empty">
            暂无记录
          </div>
        </div>
      </div>
    </div>

    <!-- 游戏结束 -->
    <div v-else class="result-panel">
      <!-- 装饰元素 -->
      <div class="decorations">
        <span v-for="i in 12" :key="i" class="decoration" :class="'dec-' + i">
          <Star v-if="i % 3 === 0" :size="20" fill="#FFD700" color="#FFD700" />
          <Heart v-else-if="i % 3 === 1" :size="18" fill="#FF6B6B" color="#FF6B6B" />
          <PartyPopper v-else :size="18" color="#FF9F43" />
        </span>
      </div>
      
      <h2 class="result-title">
        <span v-if="accuracy >= 90">🎉 太棒了! 🎉</span>
        <span v-else-if="accuracy >= 70">💪 做得不错! 💪</span>
        <span v-else>🌟 再接再厉! 🌟</span>
      </h2>
      
      <div class="result-card" :class="{ 'card-excellent': accuracy >= 90, 'card-good': accuracy >= 70 && accuracy < 90, 'card-normal': accuracy < 70 }">
        <!-- 吉祥物 -->
        <div class="mascot">
          <span v-if="accuracy >= 90" class="mascot-emoji">🦁</span>
          <span v-else-if="accuracy >= 70" class="mascot-emoji">🐻</span>
          <span v-else class="mascot-emoji">🐨</span>
        </div>
        
        <div class="accuracy-circle" :class="{ excellent: accuracy >= 90, good: accuracy >= 70 && accuracy < 90, normal: accuracy < 70 }">
          {{ accuracy }}%
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
      </div>
      
      <div class="result-message" v-if="accuracy >= 90">
        ✨ 你是最棒的! ✨
      </div>
      <div class="result-message" v-else-if="accuracy >= 70">
        🌈 继续加油! 🌈
      </div>
      <div class="result-message normal-msg">
        💪 加油! 你可以的! 💪
      </div>
      
      <button class="btn btn-primary btn-restart" @click="startGame">
        <Play :size="20" />
        再玩一次
      </button>
    </div>
  </div>
</template>

<style scoped>
.calculation-tool {
  max-width: 100%;
  margin: 0 auto;
}

.panel-title {
  font-size: 28px;
  color: #2c3e50;
  margin-bottom: 32px;
  text-align: center;
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
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.game-panel {
  flex: 1;
  max-width: 600px;
}

.game-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.difficulty-badge {
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
  font-size: 48px;
  font-weight: 600;
  color: #2c3e50;
}

.answer-section {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
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

.score-display {
  text-align: center;
  color: #606266;
  font-size: 14px;
}

/* History Panel */
.history-panel {
  width: 280px;
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.history-title {
  font-size: 16px;
  color: #2c3e50;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.history-list {
  max-height: 400px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  background: #f5f7fa;
  transition: all 0.2s;
}

.history-item.clickable {
  cursor: pointer;
}

.history-item.clickable:hover {
  background: #e8f4fd;
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
  margin-right: 8px;
}

.history-expr {
  flex: 1;
  font-size: 14px;
  color: #2c3e50;
}

.icon-correct {
  color: #67c23a;
}

.icon-wrong {
  color: #f56c6c;
}

.history-empty {
  text-align: center;
  color: #909399;
  padding: 20px;
  font-size: 14px;
}

.result-message.normal-msg {
  color: #E6A23C;
}

/* 激励机制 */
.激励机制 {
  position: relative;
  height: 80px;
  margin-bottom: 16px;
}

.anim-star, .anim-thumbup, .anim-heart {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  animation: popIn 0.5s ease-out;
}

.anim-star .star2 {
  position: absolute;
  left: -30px;
  top: -20px;
  animation: float 1s ease-in-out infinite;
}

.anim-star .star3 {
  position: absolute;
  right: -30px;
  top: -10px;
  animation: float 1s ease-in-out infinite 0.3s;
}

@keyframes popIn {
  0% { transform: translate(-50%, -50%) scale(0); opacity: 0; }
  50% { transform: translate(-50%, -50%) scale(1.3); }
  100% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* 结果页面装饰 */
.result-panel {
  position: relative;
  overflow: hidden;
}

.decorations {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.decoration {
  position: absolute;
  animation: twinkle 2s ease-in-out infinite;
}

.dec-1 { top: 5%; left: 5%; animation-delay: 0s; }
.dec-2 { top: 10%; right: 8%; animation-delay: 0.2s; }
.dec-3 { top: 20%; left: 3%; animation-delay: 0.4s; }
.dec-4 { top: 30%; right: 5%; animation-delay: 0.6s; }
.dec-5 { top: 40%; left: 8%; animation-delay: 0.8s; }
.dec-6 { top: 50%; right: 3%; animation-delay: 1s; }
.dec-7 { top: 60%; left: 5%; animation-delay: 1.2s; }
.dec-8 { top: 70%; right: 8%; animation-delay: 1.4s; }
.dec-9 { top: 80%; left: 3%; animation-delay: 1.6s; }
.dec-10 { top: 90%; right: 5%; animation-delay: 1.8s; }
.dec-11 { top: 15%; left: 10%; animation-delay: 0.3s; }
.dec-12 { top: 85%; right: 10%; animation-delay: 0.7s; }

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

.mascot {
  text-align: center;
  margin-bottom: 16px;
}

.mascot-emoji {
  font-size: 60px;
  display: inline-block;
  animation: bounce 1s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
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
}

.btn-restart:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(52, 152, 219, 0.5);
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
  
  .game-panel {
    width: 100%;
  }
  
  .game-header {
    margin-bottom: 16px;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .header-left {
    gap: 8px;
  }
  
  .difficulty-badge {
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
    font-size: 36px;
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
  
  /* 历史记录面板 */
  .history-panel {
    width: 100%;
    border-radius: 12px;
    padding: 12px;
  }
  
  .history-title {
    font-size: 14px;
    padding-bottom: 10px;
    margin-bottom: 10px;
  }
  
  .history-list {
    max-height: 200px;
  }
  
  .history-item {
    padding: 8px 10px;
    margin-bottom: 6px;
  }
  
  .history-index {
    width: 22px;
    height: 22px;
    font-size: 11px;
  }
  
  .history-expr {
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
  
  .accuracy-circle {
    width: 100px;
    height: 100px;
    font-size: 28px;
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
  
  .result-message {
    font-size: 16px;
    margin-bottom: 20px;
  }
}

/* 更小屏幕 */
@media (max-width: 480px) {
  .question-expression {
    font-size: 28px;
  }
  
  .option-btn {
    padding: 8px 12px;
    font-size: 12px;
  }
  
  .accuracy-circle {
    width: 90px;
    height: 90px;
    font-size: 24px;
  }
}
</style>
