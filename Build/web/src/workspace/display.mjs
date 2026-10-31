// S15ar: server text keeps its words; only the em-dash separator is swapped at display time.
export const dash = (s) => String(s).replaceAll(' \u2014 ', ' \u00b7 ');
