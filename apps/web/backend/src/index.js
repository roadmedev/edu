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

app.get('/admin/finance', async (c) => {
  try {
    const sql = neon(c.env.DATABASE_URL)

    const [income] = await sql`
      SELECT COALESCE(SUM(amount), 0)::numeric AS total
      FROM payments
      WHERE date_trunc('month', month) = date_trunc('month', CURRENT_DATE)
    `
    const [expense] = await sql`
      SELECT COALESCE(SUM(amount), 0)::numeric AS total
      FROM expenses
      WHERE date_trunc('month', spent_at) = date_trunc('month', CURRENT_DATE)
    `
    const [debt] = await sql`
      SELECT COALESCE(SUM(c.price), 0)::numeric AS total
      FROM enrollments e
      JOIN courses c ON c.id = e.course_id
      WHERE e.status = 'qarzdor'
    `

    return c.json({
      income: income.total,
      expense: expense.total,
      net_profit: Number(income.total) - Number(expense.total),
      debt: debt.total,
    })
  } catch (err) {
    return c.json({ error: String(err) }, 500)
  }
})

app.get('/admin/finance/history', async (c) => {
  try {
    const type = c.req.query('type') // 'income' yoki 'expense'
    const sql = neon(c.env.DATABASE_URL)

    const rows =
      type === 'expense'
        ? await sql`
            SELECT to_char(spent_at, 'YYYY-MM') AS month, SUM(amount)::numeric AS total
            FROM expenses
            GROUP BY month
            ORDER BY month DESC
            LIMIT 6
          `
        : await sql`
            SELECT to_char(month, 'YYYY-MM') AS month, SUM(amount)::numeric AS total
            FROM payments
            GROUP BY month
            ORDER BY month DESC
            LIMIT 6
          `

    return c.json({ history: rows })
  } catch (err) {
    return c.json({ error: String(err) }, 500)
  }
})


app.get('/admin/teachers', async (c) => {
  try {
    const sql = neon(c.env.DATABASE_URL)
    const rows = await sql`
      SELECT id, full_name, degree, subject_id
      FROM teachers
      WHERE is_active = true
      ORDER BY full_name
    `
    return c.json({ teachers: rows })
  } catch (err) {
    return c.json({ error: String(err) }, 500)
  }
})

app.get('/admin/teachers/:id', async (c) => {
  try {
    const teacherId = c.req.param('id')
    const sql = neon(c.env.DATABASE_URL)

    const [teacher] = await sql`
      SELECT t.id, t.full_name, t.degree, t.certificate_info, t.salary, s.name AS subject_name
      FROM teachers t
      LEFT JOIN subjects s ON s.id = t.subject_id
      WHERE t.id = ${teacherId}
    `

    if (!teacher) {
      return c.json({ error: 'Topilmadi' }, 404)
    }

    const [groupCount] = await sql`
      SELECT COUNT(*)::int AS count FROM groups WHERE teacher_id = ${teacherId}
    `
    const [studentCount] = await sql`
      SELECT COUNT(DISTINCT e.user_id)::int AS count
      FROM enrollments e
      JOIN courses c ON c.id = e.course_id
      WHERE c.teacher_id = ${teacherId}
    `

    return c.json({
      ...teacher,
      groups_count: groupCount.count,
      students_count: studentCount.count,
    })
  } catch (err) {
    return c.json({ error: String(err) }, 500)
  }
})


// 1-bosqich: barcha fanlar
app.get('/admin/subjects', async (c) => {
  try {
    const sql = neon(c.env.DATABASE_URL)
    const rows = await sql`SELECT id, name FROM subjects ORDER BY name`
    return c.json({ subjects: rows })
  } catch (err) {
    return c.json({ error: String(err) }, 500)
  }
})

// 2-bosqich: tanlangan fan bo'yicha guruhlar
app.get('/admin/subjects/:id/groups', async (c) => {
  try {
    const subjectId = c.req.param('id')
    const sql = neon(c.env.DATABASE_URL)
    const rows = await sql`
      SELECT g.id, g.name, t.full_name AS teacher_name
      FROM groups g
      LEFT JOIN teachers t ON t.id = g.teacher_id
      WHERE g.subject_id = ${subjectId}
      ORDER BY g.name
    `
    return c.json({ groups: rows })
  } catch (err) {
    return c.json({ error: String(err) }, 500)
  }
})

// 3-bosqich: tanlangan guruhdagi o'quvchilar
app.get('/admin/groups/:id/students', async (c) => {
  try {
    const groupId = c.req.param('id')
    const sql = neon(c.env.DATABASE_URL)
    const rows = await sql`
      SELECT DISTINCT u.id, u.full_name
      FROM enrollments e
      JOIN courses c ON c.id = e.course_id
      JOIN users u ON u.id = e.user_id
      WHERE c.group_id = ${groupId}
      ORDER BY u.full_name
    `
    return c.json({ students: rows })
  } catch (err) {
    return c.json({ error: String(err) }, 500)
  }
})

