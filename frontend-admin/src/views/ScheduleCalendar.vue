<template>
  <div class="calendar-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>排班日历</span>
          <div class="calendar-filters">
            <el-select v-model="selectedDepartment" placeholder="选择科室" style="width: 200px; margin-right: 10px;" clearable>
              <el-option label="全部科室" value="" />
              <el-option v-for="dept in departments" :key="dept.id" :label="dept.name" :value="dept.id" />
            </el-select>
            <el-select v-model="selectedDoctor" placeholder="选择医生" style="width: 200px;" clearable>
              <el-option label="全部医生" value="" />
              <el-option v-for="doc in filteredDoctors" :key="doc.id" :label="doc.full_name" :value="doc.id" />
            </el-select>
          </div>
        </div>
      </template>

      <FullCalendar :options="calendarOptions" />
    </el-card>

    <!-- 排班详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="排班详情" width="600px">
      <div v-if="selectedEvent">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="日期">{{ selectedEvent.date }}</el-descriptions-item>
          <el-descriptions-item label="班次">{{ selectedEvent.shiftName }}</el-descriptions-item>
          <el-descriptions-item label="医生">{{ selectedEvent.doctorName }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ selectedEvent.status }}</el-descriptions-item>
        </el-descriptions>
        <div style="margin-top: 20px;">
          <el-button type="danger" @click="handleDeleteSchedule">删除此排班</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';
import api from '../api/axios';
import { ElMessage } from 'element-plus';

const departments = ref([]);
const selectedDepartment = ref('');
const selectedDoctor = ref('');
const schedules = ref([]);
const users = ref([]);
const shiftTypes = ref([]);
const showDetailDialog = ref(false);
const selectedEvent = ref(null);

const events = ref([]);
const doctors = ref([]); // This seems unused or redundant with users
const allDoctors = computed(() => users.value.filter(u => u.role === 'doctor'));

const filteredDoctors = computed(() => {
  if (!selectedDepartment.value) {
    return allDoctors.value;
  }
  return allDoctors.value.filter(d => d.department_id === selectedDepartment.value);
});

// Helper functions to get names (assuming these will be defined elsewhere or derived from existing data)
const getDoctorName = (id) => {
  const doctor = users.value.find(d => d.id === id); // Fix: use users instead of doctors ref
  return doctor ? doctor.full_name : '未知医生';
};

const getShiftTypeName = (id) => {
  const shiftType = shiftTypes.value.find(st => st.id === id);
  return shiftType ? shiftType.name : '未知班次';
};

// 定义事件处理函数
const handleEventClick = (clickInfo) => {
  const schedule = schedules.value.find(s => s.id === parseInt(clickInfo.event.id));
  if (schedule) {
    selectedEvent.value = {
      ...schedule,
      doctorName: getDoctorName(schedule.doctor_id),
      shiftName: getShiftTypeName(schedule.shift_type_id)
    };
    showDetailDialog.value = true;
  }
};

const calendarOptions = ref({
  plugins: [dayGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  locale: 'zh-cn',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,dayGridWeek'
  },
  events: [],
  eventClick: handleEventClick,
  height: 'auto'
});

const fetchDepartments = async () => {
  try {
    const response = await api.get('/departments/');
    departments.value = response.data;
  } catch (error) {
    ElMessage.error('获取科室列表失败');
  }
};

const fetchUsers = async () => {
  try {
    const response = await api.get('/users/');
    users.value = response.data;
  } catch (error) {
    console.error('获取用户列表失败');
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

const fetchSchedules = async () => {
  try {
    let url = '/schedules/';
    const params = new URLSearchParams();
    
    if (selectedDepartment.value) {
      params.append('department_id', selectedDepartment.value);
    }
    if (selectedDoctor.value) {
      params.append('doctor_id', selectedDoctor.value);
    }
    
    const queryString = params.toString();
    if (queryString) {
      url += `?${queryString}`;
    }
    
    const response = await api.get(url);
    schedules.value = response.data;
    updateCalendarEvents();
  } catch (error) {
    ElMessage.error('获取排班失败');
  }
};

const updateCalendarEvents = () => {
  const events = schedules.value.map(schedule => {
    const user = users.value.find(u => u.id === schedule.doctor_id);
    const shiftType = shiftTypes.value.find(st => st.id === schedule.shift_type_id);
    
    return {
      id: schedule.id,
      title: `${user?.full_name || '未知'} - ${shiftType?.name || '未知'}`,
      date: schedule.date,
      backgroundColor: getShiftColor(shiftType?.shift_category),
      extendedProps: {
        scheduleId: schedule.id,
        doctorId: schedule.doctor_id,
        doctorName: user?.full_name || '未知',
        shiftTypeId: schedule.shift_type_id,
        shiftName: shiftType?.name || '未知',
        status: schedule.status
      }
    };
  });
  
  calendarOptions.value.events = events;
};

const getShiftColor = (category) => {
  const colors = {
    'day': '#409EFF',
    'night': '#E6A23C',
    'oncall': '#909399',
    'backup': '#67C23A',
    'holiday': '#F56C6C'
  };
  return colors[category] || '#409EFF';
};

const handleDeleteSchedule = async () => {
  try {
    await api.delete(`/schedules/${selectedEvent.value.id}`);
    ElMessage.success('删除成功');
    showDetailDialog.value = false;
    await fetchSchedules();
  } catch (error) {
    ElMessage.error('删除失败');
  }
};

// 监听科室变化
watch(selectedDepartment, () => {
  selectedDoctor.value = ''; // 清空医生选择
  fetchSchedules();
});

// 监听医生变化
watch(selectedDoctor, () => {
  fetchSchedules();
});

onMounted(async () => {
  await fetchDepartments();
  await fetchUsers(); // 先获取用户，用于医生列表
  await fetchShiftTypes();
  await fetchSchedules();
});
</script>

<style scoped>
.calendar-container {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.calendar-filters {
  display: flex;
  align-items: center;
}
</style>
