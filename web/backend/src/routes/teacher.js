// src/routes/teacher.js
import { Hono } from 'hono'
import { getDb } from '../db.js'
import { ok, badRequest, notFound, serverError } from '../utils/response.js'

const router = new Hono()

// Teacher'ni telegram_id orqali topish (yordamchi)
async function getTeacherByTelegram(sql, telegramId) {
  const [teacher] = await sql`
    SELECT t.* FROM teachers t
    JOIN users u ON u.id = t.user_id
    WHERE u.telegram_id = ${telegramId} AND t.is_active = true
  `
  return teacher
}

// ============ PROFIL ============
router.get('/profile/:telegramId', async (c) => {
  try {
    const telegramId = c.req.param('telegramId')
    const sql = getDb(c.env)

    const teacher = await getTeacherByTelegram(sql, telegramId)
    if (!teacher) return notFound(c, 'Teacher topilmadi')

    const [subject] = await sql`
      SELECT name FROM subjects WHERE id = ${teacher.subject_id}
    `

    return ok(c, {
      teacher: { ...teacher, subject_name: subject?.name }
    })
  } catch (err) {
    return serverError(c, err)
  }
})

router.put('/profile/:telegramId', async (c) => {
  try {
    const telegramId = c.req.param('telegramId')
    const { field, value } = await c.req.json()

    const allowedFields = ['full_name', 'degree', 'certificate_info', 'photo_url']
    if (!allowedFields.includes(field)) {
      return badRequest(c, 'Ruxsat etilmagan maydon')
    }

    const sql = getDb(c.env)
    const teacher = await getTeacherByTelegram(sql, telegramId)
    if (!teacher) return notFound(c, 'O\'qituvchi topilmadi')

    await sql`
      UPDATE teachers SET ${sql(field)} = ${value}
      WHERE id = ${teacher.id}
    `
    return ok(c, { success: true })
  } catch (err) {
    return serverError(c, err)
  }
})

// ============ KURSLAR ============
router.get('/courses/:telegramId', async (c) => {
  try {
    const telegramId = c.req.param('telegramId')
    const sql = getDb(c.env)

    const teacher = await getTeacherByTelegram(sql, telegramId)
    if (!teacher) return notFound(c, 'O\'qituvchi topilmadi')

    const courses = await sql`
      SELECT c.id, c.title, c.description, c.price, c.group_id,
             (SELECT COUNT(*)::int FROM enrollments WHERE course_id = c.id) AS students_count
      FROM courses c
      WHERE c.teacher_id = ${teacher.id}
      ORDER BY c.created_at DESC
    `
    return ok(c, { courses })
  } catch (err) {
    return serverError(c, err)
  }
})

router.post('/courses', async (c) => {
  try {
    const body = await c.req.json()
    const { telegram_id, title, description, price, group_id } = body

    if (!telegram_id || !title) {
      return badRequest(c, 'telegram_id va title talab qilinadi')
    }

    const sql = getDb(c.env)
    const teacher = await getTeacherByTelegram(sql, telegram_id)
    if (!teacher) return notFound(c, 'O\'qituvchi topilmadi')

    const [course] = await sql`
      INSERT INTO courses (title, description, price, teacher_id, group_id)
      VALUES (${title}, ${description}, ${price || 0}, ${teacher.id}, ${group_id})
      RETURNING id, title
    `
    return ok(c, { course })
  } catch (err) {
    return serverError(c, err)
  }
})

