import { z } from 'zod';

const time = z.string().regex(/^([01]\d|2[0-3]):[0-5]\d$/, 'Vaqt HH:MM ko\'rinishida bo\'lsin');

export const slotSchema = z
  .object({
    weekday: z.number().int().min(1).max(7),
    startTime: time,
    endTime: time,
  })
  .refine((s) => s.endTime > s.startTime, { message: 'Tugash vaqti boshlanishidan keyin bo\'lishi kerak' });

export const createCourseSchema = z.object({
  telegramId: z.number().int().positive(),
  title: z.string().trim().min(3).max(100),
  description: z.string().trim().min(10).max(600), // Telegram caption limiti (1024) uchun
  price: z.number().int().min(10_000).max(100_000_000),
  photo: z.string().nullish(),
  certificate: z.string().nullish(),
  schedules: z.array(slotSchema).min(1).max(7),
});