<template>
  <view class="container">
    <view v-if="notifications.length === 0" class="empty">
      <text>暂无消息</text>
    </view>
    <view v-for="note in notifications" :key="note.id" class="note-item" :class="{ unread: !note.is_read }" @click="markRead(note)">
      <view class="note-content">
        <text class="note-text">{{ note.content }}</text>
        <text class="note-time">{{ formatTime(note.created_at) }}</text>
      </view>
      <view class="note-status" v-if="!note.is_read">
        <text class="dot"></text>
      </view>
    </view>
  </view>
</template>

<script>
import { request } from '../../utils/request';

export default {
  data() {
    return {
      notifications: []
    };
  },
  onShow() {
    this.fetchNotifications();
  },
  onPullDownRefresh() {
      this.fetchNotifications().then(() => {
          uni.stopPullDownRefresh();
      });
  },
  methods: {
    async fetchNotifications() {
      try {
        const res = await request({ url: '/notifications/' });
        this.notifications = res;
      } catch (e) {
          console.error(e);
      }
    },
    async markRead(note) {
      if (note.is_read) return;
      try {
        await request({
            url: `/notifications/${note.id}/read`,
            method: 'PUT'
        });
        note.is_read = true;
      } catch (e) {}
    },
    formatTime(t) {
       if (!t) return '';
       const d = new Date(t);
       return `${d.getMonth()+1}-${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2,'0')}`;
    }
  }
}
</script>

<style>
.container { 
    padding: 10px; 
    background-color: #f5f5f5;
    min-height: 100vh;
}
.note-item { 
  background: white; 
  padding: 15px; 
  margin-bottom: 10px; 
  border-radius: 8px; 
  display: flex; 
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.unread { border-left: 4px solid #F56C6C; }
.note-content { flex: 1; }
.note-text { font-size: 15px; color: #333; display: block; margin-bottom: 5px; line-height: 1.4; }
.note-time { font-size: 12px; color: #999; }
.dot { width: 10px; height: 10px; background: #F56C6C; border-radius: 50%; display: block; }
.empty { text-align: center; padding: 40px; color: #999; }
</style>
