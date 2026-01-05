<template>
  <el-card class="box-card">
    <template #header>
      <div class="card-header">
        <span>医生排班意愿</span>
        <el-button type="primary" @click="fetchPreferences">刷新</el-button>
      </div>
    </template>
    
    <el-table :data="preferences" style="width: 100%" stripe>
      <el-table-column prop="user_id" label="医生" :formatter="formatUser" width="150" />
      <el-table-column prop="date" label="日期" sortable width="120" />
      <el-table-column prop="type" label="意愿类型" width="120">
        <template #default="scope">
          <el-tag :type="scope.row.type === 'desire' ? 'success' : 'danger'">
            {{ scope.row.type === 'desire' ? '希望排班' : '不希望排班' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="reason" label="原因" />
      <el-table-column label="创建时间" width="180">
        <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api/axios';
import { ElMessage } from 'element-plus';

const preferences = ref([]);
const users = ref([]);

const fetchPreferences = async () => {
    try {
        const res = await api.get('/preferences/');
        preferences.value = res.data;
    } catch (e) {
        ElMessage.error('获取意愿列表失败');
    }
}

const fetchUsers = async () => {
    try {
        const res = await api.get('/users/');
        users.value = res.data;
    } catch(e) {}
}

const formatUser = (row) => {
    const u = users.value.find(x => x.id === row.user_id);
    return u ? u.full_name : row.user_id;
}

const formatDate = (dateStr) => {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleString();
}

onMounted(async () => {
    await fetchUsers();
    await fetchPreferences();
});
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
