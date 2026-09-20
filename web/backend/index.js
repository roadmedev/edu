// Faqat Apini ishga tushiradi
// index.js
import { Hono } from 'hono'
import { cors } from 'hono/cors'

import publicRouter from './src/routes/public.js'
import adminRouter from './src/routes/admin.js'
import teacherRouter from './src/routes/teacher.js'
import userRouter from './src/routes/user.js'

const app = new Hono()

// CORS
app.use('*', cors())

// Routerlarni ulash
app.route('/', publicRouter)
app.route('/admin', adminRouter)
app.route('/teacher', teacherRouter)
app.route('/user', userRouter)

export default app