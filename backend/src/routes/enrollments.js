import { Hono } from 'hono';
import { and, asc, eq, inArray } from 'drizzle-orm';
import { alias } from 'drizzle-orm/pg-core';
import { getDb } from '../db/client.js';
import { decisionSchema, joinSchema, termsSchema } from '../validators/enrollments.js';
import { tashkentDate } from '../utils/time.js';
import { attendance, courses, courseSchedules, enrollments, joinRequests, users } from '../db/schema.js';


const router = new Hono();
const teacherUser = alias(users, 'teacher_user');

const ALREADY = {
  pending: 'Bu kursga so\'rovingiz allaqachon yuborilgan, o\'qituvchi javobini kuting.',
  accepted: 'So\'rovingiz qabul qilingan. Shartlarni qabul qilishingiz kerak.',
  active: 'Siz bu kursning o\'quvchisisiz.',
};

// So'rov haqida to'liq ma'lumot (bot xabar yuborishi uchun kerakli hamma narsa)
async function loadDetails(db, id) {
  const [row] = await db
    .select({
      id: enrollments.id,
      status: enrollments.status,
      courseId: courses.id,
      courseTitle: courses.title,
      teacherTgId: teacherUser.telegramId,
      teacherName: teacherUser.fullName,
      studentId: users.id,
      studentName: users.fullName,
      studentPhone: users.phone,
      studentTgId: users.telegramId,
    })
    .from(enrollments)
    .innerJoin(courses, eq(enrollments.courseId, courses.id))
    .innerJoin(teacherUser, eq(courses.teacherId, teacherUser.id))
    .innerJoin(users, eq(enrollments.studentId, users.id))
    .where(eq(enrollments.id, id));
  if (!row) return null;

  const schedules = await db.select().from(courseSchedules)
    .where(eq(courseSchedules.courseId, row.courseId))
    .orderBy(asc(courseSchedules.weekday));

  return {
    ...row,
    schedules: schedules.map((s) => ({
      weekday: s.weekday,
      startTime: s.startTime.slice(0, 5),
      endTime: s.endTime.slice(0, 5),
    })),
  };
}

// Kursga qo'shilish so'rovi
router.post('/', async (c) => {
  const parsed = joinSchema.safeParse(await c.req.json());
  if (!parsed.success) return c.json({ error: 'Ma\'lumot noto\'g\'ri' }, 400);
  const { telegramId, courseId } = parsed.data;
  const db = getDb(c.env);

  const [user] = await db.select().from(users).where(eq(users.telegramId, telegramId));
  if (!user) return c.json({ error: 'Foydalanuvchi topilmadi' }, 404);
  if (!['user', 'student'].includes(user.role)) {
    return c.json({ error: 'Sizning rolingiz kursga yozilish uchun emas' }, 403);
  }

  const [course] = await db.select().from(courses)
    .where(and(eq(courses.id, courseId), eq(courses.isActive, true)));
  if (!course) return c.json({ error: 'Kurs topilmadi' }, 404);
  if (course.teacherId === user.id) return c.json({ error: 'O\'z kursingizga yozila olmaysiz' }, 400);

  const [existing] = await db.select().from(enrollments)
    .where(and(eq(enrollments.courseId, courseId), eq(enrollments.studentId, user.id)));
  if (existing && existing.status !== 'rejected') {
    return c.json({ error: ALREADY[existing.status] }, 409);
  }

  const logged = await db.insert(joinRequests)
    .values({ userId: user.id, requestDate: tashkentDate() })
    .onConflictDoNothing()
    .returning({ id: joinRequests.id });
  if (logged.length === 0) {
    return c.json({ error: 'Bugun so\'rov yuborib bo\'lgansiz. Ertaga qayta urinib ko\'ring.' }, 429);
  }

  try {
    let enrollment;
    if (existing) {
      [enrollment] = await db.update(enrollments)
        .set({ status: 'pending', createdAt: new Date() })
        .where(eq(enrollments.id, existing.id)).returning();
    } else {
      [enrollment] = await db.insert(enrollments)
        .values({ courseId, studentId: user.id }).returning();
    }
    return c.json(await loadDetails(db, enrollment.id), 201);
  } catch (err) {
    await db.delete(joinRequests).where(eq(joinRequests.id, logged[0].id));
    throw err;
  }
});

