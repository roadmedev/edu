import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { neon } from '@neondatabase/serverless'

const app = new Hono()

app.use('*', cors())

app.get('/', (c) => c.text('Edu Platform API ishlayapti ✅'))

// Neon'dan test matnini o'qiydi
app.get('/hello', async (c) => {
  try {
    const sql = neon(c.env.DATABASE_URL)
    const rows = await sql`SELECT text FROM messages ORDER BY id LIMIT 1`
    return c.json({ message: rows[0]?.text ?? "Jadval bo'sh" })
  } catch (err) {
    return c.json({ error: String(err) }, 500)
  }
})

app.get('/users/by-telegram/:telegramId', async (c) => {
  try {
    const telegramId = c.req.param('telegramId')
    const sql = neon(c.env.DATABASE_URL)
    const rows = await sql`
      SELECT id, full_name, phone_number, telegram_id
      FROM users
      WHERE telegram_id = ${telegramId}
    `
    if (rows.length === 0) {
      return c.json({ user: null }, 200)
    }
    return c.json({ user: rows[0] })
  } catch (err) {
    return c.json({ error: String(err) }, 500)
  }
})

// Bot/web'dan kelgan foydalanuvchini ro'yxatdan o'tkazadi
app.post('/register', async (c) => {
  try {
    const body = await c.req.json()
    const { full_name, phone_number, telegram_id } = body

    if (!phone_number) {
      return c.json({ error: 'phone_number talab qilinadi' }, 400)
    }

    const sql = neon(c.env.DATABASE_URL)

    // Agar shu telefon raqam  bilan foydalanuvchi bo'lsa, uni yangilaymiz;
    // bo'lmasa, yangi qator qo'shamiz (unified account uchun muhim)
    const rows = await sql`
      INSERT INTO users (full_name, phone_number, telegram_id)
      VALUES (${full_name}, ${phone_number}, ${telegram_id})
      ON CONFLICT (phone_number)
      DO UPDATE SET telegram_id = EXCLUDED.telegram_id, full_name = EXCLUDED.full_name
      RETURNING id, full_name, phone_number, telegram_id
    `

    return c.json({ user: rows[0] })
  } catch (err) {
    return c.json({ error: String(err) }, 500)
  }
})

export default app