// 4-bosqich: bitta o'quvchi bo'yicha to'liq ma'lumot
app.get('/admin/students/:id', async (c) => {
  try {
    const studentId = c.req.param('id')
    const sql = neon(c.env.DATABASE_URL)

    const [student] = await sql`
      SELECT id, full_name, phone_number FROM users WHERE id = ${studentId}
    `
    if (!student) {
      return c.json({ error: 'Topilmadi' }, 404)
    }

    const [attendance] = await sql`
      SELECT
        COUNT(*) FILTER (WHERE present = true)::int AS present,
        COUNT(*)::int AS total
      FROM attendance
      WHERE user_id = ${studentId}
    `

    const enrollments = await sql`
      SELECT c.title, e.status
      FROM enrollments e
      JOIN courses c ON c.id = e.course_id
      WHERE e.user_id = ${studentId}
    `

    return c.json({
      ...student,
      attendance: `${attendance.present}/${attendance.total}`,
      enrollments,
    })
  } catch (err) {
    return c.json({ error: String(err) }, 500)
  }
})


// Joriy oyda to'lov qilgan o'quvchilar
app.get('/admin/payments/paid', async (c) => {
  try {
    const sql = neon(c.env.DATABASE_URL)
    const rows = await sql`
      SELECT DISTINCT ON (u.id) u.id, u.full_name, u.phone_number, p.amount, p.paid_at
      FROM payments p
      JOIN users u ON u.id = p.user_id
      WHERE date_trunc('month', p.month) = date_trunc('month', CURRENT_DATE)
      ORDER BY u.id, p.paid_at DESC
    `
    return c.json({ students: rows })
  } catch (err) {
    return c.json({ error: String(err) }, 500)
  }
})

// Qarzdorlar
app.get('/admin/payments/debtors', async (c) => {
  try {
    const sql = neon(c.env.DATABASE_URL)
    const rows = await sql`
      SELECT u.id, u.full_name, u.phone_number, c.title AS course_title, c.price
      FROM enrollments e
      JOIN users u ON u.id = e.user_id
      JOIN courses c ON c.id = e.course_id
      WHERE e.status = 'qarzdor'
      ORDER BY u.full_name
    `
    return c.json({ students: rows })
  } catch (err) {
    return c.json({ error: String(err) }, 500)
  }
})


// Yangi o'qituvchi qo'shish
app.post('/admin/teachers', async (c) => {
  try {
    const body = await c.req.json()
    const { full_name, degree, subject_id, certificate_info, salary } = body

    if (!full_name) {
      return c.json({ error: 'full_name talab qilinadi' }, 400)
    }

    const sql = neon(c.env.DATABASE_URL)
    const rows = await sql`
      INSERT INTO teachers (full_name, degree, subject_id, certificate_info, salary)
      VALUES (${full_name}, ${degree}, ${subject_id}, ${certificate_info}, ${salary || 0})
      RETURNING id, full_name
    `
    return c.json({ teacher: rows[0] })
  } catch (err) {
    return c.json({ error: String(err) }, 500)
  }
})

// O'qituvchini tahrirlash (bitta maydonni yangilash)
app.put('/admin/teachers/:id', async (c) => {
  try {
    const teacherId = c.req.param('id')
    const body = await c.req.json()
    const { field, value } = body

    const allowedFields = ['full_name', 'degree', 'certificate_info', 'salary']
    if (!allowedFields.includes(field)) {
      return c.json({ error: "Ruxsat etilmagan maydon" }, 400)
    }

    const sql = neon(c.env.DATABASE_URL)
    const rows = await sql`
      UPDATE teachers SET ${sql(field)} = ${value}
      WHERE id = ${teacherId}
      RETURNING id, full_name
    `
    return c.json({ teacher: rows[0] })
  } catch (err) {
    return c.json({ error: String(err) }, 500)
  }
})

// O'qituvchini o'chirish (soft delete — is_active=false)
app.delete('/admin/teachers/:id', async (c) => {
  try {
    const teacherId = c.req.param('id')
    const sql = neon(c.env.DATABASE_URL)
    await sql`UPDATE teachers SET is_active = false WHERE id = ${teacherId}`
    return c.json({ success: true })
  } catch (err) {
    return c.json({ error: String(err) }, 500)
  }
})

app.get('/courses/:id', async (c) => {
  try {
    const courseId = c.req.param('id')
    const sql = neon(c.env.DATABASE_URL)

    const [course] = await sql`
      SELECT
        c.id, c.title, c.description, c.price,
        t.full_name AS teacher_name, t.photo_url AS teacher_photo,
        t.degree AS teacher_degree, t.certificate_info AS teacher_certificate
      FROM courses c
      LEFT JOIN teachers t ON t.id = c.teacher_id
      WHERE c.id = ${courseId}
    `

    if (!course) {
      return c.json({ error: 'Topilmadi' }, 404)
    }

    return c.json({ course })
  } catch (err) {
    return c.json({ error: String(err) }, 500)
  }
})

app.post('/enroll', async (c) => {
  try {
    const body = await c.req.json()
    const { telegram_id, course_id } = body

    if (!telegram_id || !course_id) {
      return c.json({ error: 'telegram_id va course_id talab qilinadi' }, 400)
    }

    const sql = neon(c.env.DATABASE_URL)

    const [user] = await sql`SELECT id FROM users WHERE telegram_id = ${telegram_id}`
    if (!user) {
      return c.json({ error: 'Foydalanuvchi topilmadi' }, 404)
    }

    const rows = await sql`
      INSERT INTO enrollments (user_id, course_id, status)
      VALUES (${user.id}, ${course_id}, 'qarzdor')
      ON CONFLICT (user_id, course_id) DO NOTHING
      RETURNING id
    `

    if (rows.length === 0) {
      return c.json({ already_enrolled: true })
    }

    return c.json({ success: true, enrollment_id: rows[0].id })
  } catch (err) {
    return c.json({ error: String(err) }, 500)
  }
})

export default app