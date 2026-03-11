<script lang="ts" setup>
import { ref } from 'vue'
import ToolSidebar from './components/ToolSidebar.vue'
import CalculationTool from './components/CalculationTool.vue'

const currentTool = ref('calculation')
const tools = [
  { id: 'calculation', name: '计算练习' }
]

const handleToolChange = (toolId: string) => {
  currentTool.value = toolId
}
</script>

<template>
  <div class="app-container">
    <ToolSidebar 
      :tools="tools" 
      :currentTool="currentTool" 
      @change="handleToolChange"
    />
    <main class="main-content">
      <CalculationTool v-if="currentTool === 'calculation'" />
    </main>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #f5f7fa;
}

.app-container {
  display: flex;
  height: 100vh;
  width: 100vw;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}
</style>
