<template>
  <div id="app">
    <!-- 登录/注册页面使用单独布局 -->
    <template v-if="isAuthPage">
      <router-view />
    </template>

    <!-- 应用主布局 -->
    <el-container v-else class="app-container">
      <!-- 侧边栏 -->
      <el-aside width="200px" class="sidebar">
        <div class="logo">
          <h2>📺 单词助手</h2>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          router
        >
          <el-menu-item index="/query">
            <el-icon><Search /></el-icon>
            <span>快速查询</span>
          </el-menu-item>
          <el-menu-item index="/words">
            <el-icon><Collection /></el-icon>
            <span>单词库</span>
          </el-menu-item>
          <el-menu-item index="/learning">
            <el-icon><Edit /></el-icon>
            <span>学习计划</span>
          </el-menu-item>
          <el-menu-item index="/statistics">
            <el-icon><DataAnalysis /></el-icon>
            <span>学习统计</span>
          </el-menu-item>
          <el-menu-item index="/ai-assistant">
            <el-icon><ChatDotRound /></el-icon>
            <span>AI 助手</span>
          </el-menu-item>
        </el-menu>

        <!-- 用户信息 -->
        <div class="user-info" v-if="authStore.user">
          <el-dropdown @command="handleUserCommand">
            <div class="user-profile">
              <el-icon class="user-icon"><User /></el-icon>
              <span class="username">{{ authStore.user.username }}</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item disabled>
                  {{ authStore.user.email }}
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-aside>

      <!-- 主内容区 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>

    <!-- 主题切换按钮 -->
    <div v-if="!isAuthPage" class="theme-toggle">
      <el-dropdown trigger="click" @command="handleThemeCommand">
        <el-button circle size="large" type="primary">
          <el-icon v-if="themeMode === 'light'"><Sunny /></el-icon>
          <el-icon v-else-if="themeMode === 'dark'"><Moon /></el-icon>
          <el-icon v-else><Monitor /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item disabled>主题模式</el-dropdown-item>
            <el-dropdown-item :command="'light'" divided>
              <el-icon><Sunny /></el-icon>
              <span style="margin-left: 8px">浅色模式{{ themeMode === 'light' ? ' ✓' : '' }}</span>
            </el-dropdown-item>
            <el-dropdown-item :command="'dark'">
              <el-icon><Moon /></el-icon>
              <span style="margin-left: 8px">深色模式{{ themeMode === 'dark' ? ' ✓' : '' }}</span>
            </el-dropdown-item>
            <el-dropdown-item :command="'auto'">
              <el-icon><Monitor /></el-icon>
              <span style="margin-left: 8px">跟随系统{{ themeMode === 'auto' ? ' ✓' : '' }}</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useDarkMode } from '@/utils/useDarkMode'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ChatDotRound } from '@element-plus/icons-vue'
import '@/styles/modern.css'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 深色模式
const { themeMode, setThemeMode, getThemeModeText } = useDarkMode()

const activeMenu = computed(() => route.path)
const isAuthPage = computed(() => ['/login', '/register'].includes(route.path))

// 初始化时加载用户信息
onMounted(async () => {
  if (authStore.token && !authStore.user) {
    await authStore.initialize()
  }
})

// 处理用户菜单命令
const handleUserCommand = async (command) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })

      authStore.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
    } catch {
      // 用户取消
    }
  }
}

// 处理主题切换命令
const handleThemeCommand = (mode) => {
  setThemeMode(mode)
  const modeText = getThemeModeText(mode)
  ElMessage.success(`已切换到${modeText}`)
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.app-container {
  height: 100vh;
  position: relative;
  overflow: hidden;
}

.sidebar {
  background: rgba(48, 65, 86, 0.95);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 100;
}

.logo {
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  position: relative;
  overflow: hidden;
}

.logo::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  animation: float 6s ease-in-out infinite;
}

.logo h2 {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 1px;
  position: relative;
  z-index: 1;
}

.sidebar-menu {
  border: none;
  background: transparent;
  padding: 12px 8px;
}

.sidebar-menu .el-menu-item {
  color: #bfcbd9;
  border-radius: 12px;
  margin: 6px 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 500;
}

.sidebar-menu .el-menu-item:hover {
  background: rgba(255, 255, 255, 0.1) !important;
  color: #ffffff !important;
  transform: translateX(4px);
}

.sidebar-menu .el-menu-item.is-active {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.8) 0%, rgba(118, 75, 162, 0.8) 100%) !important;
  color: #ffffff !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transform: translateX(4px);
}

.main-content {
  background: transparent;
  padding: 24px;
  overflow-y: auto;
  position: relative;
}

.main-content::before {
  content: '';
  position: fixed;
  top: 0;
  left: 200px;
  right: 0;
  bottom: 0;
  background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
  background-size: 400% 400%;
  animation: gradient-animation 15s ease infinite;
  z-index: -1;
  opacity: 0.15;
}

.user-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px;
  background: rgba(38, 52, 69, 0.95);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  color: #bfcbd9;
  padding: 10px 12px;
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.user-profile:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.user-icon {
  font-size: 22px;
}

.username {
  font-size: 14px;
  font-weight: 600;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.theme-toggle {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 1000;
}

.theme-toggle .el-button {
  width: 56px;
  height: 56px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.theme-toggle .el-button:hover {
  transform: translateY(-4px) rotate(15deg);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.25);
}
</style>

