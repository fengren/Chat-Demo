import { defineStore } from 'pinia'
import { ref } from 'vue'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
}

interface Session {
  id: string
  title: string
  created_at?: string
}

export const useSessionStore = defineStore('session', () => {
  const sessions = ref<Session[]>([])
  const currentSessionId = ref<string | null>(null)
  const messages = ref<Message[]>([])

  // 加载会话列表
  async function loadSessions() {
    try {
      const response = await fetch('/api/sessions')
      if (response.ok) {
        const data = await response.json()
        // 确保列表按创建时间倒序（最新的在前）
        sessions.value = data.sort((a: Session, b: Session) => {
          const timeA = a.created_at ? new Date(a.created_at).getTime() : 0
          const timeB = b.created_at ? new Date(b.created_at).getTime() : 0
          return timeB - timeA
        })
      }
    } catch (error) {
      console.error('Failed to load sessions:', error)
    }
  }
  
  // 更新会话（用于标题更新等）
  function updateSession(sessionId: string, updates: Partial<Session>) {
    const index = sessions.value.findIndex(s => s.id === sessionId)
    if (index !== -1) {
      sessions.value[index] = { ...sessions.value[index], ...updates }
    }
  }

  // 创建新会话
  async function createSession(title?: string): Promise<Session> {
    try {
      const response = await fetch('/api/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title })
      })
      if (response.ok) {
        const session = await response.json()
        sessions.value.unshift(session)
        return session
      }
    } catch (error) {
      console.error('Failed to create session:', error)
    }
    throw new Error('Failed to create session')
  }

  // 切换会话
  async function switchSession(sessionId: string) {
    currentSessionId.value = sessionId
    await loadMessages(sessionId)
  }

  // 加载消息历史
  async function loadMessages(sessionId: string) {
    try {
      const response = await fetch(`/api/sessions/${sessionId}/messages`)
      if (response.ok) {
        const data = await response.json()
        messages.value = data.map((m: any) => ({
          id: m.id,
          role: m.role,
          content: m.content,
          timestamp: m.created_at
        }))
      }
    } catch (error) {
      console.error('Failed to load messages:', error)
    }
  }

  // 更新会话标题
  async function updateSessionTitle(sessionId: string, title: string) {
    try {
      const response = await fetch(`/api/sessions/${sessionId}/title`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title })
      })
      if (response.ok) {
        const updatedSession = await response.json()
        const index = sessions.value.findIndex(s => s.id === sessionId)
        if (index !== -1) {
          sessions.value[index] = updatedSession
        }
      }
    } catch (error) {
      console.error('Failed to update session title:', error)
    }
  }

  // 添加消息到当前会话
  function addMessage(message: Message) {
    messages.value.push(message)
  }

  // 清空消息
  function clearMessages() {
    messages.value = []
  }

  // 删除会话
  async function deleteSession(sessionId: string) {
    try {
      const response = await fetch(`/api/sessions/${sessionId}`, {
        method: 'DELETE'
      })
      if (response.ok) {
        // 从列表中移除
        sessions.value = sessions.value.filter(s => s.id !== sessionId)
        // 如果删除的是当前会话，切换到新对话
        if (currentSessionId.value === sessionId) {
          currentSessionId.value = null
          clearMessages()
        }
        return true
      }
    } catch (error) {
      console.error('Failed to delete session:', error)
    }
    return false
  }

  return {
    sessions,
    currentSessionId,
    messages,
    loadSessions,
    createSession,
    switchSession,
    loadMessages,
    updateSessionTitle,
    updateSession,
    addMessage,
    clearMessages,
    deleteSession
  }
})

