//Standart javoblar
export function ok(c, data) {
    return c.json(data, 200)
}

export function badRequest(c, message) {
    return c.json({ error: message }, 400)
}

export function notFound(c, message = 'Topilmadi'){
    return c.json({ error: message }, 404)
}

export function serverError(c, err) {
    console.error('[SERVER ERROR]', err)
    return c.json ({ error: 'Server xatosi'}, 500)
}