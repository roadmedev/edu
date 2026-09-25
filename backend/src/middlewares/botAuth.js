// Faqat bizning bot (yoki keyin web) API'ga murojaat qila olsin
export async function botAuth(c, next) {
  const key = c.req.header('X-Bot-Key');
  if (!key || key !== c.env.BOT_API_KEY) {
    return c.json({ error: 'Ruxsat yoq' }, 401);
  }
  await next();
}