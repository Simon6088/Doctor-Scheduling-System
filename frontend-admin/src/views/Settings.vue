<template>
  <div class="settings-container">
    <el-card>
      <template #header>
        <span>系统设置</span>
      </template>
      
      <el-descriptions title="用户信息" :column="2" border>
        <el-descriptions-item label="用户名">{{ user?.username }}</el-descriptions-item>
        <el-descriptions-item label="姓名">{{ user?.full_name }}</el-descriptions-item>
        <el-descriptions-item label="角色">{{ user?.role }}</el-descriptions-item>
        <el-descriptions-item label="职称">{{ user?.title || '未设置' }}</el-descriptions-item>
        <el-descriptions-item label="电话">{{ user?.phone || '未设置' }}</el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <h3>修改密码</h3>
      <el-form :model="passwordForm" label-width="100px" style="max-width: 500px">
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.newPassword" type="password" />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="passwordForm.confirmPassword" type="password" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleChangePassword">修改密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { ElMessage } from 'element-plus';

const authStore = useAuthStore();
const user = ref(null);
const passwordForm = ref({
  newPassword: '',
  confirmPassword: ''
});

const handleChangePassword = () => {
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    ElMessage.error('两次密码不一致');
    return;
  }
  ElMessage.info('密码修改功能待实现');
};

onMounted(() => {
  user.value = authStore.user;
});
</script>

<style scoped>
.settings-container {
  max-width: 800px;
}
</style>
