import { createRouter, createWebHistory } from 'vue-router'
import ChatWindow from './components/ChatWindow.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'new-chat',
      component: ChatWindow,
      props: true
    },
    {
      path: '/:sessionId',
      name: 'chat',
      component: ChatWindow,
      props: true
    }
  ]
})

export default router

