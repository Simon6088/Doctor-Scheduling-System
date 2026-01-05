<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <span>Login</span>
        </div>
      </template>
      <el-form :model="form" label-width="80px">
        <el-form-item label="Username">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="Password">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading">Login</el-button>
        </el-form-item>
      </el-form>
      <el-alert v-if="error" :title="error" type="error" show-icon />
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';

const authStore = useAuthStore();
const form = ref({
  username: '',
  password: '',
});
const loading = ref(false);
const error = ref('');

const handleLogin = async () => {
  loading.value = true;
  error.value = '';
  try {
    await authStore.login(form.value.username, form.value.password);
  } catch (err) {
    error.value = 'Login failed. Please check credentials.';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}
.login-card {
  width: 400px;
}
.card-header {
  text-align: center;
  font-weight: bold;
}
</style>
