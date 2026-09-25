import { z } from 'zod';

export const markPaidSchema = z.object({ telegramId: z.number().int().positive() });
export const markPartialSchema = z.object({
  telegramId: z.number().int().positive(),
  amount: z.number().int().min(0).max(100_000_000),
});