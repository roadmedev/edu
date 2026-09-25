import { Hono } from 'hono';
import { and, asc, count, eq, inArray } from 'drizzle-orm';
import { getDb } from '../db/client.js';
import { courses, courseSchedules, enrollments, teacherProfiles, users } from '../db/schema.js';
import { createCourseSchema, slotSchema } from '../validators/courses.js';
import { findConflict, hasInternalOverlap } from '../services/scheduleService.js';
import { ensurePaymentsForPeriod } from '../services/paymentService.js';
import { attendance, payments } from '../db/schema.js';
import { attendanceSchema } from '../validators/attendance.js';
import { tashkentDate, tashkentPeriod } from '../utils/time.js';


const router = new Hono();

// Kurslarni o'qituvchi ma'lumoti va jadvali bilan yuklaydi
async function loadCourses(db, where) {
  const rows = await db
    .select({
      id: courses.id,
      title: courses.title,
      description: courses.description,
      price: courses.price,
      durationMonths: courses.durationMonths,
      photo: courses.photo,
      certificate: courses.certificate,
      teacherName: users.fullName,
      teacherPhoto: teacherProfiles.photo,
      subject: teacherProfiles.subject,
    })
    .from(courses)
    .innerJoin(users, eq(courses.teacherId, users.id))
    .leftJoin(teacherProfiles, eq(teacherProfiles.userId, users.id))
    .where(where)
    .orderBy(asc(courses.id));

  if (rows.length === 0) return [];

  const schedules = await db
    .select()
    .from(courseSchedules)
    .where(inArray(courseSchedules.courseId, rows.map((r) => r.id)))
    .orderBy(asc(courseSchedules.weekday));

  return rows.map((r) => ({
    ...r,
    schedules: schedules
      .filter((s) => s.courseId === r.id)
      .map((s) => ({
        weekday: s.weekday,
        startTime: s.startTime.slice(0, 5),
        endTime: s.endTime.slice(0, 5),
      })),
  }));
}

// Barcha faol kurslar
router.get('/', async (c) => {
  return c.json(await loadCourses(getDb(c.env), eq(courses.isActive, true)));
});

// O'qituvchining o'z kurslari
router.get('/mine/:tgId', async (c) => {
  const db = getDb(c.env);
  const [teacher] = await db.select().from(users)
    .where(eq(users.telegramId, Number(c.req.param('tgId'))));
  if (!teacher) return c.json({ error: 'Topilmadi' }, 404);

  return c.json(await loadCourses(db, and(eq(courses.isActive, true), eq(courses.teacherId, teacher.id))));
});

// Bitta vaqt bandmi? (bot jadval kiritish paytida chaqiradi)
router.post('/check-slot', async (c) => {
  const parsed = slotSchema.safeParse(await c.req.json());
  if (!parsed.success) return c.json({ error: parsed.error.issues[0].message }, 400);

  const conflict = await findConflict(getDb(c.env), parsed.data);
  return c.json({ conflict });
});

// Yangi kurs yaratish
router.post('/', async (c) => {
  const parsed = createCourseSchema.safeParse(await c.req.json());
  if (!parsed.success) {
    return c.json({ error: 'Ma\'lumot noto\'g\'ri', details: parsed.error.issues }, 400);
  }
  const { telegramId, schedules, ...data } = parsed.data;
  const db = getDb(c.env);

  const [teacher] = await db.select().from(users).where(eq(users.telegramId, telegramId));
  if (!teacher || teacher.role !== 'teacher') return c.json({ error: 'Faqat o\'qituvchi kurs yarata oladi' }, 403);

  if (hasInternalOverlap(schedules)) {
    return c.json({ error: 'Kiritilgan vaqtlar bir-biri bilan kesishadi' }, 400);
  }
  // Saqlash paytida qayta tekshiramiz: tekshiruv bilan saqlash orasida boshqa o'qituvchi band qilgan bo'lishi mumkin
  for (const slot of schedules) {
    const conflict = await findConflict(db, slot);
    if (conflict) return c.json({ error: 'Tanlangan vaqt band bo\'lib qolgan', conflict }, 409);
  }

  const [course] = await db.insert(courses).values({ ...data, teacherId: teacher.id }).returning();
  try {
    await db.insert(courseSchedules).values(schedules.map((s) => ({ ...s, courseId: course.id })));
  } catch (err) {
    await db.delete(courses).where(eq(courses.id, course.id)); // tranzaksiya yo'q, qo'lda qaytaramiz
    throw err;
  }
  return c.json(course, 201);
});

