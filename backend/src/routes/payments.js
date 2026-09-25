import { Hono } from 'hono';
import { and, eq } from 'drizzle-orm';
import { alias } from 'drizzle-orm/pg-core';
import { getDb } from '../db/client.js';
import { courses, enrollments, payments, users } from '../db/schema.js';
import { markPaidSchema, markPartialSchema } from '../validators/payments.js';
import { tashkentPeriod } from '../utils/time.js';

const router = new Hono();
const studentUser = alias(users, 'student_user');

// Berilgan enrollment shu o'qituvchiga tegishlimi, tekshirib qaytaradi
async function findOwnedEnrollment(db, enrollmentId, teacherTgId) {
  const [row] = await db
    .select({
      teacherId: courses.teacherId,
      studentName: studentUser.fullName,
    })
    .from(enrollments)
    .innerJoin(courses, eq(enrollments.courseId, courses.id))
    .innerJoin(studentUser, eq(enrollments.studentId, studentUser.id))
    .where(eq(enrollments.id, enrollmentId));
  if (!row) return null;

  const [teacher] = await db.select().from(users).where(eq(users.telegramId, teacherTgId));
  if (!teacher || teacher.id !== row.teacherId) return null;
  return row;
}

router.post('/:enrollmentId/mark-paid', async (c) => {
  const enrollmentId = Number(c.req.param('enrollmentId'));
  const parsed = markPaidSchema.safeParse(await c.req.json());
  if (!Number.isInteger(enrollmentId) || !parsed.success) return c.json({ error: 'Ma\'lumot noto\'g\'ri' }, 400);
  const db = getDb(c.env);

  const owned = await findOwnedEnrollment(db, enrollmentId, parsed.data.telegramId);
  if (!owned) return c.json({ error: 'Ruxsat yo\'q yoki topilmadi' }, 403);

  const period = tashkentPeriod();
  const [payment] = await db.select().from(payments)
    .where(and(eq(payments.enrollmentId, enrollmentId), eq(payments.period, period)));
  if (!payment) return c.json({ error: 'To\'lov yozuvi topilmadi' }, 404);

  const [updated] = await db.update(payments)
    .set({ amountPaid: payment.amountDue, status: 'paid', updatedAt: new Date() })
    .where(eq(payments.id, payment.id)).returning();

  return c.json({ studentName: owned.studentName, payment: updated });
});

router.post('/:enrollmentId/mark-partial', async (c) => {
  const enrollmentId = Number(c.req.param('enrollmentId'));
  const parsed = markPartialSchema.safeParse(await c.req.json());
  if (!Number.isInteger(enrollmentId) || !parsed.success) return c.json({ error: 'Ma\'lumot noto\'g\'ri' }, 400);
  const db = getDb(c.env);

  const owned = await findOwnedEnrollment(db, enrollmentId, parsed.data.telegramId);
  if (!owned) return c.json({ error: 'Ruxsat yo\'q yoki topilmadi' }, 403);

  const period = tashkentPeriod();
  const [payment] = await db.select().from(payments)
    .where(and(eq(payments.enrollmentId, enrollmentId), eq(payments.period, period)));
  if (!payment) return c.json({ error: 'To\'lov yozuvi topilmadi' }, 404);

  const amount = Math.min(parsed.data.amount, payment.amountDue);
  const status = amount >= payment.amountDue ? 'paid' : amount > 0 ? 'partial' : 'unpaid';

  const [updated] = await db.update(payments)
    .set({ amountPaid: amount, status, updatedAt: new Date() })
    .where(eq(payments.id, payment.id)).returning();

  return c.json({ studentName: owned.studentName, payment: updated });
});

export default router;