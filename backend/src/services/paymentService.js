import { and, eq, sql } from 'drizzle-orm';
import { courses, enrollments, payments, teacherPayouts } from '../db/schema.js';

// Joriy oy uchun faol yozilishlarga to'lov yozuvi yo'q bo'lsa, yaratadi
export async function ensurePaymentsForPeriod(db, period) {
  const rows = await db
    .select({ enrollmentId: enrollments.id, price: courses.price })
    .from(enrollments)
    .innerJoin(courses, eq(enrollments.courseId, courses.id))
    .where(eq(enrollments.status, 'active'));
  if (rows.length === 0) return;

  await db.insert(payments)
    .values(rows.map((r) => ({ enrollmentId: r.enrollmentId, period, amountDue: r.price })))
    .onConflictDoNothing({ target: [payments.enrollmentId, payments.period] });
}


// Har o'qituvchining shu oy yig'gan puliga qarab 30% ulushni hisoblaydi va saqlaydi
export async function ensureTeacherPayouts(db, period) {
  const rows = await db
    .select({
      teacherId: courses.teacherId,
      totalPaid: sql`coalesce(sum(${payments.amountPaid}), 0)`.mapWith(Number),
    })
    .from(payments)
    .innerJoin(enrollments, eq(payments.enrollmentId, enrollments.id))
    .innerJoin(courses, eq(enrollments.courseId, courses.id))
    .where(and(eq(payments.period, period), eq(enrollments.status, 'active')))
    .groupBy(courses.teacherId);

  for (const r of rows) {
    const amountDue = Math.round(r.totalPaid * 0.3);
    await db.insert(teacherPayouts)
      .values({ teacherId: r.teacherId, period, amountDue })
      .onConflictDoUpdate({ target: [teacherPayouts.teacherId, teacherPayouts.period], set: { amountDue } });
  }
}