// Kursni o'chirish (soft delete)
router.delete('/:id', async (c) => {
  const id = Number(c.req.param('id'));
  const tgId = Number(c.req.query('telegramId'));
  if (!Number.isInteger(id) || !Number.isInteger(tgId)) return c.json({ error: 'Ma\'lumot noto\'g\'ri' }, 400);
  const db = getDb(c.env);

  const [teacher] = await db.select().from(users).where(eq(users.telegramId, tgId));
  if (!teacher) return c.json({ error: 'Topilmadi' }, 404);

  const [course] = await db.select().from(courses)
    .where(and(eq(courses.id, id), eq(courses.teacherId, teacher.id), eq(courses.isActive, true)));
  if (!course) return c.json({ error: 'Kurs topilmadi' }, 404);

  const [{ value }] = await db.select({ value: count() }).from(enrollments)
    .where(and(eq(enrollments.courseId, id), eq(enrollments.status, 'active')));
  if (value > 0) return c.json({ error: `Kursda ${value} ta faol o'quvchi bor, o'chirib bo'lmaydi` }, 409);

  await db.update(courses).set({ isActive: false }).where(eq(courses.id, id));
  return c.json({ ok: true });
});

// O'qituvchining bitta kursidagi o'quvchilar + joriy oy to'lovi
router.get('/:id/students', async (c) => {
  const courseId = Number(c.req.param('id'));
  const tgId = Number(c.req.query('telegramId'));
  if (!Number.isInteger(courseId) || !Number.isInteger(tgId)) return c.json({ error: 'Ma\'lumot noto\'g\'ri' }, 400);
  const db = getDb(c.env);

  const [teacher] = await db.select().from(users).where(eq(users.telegramId, tgId));
  if (!teacher) return c.json({ error: 'Topilmadi' }, 404);

  const [course] = await db.select().from(courses)
    .where(and(eq(courses.id, courseId), eq(courses.teacherId, teacher.id)));
  if (!course) return c.json({ error: 'Kurs topilmadi' }, 404);

  const period = tashkentPeriod();
  await ensurePaymentsForPeriod(db, period);

  const rows = await db
    .select({
      enrollmentId: enrollments.id,
      studentName: users.fullName,
      studentPhone: users.phone,
      amountDue: payments.amountDue,
      amountPaid: payments.amountPaid,
      status: payments.status,
    })
    .from(enrollments)
    .innerJoin(users, eq(enrollments.studentId, users.id))
    .leftJoin(payments, and(eq(payments.enrollmentId, enrollments.id), eq(payments.period, period)))
    .where(and(eq(enrollments.courseId, courseId), eq(enrollments.status, 'active')))
    .orderBy(asc(users.fullName));

  return c.json({ courseTitle: course.title, price: course.price, period, students: rows });
});

export async function loadCoursesByTeacherId(db, teacherId) {
  return loadCourses(db, and(eq(courses.isActive, true), eq(courses.teacherId, teacherId)));
}

// Bugungi davomatni saqlash/yangilash
router.post('/:id/attendance', async (c) => {
  const courseId = Number(c.req.param('id'));
  const parsed = attendanceSchema.safeParse(await c.req.json());
  if (!Number.isInteger(courseId) || !parsed.success) return c.json({ error: 'Ma\'lumot noto\'g\'ri' }, 400);
  const { telegramId, records } = parsed.data;
  const db = getDb(c.env);

  const [teacher] = await db.select().from(users).where(eq(users.telegramId, telegramId));
  if (!teacher) return c.json({ error: 'Topilmadi' }, 404);

  const [course] = await db.select().from(courses)
    .where(and(eq(courses.id, courseId), eq(courses.teacherId, teacher.id)));
  if (!course) return c.json({ error: 'Kurs topilmadi' }, 404);

  // Faqat shu o'qituvchining o'z faol o'quvchilariga tegishli enrollmentId'lar qabul qilinadi
  const own = await db.select({ id: enrollments.id }).from(enrollments)
    .where(and(eq(enrollments.courseId, courseId), eq(enrollments.status, 'active')));
  const ownIds = new Set(own.map((o) => o.id));
  const filtered = records.filter((r) => ownIds.has(r.enrollmentId));
  if (filtered.length === 0) return c.json({ error: 'Bunday o\'quvchilar topilmadi' }, 400);

  const date = tashkentDate();
  for (const r of filtered) {
    await db.insert(attendance)
      .values({ enrollmentId: r.enrollmentId, date, present: r.present })
      .onConflictDoUpdate({ target: [attendance.enrollmentId, attendance.date], set: { present: r.present } });
  }

  return c.json({ ok: true, date, count: filtered.length });
});

export default router;