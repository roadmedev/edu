import { and, eq, gt, lt } from 'drizzle-orm';
import { courses, courseSchedules } from '../db/schema.js';

// Markaz bo'yicha (xona bitta) kesishuvchi dars bormi?
export async function findConflict(db, { weekday, startTime, endTime }) {
  const [row] = await db
    .select({
      title: courses.title,
      startTime: courseSchedules.startTime,
      endTime: courseSchedules.endTime,
    })
    .from(courseSchedules)
    .innerJoin(courses, eq(courseSchedules.courseId, courses.id))
    .where(and(
      eq(courses.isActive, true),
      eq(courseSchedules.weekday, weekday),
      lt(courseSchedules.startTime, endTime),
      gt(courseSchedules.endTime, startTime),
    ))
    .limit(1);

  return row
    ? { title: row.title, startTime: row.startTime.slice(0, 5), endTime: row.endTime.slice(0, 5) }
    : null;
}

// Yangi kursning o'z ichidagi vaqtlari bir-biri bilan kesishmasin ('HH:MM' matn sifatida to'g'ri solishtiriladi)
export function hasInternalOverlap(slots) {
  for (let i = 0; i < slots.length; i++) {
    for (let j = i + 1; j < slots.length; j++) {
      const a = slots[i], b = slots[j];
      if (a.weekday === b.weekday && a.startTime < b.endTime && a.endTime > b.startTime) return true;
    }
  }
  return false;
}