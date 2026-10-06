export function normalizePhone(raw) {
    const digits = String(raw || '').replace(/\D/g, '');
    return digits ? `+${digits}` : '';
}