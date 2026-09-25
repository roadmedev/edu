import { Hono } from 'hono';
import { and, eq } from 'drizzle-orm';
import { getDb } from '../db/client.js';
import { courses, enrollments, payments, users } from '../db/schema.js';
import { ensurePaymentsForPeriod } from '../services/paymentService.js';
import { tashkentDate, tashkentPeriod } from '../utils/time.js';

const router = new Hono();

router.get('/:tgId/balance', async (c) => {
  const tgId = Number(c.req.param('tgId'));
  const db = getDb(c.env);
  const [teacher] = await db.select().from(users).where(eq(users.telegramId, tgId));
  if (!teacher || teacher.role !== 'teacher') return c.json({ error: 'Topilmadi' }, 404);

  const period = tashkentPeriod();
  await ensurePaymentsForPeriod(db, period);

  const rows = await db
    .select({ amountDue: payments.amountDue, amountPaid: payments.amountPaid, status: payments.status, updatedAt: payments.updatedAt })
    .from(payments)
    .innerJoin(enrollments, eq(payments.enrollmentId, enrollments.id))
    .innerJoin(courses, eq(enrollments.courseId, courses.id))
    .where(and(eq(courses.teacherId, teacher.id), eq(payments.period, period), eq(enrollments.status, 'active')));

  const today = tashkentDate();
  const totalDue = rows.reduce((s, r) => s + r.amountDue, 0);
  const totalPaid = rows.reduce((s, r) => s + r.amountPaid, 0);
  const dailyIncome = rows
    .filter((r) => r.updatedAt.toISOString().slice(0, 10) === today)
    .reduce((s, r) => s + r.amountPaid, 0);

  return c.json({
    period,
    studentsCount: rows.length,
    paidCount: rows.filter((r) => r.status === 'paid').length,
    totalDue,
    totalPaid,
    totalDebt: totalDue - totalPaid,
    dailyIncome,
  });
});

export default router;