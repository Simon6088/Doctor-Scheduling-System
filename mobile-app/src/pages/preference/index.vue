<template>
  <view class="container">
    <view class="header">
      <view class="title">我的意愿申报</view>
      <button type="primary" size="mini" @click="showAddPopup">添加意愿</button>
    </view>
    
    <!-- Main Calendar View -->
    <view class="main-calendar card">
        <view class="calendar-header">
            <text class="arrow" @click="changeViewDate(-1)"> &lt; </text>
            <text class="current-date-label">{{ mainDateLabel }}</text>
            <text class="arrow" @click="changeViewDate(1)"> &gt; </text>
        </view>
        <view class="week-header">
            <text v-for="d in ['周日','周一','周二','周三','周四','周五','周六']" :key="d" class="week-cell header-cell">{{d}}</text>
        </view>
        <view class="calendar-body">
            <view class="calendar-row" v-for="(week, wIndex) in mainCalendarWeeks" :key="wIndex">
                <view class="week-cell day-cell main-day-cell" 
                      v-for="(day, dIndex) in week" 
                      :key="dIndex" 
                      :class="{ 'other-month': day.otherMonth, 'is-today': day.isToday }"
                      @click="handleDayClick(day)">
                     <text class="day-num">{{ day.dayNum }}</text>
                     <view v-if="getPref(day)" class="pref-badge" :class="getPref(day).type">
                        {{ getPref(day).type === 'avoid' ? '休' : '班' }}
                     </view>
                </view>
            </view>
        </view>
    </view>

    <!-- Popup for Adding -->
    <view v-if="showPopup" class="popup-mask">
       <view class="popup-content">
          
          <!-- Mode Toggle: Week Left, Month Right -->
          <view class="toggle-container">
             <view class="toggle-btn" :class="{active: mode==='week'}" @click="setMode('week')">week</view>
             <view class="toggle-btn" :class="{active: mode==='month'}" @click="setMode('month')">month</view>
          </view>

          <!-- Popup Calendar View (Date Selection) -->
          <view class="calendar-container">
              <view class="calendar-header">
                  <text class="arrow" @click="changeDate(-1)"> &lt; </text>
                  <text class="current-date-label">{{ currentDateLabel }}</text>
                  <text class="arrow" @click="changeDate(1)"> &gt; </text>
              </view>
              <view class="week-header">
                  <text v-for="d in ['周日','周一','周二','周三','周四','周五','周六']" :key="d" class="week-cell header-cell">{{d}}</text>
              </view>
              <view class="calendar-body">
                  <view class="calendar-row" v-for="(week, wIndex) in calendarWeeks" :key="wIndex">
                      <view class="week-cell day-cell" 
                            v-for="(day, dIndex) in week" 
                            :key="dIndex" 
                            :class="{ 
                                'other-month': day.otherMonth, 
                                'is-today': day.isToday,
                                'is-selected': isSelected(day)
                            }"
                            @click="toggleDaySelection(day)">
                           <text>{{ day.dayNum }}日</text>
                      </view>
                  </view>
              </view>
          </view>
          
          <view class="form-item mt-10">
             <text class="label">包含星期</text>
             <checkbox-group @change="onWeekDayChange" class="weekday-group">
                <label v-for="(day, index) in weekDays" :key="index" class="weekday-label">
                    <checkbox :value="String(day.value)" :checked="selectedWeekDays.includes(String(day.value))" style="transform:scale(0.7)"/>
                    <text>{{ day.text }}</text>
                </label>
             </checkbox-group>
          </view>
          
          <view class="form-item">
             <text class="label">类型</text>
             <radio-group @change="onTypeChange" class="radio-group">
                <label class="radio-label"><radio value="desire" :checked="form.type==='desire'"/>希望排班</label>
                <label class="radio-label"><radio value="avoid" :checked="form.type==='avoid'"/>不希望排班</label>
             </radio-group>
          </view>

          <view class="form-item">
             <text class="label">原因</text>
             <view class="input-wrapper">
                 <input class="input" :value="form.reason" @input="onReasonInput" placeholder="请输入原因（可选）" />
                 <view class="mic-icon" @click="startVoiceInput">🎤</view>
             </view>
          </view>
          
          <view class="popup-actions">
             <button size="mini" @click="showPopup = false">取消</button>
             <button size="mini" type="primary" @click="submitPreference">提交</button>
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
            preferences: [],
            viewDate: new Date(), // Main calendar
            
            showPopup: false,
            mode: 'week', // Popup mode
            displayDate: new Date(), // Popup calendar
            form: {
                type: 'avoid',
                reason: ''
            },
            weekDays: [
                { text: '一', value: 1 },
                { text: '二', value: 2 },
                { text: '三', value: 3 },
                { text: '四', value: 4 },
                { text: '五', value: 5 },
                { text: '六', value: 6 },
                { text: '日', value: 0 },
            ],
            selectedWeekDays: ['1', '2', '3', '4', '5', '6', '0']
        };
    },
    computed: {
        mainDateLabel() {
            const y = this.viewDate.getFullYear();
            const m = this.viewDate.getMonth() + 1;
            return `${y}年 ${m}月`;
        },
        currentDateLabel() {
            const y = this.displayDate.getFullYear();
            const m = this.displayDate.getMonth() + 1;
            return `${y}年 ${m}月`;
        },
        // Reused logic function (would be better in mixin but copying for speed)
        mainCalendarWeeks() {
            return this.generateWeeks(this.viewDate, 'month');
        },
        calendarWeeks() {
            return this.generateWeeks(this.displayDate, this.mode);
        }
    },
    onShow() {
        this.fetchPreferences();
    },
    methods: {
        generateWeeks(baseDate, mode) {
            const y = baseDate.getFullYear();
            const m = baseDate.getMonth();
            const firstDayOfMonth = new Date(y, m, 1);
            const startDay = new Date(firstDayOfMonth);
            startDay.setDate(1 - startDay.getDay()); 
            
            const weeks = [];
            const today = new Date();
            let current = new Date(startDay);
            
            for(let i=0; i<6; i++) {
                const week = [];
                for(let j=0; j<7; j++) {
                    const d = new Date(current);
                    week.push({
                        dateObj: d,
                        dayNum: d.getDate(),
                        otherMonth: d.getMonth() !== m,
                        isToday: d.toDateString() === today.toDateString()
                    });
                    current.setDate(current.getDate() + 1);
                }
                weeks.push(week);
            }
            
            if (mode === 'month') {
                return weeks;
            } else {
                const targetSunday = new Date(baseDate);
                targetSunday.setDate(targetSunday.getDate() - targetSunday.getDay());
                const found = weeks.find(w => w[0].dateObj.toDateString() === targetSunday.toDateString());
                return found ? [found] : weeks.slice(0, 1); 
            }
        },
        async fetchPreferences() {
            try {
                this.preferences = await request({ url: '/preferences/me' });
            } catch (e) {
                console.error(e);
                uni.showToast({ title: '加载失败', icon: 'none' });
            }
        },
        changeViewDate(step) {
             this.viewDate = new Date(this.viewDate.setMonth(this.viewDate.getMonth() + step));
        },
        showAddPopup() {
            this.mode = 'week'; 
            this.displayDate = new Date();
            this.form.type = 'avoid';
            this.form.reason = '';
            this.selectedWeekDays = ['1', '2', '3', '4', '5', '6', '0']; 
            this.showPopup = true;
        },
        setMode(m) {
            this.mode = m;
            this.displayDate = new Date(); 
        },
        changeDate(step) {
            if (this.mode === 'month') {
                this.displayDate = new Date(this.displayDate.setMonth(this.displayDate.getMonth() + step));
            } else {
                this.displayDate = new Date(this.displayDate.setDate(this.displayDate.getDate() + step * 7));
            }
        },
        formatDate(date) {
            const y = date.getFullYear();
            const m = String(date.getMonth() + 1).padStart(2, '0');
            const d = String(date.getDate()).padStart(2, '0');
            return `${y}-${m}-${d}`;
        },
        getPref(day) {
            const dateStr = this.formatDate(day.dateObj);
            return this.preferences.find(p => p.date === dateStr);
        },
        handleDayClick(day) {
            const pref = this.getPref(day);
            if (pref) {
                 uni.showModal({
                     title: '意愿详情',
                     content: `日期: ${pref.date}\n类型: ${pref.type==='avoid'?'不希望排班':'希望排班'}\n原因: ${pref.reason||'无'}`,
                     confirmText: '删除',
                     cancelText: '关闭',
                     success: (res) => {
                         if (res.confirm) this.handleDelete(pref.id);
                     }
                 });
            } else {
                // Optional: Click empty cell to add single day preference?
                // For now, adhere to requirement to keep "Add Preference" button pattern.
            }
        },
        onTypeChange(e) {
            this.form.type = e.detail.value;
        },
        onWeekDayChange(e) {
            this.selectedWeekDays = e.detail.value;
        },
        onReasonInput(e) {
            this.form.reason = e.detail.value;
        },
        isSelected(day) {
            return this.selectedWeekDays.includes(String(day.dateObj.getDay()));
        },
        toggleDaySelection(day) {
            const weekday = String(day.dateObj.getDay());
            const index = this.selectedWeekDays.indexOf(weekday);
            if (index >= 0) {
                this.selectedWeekDays = this.selectedWeekDays.filter(d => d !== weekday); 
            } else {
                this.selectedWeekDays = [...this.selectedWeekDays, weekday];
            }
        },
        startVoiceInput() {
            if ('webkitSpeechRecognition' in window) {
                const recognition = new webkitSpeechRecognition();
                recognition.lang = 'zh-CN';
                recognition.onresult = (event) => {
                    this.form.reason = event.results[0][0].transcript;
                };
                recognition.start();
                uni.showToast({title: '正在听...', icon: 'none'});
            } else {
                uni.showToast({title: '当前浏览器不支持语音输入', icon: 'none'});
            }
        },
        async submitPreference() {
            if (this.selectedWeekDays.length === 0) {
                 uni.showToast({title: '请至少选择一个星期', icon: 'none'});
                 return;
            }

            let datesToSubmit = [];
            // Use displayDate context
            if (this.mode === 'month') {
                const y = this.displayDate.getFullYear();
                const m = this.displayDate.getMonth(); 
                const daysInMonth = new Date(y, m + 1, 0).getDate();
                for (let d = 1; d <= daysInMonth; d++) {
                    const current = new Date(y, m, d);
                    if (this.selectedWeekDays.includes(String(current.getDay()))) {
                        datesToSubmit.push(this.formatDate(current));
                    }
                }
            } else {
                // Week mode
                const weekDays = this.generateWeeks(this.displayDate, 'week')[0]; // Quick reuse
                for (const day of weekDays) {
                    if (this.selectedWeekDays.includes(String(day.dateObj.getDay()))) {
                        datesToSubmit.push(this.formatDate(day.dateObj));
                    }
                }
            }
            
            if (datesToSubmit.length === 0) {
                 uni.showToast({title: '未生成有效日期', icon: 'none'});
                 return;
            }

            uni.showLoading({ title: '提交中' });
            try {
                const chunks = [];
                for (const d of datesToSubmit) {
                    chunks.push(request({ url: '/preferences/', method: 'POST', data: { date: d, type: this.form.type, reason: this.form.reason } }).catch(e => null));
                }
                await Promise.all(chunks);
                uni.hideLoading();
                uni.showToast({ title: '提交成功' });
                this.showPopup = false;
                this.fetchPreferences();
            } catch (e) {
                uni.hideLoading();
                uni.showToast({ title: '提交异常', icon: 'none' });
            }
        },
        async handleDelete(id) {
            try {
                await uni.showModal({ title: '确认删除?', content: '删除后无法恢复' });
                await request({ url: `/preferences/${id}`, method: 'DELETE' });
                uni.showToast({ title: '已删除' });
                this.fetchPreferences();
            } catch (e) { }
        }
    }
}
</script>

