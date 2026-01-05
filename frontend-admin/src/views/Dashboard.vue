<template>
  <div class="common-layout">
    <el-container>
      <el-header class="header">
        <div class="logo">{{ t('common.systemName') }}</div>
        <div class="right-actions" style="display:flex; align-items:center;">
             <el-dropdown @command="handleLangChange" style="margin-right: 20px; cursor: pointer; color: white;">
                <span class="el-dropdown-link">
                   {{ currentLang === 'zh' ? '中文' : 'English' }}
                   <el-icon class="el-icon--right"><arrow-down /></el-icon>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="zh">中文</el-dropdown-item>
                    <el-dropdown-item command="en">English</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
             </el-dropdown>

            <div class="user-info" v-if="authStore.user">
              {{ t('common.welcome') }}, {{ authStore.user.full_name }} ({{ authStore.user.role }})
              <el-button @click="handleLogout" type="danger" size="small" class="ml-4">{{ t('common.logout') }}</el-button>
            </div>
        </div>
      </el-header>
      <el-container>
        <el-aside width="200px" class="aside">
          <el-menu :default-active="activeMenu" class="el-menu-vertical-demo menu-flex" router>
            <el-menu-item index="/schedule-calendar">
              <el-icon><Calendar /></el-icon>
              <span>{{ t('menu.calendar') }}</span>
            </el-menu-item>
            <el-menu-item index="/schedule">
              <el-icon><Calendar /></el-icon>
              <span>{{ t('menu.schedule') }}</span>
            </el-menu-item>
            <el-menu-item index="/doctors" v-if="authStore.isAdmin">
              <el-icon><User /></el-icon>
              <span>{{ t('menu.doctors') }}</span>
            </el-menu-item>
            <el-menu-item index="/departments" v-if="authStore.isAdmin">
              <el-icon><OfficeBuilding /></el-icon>
              <span>{{ t('menu.departments') }}</span>
            </el-menu-item>
            <el-menu-item index="/rooms" v-if="authStore.isAdmin">
              <el-icon><House /></el-icon>
              <span>{{ t('menu.rooms') }}</span>
            </el-menu-item>
            <el-menu-item index="/shift-types" v-if="authStore.isAdmin">
              <el-icon><Clock /></el-icon>
              <span>{{ t('menu.shifts') }}</span>
            </el-menu-item>
            <el-menu-item index="/trade-approval" v-if="authStore.isAdmin">
              <el-icon><Document /></el-icon>
              <span>{{ t('menu.trades') }}</span>
            </el-menu-item>
            <el-menu-item index="/preferences" v-if="authStore.isManager">
              <el-icon><ChatDotSquare /></el-icon>
              <span>{{ t('menu.preferences') }}</span>
            </el-menu-item>
            <el-menu-item index="/statistics" v-if="authStore.isManager">
              <el-icon><DataAnalysis /></el-icon>
              <span>{{ t('menu.stats') }}</span>
            </el-menu-item>
            <el-menu-item index="/feedback" v-if="authStore.isAdmin">
              <el-icon><Message /></el-icon>
              <span>{{ t('menu.feedback') }}</span>
            </el-menu-item>
            <el-menu-item index="/audit-logs" v-if="authStore.isAdmin">
              <el-icon><Notebook /></el-icon>
              <span>{{ t('menu.audit') }}</span>
            </el-menu-item>
            <el-menu-item index="/settings" v-if="authStore.isAdmin">
              <el-icon><Setting /></el-icon>
              <span>{{ t('menu.settings') }}</span>
            </el-menu-item>
          </el-menu>
          <div class="aside-footer">
            <el-button type="danger" plain @click="handleLogout" style="width: 100%">
               <el-icon style="margin-right: 5px"><SwitchButton /></el-icon> {{ t('common.logout') }}
            </el-button>
          </div>
        </el-aside>
        <el-main>
          <router-view></router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useI18n } from 'vue-i18n';
import { Calendar, User, OfficeBuilding, House, Clock, Document, Setting, ChatDotSquare, DataAnalysis, SwitchButton, Notebook, Message, ArrowDown } from '@element-plus/icons-vue';

const authStore = useAuthStore();
const route = useRoute();
const { t, locale } = useI18n();

const currentLang = computed(() => locale.value);

const activeMenu = computed(() => route.path);

const handleLangChange = (lang) => {
    locale.value = lang;
    localStorage.setItem('lang', lang);
};

const handleLogout = () => {
  authStore.logout();
};
</script>

<style scoped>
.header {
  background-color: #409EFF;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.aside {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px);
  border-right: 1px solid #dcdfe6;
}
.menu-flex {
    flex: 1;
    overflow-y: auto;
    border-right: none;
}
.aside-footer {
    padding: 10px;
    border-top: 1px solid #eee;
    background-color: #fff;
}
.ml-4 {
  margin-left: 1rem;
}
</style>
