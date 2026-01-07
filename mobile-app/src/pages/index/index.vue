<template>
  <view class="container">
    <view class="header">
      <view class="user-info">
        <text class="title">{{ $t('home.title') }}</text>
        <view v-if="currentUser" class="user-details">
          <text class="user-name">{{ currentUser.full_name }}</text>
          <text class="user-dept">{{ getDepartmentName(currentUser.department_id) }}</text>
        </view>
      </view>
      <view class="header-buttons">
        <button class="notif-btn" @click="goToNotifications">消息<text v-if="unreadCount > 0">({{unreadCount}})</text></button>
        <button class="dept-schedule-btn" @click="goToDepartmentSchedule">科室排班</button>
        <button class="trade-list-btn" @click="goToTradeList">换班请求</button>
        <button class="pref-btn" @click="goToPreferences">意愿申报</button>
        <button class="logout-btn" @click="switchLang">{{ $t('common.switchLang') }}</button>
        <button class="logout-btn" @click="handleLogout">退出</button>
      </view>
    </view>
    <view class="schedule-list">
      <view v-if="schedules.length === 0" class="empty">
        <text>{{ $t('home.empty') }}</text>
      </view>
      <view v-for="schedule in schedules" :key="schedule.id" class="schedule-item">
        <view class="schedule-info">
          <text class="date">{{ schedule.date }} - {{ schedule.shiftName }}, {{ schedule.status }}</text>
        </view>
        <button class="trade-btn" @click="handleTrade(schedule)">{{ $t('home.tradeBtn') }}</button>
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
      schedules: [],
      currentUser: null,
      shiftTypes: [],
      departments: [],
      unreadCount: 0
    };
  },
  onShow() {
    this.fetchUnreadCount();
  },
  onLoad() {
    this.fetchDepartments();
    this.fetchCurrentUser();
    this.fetchShiftTypes();
    this.fetchSchedules();
  },
  methods: {
    switchLang() {
        const current = this.$i18n.locale;
        this.$i18n.locale = current === 'zh' ? 'en' : 'zh';
    },
    async fetchUnreadCount() {
        try {
            const res = await request({ url: '/notifications/unread-count' });
            this.unreadCount = res.count;
        } catch(e) {}
    },
    goToNotifications() {
        uni.navigateTo({ url: '/pages/notifications/list' });
    },
    async fetchCurrentUser() {
      try {
        const response = await request({
          url: '/users/me',
          method: 'GET'
        });
        this.currentUser = response;
        console.log('当前用户:', this.currentUser);
      } catch (error) {
        console.error('获取当前用户失败:', error);
      }
    },
    async fetchShiftTypes() {
      try {
        const response = await request({
          url: '/shift-types/',
          method: 'GET'
        });
        this.shiftTypes = response;
        console.log('班次类型:', this.shiftTypes);
      } catch (error) {
        console.error('获取班次类型失败:', error);
      }
    },
    async fetchDepartments() {
      try {
        const response = await request({
          url: '/departments/',
          method: 'GET'
        });
        this.departments = response;
      } catch (error) {
        console.error('获取科室列表失败:', error);
      }
    },
    getDepartmentName(departmentId) {
      if (!departmentId) return '未分配科室';
      const dept = this.departments.find(d => d.id === departmentId);
      return dept ? dept.name : '未知科室';
    },
    async fetchSchedules() {
      try {
        // Ensure shift types are loaded first
        if (this.shiftTypes.length === 0) {
          await this.fetchShiftTypes();
        }

        const userRes = await request({ url: '/users/me' });
        const myId = userRes.id;
        
        const data = await request({
          url: '/schedules/?doctor_id=' + myId,
          method: 'GET'
        });
        
        // Enrich data
        this.schedules = data.map(s => ({
          ...s,
          shiftName: this.getShiftName(s.shift_type_id),
          status: s.status || 'draft'
        }));
      } catch (e) {
        console.error('获取排班失败:', e);
        uni.showToast({ title: '获取排班失败', icon: 'none' });
      }
    },
    getShiftName(shiftTypeId) {
      if (!this.shiftTypes || this.shiftTypes.length === 0) return '未知班次';
      // Use loose equality for safety
      const shiftType = this.shiftTypes.find(st => st.id == shiftTypeId);
      return shiftType ? shiftType.name : '未知班次';
    },
    handleTrade(schedule) {
      uni.navigateTo({
        url: `/pages/trade/create?shiftId=${schedule.id}&date=${schedule.date}&shiftName=${this.getShiftName(schedule.shift_type_id)}`
      });
    },
    goToTradeList() {
      uni.navigateTo({
        url: '/pages/trade/list'
      });
    },
    goToPreferences() {
      uni.navigateTo({
        url: '/pages/preference/index'
      });
    },
    goToDepartmentSchedule() {
      uni.navigateTo({
        url: '/pages/department/schedule'
      });
    },
    handleLogout() {
      uni.showModal({
        title: '确认退出',
        content: '确定要退出登录吗？',
        success: (res) => {
          if (res.confirm) {
            // 清除token
            uni.removeStorageSync('token');
            // 跳转到登录页
            uni.reLaunch({
              url: '/pages/login/login'
            });
          }
        }
      });
    }
  }
}
</script>

<style>
.container {
  padding: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}
.user-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.title {
  font-size: 24px;
  font-weight: bold;
}
.user-details {
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.user-name {
  font-size: 16px;
  color: #333;
  font-weight: 500;
}
.user-dept {
  font-size: 14px;
  color: #666;
}
.header-buttons {
  display: flex;
  gap: 10px;
}
.notif-btn {
  background-color: #409EFF;
  color: white;
  padding: 8px 12px;
  font-size: 13px;
  border-radius: 4px;
}
.dept-schedule-btn {
  background-color: #67C23A;
  color: white;
  padding: 8px 12px;
  font-size: 13px;
  border-radius: 4px;
}
.trade-list-btn {
  background-color: #28a745;
  color: white;
  padding: 8px 15px;
  font-size: 14px;
  border-radius: 4px;
}
.pref-btn {
  background-color: #E6A23C;
  color: white;
  padding: 8px 12px;
  font-size: 13px;
  border-radius: 4px;
}
.logout-btn {
  background-color: #f56c6c;
  color: white;
  padding: 8px 15px;
  font-size: 14px;
  border-radius: 4px;
}
.empty {
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
  background-color: #f5f5f5;
  border-radius: 8px;
}
.schedule-info {
  flex: 1;
}
.date {
  font-size: 16px;
}
.trade-btn {
  background-color: #007aff;
  color: white;
  padding: 8px 20px;
  border-radius: 4px;
  font-size: 14px;
}
</style>