<style>
.container { padding: 20px; background-color: #f8f8f8; min-height: 100vh; }
.header { margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
.title { font-size: 18px; font-weight: bold; }
.card { background: #fff; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); overflow: hidden; }

/* Calendar Styles */
.calendar-container, .main-calendar { border: 1px solid #eee; border-radius: 4px; overflow: hidden; background: #fff; }
.calendar-header { display: flex; justify-content: space-between; align-items: center; padding: 10px; background: #f5f5f5; border-bottom: 1px solid #eee; }
.arrow { font-size: 18px; padding: 0 10px; color: #666; font-weight: bold; }
.current-date-label { font-weight: bold; font-size: 16px; }
.week-header { display: flex; border-bottom: 1px solid #eee; background: #fafafa; }
.week-cell { flex: 1; text-align: center; padding: 8px 0; font-size: 14px; border-right: 1px solid #eee; }
.week-cell:last-child { border-right: none; }
.header-cell { font-weight: bold; color: #333; }

.calendar-row { display: flex; border-bottom: 1px solid #eee; }
.calendar-row:last-child { border-bottom: none; }
.day-cell { flex: 1; height: 50px; display: flex; align-items: center; justify-content: center; font-size: 14px; color: #333; border-right: 1px solid #eee; background: #fff; position: relative; }
.day-cell:last-child { border-right: none; }
.other-month { color: #ccc; background: #fcfcfc; }
.is-today { background-color: #fdfdfd; font-weight: bold; } /* Removed blue bg for today to avoid clash with selection */
.is-selected { background-color: #e6f7ff !important; }

/* Main Calendar Specific */
.main-day-cell { height: 60px; flex-direction: column; justify-content: flex-start; padding-top: 5px; }
.pref-badge { font-size: 10px; padding: 2px 4px; border-radius: 4px; margin-top: 2px; }
.pref-badge.avoid { background: #fff1f0; color: #ff4d4f; border: 1px solid #ffa39e; }
.pref-badge.desire { background: #f6ffed; color: #52c41a; border: 1px solid #b7eb8f; }

/* Popup Styles */
.popup-mask { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 999; }
.popup-content { background: #fff; padding: 20px; width: 90%; border-radius: 12px; max-height: 85vh; overflow-y: auto; }
.form-item { margin-bottom: 15px; }
.mt-10 { margin-top: 10px; }
.label { display: block; margin-bottom: 8px; font-weight: bold; color: #333; }
.input-wrapper { display: flex; align-items: center; gap: 10px; }
.input { padding: 10px; background: #f5f5f5; border-radius: 6px; border: 1px solid #eaeaea; flex: 1; box-sizing: border-box; }
.mic-icon { font-size: 24px; padding: 5px; cursor: pointer; }
.radio-group { display: flex; gap: 20px; }
.radio-label { display: flex; align-items: center; }
.popup-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }

.toggle-container { display: flex; background-color: #333; border-radius: 8px; overflow: hidden; margin-bottom: 15px; }
.toggle-btn { flex: 1; text-align: center; padding: 8px; color: #fff; font-size: 14px; background: #333; }
.toggle-btn.active { background-color: #2c3e50; font-weight: bold; }

.weekday-group { display: flex; flex-wrap: wrap; gap: 10px; }
.weekday-label { display: flex; align-items: center; font-size: 14px; }
</style>
