import { Hono } from 'hono';
import { SignJWT } from 'jose';
import { and, desc, eq, gt } from 'drizzle-orm';
import { getDb } from '../db/client.js';
import { otpCodes, users } from '../db/schema.js';
import { requestOtpSchema, verifyOtpSchema } from '../validators/auth.js';
import { normalizePhone } from '../utils/phone.js';
import { sendTelegramMessage } from '../services/telegramApi.js';

const router = new Hono();

const OTP_TTL_MS = 5 * 60 * 1000;
const COOLDOWN_MS = 60 * 1000;

// 1-qadam: telefon bo'yicha kod yuborish
router.post('/request-otp', async (c) => {
  const parsed = requestOtpSchema.safeParse(await c.req.json());
  if (!parsed.success) return c.json({ error: 'Telefon raqam noto\'g\'ri' }, 400);
  const phone = normalizePhone(parsed.data.phone);
  const db = getDb(c.env);

  const [user] = await db.select().from(users).where(eq(users.phone, phone));
  if (!user) {
    return c.json({
      error: 'Bu raqam ro\'yxatdan o\'tmagan. Avval Telegram botimizda ro\'yxatdan o\'ting.',
      botUsername: c.env.BOT_USERNAME,
    }, 404);
  }

  // Spamdan himoya: 60 soniyada bir marta
  const [recent] = await db.select().from(otpCodes)
    .where(eq(otpCodes.phone, phone)).orderBy(desc(otpCodes.createdAt)).limit(1);
  if (recent && Date.now() - new Date(recent.createdAt).getTime() < COOLDOWN_MS) {
    return c.json({ error: 'Iltimos, biroz kuting va qayta urinib ko\'ring' }, 429);
  }

  const code = String(Math.floor(100000 + Math.random() * 900000));
  await db.insert(otpCodes).values({
    phone, code, telegramId: user.telegramId,
    expiresAt: new Date(Date.now() + OTP_TTL_MS),
  });

  try {
    await sendTelegramMessage(
      c.env.BOT_TOKEN, user.telegramId,
      `🔐 Kirish kodi: <b>${code}</b>\n\n5 daqiqa davomida amal qiladi. Hech kimga aytmang.`,
    );
  } catch {
    return c.json({ error: 'Kodni yuborib bo\'lmadi. Avval botga /start bosganingizga ishonch hosil qiling.' }, 502);
  }

  return c.json({ ok: true });
});

// 2-qadam: kodni tekshirish -> JWT
router.post('/verify-otp', async (c) => {
  const parsed = verifyOtpSchema.safeParse(await c.req.json());
  if (!parsed.success) return c.json({ error: 'Ma\'lumot noto\'g\'ri' }, 400);
  const phone = normalizePhone(parsed.data.phone);
  const db = getDb(c.env);

  const [otp] = await db.select().from(otpCodes).where(and(
    eq(otpCodes.phone, phone),
    eq(otpCodes.code, parsed.data.code),
    eq(otpCodes.used, false),
    gt(otpCodes.expiresAt, new Date()),
  ));
  if (!otp) return c.json({ error: 'Kod noto\'g\'ri yoki muddati tugagan' }, 401);

  await db.update(otpCodes).set({ used: true }).where(eq(otpCodes.id, otp.id));

  const [user] = await db.select().from(users).where(eq(users.phone, phone));
  if (!user) return c.json({ error: 'Foydalanuvchi topilmadi' }, 404);

  const secret = new TextEncoder().encode(c.env.JWT_SECRET);
  const token = await new SignJWT({ telegramId: user.telegramId, role: user.role, fullName: user.fullName })
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime('30d')
    .sign(secret);

  return c.json({ token, role: user.role, fullName: user.fullName });
});

export default router;