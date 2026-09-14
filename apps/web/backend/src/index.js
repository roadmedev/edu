import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { neon } from '@neondatabase/serverless'

const app = new Hono()

app.use('*', cors())

app.get('/', (c) => c.text('Edu Platform API ishlayapti ✅'))

// Barcha kurslarni qaytaradi
app.get('/courses', async (c) => {
  try {
    const sql = neon(c.env.DATABASE_URL)
    const rows = await sql`SELECT id, title, description FROM courses ORDER BY id`
    return c.json({ courses: rows })
  } catch (err) {
    return c.json({ error: String(err) }, 500)
  }
})


app.get('/users/by-telegram/:telegramId', async (c) => {
  try {
    const telegramId = c.req.param('telegramId')
    const sql = neon(c.env.DATABASE_URL)
    const rows = await sql`
      SELECT id, full_name, phone_number, telegram_id, role
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

app.get('/admin/stats', async (c) => {
  try {
    const sql = neon(c.env.DATABASE_URL)

    const [subjects] = await sql`SELECT COUNT(*)::int AS count FROM subjects`
    const [teachers] = await sql`SELECT COUNT(*)::int AS count FROM teachers WHERE is_active = true`
    const [groups] = await sql`SELECT COUNT(*)::int AS count FROM groups`
    const [students] = await sql`SELECT COUNT(*)::int AS count FROM users WHERE role = 'student'`

    const [todayLessons] = await sql`
      SELECT COUNT(DISTINCT group_id)::int AS count
      FROM attendance
      WHERE lesson_date = CURRENT_DATE
    `
    const [todayAttendance] = await sql`
      SELECT
        COUNT(*) FILTER (WHERE present = true)::int AS present,
        COUNT(*)::int AS total
      FROM attendance
      WHERE lesson_date = CURRENT_DATE
    `

    const [monthPayments] = await sql`
      SELECT COALESCE(SUM(amount), 0)::numeric AS total
      FROM payments
      WHERE date_trunc('month', month) = date_trunc('month', CURRENT_DATE)
    `
    const [debtors] = await sql`
      SELECT COUNT(*)::int AS count
      FROM enrollments
      WHERE status = 'qarzdor'
    `

    return c.json({
      subjects: subjects.count,
      teachers: teachers.count,
      groups: groups.count,
      students: students.count,
      today_lessons: todayLessons.count,
      today_attendance: `${todayAttendance.present}/${todayAttendance.total}`,
      month_payments: monthPayments.total,
      debtors: debtors.count,
    })
  } catch (err) {
    return c.json({ error: String(err) }, 500)
  }
})

export default app