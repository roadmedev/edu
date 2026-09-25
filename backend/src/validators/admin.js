import { z } from 'zod';

export const promoteSchema = z.object({
  userId: z.number().int().positive(),
  subject: z.string().trim().min(2).max(100),
  photo: z.string().nullish(),
  certificate: z.string().nullish(),
});

export const payoutPartialSchema = z.object({ 
    amount: z.number().int().min(0).max(100_000_000) 
});