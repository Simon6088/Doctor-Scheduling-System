<template>
  <div class="shift-types-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>班次管理</span>
          <el-button type="primary" @click="showAddDialog">添加班次</el-button>
        </div>
      </template>

      <el-table :data="shiftTypes" style="width: 100%">
        <el-table-column prop="name" label="班次名称" width="150" />
        <el-table-column prop="shift_category" label="类别" width="120">
          <template #default="scope">
            <el-tag :type="getCategoryType(scope.row.shift_category)">
              {{ getCategoryName(scope.row.shift_category) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" width="100" />
        <el-table-column prop="end_time" label="结束时间" width="100" />
        <el-table-column prop="weight" label="计分权重" width="100" />
        <el-table-column prop="required_qualification" label="所需资质" width="150" />
        <el-table-column prop="description" label="描述" />
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="班次名称">
          <el-input v-model="form.name" placeholder="例如：白班、夜班" />
        </el-form-item>
        <el-form-item label="班次类别">
          <el-select v-model="form.shift_category" placeholder="请选择">
            <el-option label="白班" value="day" />
            <el-option label="夜班" value="night" />
            <el-option label="听班" value="oncall" />
            <el-option label="备班" value="backup" />
            <el-option label="节假日班" value="holiday" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始时间">
          <el-time-picker v-model="form.start_time" format="HH:mm" value-format="HH:mm" placeholder="选择时间" />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-time-picker v-model="form.end_time" format="HH:mm" value-format="HH:mm" placeholder="选择时间" />
        </el-form-item>
        <el-form-item label="计分权重">
          <el-input-number v-model="form.weight" :min="0.1" :max="10" :step="0.1" />
        </el-form-item>
        <el-form-item label="所需资质">
          <el-input v-model="form.required_qualification" placeholder="例如：主治医师" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="班次说明" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api/axios';
import { ElMessage, ElMessageBox } from 'element-plus';

const shiftTypes = ref([]);
const dialogVisible = ref(false);
const dialogTitle = ref('添加班次');
const isEdit = ref(false);
const editId = ref(null);

const form = ref({
  name: '',
  shift_category: 'day',
  start_time: '',
  end_time: '',
  weight: 1.0,
  required_qualification: '',
  description: ''
});

const fetchShiftTypes = async () => {
  try {
    const response = await api.get('/shift-types/');
    shiftTypes.value = response.data;
  } catch (error) {
    ElMessage.error('获取班次列表失败');
  }
};

const showAddDialog = () => {
  isEdit.value = false;
  dialogTitle.value = '添加班次';
  form.value = {
    name: '',
    shift_category: 'day',
    start_time: '',
    end_time: '',
    weight: 1.0,
    required_qualification: '',
    description: ''
  };
  dialogVisible.value = true;
};

const handleEdit = (row) => {
  isEdit.value = true;
  editId.value = row.id;
  dialogTitle.value = '编辑班次';
  form.value = { ...row };
  dialogVisible.value = true;
};

const handleSubmit = async () => {
  try {
    if (isEdit.value) {
      await api.put(`/shift-types/${editId.value}`, form.value);
      ElMessage.success('更新成功');
    } else {
      await api.post('/shift-types/', form.value);
      ElMessage.success('添加成功');
    }
    dialogVisible.value = false;
    await fetchShiftTypes();
  } catch (error) {
    ElMessage.error(isEdit.value ? '更新失败' : '添加失败');
  }
};

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除班次"${row.name}"吗？`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });
    await api.delete(`/shift-types/${row.id}`);
    ElMessage.success('删除成功');
    await fetchShiftTypes();
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败');
    }
  }
};

const getCategoryName = (category) => {
  const names = {
    'day': '白班',
    'night': '夜班',
    'oncall': '听班',
    'backup': '备班',
    'holiday': '节假日班'
  };
  return names[category] || category;
};

const getCategoryType = (category) => {
  const types = {
    'day': '',
    'night': 'warning',
    'oncall': 'info',
    'backup': 'success',
    'holiday': 'danger'
  };
  return types[category] || '';
};

onMounted(() => {
  fetchShiftTypes();
});
</script>

<style scoped>
.shift-types-container {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
