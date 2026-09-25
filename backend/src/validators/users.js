import { z } from 'zod';

export const registerSchema = z.object({
    telegramId: z.number().int().positive(),
    fullName: z.string().trim().min(3).max(100),
    phone: z.string().trim().min(7).max(20),
});