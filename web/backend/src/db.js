// Neon ulanish
import { neon } from '@neondatabase/serverless'

let _sql = null

export function getDb(env) {
    if (!_sql) {
        _sql = neon(env.DATABASE_URL)
    }
    return _sql
}