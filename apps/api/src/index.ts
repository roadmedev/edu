import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { Client } from '@neondatabase/serverless'

type Bindings = {
  DATABASE_URL: string
}

const app = new Hono<{ Bindings: Bindings }>()

// Frontend so'rovlariga ruxsat berish
app.use('*', cors())

app.get('/api/hello', async (c) => {
  try {
    const client = new Client(c.env.DATABASE_URL)
    await client.connect()
    
    const { rows } = await client.query('SELECT content FROM messages LIMIT 1')
    await client.end()

    const message = rows[0]?.content || `Ma'lumot topilmadi`
    return c.json({ message })
  } catch (error: any) {
    return c.json({ error: error.message }, 500)
  }
})

export default app