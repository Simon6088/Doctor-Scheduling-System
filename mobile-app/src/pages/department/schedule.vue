<template>
  <view class="container">
    <!-- Header with doctor filter -->
    <view class="header">
      <picker @change="onDoctorChange" :range="doctorList" range-key="full_name" :value="selectedDoctorIndex">
        <view class="doctor-picker">
          <text>{{ selectedDoctorIndex >= 0 ? doctorList[selectedDoctorIndex].full_name : '全部医生' }}</text>
          <text class="arrow">▼</text>
        </view>
      </picker>
    </view>

    <!-- Calendar Navigation -->
    <view class="calendar-nav">
      <view class="nav-btn" @click="prevMonth">
        <text>◀</text>
      </view>
      <view class="current-month">
        <text>{{ currentYear }}年{{ currentMonth }}月</text>
      </view>
      <view class="nav-btn" @click="nextMonth">
        <text>▶</text>
      </view>
      <view class="today-btn" @click="goToday">
        <text>今天</text>
      </view>
    </view>

    <!-- Calendar Grid -->
    <view class="calendar">
      <!-- Weekday Headers -->
      <view class="weekdays">
        <view class="weekday" v-for="day in weekdays" :key="day">
          <text>{{ day }}</text>
        </view>
      </view>

      <!-- Calendar Days -->
      <view class="days-grid">
        <view 
          v-for="(day, index) in calendarDays" 
          :key="index"
          class="day-cell"
          :class="{
            'other-month': !day.isCurrentMonth,
            'today': day.isToday
          }"
        >
          <view class="day-number">
            <text>{{ day.day }}</text>
          </view>
          <view class="day-schedules">
            <view 
              v-for="schedule in day.schedules" 
              :key="schedule.id"
              class="schedule-badge"
              :style="{ backgroundColor: getShiftColor(schedule.shift_type_id) }"
            >
              <text class="schedule-text">{{ schedule.doctorName }}-{{ schedule.shiftName }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view v-if="loading" class="loading-overlay">
      <text>加载中...</text>
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
      currentYear: new Date().getFullYear(),
      currentMonth: new Date().getMonth() + 1,
      weekdays: ['周日', '周一', '周二', '周三', '周四', '周五', '周六'],
      calendarDays: [],
      schedules: [],
      shiftTypes: [],
      doctorList: [],
      selectedDoctorIndex: -1,
      selectedDoctorId: null,
      myDepartmentId: null,
      loading: false,
      shiftColors: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399']
    }
  },
  onLoad() {
    this.init();
  },
  methods: {
    async init() {
      try {
        // 获取当前用户信息
        const currentUser = await request({ url: '/users/me' });
        this.myDepartmentId = currentUser.department_id;
        
        if (!this.myDepartmentId) {
          uni.showToast({ title: '您未分配科室', icon: 'none' });
          return;
        }
        
        // 获取同科室的所有医生
        const allUsers = await request({ url: '/users/' });
        this.doctorList = allUsers.filter(u => u.department_id === this.myDepartmentId && u.role === 'doctor');
        
        // 获取班次类型
        this.shiftTypes = await request({ url: '/shift-types/' });
        
        // 加载当前月份的排班
        await this.loadMonthSchedules();
      } catch (error) {
        console.error('初始化失败:', error);
        uni.showToast({ title: '初始化失败', icon: 'none' });
      }
    },
    
    async loadMonthSchedules() {
      this.loading = true;
      try {
        // 计算月份的起止日期
        const startDate = `${this.currentYear}-${String(this.currentMonth).padStart(2, '0')}-01`;
        const lastDay = new Date(this.currentYear, this.currentMonth, 0).getDate();
        const endDate = `${this.currentYear}-${String(this.currentMonth).padStart(2, '0')}-${lastDay}`;
        
        // 构建查询参数
        let queryParams = `department_id=${this.myDepartmentId}&start_date=${startDate}&end_date=${endDate}`;
        if (this.selectedDoctorId) {
          queryParams += `&doctor_id=${this.selectedDoctorId}`;
        }
        
        // 获取排班数据
        const schedulesData = await request({ url: `/schedules/?${queryParams}` });
        
        // 获取所有用户信息用于显示医生姓名
        const allUsers = await request({ url: '/users/' });
        
        // 组装排班数据
        this.schedules = schedulesData.map(schedule => {
          const doctor = allUsers.find(u => u.id === schedule.doctor_id);
          const shiftType = this.shiftTypes.find(st => st.id == schedule.shift_type_id);
          
          return {
            ...schedule,
            doctorName: doctor ? doctor.full_name : '未知',
            shiftName: shiftType ? shiftType.name : '未知班次',
            date: schedule.date
          };
        });
        
        // 生成日历
        this.generateCalendar();
        
      } catch (error) {
        console.error('获取排班失败:', error);
        uni.showToast({ title: '获取排班失败', icon: 'none' });
      } finally {
        this.loading = false;
      }
    },
    
    generateCalendar() {
      const year = this.currentYear;
      const month = this.currentMonth;
      
      // 当月第一天和最后一天
      const firstDay = new Date(year, month - 1, 1);
      const lastDay = new Date(year, month, 0);
      
      // 日历起始日（可能是上月末）
      const startDay = new Date(firstDay);
      startDay.setDate(startDay.getDate() - firstDay.getDay());
      
      // 日历结束日（可能是下月初）
      const endDay = new Date(lastDay);
      endDay.setDate(endDay.getDate() + (6 - lastDay.getDay()));
      
      // 今天
      const today = new Date();
      const todayStr = this.formatDate(today);
      
      // 生成日历数组
      this.calendarDays = [];
      const current = new Date(startDay);
      
      while (current <= endDay) {
        const dateStr = this.formatDate(current);
        const daySchedules = this.schedules.filter(s => s.date === dateStr);
        
        this.calendarDays.push({
          day: current.getDate(),
          date: dateStr,
          isCurrentMonth: current.getMonth() === month - 1,
          isToday: dateStr === todayStr,
          schedules: daySchedules
        });
        
        current.setDate(current.getDate() + 1);
      }
    },
    
    formatDate(date) {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    
    getShiftColor(shiftTypeId) {
      const index = (shiftTypeId || 0) % this.shiftColors.length;
      return this.shiftColors[index];
    },
    
    prevMonth() {
      if (this.currentMonth === 1) {
        this.currentMonth = 12;
        this.currentYear--;
      } else {
        this.currentMonth--;
      }
      this.loadMonthSchedules();
    },
    
    nextMonth() {
      if (this.currentMonth === 12) {
        this.currentMonth = 1;
        this.currentYear++;
      } else {
        this.currentMonth++;
      }
      this.loadMonthSchedules();
    },
    
    goToday() {
      const today = new Date();
      this.currentYear = today.getFullYear();
      this.currentMonth = today.getMonth() + 1;
      this.loadMonthSchedules();
    },
    
    onDoctorChange(e) {
      this.selectedDoctorIndex = e.detail.value;
      if (this.selectedDoctorIndex >= 0) {
        this.selectedDoctorId = this.doctorList[this.selectedDoctorIndex].id;
      } else {
        this.selectedDoctorId = null;
      }
      this.loadMonthSchedules();
    }
  }
}
</script>

