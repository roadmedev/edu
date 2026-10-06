import { api } from './client';

export const requestOtp = (phone) => api.post('/auth/request-otp', { phone });
export const verifyOtp = (phone, code) => api.post('/auth/verify-otp', { phone, code });
