import { defineStore } from 'pinia';
import api from '../api/axios';
import router from '../router';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        token: localStorage.getItem('token') || null,
        user: null,
    }),
    getters: {
        isAuthenticated: (state) => !!state.token,
        isAdmin: (state) => state.user && state.user.role === 'admin',
        isManager: (state) => state.user && (state.user.role === 'manager' || state.user.role === 'admin'),
    },
    actions: {
        async login(username, password) {
            try {
                const response = await api.post('/token',
                    new URLSearchParams({ username, password }),
                    { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
                );
                const { access_token } = response.data;
                this.token = access_token;
                localStorage.setItem('token', access_token);

                await this.fetchUser();
                router.push('/');
            } catch (error) {
                console.error('Login failed', error);
                throw error;
            }
        },
        async fetchUser() {
            try {
                const response = await api.get('/users/me');
                this.user = response.data;
            } catch (error) {
                console.error('Fetch user failed', error);
                this.logout();
            }
        },
        logout() {
            this.token = null;
            this.user = null;
            localStorage.removeItem('token');
            router.push('/login');
        },
    },
});
