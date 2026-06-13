---
name: convert-to-vue3
overview: 将 Wails + Go + Vue3 项目转换为纯 Vue3 前端项目，移除 Go 后端，题目生成逻辑移植到前端
todos:
  - id: clean-wails-files
    content: 删除所有 Go 和 Wails 相关文件（app.go, main.go, go.mod, go.sum, wails.json, build/, wailsjs/, dist/, HelloWorld.vue）
    status: completed
  - id: move-frontend-root
    content: 将 frontend 目录内容（src/, index.html, package.json, vite.config.ts 等）移动到项目根目录
    status: completed
    dependencies:
      - clean-wails-files
  - id: impl-question-gen
    content: 将 Go 后端 4 级题目生成逻辑完整移植为 TypeScript，替换简化的 generateMockQuestions
    status: completed
    dependencies:
      - move-frontend-root
  - id: remove-go-calls
    content: 移除 CalculationTool.vue 中 window.go 条件判断，直接调用前端生成函数
    status: completed
    dependencies:
      - impl-question-gen
  - id: update-config-docs
    content: 更新 package.json 项目名称和 README.md 文档
    status: completed
    dependencies:
      - move-frontend-root
---

## 产品概述

将现有的 Wails（Go + Vue3）桌面应用项目完全转换为独立的纯 Vue3 Web 项目。当前应用是一个儿童数学计算练习工具，所有功能均可直接在前端实现，无需 Go 后端。

## 核心功能（保持不变）

- 4种难度级别题目生成（10以内加减、10以内连加连减混合、20以内无需借位进位、20以内需要借位进位）
- 答题界面、提交答案、正确/错误反馈
- 语音激励和音效
- 动画效果（星星、竖大拇指、爱心）
- 历史记录面板和回溯修改
- 结算界面（分数、统计、再玩一次/完成按钮）
- 移动端适配
- 题目数量选择

## 变更内容

- 移除 Go 后端及 Wails 框架依赖
- 将 Go 后端的题目生成逻辑完整移植到前端 TypeScript
- 调整项目结构（frontend 目录内容提升到根目录）
- 清理 Wails 相关文件和示例代码
- 更新项目配置和文档

## 技术栈

- **前端框架**: Vue 3 + TypeScript + Vite
- **UI 组件**: 自定义组件（继续使用现有组件）
- **图标库**: lucide-vue-next
- **构建工具**: Vite

## 实现方案

### 总体策略

1. 清理所有 Go 和 Wails 相关文件
2. 将 `frontend/` 目录内容提升到项目根目录
3. 将 Go 后端的 4 级题目生成逻辑完整移植为 TypeScript 函数
4. 移除 `window.go` 条件分支，前端直接调用生成函数
5. 更新配置文件和文档

### 题目生成逻辑移植

Go 后端的题目生成逻辑较为复杂，需要完整移植到前端：

- **Level 1**: 加法（加数1-9，和<10）；减法（被减数1-9，减数1到a-1，差>=1）
- **Level 2**: 三个数1-9，中间结果和最终结果均>=1且<10，随机加减
- **Level 3**: 至少一个数>=11，个位相加<10（不进位）或被减数个位>=减数个位（不借位），和<=20
- **Level 4**: 至少一个数>=11，个位相加>=10（必须进位）或被减数个位<减数个位（必须借位），和<=20
- **去重**: 使用 Set 确保同局内不重复题目

### 目录结构调整

```
当前:                    调整后:
study/                   study/
├── app.go               ├── src/
├── main.go              │   ├── components/
├── go.mod               │   │   ├── App.vue
├── go.sum               │   │   ├── CalculationTool.vue
├── wails.json           │   │   └── ToolSidebar.vue
├── build/               │   ├── main.ts
├── frontend/            │   └── style.css
│   ├── src/             ├── index.html
│   ├── wailsjs/         ├── package.json
│   ├── dist/            ├── vite.config.ts
│   ├── index.html       ├── tsconfig.json
│   └── package.json     └── README.md
```

## 关键执行要点

- **去重逻辑**: 移植 Go 的 `map[string]bool` 去重机制到 TypeScript 的 `Set<string>`
- **随机种子**: 前端使用 `Math.random()`，无需显式设置种子
- **字段命名**: JSON 字段名统一为小写（expression/answer）
- **兼容性**: 移除 `window.go` 判断后，直接调用前端函数，无需异步 `await`
- **清理彻底**: 一并移除 HelloWorld.vue 示例组件和 Wails README

## Agent Extensions

### SubAgent

- **code-explorer**
- Purpose: 辅助确认需要删除、移动、修改的文件完整清单，确保不遗漏任何 Wails 相关引用
- Expected outcome: 完整的文件变更清单