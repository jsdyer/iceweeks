const DAY = 86400000;
export const weeks = 22;
export function season(date) {
  const [year,month] = date.split("-").map(Number);
  return month === 12 ? year : year - 1;
}
export function weekIndex(date) {
  return Math.floor((Date.parse(date + "T00:00:00Z") - Date.UTC(season(date),11,1)) / (7 * DAY));
}
export function weekDates(year, week) {
  const start = Date.UTC(year,11,1) + 7 * week * DAY;
  const end = Math.min(start + 6 * DAY, Date.UTC(year+1,3,30));
  return [start,end].map(n=>new Date(n).toISOString().slice(0,10));
}
export function match(charts, year, week) {
  return charts.filter(c=>season(c.date)===year && weekIndex(c.date)===week);
}
