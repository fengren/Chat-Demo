<template>
  <div class="chat-window">
    <!-- Sidebar -->
    <div class="sidebar" :class="{ collapsed: isSidebarCollapsed }">
      <button class="collapse-btn" @click="toggleSidebar" :title="isSidebarCollapsed ? '展开侧边栏' : '折叠侧边栏'">
        <svg v-if="!isSidebarCollapsed" width="14" height="14" viewBox="0 0 16 16" fill="none">
          <path d="M10 12L6 8L10 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <svg v-else width="14" height="14" viewBox="0 0 16 16" fill="none">
          <path d="M6 12L10 8L6 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
      
      <div class="sidebar-content">
        <button class="new-chat-btn" @click="startNewChat">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M0.5 8C0.5 3.85786 3.85786 0.5 8 0.5C12.1421 0.5 15.5 3.85786 15.5 8C15.5 12.1421 12.1421 15.5 8 15.5C3.85786 15.5 0.5 12.1421 0.5 8Z" stroke="currentColor" stroke-linecap="round"/>
            <path d="M8 4.5V11.5" stroke="currentColor" stroke-linecap="round"/>
            <path d="M4.5 8H11.5" stroke="currentColor" stroke-linecap="round"/>
          </svg>
          新对话
        </button>
        
        <div class="chat-history">
          <template v-for="session in sessionStore.sessions" :key="session.id">
            <div v-if="!editingSessions[session.id]"
                 class="chat-item" 
                 :class="{ active: session.id === sessionStore.currentSessionId }"
                 @click="switchToSession(session.id)"
                 @dblclick="enableTitleEdit(session)"
                 @mouseenter="hoveredSessionId = session.id"
                 @mouseleave="hoveredSessionId = null">
              <span class="chat-item-title">{{ session.title }}</span>
              <button v-if="hoveredSessionId === session.id"
                      @click.stop="handleDeleteSession(session.id)"
                      class="delete-btn"
                      title="删除会话">
                <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
                  <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                  <path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                </svg>
              </button>
            </div>
            <input v-else
                   v-model="editingSession.title" 
                   @blur="saveTitleEdit"
                   @keydown.enter="saveTitleEdit"
                   class="editing-title-input"
                   ref="titleInputRef">
          </template>
        </div>
        
        <div class="sidebar-footer">
          <button class="settings-btn">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="8" r="1.5" stroke="currentColor"/>
              <circle cx="8" cy="3" r="1.5" stroke="currentColor"/>
              <circle cx="8" cy="13" r="1.5" stroke="currentColor"/>
            </svg>
            设置
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <div class="chat-container">
        <div class="messages">
          <div v-if="sessionStore.messages.length === 0" class="empty-state">
            <div class="empty-state-content">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              </svg>
              <p>开始新的对话</p>
            </div>
          </div>
          <div v-for="msg in sessionStore.messages" :key="msg.id" class="message" :class="msg.role">
            <div class="message-avatar">
              <template v-if="msg.role === 'user'">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
                </svg>
              </template>
              <template v-else>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z"/>
                </svg>
              </template>
            </div>
            <div class="message-content">{{ msg.content }}</div>
          </div>
          <div v-if="isLoading && sessionStore.messages.length > 0" class="loading-indicator">
            <div class="typing-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>

        <div class="input-area">
          <div class="input-wrapper">
            <textarea 
              ref="textareaRef"
              v-model="input" 
              @keydown.enter.prevent="handleSend"
              @input="handleInputResize"
              placeholder="输入消息..." 
              rows="1"
            ></textarea>
            <button @click="handleSend" :disabled="isLoading || !input.trim()" class="send-btn">
              <svg v-if="!isLoading" width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M.5 1.163A1 1 0 0 1 1.97.28l12.868 6.837a1 1 0 0 1 0 1.706L1.969 15.72A1 1 0 0 1 .5 14.836V10.33a1 1 0 0 1 .816-.983L8.5 8 1.316 6.653A1 1 0 0 1 .5 5.67V1.163Z"/>
              </svg>
              <svg v-else width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="20" stroke-linecap="round">
                  <animate attributeName="stroke-dashoffset" values="0;40" dur="1s" repeatCount="indefinite"/>
                </circle>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSessionStore } from '../stores/session'

