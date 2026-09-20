// src/routes/user.js
import { Hono } from 'hono'
import { getDb } from '../db.js'
import { ok, badRequest, notFound, serverError } from '../utils/response.js'

const router = new Hono()

// ============ KURSLAR (pagination) ============
router.get('/courses', async (c) => {
  try {
    const page = parseInt(c.req.query('page') || '1')
    const limit = parseInt(c.req.query('limit') || '10')
    const offset = (page - 1) * limit

    const sql = getDb(c.env)

    const [count] = await sql`SELECT COUNT(*)::int AS total FROM courses`
    const courses = await sql`
      SELECT c.id, c.title, c.description, c.price,
             t.full_name AS teacher_name, t.photo_url AS teacher_photo
      FROM courses c
      LEFT JOIN teachers t ON t.id = c.teacher_id
      ORDER BY c.id
      LIMIT ${limit} OFFSET ${offset}
    `

    return ok(c, {
      courses,
      pagination: {
        page,
        limit,
        total: count.total,
        total_pages: Math.ceil(count.total / limit),
      },
    })
  } catch (err) {
    return serverError(c, err)
  }
})

// Bir fan bo'yicha o'qituvchilar
router.get('/courses/:id/teachers', async (c) => {
  try {
    const courseId = c.req.param('id')
    const sql = getDb(c.env)

    const rows = await sql`
      SELECT t.id, t.full_name, t.photo_url, t.degree, t.certificate_info
      FROM courses c
      JOIN teachers t ON t.id = c.teacher_id
      WHERE c.id = ${courseId}
    `
    return ok(c, { teachers: rows })
  } catch (err) {
    return serverError(c, err)
  }
})

// ============ KURSGA SO'ROV YUBORISH ============
router.post('/course-requests', async (c) => {
  try {
    const { telegram_id, course_id, message } = await c.req.json()

    if (!telegram_id || !course_id) {
      return badRequest(c, 'telegram_id va course_id talab qilinadi')
    }

    const sql = getDb(c.env)

    const [user] = await sql`SELECT id FROM users WHERE telegram_id = ${telegram_id}`
    if (!user) return notFound(c, 'Foydalanuvchi topilmadi')

    const [course] = await sql`
      SELECT id, teacher_id FROM courses WHERE id = ${course_id}
    `
    if (!course) return notFound(c, 'Kurs topilmadi')

    // 1 kunda 1 marta pending so'rov
    const [existing] = await sql`
      SELECT id FROM course_requests
      WHERE user_id = ${user.id} 
        AND course_id = ${course_id}
        AND status = 'pending'
        AND DATE(created_at) = CURRENT_DATE
    `
    if (existing) {
      return c.json({ 
        error: 'Bugun bu kursga allaqachon so\'rov yuborgansiz',
        already_sent: true,
      }, 409)
    }

    // Allaqachon enrollment bormi?
    const [enrolled] = await sql`
      SELECT id FROM enrollments
      WHERE user_id = ${user.id} AND course_id = ${course_id}
    `
    if (enrolled) {
      return c.json({ error: 'Siz allaqachon bu kursga yozilgansiz' }, 409)
    }

    const [request] = await sql`
      INSERT INTO course_requests (user_id, course_id, teacher_id, message)
      VALUES (${user.id}, ${course_id}, ${course.teacher_id}, ${message || null})
      RETURNING id
    `

    return ok(c, { request })
  } catch (err) {
    return serverError(c, err)
  }
})

router.get('/my-requests/:telegramId', async (c) => {
  try {
    const telegramId = c.req.param('telegramId')
    const sql = getDb(c.env)

    const [user] = await sql`SELECT id FROM users WHERE telegram_id = ${telegramId}`
    if (!user) return notFound(c, 'Foydalanuvchi topilmadi')

    const requests = await sql`
      SELECT cr.id, cr.status, cr.created_at, cr.responded_at,
             cr.rejection_reason,
             c.title AS course_title, c.id AS course_id
      FROM course_requests cr
      JOIN courses c ON c.id = cr.course_id
      WHERE cr.user_id = ${user.id}
      ORDER BY cr.created_at DESC
    `
    return ok(c, { requests })
  } catch (err) {
    return serverError(c, err)
  }
})

// ============ MENING KURSLARIM ============
router.get('/my-courses/:telegramId', async (c) => {
  try {
    const telegramId = c.req.param('telegramId')
    const sql = getDb(c.env)

    const [user] = await sql`SELECT id FROM users WHERE telegram_id = ${telegramId}`
    if (!user) return notFound(c, 'Foydalanuvchi topilmadi')

    const courses = await sql`
      SELECT c.id, c.title, c.description, c.price,
             e.status, e.created_at AS enrolled_at,
             t.full_name AS teacher_name,
             (SELECT grade FROM grades WHERE user_id = ${user.id} AND course_id = c.id
              ORDER BY graded_at DESC LIMIT 1) AS last_grade
      FROM enrollments e
      JOIN courses c ON c.id = e.course_id
      LEFT JOIN teachers t ON t.id = c.teacher_id
      WHERE e.user_id = ${user.id}
      ORDER BY e.created_at DESC
    `
    return ok(c, { courses })
  } catch (err) {
    return serverError(c, err)
  }
})

// ============ DARS JADVALI ============
router.get('/schedule', async (c) => {
  try {
    const sql = getDb(c.env)

    const schedules = await sql`
      SELECT cs.id, cs.day_of_week, cs.start_time, cs.end_time, cs.room,
             c.id AS course_id, c.title AS course_title,
             t.full_name AS teacher_name
      FROM course_schedules cs
      JOIN courses c ON c.id = cs.course_id
      LEFT JOIN teachers t ON t.id = c.teacher_id
      ORDER BY cs.day_of_week, cs.start_time
    `
    return ok(c, { schedules })
  } catch (err) {
    return serverError(c, err)
  }
})

// ============ REYTING ============
router.get('/my-rating/:telegramId', async (c) => {
  try {
    const telegramId = c.req.param('telegramId')
    const sql = getDb(c.env)

    const [user] = await sql`SELECT id FROM users WHERE telegram_id = ${telegramId}`
    if (!user) return notFound(c, 'Foydalanuvchi topilmadi')

    const grades = await sql`
      SELECT g.grade, g.comment, g.graded_at, c.title AS course_title
      FROM grades g
      JOIN courses c ON c.id = g.course_id
      WHERE g.user_id = ${user.id}
      ORDER BY g.graded_at DESC
    `

    const [avg] = await sql`
      SELECT COALESCE(AVG(grade), 0)::numeric AS avg_grade,
             COUNT(*)::int AS total_grades
      FROM grades WHERE user_id = ${user.id}
    `

    return ok(c, {
      grades,
      average: avg.avg_grade,
      total_grades: avg.total_grades,
    })
  } catch (err) {
    return serverError(c, err)
  }
})

// ============ TAKLIF YUBORISH ============
router.post('/suggestions', async (c) => {
  try {
    const { telegram_id, message } = await c.req.json()

    if (!telegram_id || !message) {
      return badRequest(c, 'telegram_id va message talab qilinadi')
    }

    const sql = getDb(c.env)
    const [user] = await sql`
      SELECT id, role FROM users WHERE telegram_id = ${telegram_id}
    `
    if (!user) return notFound(c, 'Foydalanuvchi topilmadi')

    const [suggestion] = await sql`
      INSERT INTO suggestions (user_id, role, message)
      VALUES (${user.id}, ${user.role}, ${message})
      RETURNING id
    `
    return ok(c, { suggestion })
  } catch (err) {
    return serverError(c, err)
  }
})

export default router