// src/routes/public.js
import { Hono } from 'hono'
import { getDb } from '../db.js'
import { ok, badRequest, notFound, serverError } from '../utils/response.js'

const router = new Hono()

// Health check
router.get('/', (c) => c.text('Edu Platform API ishlayapti ✅'))

// Barcha kurslar
router.get('/courses', async (c) => {
  try {
    const sql = getDb(c.env)
    const rows = await sql`
      SELECT id, title, description, price, teacher_id 
      FROM courses 
      ORDER BY id
    `
    return ok(c, { courses: rows })
  } catch (err) {
    return serverError(c, err)
  }
})

// Bitta kurs
router.get('/courses/:id', async (c) => {
  try {
    const courseId = c.req.param('id')
    const sql = getDb(c.env)

    const [course] = await sql`
      SELECT
        c.id, c.title, c.description, c.price,
        t.full_name AS teacher_name, t.photo_url AS teacher_photo,
        t.degree AS teacher_degree, t.certificate_info AS teacher_certificate
      FROM courses c
      LEFT JOIN teachers t ON t.id = c.teacher_id
      WHERE c.id = ${courseId}
    `

    if (!course) return notFound(c, 'Kurs topilmadi')

    return ok(c, { course })
  } catch (err) {
    return serverError(c, err)
  }
})

// Foydalanuvchi telegram_id bo'yicha
router.get('/users/by-telegram/:telegramId', async (c) => {
  try {
    const telegramId = c.req.param('telegramId')
    const sql = getDb(c.env)

    const rows = await sql`
      SELECT id, full_name, phone_number, telegram_id, role
      FROM users
      WHERE telegram_id = ${telegramId}
    `

    if (rows.length === 0) return ok(c, { user: null })
    return ok(c, { user: rows[0] })
  } catch (err) {
    return serverError(c, err)
  }
})

// Ro'yxatdan o'tish
router.post('/register', async (c) => {
  try {
    const { full_name, phone_number, telegram_id } = await c.req.json()

    if (!phone_number) return badRequest(c, 'phone_number talab qilinadi')

    const sql = getDb(c.env)

    const rows = await sql`
      INSERT INTO users (full_name, phone_number, telegram_id)
      VALUES (${full_name}, ${phone_number}, ${telegram_id})
      ON CONFLICT (phone_number)
      DO UPDATE SET telegram_id = EXCLUDED.telegram_id, full_name = EXCLUDED.full_name
      RETURNING id, full_name, phone_number, telegram_id, role
    `

    return ok(c, { user: rows[0] })
  } catch (err) {
    return serverError(c, err)
  }
})

export default router