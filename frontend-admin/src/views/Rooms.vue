<template>
  <div class="rooms-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>诊室管理</span>
          <el-button type="primary" @click="showDialog = true">添加诊室</el-button>
        </div>
      </template>

      <el-table :data="rooms" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="room_number" label="房间号" width="100" />
        <el-table-column prop="name" label="诊室名称" width="150" />
        <el-table-column label="所属科室" width="150">
          <template #default="scope">
            {{ getDepartmentName(scope.row.department_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="capacity" label="容量" width="80" />
        <el-table-column prop="description" label="描述" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="showDialog" :title="dialogTitle" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="房间号">
          <el-input v-model="form.room_number" />
        </el-form-item>
        <el-form-item label="诊室名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="所属科室">
          <el-select v-model="form.department_id" placeholder="选择科室" clearable>
            <el-option v-for="dept in departments" :key="dept.id" :label="dept.name" :value="dept.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="容量">
          <el-input-number v-model="form.capacity" :min="1" :max="10" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">{{ form.id ? '更新' : '添加' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api/axios';
import { ElMessage, ElMessageBox } from 'element-plus';

const rooms = ref([]);
const departments = ref([]);
const showDialog = ref(false);
const dialogTitle = ref('添加诊室');
const submitting = ref(false);
const form = ref({
  id: null,
  room_number: '',
  name: '',
  department_id: null,
  capacity: 1,
  description: ''
});

const fetchRooms = async () => {
  try {
    const response = await api.get('/rooms/');
    rooms.value = response.data;
  } catch (error) {
    ElMessage.error('获取诊室列表失败');
  }
};

const fetchDepartments = async () => {
  try {
    const response = await api.get('/departments/');
    departments.value = response.data;
  } catch (error) {
    console.error('获取科室列表失败');
  }
};

const getDepartmentName = (departmentId) => {
  const dept = departments.value.find(d => d.id === departmentId);
  return dept ? dept.name : '未分配';
};

const handleEdit = (room) => {
  form.value = {
    id: room.id,
    room_number: room.room_number,
    name: room.name,
    department_id: room.department_id,
    capacity: room.capacity,
    description: room.description || ''
  };
  dialogTitle.value = '编辑诊室';
  showDialog.value = true;
};

const handleSubmit = async () => {
  submitting.value = true;
  try {
    if (form.value.id) {
      // 更新
      await api.put(`/rooms/${form.value.id}`, {
        room_number: form.value.room_number,
        name: form.value.name,
        department_id: form.value.department_id,
        capacity: form.value.capacity,
        description: form.value.description
      });
      ElMessage.success('更新成功');
    } else {
      // 添加
      await api.post('/rooms/', form.value);
      ElMessage.success('添加成功');
    }
    showDialog.value = false;
    resetForm();
    await fetchRooms();
  } catch (error) {
    ElMessage.error(form.value.id ? '更新失败' : '添加失败');
  } finally {
    submitting.value = false;
  }
};

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该诊室吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });
    await api.delete(`/rooms/${id}`);
    ElMessage.success('删除成功');
    await fetchRooms();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败');
    }
  }
};

const resetForm = () => {
  form.value = {
    id: null,
    room_number: '',
    name: '',
    department_id: null,
    capacity: 1,
    description: ''
  };
  dialogTitle.value = '添加诊室';
};

onMounted(async () => {
  await fetchDepartments();
  await fetchRooms();
});
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
