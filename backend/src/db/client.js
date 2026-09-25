import { neon } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-http';
import * as schema from './schema.js';

// Workers'da env har so'rovda keladi, shuning uchun har so'rovda yaratamiz (arzon operatsiya)
export function getDb(env) {
  return drizzle(neon(env.DATABASE_URL), { schema });
}