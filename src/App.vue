<script lang="ts" setup>
import { ref } from 'vue'
import ToolSidebar from './components/ToolSidebar.vue'
import CalculationTool from './components/CalculationTool.vue'

const currentTool = ref('calculation')
const tools = [
  { id: 'calculation', name: '计算练习' }
]
const sidebarOpen = ref(false)

const handleToolChange = (toolId: string) => {
  currentTool.value = toolId
  sidebarOpen.value = false
}

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}
</script>

<template>
  <div class="app-container">
    <!-- 移动端菜单按钮 -->
    <button class="mobile-menu-btn" @click="toggleSidebar">
      <span class="menu-icon"></span>
    </button>
    
    <ToolSidebar 
      :tools="tools" 
      :currentTool="currentTool" 
      :isOpen="sidebarOpen"
      @change="handleToolChange"
    />
    
    <!-- 移动端遮罩层 -->
    <div 
      v-if="sidebarOpen" 
      class="sidebar-overlay" 
      @click="sidebarOpen = false"
    ></div>
    
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
  position: relative;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  min-width: 0;
}

/* 移动端菜单按钮 */
.mobile-menu-btn {
  display: none;
  position: fixed;
  top: 12px;
  left: 12px;
  z-index: 1001;
  width: 44px;
  height: 44px;
  background: #2c3e50;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  padding: 10px;
}

.menu-icon {
  display: block;
  width: 24px;
  height: 2px;
  background: #fff;
  position: relative;
}

.menu-icon::before,
.menu-icon::after {
  content: '';
  position: absolute;
  width: 24px;
  height: 2px;
  background: #fff;
  left: 0;
}

.menu-icon::before {
  top: -7px;
}

.menu-icon::after {
  top: 7px;
}

/* 移动端遮罩层 */
.sidebar-overlay {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

/* 平板 */
@media (max-width: 1024px) {
  .main-content {
    padding: 20px;
  }
}

/* 手机 */
@media (max-width: 768px) {
  .mobile-menu-btn {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .sidebar-overlay {
    display: block;
  }
  
  .main-content {
    padding: 16px;
    padding-top: 68px;
  }
}
</style>
