<template>
  <view class="container">
    <view class="header">
      <text class="title">医生排班系统</text>
    </view>
    <view class="form">
      <input class="input" v-model="username" placeholder="用户名" value="hjz" />
      <input class="input" v-model="password" password placeholder="密码" value="hjz123" />
      <button class="btn" @click="handleLogin">登录</button>
    </view>
    <view class="debug">
      <text class="debug-title">调试信息:</text>
      <text class="debug-text">{{ debugInfo }}</text>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      username: 'hjz',
      password: 'hjz123',
      debugInfo: '等待登录...'
    }
  },
  methods: {
    async handleLogin() {
      if (!this.username || !this.password) {
        this.debugInfo = '错误: 用户名或密码为空';
        uni.showToast({ title: '请输入用户名和密码', icon: 'none' });
        return;
      }
      
      this.debugInfo = '正在登录...';
      
      try {
        // 手动构造 URL 编码的数据
        const formData = `username=${encodeURIComponent(this.username)}&password=${encodeURIComponent(this.password)}`;
        const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';
        const requestUrl = BASE_URL + '/token';
        
        console.log('=== 登录调试 ===');
        console.log('用户名:', this.username);
        console.log('密码:', this.password);
        console.log('表单数据:', formData);
        console.log('请求URL:', requestUrl);
        
        uni.request({
            url: requestUrl,
            method: 'POST',
            timeout: 100000, // 增加超时时间至 100s 以应对 Render 冷启动
            header: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data: formData,
            success: (res) => {
                console.log('=== 登录响应 ===');
                console.log('状态码:', res.statusCode);
                console.log('响应数据:', res.data);
                console.log('响应头:', res.header);
                
                this.debugInfo = `状态码: ${res.statusCode}\n响应: ${JSON.stringify(res.data, null, 2)}`;
                
                if (res.statusCode === 200 && res.data && res.data.access_token) {
                    console.log('登录成功，Token:', res.data.access_token);
                    uni.setStorageSync('token', res.data.access_token);
                    this.debugInfo = '登录成功！即将跳转...';
                    uni.showToast({ title: '登录成功', icon: 'success' });
                    setTimeout(() => {
                        uni.reLaunch({ url: '/pages/index/index' });
                    }, 1500);
                } else {
                    const errorMsg = (res.data && res.data.detail) || '登录失败';
                    console.error('登录失败:', errorMsg);
                    this.debugInfo = `失败: ${res.statusCode}\n${errorMsg}`;
                    uni.showToast({ title: errorMsg, icon: 'none', duration: 3000 });
                }
            },
            fail: (err) => {
                console.error('=== 请求失败 ===');
                console.error('错误对象:', err);
                this.debugInfo = `请求失败:\n${JSON.stringify(err, null, 2)}`;
                uni.showToast({ title: '网络错误', icon: 'none', duration: 3000 });
            }
        });
      } catch (e) {
        console.error('=== 异常 ===');
        console.error('异常对象:', e);
        this.debugInfo = `异常: ${e.message}\n${e.stack}`;
        uni.showToast({ title: '登录异常', icon: 'none' });
      }
    }
  }
}
</script>

<style>
.container {
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 100vh;
}
.header {
  margin-bottom: 30px;
  text-align: center;
}
.title {
  font-size: 24px;
  font-weight: bold;
}
.input {
  border: 1px solid #ccc;
  padding: 10px;
  margin-bottom: 15px;
  border-radius: 4px;
}
.btn {
  background-color: #007aff;
  color: white;
  margin-bottom: 10px;
}
.debug {
  margin-top: 30px;
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 4px;
  max-height: 400px;
  overflow-y: auto;
}
.debug-title {
  font-weight: bold;
  display: block;
  margin-bottom: 10px;
  color: #333;
}
.debug-text {
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: monospace;
  color: #666;
}
</style>