const route = useRoute()
const router = useRouter()
const sessionStore = useSessionStore()
const input = ref('')
const isLoading = ref(false)
const editingSessions = ref<Record<string, boolean>>({})
const editingSession = ref<any>(null)
const titleInputRef = ref<HTMLInputElement | null>(null)
const hoveredSessionId = ref<string | null>(null)
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const isSidebarCollapsed = ref(false)
let es: EventSource | null = null

// 从路由参数读取 sessionId
const sessionIdFromRoute = computed(() => route.params.sessionId as string | undefined)

onMounted(async () => {
  await sessionStore.loadSessions()
  
  // 如果有路由参数，加载对应的会话
  if (sessionIdFromRoute.value) {
    await sessionStore.switchSession(sessionIdFromRoute.value)
  }
})

// 监听路由变化
watch(sessionIdFromRoute, async (newSessionId, oldSessionId) => {
  if (newSessionId && newSessionId !== oldSessionId) {
    if (newSessionId !== sessionStore.currentSessionId) {
      await sessionStore.switchSession(newSessionId)
    }
  } else if (!newSessionId && oldSessionId) {
    // 从有会话的路径跳转到新对话
    sessionStore.currentSessionId = null
    sessionStore.clearMessages()
  }
})


function handleSend() {
  if (!input.value.trim() || isLoading.value) return
  
  const userMessage = input.value.trim()
  input.value = ''
  // 重置输入框高度
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
  }
  
  // 添加用户消息到 UI
  const userMsg = {
    id: Date.now().toString(),
    role: 'user' as const,
    content: userMessage,
    timestamp: Date.now().toString()
  }
  
  sessionStore.addMessage(userMsg)
  
  // 添加 assistant 占位
  const assistantMsg = {
    id: (Date.now() + 1).toString(),
    role: 'assistant' as const,
    content: '',
    timestamp: (Date.now() + 1).toString()
  }
  
  sessionStore.addMessage(assistantMsg)
  
  // 开始流式接收
  isLoading.value = true
  startStreaming(userMessage)
}

function startStreaming(query: string) {
  es?.close()
  // 优先使用路由中的 sessionId，如果没有则使用 store 中的
  let sessionId = sessionIdFromRoute.value || sessionStore.currentSessionId
  const params = new URLSearchParams({ q: query })
  if (sessionId) {
    params.append('session_id', sessionId)
  }
  
  es = new EventSource(`/api/chat/stream?${params.toString()}`)
  
  const assistantMsg = sessionStore.messages[sessionStore.messages.length - 1]
  
  es.onmessage = (e) => {
    try {
      const obj = JSON.parse(e.data)
      if (obj.session_id) {
        const newSessionId = obj.session_id
        sessionStore.currentSessionId = newSessionId
        sessionId = newSessionId
        // 如果当前路由没有 sessionId 或 sessionId 不匹配，跳转到新的会话路径
        if (!sessionIdFromRoute.value || sessionIdFromRoute.value !== newSessionId) {
          router.replace(`/${newSessionId}`)
        }
      }
      if (obj.delta) {
        assistantMsg.content += obj.delta
      }
      if (obj.title_update) {
        // 接收到标题更新，更新当前会话的标题并刷新列表
        if (sessionStore.currentSessionId) {
          sessionStore.updateSession(sessionStore.currentSessionId, { title: obj.title_update })
        }
        // 同时刷新整个列表以确保同步
        sessionStore.loadSessions()
      }
      if (obj.error) {
        assistantMsg.content = `错误: ${obj.error}`
        isLoading.value = false
      }
    } catch (err) {
      console.error('Parse SSE message error:', err)
    }
  }
  
  es.addEventListener('done', () => {
    isLoading.value = false
    es?.close()
    es = null
  })
  
  es.onerror = (error) => {
    console.error('SSE error:', error)
    assistantMsg.content = assistantMsg.content || '连接错误，请检查后端服务是否正常运行'
    isLoading.value = false
    es?.close()
    es = null
  }
}

