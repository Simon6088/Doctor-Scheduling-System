// 适配 Vercel 部署：优先使用环境变量，否则使用 '/api' (本地代理)
const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export function request(options) {
    const token = uni.getStorageSync('token');

    console.log('[Request] 发起请求:', options.url, options.method || 'GET');

    return new Promise((resolve, reject) => {
        uni.request({
            url: BASE_URL + options.url,
            method: options.method || 'GET',
            data: options.data,
            header: {
                'Authorization': token ? `Bearer ${token}` : '',
                ...options.header
            },
            success: (res) => {
                console.log('[Request] 响应:', options.url, '状态码:', res.statusCode);
                console.log('[Request] 数据:', res.data);

                if (res.statusCode === 401) {
                    console.error('[Request] 未授权，清除token');
                    uni.removeStorageSync('token');
                    uni.reLaunch({ url: '/pages/login/login' });
                    reject(new Error('Unauthorized'));
                } else if (res.statusCode === 200) {
                    resolve(res.data);
                } else {
                    console.error('[Request] 请求失败:', res.statusCode, res.data);
                    reject(new Error(res.data?.detail || `请求失败: ${res.statusCode}`));
                }
            },
            fail: (err) => {
                console.error('[Request] 网络错误:', options.url, err);
                reject(err);
            }
        });
    });
};
