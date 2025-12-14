import { defineStore } from 'pinia';
import request from '../utils/request';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || null,
  }),
  actions: {
    async login(username, password) {
      // POST /api/auth/login
      const res = await request.post('/auth/login', { username, password });
      this.token = res.token;
      this.user = res.user;
      localStorage.setItem('token', res.token);
      localStorage.setItem('user', JSON.stringify(res.user));
    },
    logout() {
      this.token = null;
      this.user = null;
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.reload();
    }
  }
});