// ============ DARS JADVALI ============
router.post('/schedules', async (c) => {
  try {
    const body = await c.req.json()
    const { course_id, day_of_week, start_time, end_time, room } = body

    if (!course_id || !day_of_week || !start_time || !end_time) {
      return badRequest(c, 'Barcha maydonlar talab qilinadi')
    }

    const sql = getDb(c.env)

    // Conflict check
    const conflicts = await sql`
      SELECT cs.id, c.title
      FROM course_schedules cs
      JOIN courses c ON c.id = cs.course_id
      WHERE cs.day_of_week = ${day_of_week}
        AND cs.course_id != ${course_id}
        AND (cs.start_time, cs.end_time) OVERLAPS (${start_time}::time, ${end_time}::time)
    `

    if (conflicts.length > 0) {
      return c.json({
        error: 'Bu vaqtda boshqa kurs mavjud',
        conflicts: conflicts.map(c => ({
          id: c.id,
          title: c.title,
        })),
      }, 409)
    }

    const [schedule] = await sql`
      INSERT INTO course_schedules (course_id, day_of_week, start_time, end_time, room)
      VALUES (${course_id}, ${day_of_week}, ${start_time}, ${end_time}, ${room})
      RETURNING id
    `
    return ok(c, { schedule })
  } catch (err) {
    return serverError(c, err)
  }
})

router.get('/schedules/:courseId', async (c) => {
  try {
    const courseId = c.req.param('courseId')
    const sql = getDb(c.env)

    const rows = await sql`
      SELECT id, day_of_week, start_time, end_time, room
      FROM course_schedules
      WHERE course_id = ${courseId}
      ORDER BY day_of_week, start_time
    `
    return ok(c, { schedules: rows })
  } catch (err) {
    return serverError(c, err)
  }
})

// ============ SO'ROVLAR ============
router.get('/requests/:telegramId', async (c) => {
  try {
    const telegramId = c.req.param('telegramId')
    const sql = getDb(c.env)

    const teacher = await getTeacherByTelegram(sql, telegramId)
    if (!teacher) return notFound(c, 'O\'qituvchi topilmadi')

    const requests = await sql`
      SELECT cr.id, cr.status, cr.message, cr.created_at,
             u.id AS user_id, u.full_name, u.phone_number, u.telegram_id,
             c.id AS course_id, c.title AS course_title, c.price
      FROM course_requests cr
      JOIN users u ON u.id = cr.user_id
      JOIN courses c ON c.id = cr.course_id
      WHERE cr.teacher_id = ${teacher.id} AND cr.status = 'pending'
      ORDER BY cr.created_at ASC
    `
    return ok(c, { requests })
  } catch (err) {
    return serverError(c, err)
  }
})

router.put('/requests/:id', async (c) => {
  try {
    const requestId = c.req.param('id')
    const { status, rejection_reason } = await c.req.json()

    if (!['accepted', 'rejected'].includes(status)) {
      return badRequest(c, 'status accepted yoki rejected bo\'lishi kerak')
    }

    const sql = getDb(c.env)

    const [request] = await sql`
      SELECT * FROM course_requests WHERE id = ${requestId} AND status = 'pending'
    `
    if (!request) return notFound(c, 'So\'rov topilmadi yoki allaqachon javob berilgan')

    await sql`
      UPDATE course_requests
      SET status = ${status}, 
          rejection_reason = ${rejection_reason || null},
          responded_at = NOW()
      WHERE id = ${requestId}
    `

    if (status === 'accepted') {
      // Enrollment yaratish
      await sql`
        INSERT INTO enrollments (user_id, course_id, status)
        VALUES (${request.user_id}, ${request.course_id}, 'qarzdor')
        ON CONFLICT (user_id, course_id) DO NOTHING
      `
    }

    return ok(c, { success: true })
  } catch (err) {
    return serverError(c, err)
  }
})

