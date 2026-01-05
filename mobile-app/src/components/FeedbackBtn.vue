<template>
  <view>
    <view class="feedback-fab" @click="showPopup = true">
      <text class="fab-icon">📝</text>
    </view>

    <view v-if="showPopup" class="popup-mask" @click="closePopup">
      <view class="popup-content" @click.stop="">
        <text class="popup-title">意见反馈</text>
        
        <view class="form-item">
           <text class="label">类型</text>
           <radio-group @change="onTypeChange" class="rg">
               <label class="radio-label"><radio value="review" :checked="formData.type==='review'"/>评价</label>
               <label class="radio-label"><radio value="bug" :checked="formData.type==='bug'"/>Bug</label>
               <label class="radio-label"><radio value="suggestion" :checked="formData.type==='suggestion'"/>建议</label>
           </radio-group>
        </view>

        <view class="form-item">
           <text class="label">紧急程度</text>
           <view class="urgency-opts">
               <view class="u-tag" :class="{active: formData.urgency==='low'}" @click="formData.urgency='low'">低</view>
               <view class="u-tag" :class="{active: formData.urgency==='medium'}" @click="formData.urgency='medium'">中</view>
               <view class="u-tag" :class="{active: formData.urgency==='high'}" @click="formData.urgency='high'">高</view>
           </view>
        </view>
        
        <view class="form-item">
            <textarea class="textarea" :value="formData.content" @input="onContentInput" placeholder="请输入反馈内容..." />
        </view>

        <view class="actions">
           <button size="mini" @click="showPopup = false">取消</button>
           <button size="mini" type="primary" @click="submit">提交</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { request } from '../utils/request';

export default {
    name: 'FeedbackBtn',
    data() {
        return {
            showPopup: false,
            formData: {
                type: 'suggestion',
                urgency: 'low',
                content: ''
            }
        }
    },
    methods: {
        closePopup(e) {
            // Check target if needed, simplistic click self
            this.showPopup = false;
        },
        onTypeChange(e) {
            this.formData.type = e.detail.value;
        },
        onContentInput(e) {
            this.formData.content = e.detail.value;
        },
        async submit() {
            if (!this.formData.content) return uni.showToast({title:'请输入内容', icon:'none'});
            
            try {
                const pages = getCurrentPages();
                const route = pages.length > 0 ? pages[pages.length - 1].route : 'unknown';
                
                const pageMap = {
                    'pages/index/index': '首页',
                    'pages/department/schedule': '科室排班',
                    'pages/preference/index': '意愿申报',
                    'pages/trade/list': '换班列表',
                    'pages/trade/create': '发起换班',
                    'pages/notifications/list': '消息通知',
                    'pages/login/login': '登录页'
                };
                const pageName = pageMap[route] || route;

                await request({
                    url: '/feedback/',
                    method: 'POST',
                    data: {
                        ...this.formData,
                        page: pageName
                    }
                });
                uni.showToast({title:'提交成功'});
                this.showPopup = false;
                this.formData.content = '';
            } catch (e) {
                uni.showToast({title:'提交失败', icon:'none'});
            }
        }
    }
}
</script>

<style>
.feedback-fab {
    position: fixed; right: 20px; bottom: 80px;
    width: 50px; height: 50px; background: #007aff; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2); z-index: 999;
}
.fab-icon { font-size: 24px; color: #fff; }
.popup-mask { position: fixed; top: 0; left: 0; bottom: 0; right: 0; background: rgba(0,0,0,0.5); z-index: 1000; display: flex; align-items: center; justify-content: center; }
.popup-content { width: 80%; background: #fff; border-radius: 10px; padding: 20px; box-sizing: border-box; }
.popup-title { font-weight: bold; font-size: 18px; display: block; margin-bottom: 20px; text-align: center; }
.form-item { margin-bottom: 15px; }
.label { display: block; margin-bottom: 8px; font-weight: bold; font-size: 14px; color: #333; }
.rg { display: flex; gap: 10px; font-size: 14px; flex-wrap: wrap; }
.radio-label { display: flex; align-items: center; }
.textarea { width: 100%; height: 80px; border: 1px solid #eee; padding: 8px; border-radius: 4px; box-sizing: border-box; font-size: 14px; }
.urgency-opts { display: flex; gap: 10px; }
.u-tag { padding: 4px 12px; border: 1px solid #ddd; border-radius: 15px; font-size: 12px; }
.u-tag.active { background: #007aff; color: #fff; border-color: #007aff; }
.actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 10px; }
</style>