async function startNewChat() {
  sessionStore.currentSessionId = null
  sessionStore.clearMessages()
  input.value = ''
  es?.close()
  isLoading.value = false
  // 跳转到根路径
  router.push('/')
}

async function switchToSession(sessionId: string) {
  // 跳转到对应会话路径
  router.push(`/${sessionId}`)
}

async function enableTitleEdit(session: any) {
  editingSession.value = { ...session }
  editingSessions.value[session.id] = true
  await nextTick()
  if (titleInputRef.value) {
    titleInputRef.value.focus()
    titleInputRef.value.select()
  }
}

async function saveTitleEdit() {
  if (editingSession.value) {
    await sessionStore.updateSessionTitle(editingSession.value.id, editingSession.value.title)
    editingSessions.value[editingSession.value.id] = false
    editingSession.value = null
  }
}

async function handleDeleteSession(sessionId: string) {
  if (confirm('确定要删除这个会话吗？')) {
    const deleted = await sessionStore.deleteSession(sessionId)
    if (deleted) {
      // 如果删除的是当前会话，跳转到新对话页面
      if (sessionStore.currentSessionId === sessionId) {
        router.push('/')
      }
    }
  }
}

function handleInputResize() {
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
    textareaRef.value.style.height = textareaRef.value.scrollHeight + 'px'
  }
}

function toggleSidebar() {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

onUnmounted(() => {
  es?.close()
})
</script>

<style scoped>
.chat-window {
  display: flex;
  height: 100vh;
  background: #ffffff;
  color: #2d2d2d;
  font-family: Söhne, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Ubuntu, Cantarell, "Noto Sans", sans-serif, "Helvetica Neue", Arial, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
}

/* Sidebar */
.sidebar {
  width: 260px;
  background: #f7f7f8;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #e5e5e6;
  position: relative;
  transition: width 0.3s ease;
  overflow: visible;
}

.sidebar.collapsed {
  width: 0;
  border-right: none;
}

.sidebar-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  opacity: 1;
  transition: opacity 0.2s ease;
}

.sidebar.collapsed .sidebar-content {
  opacity: 0;
  pointer-events: none;
}

.new-chat-btn {
  margin: 8px;
  padding: 12px 16px;
  background: transparent;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  color: #2d2d2d;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: opacity 0.2s ease;
  white-space: nowrap;
  opacity: 1;
}


.new-chat-btn:hover {
  background: #ececec;
  border-color: #c5c5d2;
}

.new-chat-btn svg {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  overflow-x: hidden;
}


.chat-item {
  padding: 10px 12px;
  margin-bottom: 2px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #565869;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  transition: opacity 0.2s ease, background-color 0.15s ease;
  position: relative;
  min-height: 36px;
  white-space: nowrap;
  opacity: 1;
}


.chat-item-title {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.5;
}

.delete-btn {
  flex-shrink: 0;
  background: transparent;
  border: none;
  padding: 6px;
  cursor: pointer;
  color: #8e8ea0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.15s ease;
  opacity: 0;
  min-width: 24px;
  min-height: 24px;
}

.chat-item:hover {
  background: #ececec;
}

.chat-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background: #d1d5db;
  color: #dc2626;
}

.chat-item.active {
  background: #ececec;
}

.editing-title-input {
  width: 100%;
  padding: 10px 12px;
  margin-bottom: 2px;
  background: #ffffff;
  border: 1px solid #10a37f;
  border-radius: 8px;
  color: #2d2d2d;
  font-size: 14px;
  outline: none;
  font-family: inherit;
}

.sidebar-footer {
  padding: 8px;
  border-top: 1px solid #e5e5e6;
  opacity: 1;
  transition: opacity 0.2s ease;
}


.settings-btn {
  width: 100%;
  padding: 10px 12px;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: #565869;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.15s ease;
  white-space: nowrap;
}

