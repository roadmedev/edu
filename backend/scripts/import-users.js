// ikkinchi neon.tech bazadan users jadvalidagi ma'lumotlarni tortib olish

import 'dotenv/config';
import { neon } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-http';
import { inArray } from 'drizzle-orm';
import * as s from '../src/db/schema.js';

const oldSql = neon(process.env.OLD_DATABASE_URL);
const db = drizzle(neon(process.env.DATABASE_URL), { schema: s });

const ROLES = ['admin', 'teacher', 'user'];
const normPhone = (p) => {
  const digits = String(p || '').replace(/\D/g, '');
  return digits ? `+${digits}` : '+000000000';
};

// Eski jadval nomi `users` deb faraz qilindi
const rows = await oldSql`
  select full_name, phone_number, telegram_id, created_at, role
  from users order by id`;

let added = 0, skipped = 0;
const teacherTgIds = [];

for (const r of rows) {
  const telegramId = Number(r.telegram_id);
  const role = ROLES.includes(r.role) ? r.role : 'user';

  const inserted = await db.insert(s.users).values({
    telegramId,
    fullName: String(r.full_name).trim(),
    phone: normPhone(r.phone_number),
    role,
    createdAt: new Date(r.created_at),
  }).onConflictDoNothing({ target: s.users.telegramId }).returning({ id: s.users.id });

  if (inserted.length) added++; else skipped++;
  if (role === 'teacher') teacherTgIds.push(telegramId);
}

// O'qituvchilar uchun bo'sh profil (allaqachon bo'lsa tegmaydi)
if (teacherTgIds.length) {
  const teachers = await db.select({ id: s.users.id }).from(s.users)
    .where(inArray(s.users.telegramId, teacherTgIds));
  for (const t of teachers) {
    await db.insert(s.teacherProfiles).values({ userId: t.id })
      .onConflictDoNothing({ target: s.teacherProfiles.userId });
  }
}

console.log(`Eski bazada: ${rows.length} | qo'shildi: ${added} | o'tkazib yuborildi: ${skipped}`);