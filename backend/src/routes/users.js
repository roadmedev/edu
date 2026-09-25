import { Hono } from 'hono';
import { eq } from 'drizzle-orm';
import { getDb } from '../db/client.js';
import { users } from '../db/schema.js';
import { registerSchema } from '../validators/users.js';
import { isAdminId } from '../config/roles.js';

const router = new Hono();

// Telegram ID bo'yicha foydalanuvchini olish (bot har xabarda shuni chaqiradi)
router.get('/by-telegram/:tgId', async (c) => {
  const db = getDb(c.env);
  const tgId = Number(c.req.param('tgId'));

  const [user] = await db.select().from(users).where(eq(users.telegramId, tgId));
  if (!user) return c.json({ error: 'Topilmadi' }, 404);

  // Admin ro'yxatiga keyin qo'shilgan bo'lsa ham rolni yangilab qo'yamiz
  if (isAdminId(c.env, tgId) && user.role !== 'admin') {
    const [updated] = await db
      .update(users).set({ role: 'admin' })
      .where(eq(users.id, user.id)).returning();
    return c.json(updated);
  }
  return c.json(user);
});

// Ro'yxatdan o'tish (bir marta)
router.post('/', async (c) => {
  const parsed = registerSchema.safeParse(await c.req.json());
  if (!parsed.success) {
    return c.json({ error: 'Ma\'lumot noto\'g\'ri', details: parsed.error.issues }, 400);
  }
  const { telegramId, fullName, phone } = parsed.data;
  const db = getDb(c.env);

  const [exists] = await db.select({ id: users.id }).from(users)
    .where(eq(users.telegramId, telegramId));
  if (exists) return c.json({ error: 'Allaqachon ro\'yxatdan o\'tgan' }, 409);

  const [created] = await db.insert(users).values({
    telegramId,
    fullName,
    phone: phone.startsWith('+') ? phone : `+${phone}`,
    role: isAdminId(c.env, telegramId) ? 'admin' : 'user',
  }).returning();

  return c.json(created, 201);
});

export default router;