import { z } from 'zod';

export const suggestionSchema = z.object({
  telegramId: z.number().int().positive(),
  text: z.string().trim().min(3).max(500),
});