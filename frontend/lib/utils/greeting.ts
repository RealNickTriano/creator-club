/**
 * Maps a time of day to a greeting: morning before noon, afternoon until 6pm,
 * evening after. Pure so it stays testable; pass a fixed `date` in tests.
 */
export function getTimeOfDayGreeting(date: Date = new Date()): string {
  const hour = date.getHours();
  if (hour < 12) return "Good morning";
  if (hour < 18) return "Good afternoon";
  return "Good evening";
}

/**
 * The set of returning-member greetings to choose from: the time-of-day
 * greeting plus a handful of playful one-offs. All are personalized with the
 * member's first name.
 */
export function buildGreetings(
  name: string,
  date: Date = new Date(),
): string[] {
  return [
    `${getTimeOfDayGreeting(date)}, ${name}`,
    `Hey, ${name}`,
    `Look who's back, ${name}`,
    `There you are, ${name}`,
    `Good to see you, ${name}`,
    `What's the move, ${name}?`,
    `Ready to dive in, ${name}?`,
  ];
}

/** Picks one greeting at random. */
export function pickGreeting(name: string, date: Date = new Date()): string {
  const options = buildGreetings(name, date);
  return options[Math.floor(Math.random() * options.length)];
}
