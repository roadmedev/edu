import { Hono } from 'hono';
import { and, asc, desc, eq, inArray, sql } from 'drizzle-orm';
import { getDb } from '../db/client.js';
import {
  courses, enrollments, payments, suggestions, teacherPayouts, teacherProfiles, users,
} from '../db/schema.js';
import { loadCoursesByTeacherId } from './courses.js';
import { ensurePaymentsForPeriod, ensureTeacherPayouts } from '../services/paymentService.js';
import { tashkentPeriod } from '../utils/time.js';
import { payoutPartialSchema, promoteSchema } from '../validators/admin.js';

const router = new Hono();

// Har endpointda: so'rovchi haqiqatan admin ekanligini tekshiradi
async function requireAdmin(db, tgId) {
  const [u] = await db.select().from(users).where(eq(users.telegramId, tgId));
  return u && u.role === 'admin' ? u : null;
}


// ---------- Statistika ----------
router.get('/:tgId/stats', async (c) => {
  const db = getDb(c.env);
  if (!(await requireAdmin(db, Number(c.req.param('tgId'))))) return c.json({ error: 'Ruxsat yo\'q' }, 403);

  const periodParam = c.req.query('period');  // '2026-09'
  const yearParam = c.req.query('year');      // '2026'
  const currentPeriod = tashkentPeriod();

  // Faqat joriy oy ko'rsatilayotganda yangi to'lov yozuvlarini "dangasa" yaratamiz
  if (!periodParam && !yearParam) await ensurePaymentsForPeriod(db, currentPeriod);

  const [byRole] = await db
    .select({
      users: sql`count(*) filter (where ${users.role} = 'user')`,
      teachers: sql`count(*) filter (where ${users.role} = 'teacher')`,
      students: sql`count(*) filter (where ${users.role} = 'student')`,
    })
    .from(users);

  const [{ value: coursesCount }] = await db.select({ value: sql`count(*)` }).from(courses)
    .where(eq(courses.isActive, true));

  let periodRows;
  let label;
  const isYear = Boolean(yearParam);

  if (isYear) {
    periodRows = await db.select({ amountDue: payments.amountDue, amountPaid: payments.amountPaid })
      .from(payments)
      .where(sql`${payments.period} like ${yearParam + '-%'}`);
    label = yearParam;
  } else {
    const period = periodParam || currentPeriod;
    periodRows = await db.select({ amountDue: payments.amountDue, amountPaid: payments.amountPaid })
      .from(payments)
      .where(eq(payments.period, period));
    label = period;
  }

  const totalDue = periodRows.reduce((s, r) => s + r.amountDue, 0);
  const totalPaid = periodRows.reduce((s, r) => s + r.amountPaid, 0);

  return c.json({
    period: label,
    isYear,
    usersCount: Number(byRole.users),
    teachersCount: Number(byRole.teachers),
    studentsCount: Number(byRole.students),
    coursesCount: Number(coursesCount),
    totalPaid,
    centerShare: Math.round(totalPaid * 0.3),
    totalDebt: totalDue - totalPaid,
  });
});

// Mavjud oylar/yillar ro'yxati (tugmalar uchun)
router.get('/:tgId/stats/periods', async (c) => {
  const db = getDb(c.env);
  if (!(await requireAdmin(db, Number(c.req.param('tgId'))))) return c.json({ error: 'Ruxsat yo\'q' }, 403);

  const rows = await db.selectDistinct({ period: payments.period }).from(payments).orderBy(desc(payments.period));
  const periods = rows.map((r) => r.period);
  const years = [...new Set(periods.map((p) => p.slice(0, 4)))].sort().reverse();

  return c.json({ periods, years });
});


// ---------- Oddiy foydalanuvchilar ----------
router.get('/:tgId/users', async (c) => {
  const db = getDb(c.env);
  if (!(await requireAdmin(db, Number(c.req.param('tgId'))))) return c.json({ error: 'Ruxsat yo\'q' }, 403);

  const rows = await db.select({
    id: users.id, fullName: users.fullName, phone: users.phone,
    telegramId: users.telegramId, createdAt: users.createdAt,
  }).from(users).where(eq(users.role, 'user')).orderBy(desc(users.createdAt));

  return c.json(rows);
});

// ---------- O'qituvchilar ----------
router.get('/:tgId/teachers', async (c) => {
  const db = getDb(c.env);
  if (!(await requireAdmin(db, Number(c.req.param('tgId'))))) return c.json({ error: 'Ruxsat yo\'q' }, 403);

  const rows = await db.select({
    id: users.id, fullName: users.fullName, phone: users.phone, telegramId: users.telegramId,
    photo: teacherProfiles.photo, subject: teacherProfiles.subject, certificate: teacherProfiles.certificate,
  }).from(users)
    .leftJoin(teacherProfiles, eq(teacherProfiles.userId, users.id))
    .where(eq(users.role, 'teacher')).orderBy(asc(users.fullName));

  return c.json(rows);
});

