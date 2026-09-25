import { Hono } from 'hono'
import { logger } from 'hono/logger'
import { sql } from 'drizzle-orm'
import { getDb } from './db/client'
import { botAuth } from './middlewares/botAuth'
import usersRouter from './routes/users'
import courseRouter from './routes/courses'
import enrollmentsRouter from './routes/enrollments'
import paymentsRouter from './routes/payments.js';
import teachersRouter from './routes/teachers.js';
import adminRouter from './routes/admin.js'
import suggestionsRouter from './routes/suggestions.js';

const app = new Hono();

app.use('*', logger());

//Ochiq tekshiruv
app.get('/health', (c) => c.json({ ok: true }));

// Himoyalangan Api
const api = new Hono();
api.use('*', botAuth);

api.get('/ping-db', async (c)=> {
    const db = getDb(c.env);
    const result = await db.execute(sql`select now() as now`);
    return c.json({ db: 'ulandi', now: result.rows[0].now });
});

api.route('/users', usersRouter);
api.route('/courses', courseRouter);
api.route('/enrollments', enrollmentsRouter);
api.route('/payments', paymentsRouter);
api.route('/teachers', teachersRouter);
api.route('/admin', adminRouter);
api.route('/suggestions', suggestionsRouter);



app.route('/api', api);

app.onError((err, c) => {
    console.error(err);
    return c.json({ error: 'Server xatosi'}, 500);
});

export default app;