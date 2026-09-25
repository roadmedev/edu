import {
    pgTable, pgEnum, serial, integer, bigint, text, boolean, 
    timestamp, time, date, unique } from 'drizzle-orm/pg-core';

// ---------Enumlar -----------------
export const roleEnum = pgEnum('role', ['admin', 'teacher', 'user', 'student']);
export const enrollmentStatusEnum = pgEnum('enrollment_status', [
    'pending', // user so'rov yubordi
    'accepted', // o'qituvchi qabul qildi, user shartlarni hali qabul qilmagan
    'active',  // user shartlarni qabul qildi , endi u o'quvchi
    'rejected', // o'qituvchi rad qildi
]);
export const payStatusEnum = pgEnum('pay_status', ['unpaid', 'partial', 'paid']);

// --------------Foydalananuvchilar-----------------
export const users = pgTable('users', {
    id: serial('id').primaryKey(),
    telegramId: bigint('telegram_id', { mode: 'number' }).notNull().unique(),
    fullName: text('full_name').notNull(),
    phone: text('phone').notNull(),
    role: roleEnum('role').notNull().default('user'),
    createdAt: timestamp('created_at').notNull().defaultNow(),
});

// --------------O'qituvchi profili----------------------
export const teacherProfiles = pgTable('teacher_profiles', {
  id: serial('id').primaryKey(),
  userId: integer('user_id').notNull().unique().references(() => users.id, { onDelete: 'cascade' }),
  photo: text('photo'),            // Telegram file_id
  subject: text('subject'),        // qaysi fandan
  bio: text('bio'),
  certificate: text('certificate'), // Telegram file_id (ixtiyoriy)
});

// ---------- Kurslar ----------
export const courses = pgTable('courses', {
  id: serial('id').primaryKey(),
  teacherId: integer('teacher_id').notNull().references(() => users.id),
  title: text('title').notNull(),
  description: text('description').notNull(),
  price: integer('price').notNull(),                 // oyiga, so'mda
  durationMonths: integer('duration_months').notNull().default(3),
  photo: text('photo'),
  certificate: text('certificate'),
  isActive: boolean('is_active').notNull().default(true),
  createdAt: timestamp('created_at').notNull().defaultNow(),
});

// ---------- Dars jadvali (xona bitta, shuning uchun markaz bo'yicha tekshiriladi) ----------
export const courseSchedules = pgTable('course_schedules', {
  id: serial('id').primaryKey(),
  courseId: integer('course_id').notNull().references(() => courses.id, { onDelete: 'cascade' }),
  weekday: integer('weekday').notNull(),   // 1 = Dushanba ... 7 = Yakshanba
  startTime: time('start_time').notNull(),
  endTime: time('end_time').notNull(),
});

// ---------- Kursga yozilish ----------
export const enrollments = pgTable('enrollments', {
  id: serial('id').primaryKey(),
  courseId: integer('course_id').notNull().references(() => courses.id, { onDelete: 'cascade' }),
  studentId: integer('student_id').notNull().references(() => users.id),
  status: enrollmentStatusEnum('status').notNull().default('pending'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  joinedAt: timestamp('joined_at'),
}, (t) => [unique().on(t.courseId, t.studentId)]);

// ---------- Kunlik so'rov limiti (kuniga 1 ta) ----------
export const joinRequests = pgTable('join_requests', {
  id: serial('id').primaryKey(),
  userId: integer('user_id').notNull().references(() => users.id),
  requestDate: date('request_date').notNull(),   // Toshkent vaqti bo'yicha sana
  createdAt: timestamp('created_at').notNull().defaultNow(),
}, (t) => [unique().on(t.userId, t.requestDate)]);  // bazaning o'zi limitni ta'minlaydi

// ---------- Talaba to'lovlari (oylik) ----------
export const payments = pgTable('payments', {
  id: serial('id').primaryKey(),
  enrollmentId: integer('enrollment_id').notNull().references(() => enrollments.id, { onDelete: 'cascade' }),
  period: text('period').notNull(),              // '2026-09'
  amountDue: integer('amount_due').notNull(),
  amountPaid: integer('amount_paid').notNull().default(0),
  status: payStatusEnum('status').notNull().default('unpaid'),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
}, (t) => [unique().on(t.enrollmentId, t.period)]);

// ---------- Admin -> o'qituvchi to'lovlari (30% ulush hisobi) ----------
export const teacherPayouts = pgTable('teacher_payouts', {
  id: serial('id').primaryKey(),
  teacherId: integer('teacher_id').notNull().references(() => users.id),
  period: text('period').notNull(),
  amountDue: integer('amount_due').notNull(),
  amountPaid: integer('amount_paid').notNull().default(0),
  status: payStatusEnum('status').notNull().default('unpaid'),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
}, (t) => [unique().on(t.teacherId, t.period)]);

// ---------- Takliflar ----------
export const suggestions = pgTable('suggestions', {
  id: serial('id').primaryKey(),
  fromUserId: integer('from_user_id').notNull().references(() => users.id),
  text: text('text').notNull(),
  createdAt: timestamp('created_at').notNull().defaultNow(),
});

// ---------- Davomat ----------
export const attendance = pgTable('attendance', {
  id: serial('id').primaryKey(),
  enrollmentId: integer('enrollment_id').notNull().references(() => enrollments.id, { onDelete: 'cascade' }),
  date: date('date').notNull(),
  present: boolean('present').notNull().default(true),
}, (t) => [unique().on(t.enrollmentId, t.date)]);