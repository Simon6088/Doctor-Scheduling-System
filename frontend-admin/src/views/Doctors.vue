<template>
  <div class="doctors-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>医生管理</span>
          <div class="header-actions">
            <el-select v-model="selectedDepartment" placeholder="筛选科室" style="width: 150px; margin-right: 10px;" clearable>
              <el-option label="所有科室" value="" />
              <el-option v-for="dept in departments" :key="dept.id" :label="dept.name" :value="dept.id" />
            </el-select>
            <el-button type="primary" @click="showDialog = true">添加医生</el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="filteredUsers" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="full_name" label="姓名" width="120" />
        <el-table-column label="科室" width="150">
          <template #default="scope">
            {{ getDepartmentName(scope.row.department_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="role" label="角色" width="100" />
        <el-table-column prop="title" label="职称" width="120" />
        <el-table-column prop="phone" label="电话" width="150" />
        <el-table-column label="标签" width="200">
          <template #default="scope">
             <el-tag v-for="tag in scope.row.tags" :key="tag.id" size="small" :style="{marginRight: '5px', color: tag.color}">{{ tag.name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加对话框 -->
    <el-dialog v-model="showDialog" title="添加医生" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.full_name" />
        </el-form-item>
        <el-form-item label="科室">
          <el-select v-model="form.department_id" placeholder="选择科室">
             <el-option v-for="dept in departments" :key="dept.id" :label="dept.name" :value="dept.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role">
            <el-option label="医生" value="doctor" />
            <el-option label="科室主任" value="manager" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item label="职称">
          <el-input v-model="form.title" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="form.phone" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAdd" :loading="adding">添加</el-button>
      </template>
    </el-dialog>

    <!-- 编辑对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑医生" width="500px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="姓名">
          <el-input v-model="editForm.full_name" />
        </el-form-item>
        <el-form-item label="职称">
          <el-input v-model="editForm.title" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="editForm.phone" />
        </el-form-item>
        <el-form-item label="标签">
          <el-select v-model="editForm.tagIds" multiple filterable allow-create default-first-option placeholder="选择或创建标签">
            <el-option v-for="tag in tags" :key="tag.id" :label="tag.name" :value="tag.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="editForm.password" type="password" placeholder="留空则不修改" />
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
import { ref, onMounted, computed } from 'vue';
import api from '../api/axios';
import { ElMessage, ElMessageBox } from 'element-plus';

const users = ref([]);
const departments = ref([]);
const showDialog = ref(false); // Used for Add Dialog
const showEditDialog = ref(false);
const selectedDepartment = ref(''); // Added for filter

const adding = ref(false);
const updating = ref(false);

const tags = ref([]);

const form = ref({
  id: null,
  username: '',
  password: '',
  full_name: '',
  role: 'doctor',
  department_id: null,
  title: '',
  phone: ''
});

const editForm = ref({
  id: null,
  full_name: '',
  title: '',
  phone: '',
  password: '',
  tagIds: []
});

const filteredUsers = computed(() => {
  if (!selectedDepartment.value) {
    return users.value;
  }
  return users.value.filter(user => user.department_id === selectedDepartment.value);
});

const fetchUsers = async () => {
  try {
    const response = await api.get('/users/');
    users.value = response.data;
  } catch (error) {
    ElMessage.error('获取用户列表失败');
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

const fetchTags = async () => {
    try {
        const response = await api.get('/tags/');
        tags.value = response.data;
    } catch (e) { console.error(e); }
};

const getDepartmentName = (departmentId) => {
  const dept = departments.value.find(d => d.id === departmentId);
  return dept ? dept.name : '未分配';
};

const handleAdd = async () => {
  adding.value = true;
  try {
    await api.post('/users/', form.value);
    ElMessage.success('添加成功');
    showDialog.value = false; // Close dialog
    form.value = { // Reset form
        id: null, department_id: null, role: 'doctor', 
        username: '', password: '', full_name: '', title: '', phone: '' 
    };
    await fetchUsers(); // Fix: fetchDoctors -> fetchUsers
  } catch (error) {
    ElMessage.error('添加失败');
  } finally {
    adding.value = false;
  }
};

const handleEdit = (row) => {
  editForm.value = {
    id: row.id,
    full_name: row.full_name,
    title: row.title || '',
    phone: row.phone || '',
    password: '',
    tagIds: row.tags ? row.tags.map(t => t.id) : []
  };
  showEditDialog.value = true;
};

const handleUpdate = async () => {
  updating.value = true;
  try {
    const updateData = {
      full_name: editForm.value.full_name,
      phone: editForm.value.phone
    };
    if (editForm.value.password) {
      updateData.password = editForm.value.password;
    }
    await api.put(`/users/${editForm.value.id}`, updateData);
    
    // Tag Sync
    const currentUser = users.value.find(u => u.id === editForm.value.id);
    const oldTagIds = currentUser.tags ? currentUser.tags.map(t => t.id) : [];
    const newTagIds = [];
    
    for (const val of editForm.value.tagIds) {
        if (typeof val === 'string') {
             const res = await api.post('/tags/', { name: val });
             tags.value.push(res.data); 
             newTagIds.push(res.data.id);
        } else {
             newTagIds.push(val);
        }
    }
    
    const toAdd = newTagIds.filter(id => !oldTagIds.includes(id));
    const toRemove = oldTagIds.filter(id => !newTagIds.includes(id));
    
    for (const tid of toAdd) await api.post(`/tags/${tid}/users/${editForm.value.id}`);
    for (const tid of toRemove) await api.delete(`/tags/${tid}/users/${editForm.value.id}`);

    ElMessage.success('更新成功');
    showEditDialog.value = false;
    await fetchUsers(); 
  } catch (error) {
    ElMessage.error('更新失败');
  } finally {
    updating.value = false;
  }
};

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除医生 ${row.full_name} 吗？`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });
    await api.delete(`/users/${row.id}`);
    ElMessage.success('删除成功');
    await fetchUsers(); // Fix: fetchDoctors -> fetchUsers
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败');
    }
  }
};

onMounted(async () => {
  await fetchDepartments();
  await fetchTags();
  await fetchUsers();
});
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
