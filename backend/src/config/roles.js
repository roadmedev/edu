export function isAdminId(env, telegramId) {
    return (env.ADMIN_IDS || '')
        .split(',')
        .map((s)=> s.trim())
        .includes(String(telegramId));
}