router.get('/:tgId/teachers/:teacherId/courses', async (c) => {
  const db = getDb(c.env);
  if (!(await requireAdmin(db, Number(c.req.param('tgId'))))) return c.json({ error: 'Ruxsat yo\'q' }, 403);
  return c.json(await loadCoursesByTeacherId(db, Number(c.req.param('teacherId'))));
});

// user rolidagi nomzodlar ro'yxati (o'qituvchi qilish uchun)
router.get('/:tgId/teacher-candidates', async (c) => {
  const db = getDb(c.env);
  if (!(await requireAdmin(db, Number(c.req.param('tgId'))))) return c.json({ error: 'Ruxsat yo\'q' }, 403);

  const rows = await db.select({ id: users.id, fullName: users.fullName, phone: users.phone })
    .from(users).where(eq(users.role, 'user')).orderBy(desc(users.createdAt));
  return c.json(rows);
});

router.post('/:tgId/teachers', async (c) => {
  const db = getDb(c.env);
  if (!(await requireAdmin(db, Number(c.req.param('tgId'))))) return c.json({ error: 'Ruxsat yo\'q' }, 403);

  const parsed = promoteSchema.safeParse(await c.req.json());
  if (!parsed.success) return c.json({ error: 'Ma\'lumot noto\'g\'ri' }, 400);
  const { userId, subject, photo, certificate } = parsed.data;

  const [candidate] = await db.select().from(users).where(and(eq(users.id, userId), eq(users.role, 'user')));
  if (!candidate) return c.json({ error: 'Foydalanuvchi topilmadi yoki allaqachon rol o\'zgargan' }, 404);

  await db.update(users).set({ role: 'teacher' }).where(eq(users.id, userId));
  await db.insert(teacherProfiles).values({ userId, subject, photo, certificate })
    .onConflictDoUpdate({ target: teacherProfiles.userId, set: { subject, photo, certificate } });

  return c.json({ ok: true, fullName: candidate.fullName, telegramId: candidate.telegramId });
});

router.delete('/:tgId/teachers/:teacherId', async (c) => {
  const db = getDb(c.env);
  if (!(await requireAdmin(db, Number(c.req.param('tgId'))))) return c.json({ error: 'Ruxsat yo\'q' }, 403);
  const teacherId = Number(c.req.param('teacherId'));

  const [teacher] = await db.select().from(users).where(and(eq(users.id, teacherId), eq(users.role, 'teacher')));
  if (!teacher) return c.json({ error: 'O\'qituvchi topilmadi' }, 404);

  await db.update(courses).set({ isActive: false }).where(eq(courses.teacherId, teacherId));
  await db.delete(teacherProfiles).where(eq(teacherProfiles.userId, teacherId));
  await db.update(users).set({ role: 'user' }).where(eq(users.id, teacherId));

  return c.json({ ok: true, fullName: teacher.fullName });
});

// ---------- O'quvchilar (barcha, admin ko'rinishi) ----------
router.get('/:tgId/students', async (c) => {
  const db = getDb(c.env);
  if (!(await requireAdmin(db, Number(c.req.param('tgId'))))) return c.json({ error: 'Ruxsat yo\'q' }, 403);

  const period = tashkentPeriod();
  await ensurePaymentsForPeriod(db, period);

  const teacherUser = users; // aynan shu jadval, lekin ikkinchi alias kerak bo'lgani uchun pastda alias ishlatamiz
  const { alias } = await import('drizzle-orm/pg-core');
  const teacherAlias = alias(users, 'teacher_alias');

  const rows = await db
    .select({
      enrollmentId: enrollments.id,
      studentName: users.fullName,
      studentTgId: users.telegramId,
      courseTitle: courses.title,
      teacherName: teacherAlias.fullName,
      amountDue: payments.amountDue,
      amountPaid: payments.amountPaid,
      status: payments.status,
    })
    .from(enrollments)
    .innerJoin(users, eq(enrollments.studentId, users.id))
    .innerJoin(courses, eq(enrollments.courseId, courses.id))
    .innerJoin(teacherAlias, eq(courses.teacherId, teacherAlias.id))
    .leftJoin(payments, and(eq(payments.enrollmentId, enrollments.id), eq(payments.period, period)))
    .where(eq(enrollments.status, 'active'))
    .orderBy(asc(users.fullName));

  return c.json({ period, students: rows });
});

