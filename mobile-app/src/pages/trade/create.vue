<template>
  <view class="container">
    <view class="shift-info">
      <text class="label">排班信息</text>
      <text class="value">{{ shiftDate }} - {{ shiftName }}</text>
    </view>

    <view class="form-section">
      <text class="label">选择医生</text>
      <picker @change="onDoctorChange" :range="doctors" range-key="full_name" :value="selectedIndex">
        <view class="picker">
          <text>{{ selectedDoctor ? selectedDoctor.full_name : '请选择目标医生' }}</text>
          <text class="arrow">›</text>
        </view>
      </picker>
    </view>

    <view class="form-section">
      <text class="label">换班原因</text>
      <textarea 
        v-model="reason" 
        class="textarea" 
        placeholder="请输入换班原因（选填）"
        maxlength="200"
      />
      <text class="char-count">{{ reason.length }}/200</text>
    </view>

    <button class="submit-btn" @click="handleSubmit" :disabled="!selectedDoctor || submitting">
      {{ submitting ? '提交中...' : '提交换班请求' }}
    </button>
  </view>
</template>

<script>
import { request } from '../../utils/request';

export default {
  data() {
    return {
      shiftId: 0,
      shiftDate: '',
      shiftName: '',
      doctors: [],
      selectedIndex: 0,
      selectedDoctor: null,
      reason: '',
      submitting: false
    }
  },
  onLoad(options) {
    this.shiftId = parseInt(options.shiftId);
    this.shiftDate = options.date;
    this.shiftName = options.shiftName;
    this.fetchDoctors();
  },
  methods: {
    async fetchDoctors() {
      try {
        console.log('开始获取医生列表...');
        const data = await request({ url: '/users/' });
        console.log('获取到用户数据:', data);
        
        // 获取当前用户信息
        const me = await request({ url: '/users/me' });
        console.log('当前用户:', me);
        
        // 过滤掉自己和非医生用户
        this.doctors = data.filter(u => {
          const isNotMe = u.id !== me.id;
          const isDoctor = u.role === 'doctor';
          console.log(`用户 ${u.full_name}: isNotMe=${isNotMe}, isDoctor=${isDoctor}`);
          return isNotMe && isDoctor;
        });
        
        console.log('过滤后的医生列表:', this.doctors);
        
        if (this.doctors.length === 0) {
          uni.showToast({ title: '没有可选择的医生', icon: 'none' });
        }
      } catch (e) {
        console.error('获取医生列表失败:', e);
        uni.showToast({ title: '获取医生列表失败: ' + (e.message || JSON.stringify(e)), icon: 'none', duration: 3000 });
      }
    },
    onDoctorChange(e) {
      this.selectedIndex = e.detail.value;
      this.selectedDoctor = this.doctors[e.detail.value];
    },
    async handleSubmit() {
      if (!this.selectedDoctor) {
        uni.showToast({
          title: '请选择目标医生',
          icon: 'none'
        });
        return;
      }
      
      this.submitting = true;
      try {
        const requestData = {
          request_shift_id: parseInt(this.shiftId),
          target_doctor_id: this.selectedDoctor.id, // Changed from this.selectedDoctor to this.selectedDoctor.id
          reason: this.reason || '换班申请'
        };
        
        console.log('提交换班请求:', requestData);
        
        const response = await request({
          url: '/trades/',
          method: 'POST',
          data: requestData
        });
        
        console.log('换班请求创建成功:', response);
        
        uni.showToast({
          title: '换班请求已发送',
          icon: 'success'
        });
        
        setTimeout(() => {
          uni.navigateBack();
        }, 1500);
        
      } catch (error) {
        console.error('发送换班请求失败:', error);
        uni.showToast({
          title: '发送失败',
          icon: 'none'
        });
      } finally {
        this.submitting = false;
      }
    }
  }
}
</script>

<style>
.container {
  padding: 20px;
}
.shift-info {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}
.form-section {
  margin-bottom: 20px;
}
.label {
  display: block;
  font-size: 14px;
  color: #333;
  margin-bottom: 10px;
  font-weight: bold;
}
.value {
  font-size: 16px;
  color: #666;
}
.picker {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
}
.arrow {
  font-size: 20px;
  color: #999;
}
.textarea {
  width: 100%;
  min-height: 100px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}
.char-count {
  display: block;
  text-align: right;
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}
.submit-btn {
  background-color: #007aff;
  color: white;
  width: 100%;
  margin-top: 30px;
}
.submit-btn[disabled] {
  background-color: #ccc;
}
</style>
