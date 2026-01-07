<template>
  <view class="container">
    <view class="header">
      <picker @change="onDateChange" mode="date" :value="selectedDate">
        <view class="date-picker">
          <text>{{ selectedDate }}</text>
          <text class="arrow">▼</text>
        </view>
      </picker>
      
      <picker @change="onDoctorChange" :range="doctorList" range-key="full_name" :value="selectedDoctorIndex">
        <view class="doctor-picker">
          <text>{{ selectedDoctorIndex >= 0 ? doctorList[selectedDoctorIndex].full_name : '选择医生' }}</text>
          <text class="arrow">▼</text>
        </view>
      </picker>
    </view>

    <view class="schedule-list">
      <view v-if="loading" class="loading">
        <text>加载中...</text>
      </view>
      <view v-else-if="schedules.length === 0" class="empty">
        <text>当天无排班</text>
      </view>
      <view v-else>
        <view v-for="schedule in schedules" :key="schedule.id" class="schedule-item">
          <view class="doctor-info">
            <text class="doctor-name">{{ schedule.doctorName }}</text>
            <text class="doctor-title">{{ schedule.doctorTitle }}</text>
          </view>
          <view class="shift-info">
            <text class="shift-name">{{ schedule.shiftName }}</text>
            <text class="shift-time">{{ schedule.shiftTime }}</text>
          </view>
        </view>
      </view>
    </view>
    <FeedbackBtn />
  </view>
</template>

<script>
import { request } from '../../utils/request';
import FeedbackBtn from '../../components/FeedbackBtn.vue';

export default {
  components: { FeedbackBtn },
  data() {
    return {
      selectedDate: '',
      schedules: [],
      shiftTypes: [],
      doctorList: [],
      selectedDoctorIndex: -1,
      selectedDoctorId: null,
      loading: false
    }
  },
  onLoad() {
    // 默认显示今天
    const today = new Date();
    this.selectedDate = this.formatDate(today);
    this.fetchDoctorList();
  },
  methods: {
    formatDate(date) {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    async fetchDoctorList() {
      try {
        // 获取当前用户信息
        const currentUser = await request({ url: '/users/me' });
        const myDepartmentId = currentUser.department_id;
        
        if (!myDepartmentId) {
          uni.showToast({ title: '您未分配科室', icon: 'none' });
          return;
        }
        
        // 获取同科室的所有医生
        const allUsers = await request({ url: '/users/' });
        this.doctorList = allUsers.filter(u => u.department_id === myDepartmentId && u.role === 'doctor');
        
        // 默认不选择任何医生，显示全部
        this.fetchSchedules();
      } catch (error) {
        console.error('获取医生列表失败:', error);
        uni.showToast({ title: '获取医生列表失败', icon: 'none' });
      }
    },
    onDoctorChange(e) {
      this.selectedDoctorIndex = e.detail.value;
      if (this.selectedDoctorIndex >= 0) {
        this.selectedDoctorId = this.doctorList[this.selectedDoctorIndex].id;
      } else {
        this.selectedDoctorId = null;
      }
      this.fetchSchedules();
    },
    // Removed fetchMyDepartment as its logic is now part of fetchSchedules
    async fetchSchedules() {
      this.loading = true;
      try {
        // 1. 获取当前用户信息
        const currentUser = await request({ url: '/users/me' });
        const myDepartmentId = currentUser.department_id;
        
        if (!myDepartmentId) {
          uni.showToast({ title: '您未分配科室', icon: 'none' });
          this.schedules = [];
          return;
        }
        
        // 2. 构建查询参数
        let queryParams = `department_id=${myDepartmentId}&start_date=${this.selectedDate}&end_date=${this.selectedDate}`;
        if (this.selectedDoctorId) {
          queryParams += `&doctor_id=${this.selectedDoctorId}`;
        }
        
        // 3. 并行获取所需数据
        const [schedulesData, allUsers, shiftTypesData] = await Promise.all([
          request({ url: `/schedules/?${queryParams}` }),
          request({ url: '/users/' }),
          request({ url: '/shift-types/' })
        ]);

        this.shiftTypes = shiftTypesData;
        
        // 4. 组装展示数据
        this.schedules = schedulesData.map(schedule => {
          const doctor = allUsers.find(u => u.id === schedule.doctor_id);
          // 使用松散比较 (==) 以防 ID 类型不一致
          const shiftType = this.shiftTypes.find(st => st.id == schedule.shift_type_id);
          
          return {
            ...schedule,
            doctorName: doctor ? doctor.full_name : '未知医生',
            doctorTitle: doctor ? doctor.title : '',
            shiftName: shiftType ? shiftType.name : '未知班次',
            shiftTime: shiftType ? `${shiftType.start_time}-${shiftType.end_time}` : ''
          };
        });
        
        console.log('加载完成，排班数量:', this.schedules.length);
        
      } catch (error) {
        console.error('获取科室排班失败:', error);
        uni.showToast({
          title: '获取排班失败',
          icon: 'none'
        });
        this.schedules = [];
      } finally {
        this.loading = false;
      }
    },
    onDateChange(e) {
      this.selectedDate = e.detail.value;
      this.fetchSchedules(); // Call the new method
    }
  }
}
</script>

<style>
.container {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}
.header {
  margin-bottom: 20px;
}
.date-picker {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.arrow {
  color: #999;
}
.loading, .empty {
  text-align: center;
  padding: 40px;
  color: #999;
}
.schedule-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  margin-bottom: 10px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.doctor-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.doctor-name {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}
.doctor-title {
  font-size: 12px;
  color: #999;
}
.shift-info {
  text-align: right;
  display: flex;
  flex-direction: column;
}
.shift-name {
  font-size: 14px;
  color: #007aff;
  margin-bottom: 5px;
}
.shift-time {
  font-size: 12px;
  color: #666;
}
</style>
