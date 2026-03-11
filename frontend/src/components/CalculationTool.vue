<script lang="ts" setup>
import { ref, computed } from 'vue'
import { Play, RotateCcw, Volume2 } from 'lucide-vue-next'

interface Question {
  id: number
  expression: string
  answer: number
}

const difficulties = [
  { value: 1, label: '10以内加减' },
  { value: 2, label: '10以内连加连减混合' },
  { value: 3, label: '20以内无需借位进位' },
  { value: 4, label: '20以内需要借位进位' }
]

const selectedDifficulty = ref(1)
const questionCount = ref(10)
const questions = ref<Question[]>([])
const currentIndex = ref(0)
const userAnswer = ref('')
const correctCount = ref(0)
const isStarted = ref(false)
const isFinished = ref(false)
const isCorrect = ref<boolean | null>(null)

const currentQuestion = computed(() => questions.value[currentIndex.value])
const progress = computed(() => `${currentIndex.value + 1}/${questions.value.length}`)

const playSuccessSound = () => {
  try {
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
    const oscillator = audioContext.createOscillator()
    const gainNode = audioContext.createGain()
    
    oscillator.connect(gainNode)
    gainNode.connect(audioContext.destination)
    
    oscillator.frequency.setValueAtTime(800, audioContext.currentTime)
    oscillator.frequency.setValueAtTime(1000, audioContext.currentTime + 0.1)
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3)
    
    oscillator.start(audioContext.currentTime)
    oscillator.stop(audioContext.currentTime + 0.3)
  } catch (e) {
    console.log('Audio not supported')
  }
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
}

const generateMockQuestions = (difficulty: number, count: number): Question[] => {
  const result: Question[] = []
  for (let i = 0; i < count; i++) {
    let a = Math.floor(Math.random() * 10)
    let b = Math.floor(Math.random() * 10)
    let expr = `${a} + ${b}`
    let ans = a + b
    result.push({ id: i + 1, expression: expr, answer: ans })
  }
  return result
}

const submitAnswer = async () => {
  if (userAnswer.value === '' || userAnswer.value === null || userAnswer.value === undefined) return
  
  const answer = Number(userAnswer.value)
  const correct = answer === currentQuestion.value.answer
  
  if (correct) {
    correctCount.value++
    isCorrect.value = true
    playSuccessSound()
  } else {
    isCorrect.value = false
  }
  
  setTimeout(() => {
    isCorrect.value = null
    if (currentIndex.value < questions.value.length - 1) {
      currentIndex.value++
      userAnswer.value = ''
    } else {
      isFinished.value = true
    }
  }, 800)
}

const restartGame = () => {
  isStarted.value = false
  isFinished.value = false
  questions.value = []
  currentIndex.value = 0
  correctCount.value = 0
  userAnswer.value = ''
  isCorrect.value = null
}

const accuracy = computed(() => {
  if (questions.value.length === 0) return 0
  return Math.round((correctCount.value / questions.value.length) * 100)
})
</script>

<template>
  <div class="calculation-tool">
    <!-- 开始游戏前 -->
    <div v-if="!isStarted" class="setup-panel">
      <h2 class="panel-title">计算练习</h2>
      
      <div class="form-group">
        <label class="label">选择难度</label>
        <select v-model="selectedDifficulty" class="select">
          <option v-for="diff in difficulties" :key="diff.value" :value="diff.value">
            {{ diff.label }}
          </option>
        </select>
      </div>
      
      <div class="form-group">
        <label class="label">题目数量</label>
        <input 
          v-model.number="questionCount" 
          type="number" 
          class="input"
          min="1"
          max="50"
        />
      </div>
      
      <button class="btn btn-primary" @click="startGame">
        <Play :size="18" />
        开始练习
      </button>
    </div>

    <!-- 答题中 -->
    <div v-else-if="!isFinished" class="game-panel">
      <div class="game-header">
        <span class="difficulty-badge">{{ difficulties[selectedDifficulty - 1].label }}</span>
        <span class="progress">{{ progress }}</span>
      </div>
      
      <div class="question-card" :class="{ correct: isCorrect === true, wrong: isCorrect === false }">
        <div class="question-number">第 {{ currentIndex + 1 }} 题</div>
        <div class="question-expression">{{ currentQuestion?.expression }} = ?</div>
      </div>
      
      <div class="answer-section">
        <input
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

    <!-- 游戏结束 -->
    <div v-else class="result-panel">
      <h2 class="result-title">本局结束!</h2>
      
      <div class="result-card">
        <div class="accuracy-circle" :class="{ excellent: accuracy >= 90, good: accuracy >= 70 && accuracy < 90, normal: accuracy < 70 }">
          {{ accuracy }}%
        </div>
        <div class="result-stats">
          <div class="stat-item">
            <span class="stat-label">正确</span>
            <span class="stat-value correct-text">{{ correctCount }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">错误</span>
            <span class="stat-value wrong-text">{{ questions.length - correctCount }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">总计</span>
            <span class="stat-value">{{ questions.length }}</span>
          </div>
        </div>
      </div>
      
      <div class="result-message" v-if="accuracy >= 90">
        太棒了!继续保持!
      </div>
      <div class="result-message" v-else-if="accuracy >= 70">
        做得不错!继续加油!
      </div>
      <div class="result-message">
        再来一局吧!
      </div>
      
      <button class="btn btn-primary" @click="restartGame">
        <RotateCcw :size="18" />
        再来一局
      </button>
    </div>
  </div>
</template>

<style scoped>
.calculation-tool {
  max-width: 600px;
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
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
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

/* Game Panel */
.game-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.difficulty-badge {
  background: #e8f4fd;
  color: #3498db;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 14px;
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

/* Result Panel */
.result-panel {
  text-align: center;
}

.result-title {
  font-size: 32px;
  color: #2c3e50;
  margin-bottom: 32px;
}

.result-card {
  background: #fff;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
}

.accuracy-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  font-weight: 700;
  margin: 0 auto 24px;
  background: #f5f7fa;
  color: #909399;
}

.accuracy-circle.excellent {
  background: #f0f9eb;
  color: #67c23a;
}

.accuracy-circle.good {
  background: #fdf6ec;
  color: #e6a23c;
}

.accuracy-circle.normal {
  background: #fef0f0;
  color: #f56c6c;
}

.result-stats {
  display: flex;
  justify-content: center;
  gap: 32px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  color: #909399;
  font-size: 14px;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
}

.correct-text {
  color: #67c23a;
}

.wrong-text {
  color: #f56c6c;
}

.result-message {
  font-size: 18px;
  color: #67c23a;
  margin-bottom: 24px;
}
</style>