// O'qituvchi qarori: accept | reject
router.post('/:id/decision', async (c) => {
  const id = Number(c.req.param('id'));
  const parsed = decisionSchema.safeParse(await c.req.json());
  if (!Number.isInteger(id) || !parsed.success) return c.json({ error: 'Ma\'lumot noto\'g\'ri' }, 400);
  const { telegramId, action } = parsed.data;
  const db = getDb(c.env);

  const details = await loadDetails(db, id);
  if (!details) return c.json({ error: 'So\'rov topilmadi' }, 404);
  if (details.teacherTgId !== telegramId) return c.json({ error: 'Bu so\'rov sizga tegishli emas' }, 403);

  // Faqat pending holatdan o'tadi: tugma ikki marta bosilsa, ikkinchisi 0 qator o'zgartiradi
  const updated = await db.update(enrollments)
    .set({ status: action === 'accept' ? 'accepted' : 'rejected' })
    .where(and(eq(enrollments.id, id), eq(enrollments.status, 'pending')))
    .returning({ id: enrollments.id });
  if (updated.length === 0) return c.json({ error: 'Bu so\'rov allaqachon ko\'rib chiqilgan' }, 409);

  return c.json(await loadDetails(db, id));
});

// O'quvchi shartlarni qabul qiladi: active + rol student
router.post('/:id/accept-terms', async (c) => {
  const id = Number(c.req.param('id'));
  const parsed = termsSchema.safeParse(await c.req.json());
  if (!Number.isInteger(id) || !parsed.success) return c.json({ error: 'Ma\'lumot noto\'g\'ri' }, 400);
  const db = getDb(c.env);

  const details = await loadDetails(db, id);
  if (!details) return c.json({ error: 'So\'rov topilmadi' }, 404);
  if (details.studentTgId !== parsed.data.telegramId) return c.json({ error: 'Bu so\'rov sizga tegishli emas' }, 403);

  const updated = await db.update(enrollments)
    .set({ status: 'active', joinedAt: new Date() })
    .where(and(eq(enrollments.id, id), eq(enrollments.status, 'accepted')))
    .returning({ id: enrollments.id });
  if (updated.length === 0) return c.json({ error: 'Bu so\'rov allaqachon yakunlangan' }, 409);

  // Faqat oddiy user student bo'ladi (teacher/admin rollari o'zgarmaydi)
  await db.update(users).set({ role: 'student' })
    .where(and(eq(users.id, details.studentId), eq(users.role, 'user')));

  return c.json(await loadDetails(db, id));
});

// O'quvchining faol kurslari ("Mening" bo'limi uchun)
router.get('/mine/:tgId', async (c) => {
  const db = getDb(c.env);
  const [student] = await db.select().from(users).where(eq(users.telegramId, Number(c.req.param('tgId'))));
  if (!student) return c.json({ error: 'Topilmadi' }, 404);

  const rows = await db
    .select({
      enrollmentId: enrollments.id,
      courseId: courses.id,
      courseTitle: courses.title,
      joinedAt: enrollments.joinedAt,
    })
    .from(enrollments)
    .innerJoin(courses, eq(enrollments.courseId, courses.id))
    .where(and(eq(enrollments.studentId, student.id), eq(enrollments.status, 'active')))
    .orderBy(asc(enrollments.joinedAt));

  if (rows.length === 0) return c.json([]);

  const attRows = await db.select().from(attendance)
    .where(inArray(attendance.enrollmentId, rows.map((r) => r.enrollmentId)));

  return c.json(rows.map((r) => {
    const mine = attRows.filter((a) => a.enrollmentId === r.enrollmentId);
    return {
      ...r,
      presentCount: mine.filter((a) => a.present).length,
      absentCount: mine.filter((a) => !a.present).length,
    };
  }));
});

// Kurs bo'yicha reyting (davomat asosida)
router.get('/course/:courseId/rating', async (c) => {
  const courseId = Number(c.req.param('courseId'));
  const tgId = Number(c.req.query('telegramId'));
  const db = getDb(c.env);

  const [requester] = await db.select().from(users).where(eq(users.telegramId, tgId));
  if (!requester) return c.json({ error: 'Topilmadi' }, 404);

  if (requester.role === 'student') {
    const [own] = await db.select().from(enrollments).where(and(
      eq(enrollments.courseId, courseId), eq(enrollments.studentId, requester.id), eq(enrollments.status, 'active'),
    ));
    if (!own) return c.json({ error: 'Siz bu kursga yozilmagansiz' }, 403);
  } else if (requester.role !== 'admin') {
    const [course] = await db.select().from(courses).where(eq(courses.id, courseId));
    if (!course || course.teacherId !== requester.id) return c.json({ error: 'Ruxsat yo\'q' }, 403);
  }

  const rows = await db
    .select({ enrollmentId: enrollments.id, studentName: users.fullName })
    .from(enrollments)
    .innerJoin(users, eq(enrollments.studentId, users.id))
    .where(and(eq(enrollments.courseId, courseId), eq(enrollments.status, 'active')));

  if (rows.length === 0) return c.json([]);

  const attRows = await db.select().from(attendance)
    .where(inArray(attendance.enrollmentId, rows.map((r) => r.enrollmentId)));

  return c.json(
    rows
      .map((r) => ({
        studentName: r.studentName,
        presentCount: attRows.filter((a) => a.enrollmentId === r.enrollmentId && a.present).length,
      }))
      .sort((a, b) => b.presentCount - a.presentCount),
  );
});

export default router;