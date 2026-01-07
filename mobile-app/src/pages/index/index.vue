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
        <button class="icon-btn" @click="goToNotifications">🔔<text v-if="unreadCount > 0" class="badge">{{unreadCount}}</text></button>
        <button class="logout-btn" @click="handleLogout">退出</button>
      </view>
    </view>

    <!-- Calendar Toolbar (New) -->
    <view class="calendar-toolbar">
        <view class="date-nav">
            <text class="nav-btn" @click="changeDate(-1)"> &lt; </text>
            <text class="current-date">Jan 2026</text>
            <text class="nav-btn" @click="changeDate(1)"> &gt; </text>
        </view>
        <view class="toolbar-right">
             <view class="view-select">Week View ▾</view>
             <view class="overlay-switch" @click="handleOverlayClick">
                 <view class="switch-track" :class="{ 'active': isOverlayOn }">
                     <view class="switch-thumb"></view>
                 </view>
                 <text class="switch-label">Overlay my calendar</text>
             </view>
        </view>
    </view>

    <!-- Navigation Grid -->
    <view class="nav-grid">
         <button class="nav-item" @click="goToDepartmentSchedule">科室排班</button>
         <button class="nav-item" @click="goToTradeList">换班请求</button>
         <button class="nav-item" @click="goToPreferences">意愿申报</button>
         <button class="nav-item" @click="switchLang">{{ $t('common.switchLang') }}</button>
    </view>

    <view class="schedule-list">
      <view v-if="schedules.length === 0" class="empty">
        <text>{{ $t('home.empty') }}</text>
      </view>
      <view v-for="schedule in schedules" :key="schedule.id" class="schedule-item">
        <view class="schedule-time">
            <text class="time-start">{{ schedule.shiftName.includes('夜') ? '17:00' : '08:00' }}</text>
            <text class="time-end">{{ schedule.shiftName.includes('夜') ? '08:00' : '17:00' }}</text>
        </view>
        <view class="schedule-card" :class="schedule.status">
          <view class="card-header">
             <text class="date">{{ schedule.date }}</text>
             <text class="shift-tag">{{ schedule.shiftName }}</text>
          </view>
          <view class="card-actions">
             <text class="status-text">{{ schedule.status }}</text>
             <button class="trade-btn-sm" @click="handleTrade(schedule)">{{ $t('home.tradeBtn') }}</button>
          </view>
        </view>
      </view>
    </view>
    
    <FeedbackBtn />

    <!-- Overlay Connect Modal -->
    <view class="modal-mask" v-if="showConnectModal" @click="showConnectModal = false">
        <view class="modal-content" @click.stop>
            <view class="modal-header">
                <view class="icon-placeholder">☁️</view>
                <text class="close-btn" @click="showConnectModal = false">×</text>
            </view>
            <text class="modal-title">Overlay my calendar</text>
            <text class="modal-desc">Save the trouble of clicking back-and-forth! You can (and only you) will be able to see your events on SavvyCalendar links when you connect your calendar.</text>
            
            <button class="signin-btn google" @click="connectProvider('Google')">
                <text>G</text> Sign in with Google
            </button>
            <button class="signin-btn microsoft" @click="connectProvider('Microsoft')">
                 <text>M</text> Sign in with Microsoft
            </button>
            <button class="signin-btn fastmail" @click="connectProvider('Fastmail')">
                 <text>F</text> Sign in with Fastmail
            </button>
            
            <text class="privacy-note">By connecting your calendar, you accept our privacy notice and terms of use.</text>
        </view>
    </view>

    <!-- Calendar Settings Modal -->
    <view class="modal-mask" v-if="showSettingsModal" @click="showSettingsModal = false">
        <view class="modal-content" @click.stop>
            <view class="modal-header-row">
                <text class="modal-title-sm">Calendar settings</text>
                <text class="close-btn" @click="showSettingsModal = false">×</text>
            </view>
            <view class="settings-body">
                <text class="settings-intro">Choose the calendars we should check for conflicts.</text>
                
                <view class="setting-item">
                     <view class="toggle-row">
                         <switch :checked="showDeclined" @change="showDeclined = !showDeclined" style="transform:scale(0.7)"/>
                         <text>Show declined events</text>
                     </view>
                </view>

                <view class="calendar-account">
                    <view class="account-header">
                        <text>Microsoft Outlook (user@email.com)</text>
                    </view>
                    <view class="calendar-row">
                         <switch checked style="transform:scale(0.7)" color="#007aff"/>
                         <text>Calendar</text>
                    </view>
                    <view class="calendar-row">
                         <switch style="transform:scale(0.7)"/>
                         <text>中国 节假日</text>
                    </view>
                </view>
                
                <view class="add-account-row">
                    <text>+ Add a calendar account</text>
                </view>
            </view>
            <view class="modal-footer">
                <button class="save-btn" @click="saveSettings">Save and close</button>
            </view>
        </view>
    </view>

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
      unreadCount: 0,
      // Calendar Overlay State
      isOverlayOn: false,
      showConnectModal: false,
      showSettingsModal: false,
      showDeclined: false,
      hasConnectedAccount: false
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
    handleOverlayClick() {
        if (!this.hasConnectedAccount) {
            this.showConnectModal = true;
        } else {
            this.showSettingsModal = true;
        }
    },
    connectProvider(provider) {
        uni.showLoading({ title: 'Connecting...' });
        setTimeout(() => {
            uni.hideLoading();
            this.hasConnectedAccount = true;
            this.isOverlayOn = true;
            this.showConnectModal = false;
            this.showSettingsModal = true; // Show settings after connect
        }, 1000);
    },
    saveSettings() {
        this.showSettingsModal = false;
        uni.showToast({ title: 'Settings saved', icon: 'success' });
    },
    changeDate(offset) {
        // Mock Date Change
        uni.showToast({ title: 'Date changed', icon: 'none' });
    },
    // ... Existing methods ...
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
        const response = await request({ url: '/users/me', method: 'GET' });
        this.currentUser = response;
      } catch (error) {}
    },
    async fetchShiftTypes() {
      try {
        const response = await request({ url: '/shift-types/', method: 'GET' });
        this.shiftTypes = response;
      } catch (error) {}
    },
    async fetchDepartments() {
      try {
        const response = await request({ url: '/departments/', method: 'GET' });
        this.departments = response;
      } catch (error) {}
    },
    getDepartmentName(departmentId) {
      if (!departmentId) return '未分配科室';
      const dept = this.departments.find(d => d.id === departmentId);
      return dept ? dept.name : '未知科室';
    },
    async fetchSchedules() {
      try {
        if (this.shiftTypes.length === 0) await this.fetchShiftTypes();
        const userRes = await request({ url: '/users/me' });
        const data = await request({ url: '/schedules/?doctor_id=' + userRes.id, method: 'GET' });
        this.schedules = data.map(s => ({
          ...s,
          shiftName: this.getShiftName(s.shift_type_id),
          status: s.status || 'draft'
        }));
      } catch (e) {
        console.error('获取排班失败:', e);
      }
    },
    getShiftName(shiftTypeId) {
      if (!this.shiftTypes || this.shiftTypes.length === 0) return '未知班次';
      const shiftType = this.shiftTypes.find(st => st.id == shiftTypeId);
      return shiftType ? shiftType.name : '未知班次';
    },
    handleTrade(schedule) {
      uni.navigateTo({
        url: `/pages/trade/create?shiftId=${schedule.id}&date=${schedule.date}&shiftName=${this.getShiftName(schedule.shift_type_id)}`
      });
    },
    goToTradeList() { uni.navigateTo({ url: '/pages/trade/list' }); },
    goToPreferences() { uni.navigateTo({ url: '/pages/preference/index' }); },
    goToDepartmentSchedule() { uni.navigateTo({ url: '/pages/department/schedule' }); },
    handleLogout() {
      uni.showModal({
        title: '确认退出',
        content: '确定要退出登录吗？',
        success: (res) => {
          if (res.confirm) {
            uni.removeStorageSync('token');
            uni.reLaunch({ url: '/pages/login/login' });
          }
        }
      });
    }
  }
}
</script>

