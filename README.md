# 工具集合 (Study App)

一款为孩子成长各阶段提供帮助的工具集合应用，基于 Wails + Vue 3 + TypeScript 开发。

## 技术栈

- **前端框架**: Vue 3 + TypeScript
- **桌面框架**: Wails (Go + WebView)
- **构建工具**: Vite
- **UI 组件**: 自定义组件 + Lucide 图标

## 项目结构

```
study/
├── main.go                    # Go 应用入口
├── app.go                     # Go 后端逻辑（题目生成）
├── wails.json                 # Wails 配置文件
├── go.mod / go.sum           # Go 依赖
├── frontend/
│   ├── src/
│   │   ├── main.ts           # Vue 入口
│   │   ├── App.vue           # 根组件（布局）
│   │   ├── style.css         # 全局样式
│   │   └── components/
│   │       ├── ToolSidebar.vue       # 左侧工具导航栏
│   │       └── CalculationTool.vue  # 计算练习工具
│   ├── dist/                 # 构建输出
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
└── build/                    # 构建产物
```

## 功能概览

### 1. 计算练习

**难度级别**:
- 10以内加减：1-9 的简单加减法
- 10以内连加连减：3个数混合运算（如 3+4-2）
- 20以内无需借位进位：不需要进位或借位的20以内运算
- 20以内需要借位进位：需要进位或借位的20以内运算

**功能特性**:
- 题目按局生成，每局数量可选（5/10/15/20/30/50）
- 实时统计正确率
- 答题历史记录（右侧面板）
- 点击历史可回溯到指定题目
- 正确/错误音效反馈
- 自动聚焦输入框

## 实现思路

### 前端架构

采用 **动态组件** 方案实现工具切换和状态保持：

1. **布局结构** (`App.vue`)
   - 左侧：工具导航栏（ToolSidebar）
   - 右侧：主内容区（动态组件）
   - 使用 `v-if` 控制显示，不使用 Vue Router

2. **状态管理**
   - 每个工具组件独立管理自己的状态
   - 切换工具时组件销毁，状态丢失（符合需求）
   - 同一工具内切换保持状态

3. **响应式设计**
   - 桌面端：左侧固定导航
   - 移动端：汉堡菜单 + 侧滑抽屉

### 后端架构

Go 后端负责题目生成 (`app.go`)：

```
GenerateQuestions(difficulty, count) → []Question
  ├── generateLevel1()  // 10以内加减
  ├── generateLevel2()  // 10以内连加连减
  ├── generateLevel3()  // 20以内无需借位进位
  └── generateLevel4()  // 20以内需要借位进位
```

**题目生成逻辑**:

- Level 1: 随机生成 0-9 的两个数，确保结果非负
- Level 2: 三个数随机加减，确保结果在 0-10 之间
- Level 3: 20以内，个位相加 <= 9（不进位）或个位够减（不借位）
- Level 4: 20以内，个位相加 >= 10（进位）或个位不够减（借位）

### 音效实现

使用 Web Audio API 生成音效（无需外部音频文件）：

- **正确音效**: 上升音阶 (C5 → E5 → G5)
- **错误音效**: 下降音阶 (G4 → F4 → Eb4)

## 开发命令

```bash
# 开发模式
wails dev

# 生产构建
wails build

# 前端单独开发
cd frontend
npm run dev
npm run build
```

## 添加新工具

1. 在 `App.vue` 的 `tools` 数组中添加工具配置
2. 在 `components/` 目录创建对应的 Vue 组件
3. 在 `App.vue` 中导入并根据 `currentTool` 动态渲染

示例：
```vue
<!-- App.vue -->
<script setup>
const tools = [
  { id: 'calculation', name: '计算练习' },
  { id: 'newTool', name: '新工具' }  // 添加新工具
]
</script>

<template>
  <main class="main-content">
    <CalculationTool v-if="currentTool === 'calculation'" />
    <NewTool v-else-if="currentTool === 'newTool'" />
  </main>
</template>
```

## 注意事项

1. **白屏问题**: 生产构建需设置 `vite.config.ts` 中 `base: './'`
2. **macOS 打包**: 使用 `wails build` 生成的 macOS 应用包含私有 API，仅限测试使用
3. **音频兼容**: 音效依赖 Web Audio API，部分移动端浏览器可能不支持
