import { jwtVerify } from 'jose';

export async function webAuth(c, next) {
  const header = c.req.header('Authorization') || '';
  const token = header.startsWith('Bearer ') ? header.slice(7) : null;
  if (!token) return c.json({ error: 'Tizimga kiring' }, 401);

  try {
    const secret = new TextEncoder().encode(c.env.JWT_SECRET);
    const { payload } = await jwtVerify(token, secret);
    c.set('telegramId', payload.telegramId);
    c.set('role', payload.role);
    await next();
  } catch {
    return c.json({ error: 'Sessiya muddati tugagan, qayta kiring' }, 401);
  }
}