<style>
.container {
  padding: 15px;
  background-color: #f8f9fa;
  min-height: 100vh;
}
.header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;
}
.title { font-size: 20px; font-weight: bold; color: #333; }
.user-info { display: flex; flex-direction: column; }
.user-name { font-size: 16px; font-weight: 500; }
.user-dept { font-size: 12px; color: #666; }
.header-buttons { display: flex; gap: 8px; }
.icon-btn { background: none; border: none; font-size: 20px; padding: 0 5px; position: relative; }
.badge { position: absolute; top: 0; right: 0; background: red; color: white; border-radius: 50%; width: 14px; height: 14px; font-size: 9px; display: flex; align-items: center; justify-content: center; }
.logout-btn { background-color: #f5f5f5; color: #666; font-size: 12px; padding: 4px 10px; border-radius: 12px; }

/* Calendar Toolbar */
.calendar-toolbar {
    background: white; padding: 12px; border-radius: 12px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.date-nav { display: flex; align-items: center; gap: 10px; font-weight: bold; font-size: 16px; }
.nav-btn { color: #666; padding: 0 5px; }
.toolbar-right { display: flex; gap: 10px; align-items: center; }
.view-select { background-color: #f0f0f0; padding: 4px 10px; border-radius: 6px; font-size: 12px; color: #333; }
.overlay-switch { display: flex; align-items: center; gap: 6px; cursor: pointer; }
.switch-track { width: 36px; height: 20px; background-color: #ddd; border-radius: 10px; position: relative; transition: 0.3s; }
.switch-track.active { background-color: #007aff; }
.switch-thumb { width: 16px; height: 16px; background-color: white; border-radius: 50%; position: absolute; top: 2px; left: 2px; transition: 0.3s; }
.switch-track.active .switch-thumb { left: 18px; }
.switch-label { font-size: 12px; color: #333; font-weight: 500; }

/* Nav Grid (Quick Actions) */
.nav-grid { display: flex; gap: 8px; margin-bottom: 15px; overflow-x: auto; padding-bottom: 5px; }
.nav-item { flex: 1; white-space: nowrap; background: white; border: 1px solid #eee; font-size: 12px; padding: 8px; border-radius: 8px; text-align: center; color: #555; box-shadow: 0 1px 2px rgba(0,0,0,0.03); }

/* Schedule List */
.schedule-item { display: flex; gap: 15px; margin-bottom: 15px; }
.schedule-time { display: flex; flex-direction: column; font-size: 12px; color: #888; width: 40px; text-align: right; padding-top: 5px; }
.schedule-card { flex: 1; background: white; border-radius: 8px; padding: 12px; border-left: 4px solid #007aff; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.schedule-card.draft { border-left-color: #909399; }
.schedule-card.published { border-left-color: #67C23A; }
.card-header { display: flex; justify-content: space-between; margin-bottom: 8px; }
.date { font-weight: bold; color: #333; }
.shift-tag { background: #f0f7ff; color: #007aff; padding: 2px 6px; border-radius: 4px; font-size: 11px; }
.card-actions { display: flex; justify-content: space-between; align-items: center; }
.status-text { font-size: 11px; color: #999; }
.trade-btn-sm { background: #007aff; color: white; font-size: 11px; padding: 4px 10px; border-radius: 12px; margin: 0; line-height: 1.5; }

/* Modals */
.modal-mask { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); z-index: 999; display: flex; justify-content: center; align-items: center; }
.modal-content { width: 85%; background: white; border-radius: 16px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
.modal-header { display: flex; flex-direction: column; align-items: center; margin-bottom: 15px; position: relative; }
.modal-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.close-btn { position: absolute; right: 0; top: 0; font-size: 24px; color: #999; padding: 5px; }
.modal-header-row .close-btn { position: static; }
.icon-placeholder { font-size: 40px; margin-bottom: 10px; }
.modal-title { font-size: 20px; font-weight: bold; margin-bottom: 10px; text-align: center; }
.modal-title-sm { font-size: 18px; font-weight: bold; }
.modal-desc { font-size: 13px; color: #666; text-align: center; margin-bottom: 20px; line-height: 1.5; }
.signin-btn { display: flex; align-items: center; justify-content: center; background: white; border: 1px solid #ddd; border-radius: 25px; padding: 10px; margin-bottom: 10px; font-size: 14px; color: #333; gap: 10px; }
.privacy-note { font-size: 11px; color: #999; text-align: center; display: block; margin-top: 10px; }
.settings-body { max-height: 300px; overflow-y: auto; }
.settings-intro { font-size: 13px; color: #666; margin-bottom: 15px; display: block; }
.setting-item { margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid #eee; }
.toggle-row { display: flex; align-items: center; gap: 10px; font-size: 14px; }
.calendar-account { margin-top: 10px; }
.account-header { font-size: 13px; font-weight: bold; margin-bottom: 10px; }
.calendar-row { display: flex; align-items: center; gap: 10px; font-size: 13px; margin-bottom: 8px; color: #555; }
.add-account-row { color: #007aff; font-size: 13px; margin-top: 15px; cursor: pointer; }
.save-btn { background: #007aff; color: white; width: 100%; border-radius: 25px; padding: 10px; font-size: 14px; margin-top: 10px; }
</style>