<style scoped>
.container {
  padding: 10px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.header {
  margin-bottom: 15px;
}

.doctor-picker {
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

.calendar-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px;
  background-color: white;
  border-radius: 8px;
  margin-bottom: 10px;
}

.nav-btn, .today-btn {
  padding: 8px 15px;
  background-color: #409EFF;
  color: white;
  border-radius: 4px;
  font-size: 14px;
}

.current-month {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.calendar {
  background-color: white;
  border-radius: 8px;
  padding: 10px;
}

.weekdays {
  display: flex;
  margin-bottom: 5px;
}

.weekday {
  flex: 1;
  text-align: center;
  padding: 8px 0;
  font-size: 12px;
  color: #666;
  font-weight: bold;
}

.days-grid {
  display: flex;
  flex-wrap: wrap;
}

.day-cell {
  width: 14.28%;
  min-height: 80px;
  border: 1px solid #eee;
  padding: 4px;
  box-sizing: border-box;
}

.day-cell.other-month {
  background-color: #fafafa;
}

.day-cell.other-month .day-number text {
  color: #ccc;
}

.day-cell.today {
  background-color: #e3f2fd;
}

.day-number {
  text-align: center;
  font-size: 12px;
  color: #333;
  margin-bottom: 2px;
}

.day-schedules {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.schedule-badge {
  padding: 2px 4px;
  border-radius: 3px;
  font-size: 10px;
  overflow: hidden;
}

.schedule-text {
  color: white;
  font-size: 9px;
  line-height: 1.2;
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0,0,0,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
}
</style>