router.post('/:tgId/students/:enrollmentId/mark-paid', async (c) => {
  const db = getDb(c.env);
  if (!(await requireAdmin(db, Number(c.req.param('tgId'))))) return c.json({ error: 'Ruxsat yo\'q' }, 403);
  const enrollmentId = Number(c.req.param('enrollmentId'));
  const period = tashkentPeriod();

  const [payment] = await db.select().from(payments)
    .where(and(eq(payments.enrollmentId, enrollmentId), eq(payments.period, period)));
  if (!payment) return c.json({ error: 'To\'lov yozuvi topilmadi' }, 404);

  const [updated] = await db.update(payments)
    .set({ amountPaid: payment.amountDue, status: 'paid', updatedAt: new Date() })
    .where(eq(payments.id, payment.id)).returning();
  return c.json(updated);
});

// ---------- Moliya ----------
router.get('/:tgId/finance', async (c) => {
  const db = getDb(c.env);
  if (!(await requireAdmin(db, Number(c.req.param('tgId'))))) return c.json({ error: 'Ruxsat yo\'q' }, 403);

  const period = tashkentPeriod();
  await ensureTeacherPayouts(db, period);

  const rows = await db
    .select({
      teacherId: teacherPayouts.teacherId,
      teacherName: users.fullName,
      amountDue: teacherPayouts.amountDue,
      amountPaid: teacherPayouts.amountPaid,
      status: teacherPayouts.status,
    })
    .from(teacherPayouts)
    .innerJoin(users, eq(teacherPayouts.teacherId, users.id))
    .where(eq(teacherPayouts.period, period))
    .orderBy(asc(users.fullName));

  const totalDue = rows.reduce((s, r) => s + r.amountDue, 0);
  const totalPaid = rows.reduce((s, r) => s + r.amountPaid, 0);

  return c.json({ period, totalDue, totalPaid, totalDebt: totalDue - totalPaid, teachers: rows });
});

router.post('/:tgId/payouts/:teacherId/mark-paid', async (c) => {
  const db = getDb(c.env);
  if (!(await requireAdmin(db, Number(c.req.param('tgId'))))) return c.json({ error: 'Ruxsat yo\'q' }, 403);
  const teacherId = Number(c.req.param('teacherId'));
  const period = tashkentPeriod();

  const [payout] = await db.select().from(teacherPayouts)
    .where(and(eq(teacherPayouts.teacherId, teacherId), eq(teacherPayouts.period, period)));
  if (!payout) return c.json({ error: 'Yozuv topilmadi' }, 404);

  const [updated] = await db.update(teacherPayouts)
    .set({ amountPaid: payout.amountDue, status: 'paid', updatedAt: new Date() })
    .where(eq(teacherPayouts.id, payout.id)).returning();
  return c.json(updated);
});

router.post('/:tgId/payouts/:teacherId/mark-partial', async (c) => {
  const db = getDb(c.env);
  if (!(await requireAdmin(db, Number(c.req.param('tgId'))))) return c.json({ error: 'Ruxsat yo\'q' }, 403);
  const parsed = payoutPartialSchema.safeParse(await c.req.json());
  if (!parsed.success) return c.json({ error: 'Ma\'lumot noto\'g\'ri' }, 400);
  const teacherId = Number(c.req.param('teacherId'));
  const period = tashkentPeriod();

  const [payout] = await db.select().from(teacherPayouts)
    .where(and(eq(teacherPayouts.teacherId, teacherId), eq(teacherPayouts.period, period)));
  if (!payout) return c.json({ error: 'Yozuv topilmadi' }, 404);

  const amount = Math.min(parsed.data.amount, payout.amountDue);
  const status = amount >= payout.amountDue ? 'paid' : amount > 0 ? 'partial' : 'unpaid';
  const [updated] = await db.update(teacherPayouts)
    .set({ amountPaid: amount, status, updatedAt: new Date() })
    .where(eq(teacherPayouts.id, payout.id)).returning();
  return c.json(updated);
});

// ---------- Taklif qutisi ----------
router.get('/:tgId/suggestions', async (c) => {
  const db = getDb(c.env);
  if (!(await requireAdmin(db, Number(c.req.param('tgId'))))) return c.json({ error: 'Ruxsat yo\'q' }, 403);

  const rows = await db
    .select({
      id: suggestions.id, text: suggestions.text, createdAt: suggestions.createdAt,
      fromName: users.fullName, fromRole: users.role,
    })
    .from(suggestions)
    .innerJoin(users, eq(suggestions.fromUserId, users.id))
    .orderBy(desc(suggestions.createdAt));

  return c.json(rows);
});

export default router;