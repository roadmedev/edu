import 'dotenv/config';
import { neon } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-http';
import { eq } from 'drizzle-orm';
import * as s from '../src/db/schema.js';

const db = drizzle(neon(process.env.DATABASE_URL), { schema: s });
const TEACHER_TG_ID = Number(process.argv[2] || 1000000001); // haqiqiy o'qituvchi ID'ni berishingiz mumkin

let [teacher] = await db.select().from(s.users).where(eq(s.users.telegramId, TEACHER_TG_ID));
if (!teacher) {
  [teacher] = await db.insert(s.users).values({
    telegramId: TEACHER_TG_ID, fullName: "Ro'zmetov Mohirbek", phone: '+998901112233', role: 'teacher',
  }).returning();
  await db.insert(s.teacherProfiles).values({
    userId: teacher.id, subject: 'Kompyuter savodxonligi', bio: 'Tajribali o\'qituvchi',
  });
}

const data = [
  { title: 'Kompyuter Savodxonligi', description: 'Windows, Office, internet va xavfsizlik asoslari.',
    price: 400000, days: [2, 4, 6], start: '14:00', end: '17:00' },
  { title: 'Ingliz tili (Beginner)', description: 'Noldan boshlab ingliz tili.',
    price: 350000, days: [1, 3, 5], start: '09:00', end: '11:00' },
];

for (const d of data) {
  const [c] = await db.insert(s.courses).values({
    teacherId: teacher.id, title: d.title, description: d.description, price: d.price,
  }).returning();
  await db.insert(s.courseSchedules).values(
    d.days.map((w) => ({ courseId: c.id, weekday: w, startTime: d.start, endTime: d.end })),
  );
}
console.log('Tayyor: 2 ta kurs qo\'shildi');