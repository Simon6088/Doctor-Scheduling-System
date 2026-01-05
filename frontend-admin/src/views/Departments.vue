<template>
  <div class="departments-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>科室管理</span>
          <el-button type="primary" @click="showAddDialog = true">添加科室</el-button>
        </div>
      </template>
      
      <el-table :data="departments" style="width: 100%" row-key="id" :tree-props="{children: 'children'}">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="科室名称" width="200" />
        <el-table-column label="医生数量" width="120">
          <template #default="scope">
            <el-tag type="info">{{ getDoctorCount(scope.row.id) }} 人</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加对话框 -->
    <el-dialog v-model="showAddDialog" title="添加科室" width="500px">
      <el-form :model="deptForm" label-width="100px">
        <el-form-item label="科室名称">
          <el-input v-model="deptForm.name" />
        </el-form-item>
        <el-form-item label="上级科室">
          <el-select v-model="deptForm.parent_id" placeholder="选择上级科室（可选）" clearable>
            <el-option v-for="dept in flatDepartments" :key="dept.id" :label="dept.name" :value="dept.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAdd" :loading="adding">添加</el-button>
      </template>
    </el-dialog>

    <!-- 编辑对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑科室" width="500px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="科室名称">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="上级科室">
          <el-select v-model="editForm.parent_id" placeholder="选择上级科室（可选）" clearable>
            <el-option v-for="dept in flatDepartments.filter(d => d.id !== editForm.id)" :key="dept.id" :label="dept.name" :value="dept.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpdate" :loading="updating">更新</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../api/axios';
import { ElMessage, ElMessageBox } from 'element-plus';

const departments = ref([]);
const doctors = ref([]);
const showAddDialog = ref(false);
const showEditDialog = ref(false);
const adding = ref(false);
const updating = ref(false);
const deptForm = ref({
  name: '',
  parent_id: null
});
const editForm = ref({
  id: null,
  name: '',
  parent_id: null
});

const flatDepartments = computed(() => {
  const flatten = (items) => {
    let result = [];
    items.forEach(item => {
      result.push(item);
      if (item.children && item.children.length > 0) {
        result = result.concat(flatten(item.children));
      }
    });
    return result;
  };
  return flatten(departments.value);
});

const fetchDepartments = async () => {
  try {
    const response = await api.get('/departments/');
    departments.value = response.data;
  } catch (error) {
    ElMessage.error('获取科室列表失败');
  }
};

const fetchDoctors = async () => {
  try {
    const response = await api.get('/users/');
    doctors.value = response.data.filter(u => u.role === 'doctor');
  } catch (error) {
    console.error('获取医生列表失败');
  }
};

const getDoctorCount = (departmentId) => {
  return doctors.value.filter(d => d.department_id === departmentId).length;
};

const handleAdd = async () => {
  adding.value = true;
  try {
    await api.post('/departments/', deptForm.value);
    ElMessage.success('添加成功');
    showAddDialog.value = false;
    deptForm.value = { name: '', parent_id: null };
    await fetchDepartments();
  } catch (error) {
    ElMessage.error('添加失败');
  } finally {
    adding.value = false;
  }
};

const handleEdit = (row) => {
  editForm.value = {
    id: row.id,
    name: row.name,
    parent_id: row.parent_id
  };
  showEditDialog.value = true;
};

const handleUpdate = async () => {
  updating.value = true;
  try {
    await api.put(`/departments/${editForm.value.id}`, {
      name: editForm.value.name,
      parent_id: editForm.value.parent_id
    });
    ElMessage.success('更新成功');
    showEditDialog.value = false;
    await fetchDepartments();
  } catch (error) {
    ElMessage.error('更新失败');
  } finally {
    updating.value = false;
  }
};

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该科室吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });
    await api.delete(`/departments/${row.id}`);
    ElMessage.success('删除成功');
    await fetchDepartments();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败');
    }
  }
};

onMounted(async () => {
  await fetchDoctors();
  await fetchDepartments();
});
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