.settings-btn:hover {
  background: #ececec;
}

.settings-btn svg {
  width: 16px;
  height: 16px;
}

/* 折叠按钮 */
.collapse-btn {
  position: absolute;
  top: 50%;
  right: -16px;
  transform: translateY(-50%);
  width: 32px;
  height: 32px;
  background: #ffffff;
  border: 1px solid #e5e5e6;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
  color: #565869;
  flex-shrink: 0;
}

.collapse-btn:hover {
  background: #f7f7f8;
  border-color: #d1d5db;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
}

.collapse-btn svg {
  width: 14px;
  height: 14px;
}

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  position: relative;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
}

.messages {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

.message {
  display: flex;
  gap: 24px;
  padding: 20px 0;
  max-width: 768px;
  margin: 0 auto;
  width: 100%;
  padding-left: 24px;
  padding-right: 24px;
}

.message.user {
  background: #ffffff;
  justify-content: flex-end;
}

.message.assistant {
  background: transparent;
  justify-content: flex-start;
}

.message-avatar {
  min-width: 32px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 2px;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: #10a37f;
  color: white;
  order: 2;
}

.message.assistant .message-avatar {
  background: #ab68ff;
  color: white;
  order: 1;
}

.message-avatar svg {
  width: 18px;
  height: 18px;
  display: block;
}

.message-content {
  flex: 1;
  line-height: 1.75;
  white-space: pre-wrap;
  word-wrap: break-word;
  color: #2d2d2d;
  font-size: 16px;
  padding-top: 2px;
  max-width: 85%;
}

.message.user .message-content {
  order: 1;
  text-align: right;
  background: #ececec;
  color: #2d2d2d;
  padding: 10px 14px;
  border-radius: 12px;
  border-top-right-radius: 4px;
  flex: 0 1 auto;
  width: fit-content;
  max-width: 85%;
  margin-left: auto;
}

.message.assistant .message-content {
  order: 2;
  text-align: left;
  background: transparent;
}

/* Input Area */
.input-area {
  padding: 20px 0;
  border-top: 1px solid #e5e5e6;
  background: #ffffff;
  position: sticky;
  bottom: 0;
}

.input-wrapper {
  max-width: 768px;
  margin: 0 auto;
  display: flex;
  gap: 12px;
  align-items: flex-end;
  background: #ffffff;
  border-radius: 24px;
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 0 0 0 rgba(16, 163, 127, 0);
}

.input-wrapper:focus-within {
  border-color: #10a37f;
  box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.1);
}

textarea {
  flex: 1;
  background: transparent;
  border: none;
  color: #2d2d2d;
  font-size: 16px;
  resize: none;
  max-height: 200px;
  min-height: 24px;
  outline: none;
  font-family: inherit;
  line-height: 1.5;
  overflow-y: auto;
  padding: 0;
}

textarea::placeholder {
  color: #8e8ea0;
}

.send-btn {
  background: transparent;
  border: none;
  border-radius: 6px;
  padding: 8px;
  cursor: pointer;
  color: #8e8ea0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
  flex-shrink: 0;
  width: 32px;
  height: 32px;
}

.send-btn:hover:not(:disabled) {
  background: #ececec;
  color: #10a37f;
}

.send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.send-btn svg {
  width: 16px;
  height: 16px;
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #c5c5d2;
}

/* 空状态 */
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 40px 20px;
}

.empty-state-content {
  text-align: center;
  color: #8e8ea0;
}

.empty-state-content svg {
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state-content p {
  font-size: 16px;
  margin: 0;
}

/* 加载指示器 */
.loading-indicator {
  display: flex;
  gap: 24px;
  padding: 20px 0;
  max-width: 768px;
  margin: 0 auto;
  padding-left: 24px;
  padding-right: 24px;
}

.typing-dots {
  display: flex;
  gap: 4px;
  padding-left: 56px;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #8e8ea0;
  animation: typing 1.4s infinite;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.7;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}
</style>