// ============ O'QUVCHILAR ============
router.get('/students/:telegramId', async (c) => {
  try {
    const telegramId = c.req.param('telegramId')
    const sql = getDb(c.env)

    const teacher = await getTeacherByTelegram(sql, telegramId)
    if (!teacher) return notFound(c, 'O\'qituvchi topilmadi')

    const students = await sql`
      SELECT DISTINCT 
        u.id, u.full_name, u.phone_number, u.telegram_id,
        c.id AS course_id, c.title AS course_title,
        e.status, e.created_at AS enrolled_at,
        (SELECT grade FROM grades WHERE user_id = u.id AND course_id = c.id 
         ORDER BY graded_at DESC LIMIT 1) AS last_grade
      FROM enrollments e
      JOIN courses c ON c.id = e.course_id
      JOIN users u ON u.id = e.user_id
      WHERE c.teacher_id = ${teacher.id}
      ORDER BY c.title, u.full_name
    `
    return ok(c, { students })
  } catch (err) {
    return serverError(c, err)
  }
})

// "To'ladi" belgilash
router.post('/students/:telegramId/payment', async (c) => {
  try {
    const telegramId = c.req.param('telegramId')
    const { student_id, course_id, amount } = await c.req.json()

    if (!student_id || !course_id || !amount) {
      return badRequest(c, 'student_id, course_id, amount talab qilinadi')
    }

    const sql = getDb(c.env)
    const teacher = await getTeacherByTelegram(sql, telegramId)
    if (!teacher) return notFound(c, 'O\'qituvchi topilmadi')

    // To'lovni yozish
    await sql`
      INSERT INTO payments (user_id, course_id, amount, month, marked_by, method)
      VALUES (${student_id}, ${course_id}, ${amount}, 
              date_trunc('month', CURRENT_DATE)::date, 
              ${teacher.user_id}, 'cash')
    `

    // Enrollment statusini yangilash
    await sql`
      UPDATE enrollments
      SET status = 'active'
      WHERE user_id = ${student_id} AND course_id = ${course_id}
    `

    return ok(c, { success: true })
  } catch (err) {
    return serverError(c, err)
  }
})

// Baho qo'yish
router.post('/grades', async (c) => {
  try {
    const { telegram_id, student_id, course_id, grade, comment } = await c.req.json()

    if (!student_id || !course_id || grade === undefined) {
      return badRequest(c, 'student_id, course_id, grade talab qilinadi')
    }

    const sql = getDb(c.env)
    const teacher = await getTeacherByTelegram(sql, telegram_id)
    if (!teacher) return notFound(c, 'O\'qituvchi topilmadi')

    await sql`
      INSERT INTO grades (user_id, course_id, teacher_id, grade, comment)
      VALUES (${student_id}, ${course_id}, ${teacher.id}, ${grade}, ${comment || null})
    `
    return ok(c, { success: true })
  } catch (err) {
    return serverError(c, err)
  }
})

// ============ BALANS ============
router.get('/balance/:telegramId', async (c) => {
  try {
    const telegramId = c.req.param('telegramId')
    const sql = getDb(c.env)

    const teacher = await getTeacherByTelegram(sql, telegramId)
    if (!teacher) return notFound(c, 'O\'qituvchi topilmadi')

    // Oylik daromad
    const monthly = await sql`
      SELECT month, gross_income, admin_share, teacher_share
      FROM teacher_monthly_income
      WHERE teacher_id = ${teacher.id}
      ORDER BY month DESC
      LIMIT 12
    `

    // Joriy oy
    const [current] = await sql`
      SELECT gross_income, admin_share, teacher_share
      FROM teacher_monthly_income
      WHERE teacher_id = ${teacher.id}
        AND month = date_trunc('month', CURRENT_DATE)::date
    `

    // Jami
    const [total] = await sql`
      SELECT 
        COALESCE(SUM(gross_income), 0)::numeric AS total_gross,
        COALESCE(SUM(teacher_share), 0)::numeric AS total_earned
      FROM teacher_monthly_income
      WHERE teacher_id = ${teacher.id}
    `

    return ok(c, {
      current_month: current || { gross_income: 0, admin_share: 0, teacher_share: 0 },
      monthly_history: monthly,
      total: total,
    })
  } catch (err) {
    return serverError(c, err)
  }
})

export default router