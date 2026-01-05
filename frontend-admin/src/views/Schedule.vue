<template>
  <div class="schedule-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>排班管理</span>
          <el-button type="primary" @click="showDialog = true">生成排班</el-button>
        </div>
      </template>
      
      <el-table :data="schedules" style="width: 100%">
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column label="医生" width="200">
          <template #default="scope">
            {{ getDoctorName(scope.row.doctor_id) }}
          </template>
        </el-table-column>
        <el-table-column label="班次类型" width="150">
          <template #default="scope">
            {{ getShiftTypeName(scope.row.shift_type_id) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button type="danger" size="small" @click="handleDelete(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showDialog" title="生成排班" width="500px">
      <el-form :model="generateForm" label-width="100px">
        <el-form-item label="开始日期">
          <el-date-picker v-model="generateForm.startDate" type="date" placeholder="选择日期" />
        </el-form-item>
        <el-form-item label="天数">
          <el-input-number v-model="generateForm.days" :min="1" :max="30" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleGenerate" :loading="generating">生成</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api/axios';
import { ElMessage, ElMessageBox } from 'element-plus';

const schedules = ref([]);
const doctors = ref([]);
const shiftTypes = ref([]);
const showDialog = ref(false);
const generating = ref(false);
const generateForm = ref({
  startDate: new Date().toISOString().split('T')[0],
  days: 7
});

const fetchSchedules = async () => {
  try {
    const response = await api.get('/schedules/');
    schedules.value = response.data;
  } catch (error) {
    ElMessage.error('获取排班失败');
  }
};

const fetchDoctors = async () => {
  try {
    const response = await api.get('/users/');
    doctors.value = response.data;
  } catch (error) {
    console.error('获取医生列表失败');
  }
};

const fetchShiftTypes = async () => {
  try {
    const response = await api.get('/shift-types/');
    shiftTypes.value = response.data;
  } catch (error) {
    console.error('获取班次类型失败');
  }
};

const getDoctorName = (doctorId) => {
  const doctor = doctors.value.find(d => d.id === doctorId);
  return doctor ? `${doctor.full_name} (ID: ${doctorId})` : `ID: ${doctorId}`;
};

const getShiftTypeName = (shiftTypeId) => {
  const shiftType = shiftTypes.value.find(st => st.id === shiftTypeId);
  return shiftType ? shiftType.name : `ID: ${shiftTypeId}`;
};

const getStatusText = (status) => {
  const statusMap = {
    'draft': '草稿',
    'published': '已发布',
    'confirmed': '已确认',
    'cancelled': '已取消'
  };
  return statusMap[status] || status;
};

const getStatusType = (status) => {
  const typeMap = {
    'draft': 'info',
    'published': 'success',
    'confirmed': 'success',
    'cancelled': 'danger'
  };
  return typeMap[status] || '';
};

const handleGenerate = async () => {
  generating.value = true;
  try {
    const startDate = generateForm.value.startDate.toISOString ? 
      generateForm.value.startDate.toISOString().split('T')[0] : 
      generateForm.value.startDate;
    await api.post(`/schedules/generate?start_date=${startDate}&days=${generateForm.value.days}`);
    ElMessage.success('排班生成成功');
    showDialog.value = false;
    await fetchSchedules();
  } catch (error) {
    ElMessage.error('排班生成失败');
  } finally {
    generating.value = false;
  }
};


const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm(`确定要删除该排班记录吗？`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });
    await api.delete(`/schedules/${id}`);
    ElMessage.success('删除成功');
    await fetchSchedules();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败');
    }
  }
};

onMounted(async () => {
  await fetchDoctors();
  await fetchShiftTypes();
  await fetchSchedules();
});
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
