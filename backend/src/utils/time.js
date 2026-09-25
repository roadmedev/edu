// Toshkent (UTC+5) bo'yicha bugungi sana: '2026-09-24'
export function tashkentDate() {
  return new Date(Date.now() + 5 * 60 * 60 * 1000).toISOString().slice(0, 10);
}

export function tashkentPeriod() {
  return tashkentDate().slice(0, 7); // '2026-09-24' -> '2026-09'
}