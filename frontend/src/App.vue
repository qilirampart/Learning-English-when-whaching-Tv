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
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

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
}

.sidebar {
  background: #304156;
  color: white;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1f2d3d;
  color: white;
}

.logo h2 {
  font-size: 18px;
  font-weight: bold;
}

.sidebar-menu {
  border: none;
  background: #304156;
}

.sidebar-menu .el-menu-item {
  color: #bfcbd9;
}

.sidebar-menu .el-menu-item:hover,
.sidebar-menu .el-menu-item.is-active {
  background: #263445 !important;
  color: #409eff !important;
}

.main-content {
  background: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

.user-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px;
  background: #263445;
  border-top: 1px solid #1f2d3d;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #bfcbd9;
  padding: 8px;
  border-radius: 4px;
  transition: all 0.3s;
}

.user-profile:hover {
  background: #1f2d3d;
  color: #409eff;
}

.user-icon {
  font-size: 20px;
}

.username {
  font-size: 14px;
  font-weight: 500;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>

