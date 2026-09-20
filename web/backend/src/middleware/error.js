//XATOliklarni ushlash

export function errorHandler(err, c) {
    console.error('[UNHAND]', err)
    return c.json({ error: 'Server xatosi'}, 500)
}