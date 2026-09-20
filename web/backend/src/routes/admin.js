// src/routes/admin.js
import { Hono } from 'hono'
import { getDb } from '../db.js'
import { ok, badRequest, notFound, serverError } from '../utils/response.js'

const router = new Hono()

// ============ STATISTIKA ============
router.get('/stats', async (c) => {
  try {
    const sql = getDb(c.env)

    const [subjects] = await sql`SELECT COUNT(*)::int AS count FROM subjects`
    const [teachers] = await sql`SELECT COUNT(*)::int AS count FROM teachers WHERE is_active = true`
    const [groups] = await sql`SELECT COUNT(*)::int AS count FROM groups`
    const [students] = await sql`SELECT COUNT(*)::int AS count FROM users WHERE role = 'user'`

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

    return ok(c, {
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
    return serverError(c, err)
  }
})

// ============ MOLIYA ============
router.get('/finance', async (c) => {
  try {
    const sql = getDb(c.env)

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
    const [adminShare] = await sql`
      SELECT COALESCE(SUM(total_admin_share), 0)::numeric AS total
      FROM admin_total_monthly_share
      WHERE month = date_trunc('month', CURRENT_DATE)::date
    `

    return ok(c, {
      income: income.total,
      expense: expense.total,
      net_profit: Number(income.total) - Number(expense.total),
      debt: debt.total,
      admin_share: adminShare.total,
    })
  } catch (err) {
    return serverError(c, err)
  }
})

router.get('/finance/history', async (c) => {
  try {
    const type = c.req.query('type')
    const sql = getDb(c.env)

    const rows = type === 'expense'
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

    return ok(c, { history: rows })
  } catch (err) {
    return serverError(c, err)
  }
})

// 30% ulush hisoboti
router.get('/finance/shares', async (c) => {
  try {
    const sql = getDb(c.env)

    const rows = await sql`
      SELECT * FROM teacher_monthly_income
      ORDER BY month DESC, teacher_name
    `
    const [total] = await sql`
      SELECT 
        COALESCE(SUM(gross_income), 0)::numeric AS total_gross,
        COALESCE(SUM(admin_share), 0)::numeric AS total_admin,
        COALESCE(SUM(teacher_share), 0)::numeric AS total_teacher
      FROM teacher_monthly_income
      WHERE month = date_trunc('month', CURRENT_DATE)::date
    `

    return ok(c, {
      teachers: rows,
      current_month: total,
    })
  } catch (err) {
    return serverError(c, err)
  }
})

// ============ O'QITUVCHILAR ============
router.get('/teachers', async (c) => {
  try {
    const sql = getDb(c.env)
    const rows = await sql`
      SELECT t.id, t.full_name, t.degree, t.subject_id, t.photo_url, s.name AS subject_name
      FROM teachers t
      LEFT JOIN subjects s ON s.id = t.subject_id
      WHERE t.is_active = true
      ORDER BY t.full_name
    `
    return ok(c, { teachers: rows })
  } catch (err) {
    return serverError(c, err)
  }
})

router.get('/teachers/:id', async (c) => {
  try {
    const teacherId = c.req.param('id')
    const sql = getDb(c.env)

    const [teacher] = await sql`
      SELECT t.id, t.full_name, t.degree, t.certificate_info, t.salary, 
             t.photo_url, t.subject_id, t.user_id, s.name AS subject_name
      FROM teachers t
      LEFT JOIN subjects s ON s.id = t.subject_id
      WHERE t.id = ${teacherId}
    `

    if (!teacher) return notFound(c, 'O\'qituvchi topilmadi')

    const [groupCount] = await sql`
      SELECT COUNT(*)::int AS count FROM groups WHERE teacher_id = ${teacherId}
    `
    const [studentCount] = await sql`
      SELECT COUNT(DISTINCT e.user_id)::int AS count
      FROM enrollments e
      JOIN courses c ON c.id = e.course_id
      WHERE c.teacher_id = ${teacherId}
    `

    return ok(c, {
      ...teacher,
      groups_count: groupCount.count,
      students_count: studentCount.count,
    })
  } catch (err) {
    return serverError(c, err)
  }
})

router.post('/teachers', async (c) => {
  try {
    const body = await c.req.json()
    const { full_name, degree, subject_id, certificate_info, salary, photo_url, user_id } = body

    if (!full_name) return badRequest(c, 'full_name talab qilinadi')

    const sql = getDb(c.env)
    const rows = await sql`
      INSERT INTO teachers (full_name, degree, subject_id, certificate_info, salary, photo_url, user_id)
      VALUES (${full_name}, ${degree}, ${subject_id}, ${certificate_info}, ${salary || 0}, ${photo_url}, ${user_id})
      RETURNING id, full_name
    `
    return ok(c, { teacher: rows[0] })
  } catch (err) {
    return serverError(c, err)
  }
})

router.put('/teachers/:id', async (c) => {
  try {
    const teacherId = c.req.param('id')
    const { field, value } = await c.req.json()

    const allowedFields = ['full_name', 'degree', 'certificate_info', 'salary', 'photo_url', 'subject_id']
    if (!allowedFields.includes(field)) {
      return badRequest(c, 'Ruxsat etilmagan maydon')
    }

    const sql = getDb(c.env)
    const rows = await sql`
      UPDATE teachers SET ${sql(field)} = ${value}
      WHERE id = ${teacherId}
      RETURNING id, full_name
    `
    return ok(c, { teacher: rows[0] })
  } catch (err) {
    return serverError(c, err)
  }
})

router.delete('/teachers/:id', async (c) => {
  try {
    const teacherId = c.req.param('id')
    const sql = getDb(c.env)
    await sql`UPDATE teachers SET is_active = false WHERE id = ${teacherId}`
    return ok(c, { success: true })
  } catch (err) {
    return serverError(c, err)
  }
})

// ============ FANLAR VA GURUHLAR ============
router.get('/subjects', async (c) => {
  try {
    const sql = getDb(c.env)
    const rows = await sql`SELECT id, name FROM subjects ORDER BY name`
    return ok(c, { subjects: rows })
  } catch (err) {
    return serverError(c, err)
  }
})

router.get('/subjects/:id/groups', async (c) => {
  try {
    const subjectId = c.req.param('id')
    const sql = getDb(c.env)
    const rows = await sql`
      SELECT g.id, g.name, t.full_name AS teacher_name
      FROM groups g
      LEFT JOIN teachers t ON t.id = g.teacher_id
      WHERE g.subject_id = ${subjectId}
      ORDER BY g.name
    `
    return ok(c, { groups: rows })
  } catch (err) {
    return serverError(c, err)
  }
})

router.get('/groups/:id/students', async (c) => {
  try {
    const groupId = c.req.param('id')
    const sql = getDb(c.env)
    const rows = await sql`
      SELECT DISTINCT u.id, u.full_name
      FROM enrollments e
      JOIN courses c ON c.id = e.course_id
      JOIN users u ON u.id = e.user_id
      WHERE c.group_id = ${groupId}
      ORDER BY u.full_name
    `
    return ok(c, { students: rows })
  } catch (err) {
    return serverError(c, err)
  }
})

// ============ O'QUVCHILAR ============
router.get('/students', async (c) => {
  try {
    const sql = getDb(c.env)
    const rows = await sql`
      SELECT id, full_name, phone_number, telegram_id, created_at
      FROM users
      WHERE role = 'user'
      ORDER BY full_name
    `
    return ok(c, { students: rows })
  } catch (err) {
    return serverError(c, err)
  }
})

router.get('/students/:id', async (c) => {
  try {
    const studentId = c.req.param('id')
    const sql = getDb(c.env)

    const [student] = await sql`
      SELECT id, full_name, phone_number, telegram_id, created_at
      FROM users WHERE id = ${studentId}
    `
    if (!student) return notFound(c, 'O\'quvchi topilmadi')

    const enrollments = await sql`
      SELECT c.id AS course_id, c.title, e.status, e.created_at
      FROM enrollments e
      JOIN courses c ON c.id = e.course_id
      WHERE e.user_id = ${studentId}
    `

    const grades = await sql`
      SELECT g.grade, g.comment, g.graded_at, c.title AS course_title
      FROM grades g
      JOIN courses c ON c.id = g.course_id
      WHERE g.user_id = ${studentId}
      ORDER BY g.graded_at DESC
    `

    return ok(c, {
      ...student,
      enrollments,
      grades,
    })
  } catch (err) {
    return serverError(c, err)
  }
})

// ============ TO'LOVLAR ============
router.get('/payments/paid', async (c) => {
  try {
    const sql = getDb(c.env)
    const rows = await sql`
      SELECT DISTINCT ON (u.id) u.id, u.full_name, u.phone_number, p.amount, p.paid_at
      FROM payments p
      JOIN users u ON u.id = p.user_id
      WHERE date_trunc('month', p.month) = date_trunc('month', CURRENT_DATE)
      ORDER BY u.id, p.paid_at DESC
    `
    return ok(c, { students: rows })
  } catch (err) {
    return serverError(c, err)
  }
})

router.get('/payments/debtors', async (c) => {
  try {
    const sql = getDb(c.env)
    const rows = await sql`
      SELECT u.id, u.full_name, u.phone_number, c.title AS course_title, c.price
      FROM enrollments e
      JOIN users u ON u.id = e.user_id
      JOIN courses c ON c.id = e.course_id
      WHERE e.status = 'qarzdor'
      ORDER BY u.full_name
    `
    return ok(c, { students: rows })
  } catch (err) {
    return serverError(c, err)
  }
})

// ============ TAKLIF QUTISI ============
router.get('/suggestions', async (c) => {
  try {
    const status = c.req.query('status') || 'new'
    const sql = getDb(c.env)

    const rows = await sql`
      SELECT s.id, s.user_id, s.role, s.message, s.status, s.created_at,
             u.full_name, u.telegram_id
      FROM suggestions s
      JOIN users u ON u.id = s.user_id
      WHERE s.status = ${status}
      ORDER BY s.created_at DESC
    `
    return ok(c, { suggestions: rows })
  } catch (err) {
    return serverError(c, err)
  }
})

router.put('/suggestions/:id', async (c) => {
  try {
    const suggestionId = c.req.param('id')
    const { status } = await c.req.json()

    if (!['read', 'archived'].includes(status)) {
      return badRequest(c, 'Noto\'g\'ri status')
    }

    const sql = getDb(c.env)
    await sql`
      UPDATE suggestions 
      SET status = ${status}, read_at = NOW()
      WHERE id = ${suggestionId}
    `
    return ok(c, { success: true })
  } catch (err) {
    return serverError(c, err)
  }
})

// ============ FOYDALANUVCHILAR ============
router.get('/users', async (c) => {
  try {
    const role = c.req.query('role')
    const sql = getDb(c.env)

    const rows = role
      ? await sql`
          SELECT id, full_name, phone_number, telegram_id, role, created_at
          FROM users WHERE role = ${role}
          ORDER BY full_name
        `
      : await sql`
          SELECT id, full_name, phone_number, telegram_id, role, created_at
          FROM users ORDER BY role, full_name
        `

    return ok(c, { users: rows })
  } catch (err) {
    return serverError(c, err)
  }
})

export default router