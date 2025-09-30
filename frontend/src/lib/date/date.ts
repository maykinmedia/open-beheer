/**
 * Returns today's date normalized to the start of the day (00:00:00.000) in local time.
 *
 * @returns A Date object representing the current day at midnight (local time).
 */
export function today(): Date {
  const date = new Date();
  date.setHours(0, 0, 0, 0); // normalize to start of the day
  return date;
}

/**
 * Returns yesterday's date normalized to the start of the day (00:00:00.000) in local time.
 *
 * @returns A Date object representing yesterday at midnight (local time).
 */
export function yesterday(): Date {
  const date = today();
  date.setDate(date.getDate() - 1);
  return date;
}

/**
 * Converts a Date object to a string in ISO date format (`YYYY-MM-DD`)
 * using the local timezone.
 *
 * @param date - The Date object to format.
 * @returns A string representing the date in ISO format.
 */
export function dateToIsoDateString(date: Date): string {
  return date.toLocaleDateString("en-CA"); // "YYYY-MM-DD" in local time
}
