import { Hono } from 'hono';
import { eq } from 'drizzle-orm';
import { getDb } from '../db/client.js';
import { suggestions, users } from '../db/schema.js';
import { suggestionSchema } from '../validators/suggestions.js';

const router = new Hono();

router.post('/', async (c) => {
  const parsed = suggestionSchema.safeParse(await c.req.json());
  if (!parsed.success) return c.json({ error: 'Ma\'lumot noto\'g\'ri' }, 400);
  const db = getDb(c.env);

  const [user] = await db.select().from(users).where(eq(users.telegramId, parsed.data.telegramId));
  if (!user) return c.json({ error: 'Foydalanuvchi topilmadi' }, 404);

  const [created] = await db.insert(suggestions)
    .values({ fromUserId: user.id, text: parsed.data.text }).returning();
  return c.json(created, 201);
});

export default router;