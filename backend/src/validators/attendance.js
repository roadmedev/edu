import { z } from 'zod';

export const attendanceSchema = z.object({
  telegramId: z.number().int().positive(),
  records: z.array(z.object({
    enrollmentId: z.number().int().positive(),
    present: z.boolean(),
  })).min(1),
});