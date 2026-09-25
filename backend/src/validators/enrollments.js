import { z } from 'zod';

export const joinSchema = z.object({
  telegramId: z.number().int().positive(),
  courseId: z.number().int().positive(),
});

export const decisionSchema = z.object({
  telegramId: z.number().int().positive(),
  action: z.enum(['accept', 'reject']),
});

export const termsSchema = z.object({
  telegramId: z.number().int().positive(),
});