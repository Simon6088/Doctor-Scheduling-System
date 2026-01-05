<template>
  <div class="feedback">
    <el-card>
        <template #header>
            <div class="card-header">
                <span>用户反馈</span>
                <el-button @click="fetchFeedbacks" size="small">刷新</el-button>
            </div>
        </template>
        <el-table :data="feedbacks" stripe style="width: 100%">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="type" label="类型" width="100">
                <template #default="scope">
                    <el-tag :type="getTypeTag(scope.row.type)">{{ getTypeLabel(scope.row.type) }}</el-tag>
                </template>
            </el-table-column>
            <el-table-column prop="urgency" label="紧急度" width="100">
                 <template #default="scope">
                     <el-tag :type="getUrgencyTag(scope.row.urgency)" effect="dark">{{ scope.row.urgency }}</el-tag>
                 </template>
            </el-table-column>
            <el-table-column prop="content" label="内容" />
            <el-table-column prop="page" label="页面" width="150" show-overflow-tooltip/>
            <el-table-column prop="user_id" label="用户" width="120">
                <template #default="scope">{{ getUserName(scope.row.user_id) }}</template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
                 <template #default="scope">
                     <el-tag :type="scope.row.status==='open'?'warning':'info'">{{ scope.row.status }}</el-tag>
                 </template>
            </el-table-column>
            <el-table-column prop="created_at" label="时间" width="160">
                 <template #default="scope">{{ formatDate(scope.row.created_at) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="100">
                <template #default="scope">
                    <el-button v-if="scope.row.status==='open'" size="small" type="success" @click="closeFeedback(scope.row.id)">关闭</el-button>
                </template>
            </el-table-column>
        </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api/axios';
import { format } from 'date-fns';
import { ElMessage } from 'element-plus';

const feedbacks = ref([]);
const userMap = ref({});

const fetchUsers = async () => {
     try {
         const res = await api.get('/users/');
         res.data.forEach(u => userMap.value[u.id] = u.full_name);
     } catch (e) {}
};

const getUserName = (id) => userMap.value[id] || `User:${id}`;

const fetchFeedbacks = async () => {
    try {
        const res = await api.get('/feedback/');
        feedbacks.value = res.data;
    } catch (e) { ElMessage.error('加载失败'); }
};

const closeFeedback = async (id) => {
    try {
        await api.put(`/feedback/${id}/close`);
        ElMessage.success('已关闭');
        fetchFeedbacks();
    } catch (e) { ElMessage.error('操作失败'); }
};

const getTypeTag = (t) => {
    if (t === 'bug') return 'danger';
    if (t === 'review') return 'success';
    return 'primary';
};
const getTypeLabel = (t) => {
    const map = { bug: 'Bug', review: '评价', suggestion: '建议' };
    return map[t] || t;
};

const getUrgencyTag = (u) => {
    if (u === 'high') return 'danger';
    if (u === 'medium') return 'warning';
    return 'info';
};

const formatDate = (dateStr) => {
    if (!dateStr) return '';
    return format(new Date(dateStr), 'yyyy-MM-dd HH:mm');
};

onMounted(async () => {
    await fetchUsers();
    await fetchFeedbacks();
});
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
