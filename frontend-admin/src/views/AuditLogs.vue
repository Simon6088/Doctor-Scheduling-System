<template>
  <div class="audit-logs">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>审计日志 (Audit Logs)</span>
          <el-button @click="fetchLogs" size="small">刷新</el-button>
        </div>
      </template>
      <el-table :data="logs" stripe style="width: 100%" height="calc(100vh - 200px)">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="user_id" label="用户" width="150">
            <template #default="scope">
                {{ getUserName(scope.row.user_id) }}
            </template>
        </el-table-column>
        <el-table-column prop="action" label="操作" width="120">
             <template #default="scope">
                 <el-tag :type="getActionType(scope.row.action)" size="small">{{ scope.row.action }}</el-tag>
             </template>
        </el-table-column>
        <el-table-column prop="resource" label="资源类型" width="120" />
        <el-table-column prop="details" label="详情" show-overflow-tooltip />
        <el-table-column prop="created_at" label="时间" width="180">
           <template #default="scope">{{ formatDate(scope.row.created_at) }}</template> 
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api/axios';
import { format } from 'date-fns';

const logs = ref([]);
const userMap = ref({});

const fetchUsers = async () => {
    try {
        const res = await api.get('/users/');
        res.data.forEach(u => userMap.value[u.id] = u.full_name);
    } catch (e) {}
};

const fetchLogs = async () => {
    try {
        const res = await api.get('/audit-logs/?limit=100');
        logs.value = res.data;
    } catch (e) {}
};

const getUserName = (id) => userMap.value[id] || `User:${id}`;

const getActionType = (action) => {
    if (action === 'CREATE' || action === 'GENERATE') return 'success';
    if (action === 'DELETE') return 'danger';
    if (action === 'APPROVE') return 'primary';
    if (action === 'UPDATE') return 'warning';
    return 'info';
};

const formatDate = (dateStr) => {
    if (!dateStr) return '';
    return format(new Date(dateStr), 'yyyy-MM-dd HH:mm:ss');
};

onMounted(async () => {
    await fetchUsers();
    await fetchLogs();
});
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
