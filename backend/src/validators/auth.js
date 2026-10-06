import { z } from 'zod';

export const requestOtpSchema = z.object({ phone: z.string().trim().min(7).max(20) });
export const verifyOtpSchema = z.object({
  phone: z.string().trim().min(7).max(20),
  code: z.string().trim().length(6),
});