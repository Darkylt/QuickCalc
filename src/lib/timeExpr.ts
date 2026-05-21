const TZ_OFFSETS: Record<string, number> = {
  utc: 0,
  gmt: 0,
  est: -300,
  edt: -240,
  cst: -360,
  cdt: -300,
  mst: -420,
  mdt: -360,
  pst: -480,
  pdt: -420,
  cet: 60,
  cest: 120,
  eet: 120,
  eest: 180,
  ist: 330,
  jst: 540,
  aest: 600,
  aedt: 660,
  nzst: 720,
  nzdt: 780,
  hst: -600,
  hdt: -540,

  berlin: 60,
  paris: 60,
  london: 0,
  tokyo: 540,
  sydney: 600,
  nyc: -300,
  la: -480,
  chicago: -360,
  denver: -420,
  dubai: 240,
  moscow: 180,
  beijing: 480,
  shanghai: 480,
  singapore: 480,
  seoul: 540,
  mumbai: 330,
  karachi: 300,
  cairo: 120,
  nairobi: 180,
  lagos: 60,
};

const OFFSET_TO_ABBR: [number, string][] = [
  [-600, "HST"],
  [-540, "HDT"],
  [-480, "PST"],
  [-420, "PDT"],
  [-360, "CST"],
  [-300, "CDT"],
  [-240, "EDT"],
  [0, "UTC"],
  [60, "CET"],
  [120, "CEST"],
  [180, "EET"],
  [240, "GST"],
  [330, "IST"],
  [480, "CST"], // China. only shown when offset matches exactly
  [540, "JST"],
  [600, "AEST"],
  [660, "AEDT"],
  [720, "NZST"],
  [780, "NZDT"],
];

function localTzAbbr(): string {
  const offset = localTzOffset();
  try {
    const abbr = new Intl.DateTimeFormat("en", { timeZoneName: "short" })
      .formatToParts(new Date())
      .find((p) => p.type === "timeZoneName")?.value;
    if (abbr && /^[A-Z]{2,5}$/.test(abbr)) return abbr;
  } catch {}

  const match = OFFSET_TO_ABBR.find(([o]) => o === offset);
  if (match) return match[1];

  const sign = offset >= 0 ? "+" : "-";
  const abs = Math.abs(offset);
  const h = Math.floor(abs / 60);
  const m = abs % 60;
  return m === 0
    ? `UTC${sign}${h}`
    : `UTC${sign}${h}:${String(m).padStart(2, "0")}`;
}

// Minutes since midnight
type AbsTime = { kind: "time"; minutes: number; tzOffset: number | null };
// Total seconds. "scalar" is true when the value came from a bare number (multiplier/divisor)
type Duration = { kind: "dur"; seconds: number; scalar?: boolean };
type TimeValue = AbsTime | Duration;

function localTzOffset(): number {
  return -new Date().getTimezoneOffset();
}

function resolveOffset(tz: string | null): number {
  if (!tz) return localTzOffset();
  const key = tz.toLowerCase();
  if (key === "local") return localTzOffset();
  if (key in TZ_OFFSETS) return TZ_OFFSETS[key];
  // IANA-style: Europe/Berlin etc. rough static fallback not supported
  // return local as best effort
  return localTzOffset();
}

function durSeconds(s: number): Duration {
  return { kind: "dur", seconds: s };
}

function absTime(minutes: number, tzOffset: number | null = null): AbsTime {
  // Normalise to [0, 1440)
  const m = ((minutes % 1440) + 1440) % 1440;
  return { kind: "time", minutes: m, tzOffset };
}

function formatDuration(seconds: number): string {
  if (seconds < 0) {
    return "-" + formatDuration(-seconds);
  }
  const totalMinutes = Math.floor(seconds / 60);
  const d = Math.floor(totalMinutes / 1440);
  const h = Math.floor((totalMinutes % 1440) / 60);
  const m = totalMinutes % 60;
  const s = Math.round(seconds % 60);

  // Only show seconds if no larger unit
  if (d === 0 && h === 0 && m === 0) {
    return `${s}s`;
  }
  let out = "";
  if (d) out += `${d}d`;
  if (h) out += `${h}h`;
  if (m) out += `${m}m`;
  if (s) out += `${s}s`;
  return out || "0m";
}

function formatTime(minutes: number): string {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}

type Token =
  | { t: "time"; minutes: number; tz: string | null }
  | { t: "dur"; seconds: number }
  | { t: "op"; op: "+" | "-" | "*" | "/" | "->" }
  | { t: "num"; v: number }
  | { t: "kw"; w: "now" | "local" | "utc" };

const TZ_PATTERN = Object.keys(TZ_OFFSETS)
  .sort((a, b) => b.length - a.length)
  .join("|");

// Tokenise the input string into typed tokens
function tokenise(input: string): Token[] | null {
  const src = input.trim();
  const tokens: Token[] = [];
  let i = 0;

  while (i < src.length) {
    // Skip whitespace
    if (/\s/.test(src[i])) {
      i++;
      continue;
    }

    // Arrow operator ->
    if (src.slice(i, i + 2) === "->") {
      tokens.push({ t: "op", op: "->" });
      i += 2;
      continue;
    }

    // Keywords: now, local, utc (must check before tz pattern)
    const kwMatch = src.slice(i).match(/^(now|local)\b/i);
    if (kwMatch) {
      const w = kwMatch[1].toLowerCase() as "now" | "local";
      tokens.push({ t: "kw", w });
      i += kwMatch[0].length;
      continue;
    }

    // Duration: number followed immediately by unit letters (no space required)
    // e.g. 1h30m, 45m, 2d4h, 90s
    const durMatch = src.slice(i).match(/^(?:\d+(?:[dhms]))+/i);
    if (durMatch) {
      const raw = durMatch[0];
      let secs = 0;
      let j = 0;
      while (j < raw.length) {
        const nm = raw.slice(j).match(/^(\d+)([dhms])/i);
        if (!nm) break;
        const n = parseInt(nm[1]);
        switch (nm[2].toLowerCase()) {
          case "d":
            secs += n * 86400;
            break;
          case "h":
            secs += n * 3600;
            break;
          case "m":
            secs += n * 60;
            break;
          case "s":
            secs += n;
            break;
        }
        j += nm[0].length;
      }
      tokens.push({ t: "dur", seconds: secs });
      i += raw.length;
      continue;
    }

    // Time: 12h or 24h or compact
    // Try HH:MM [am/pm] [tz]
    const timeColon = src.slice(i).match(/^(\d{1,2}):(\d{2})\s*(am|pm)?/i);
    if (timeColon) {
      let h = parseInt(timeColon[1]);
      const m = parseInt(timeColon[2]);
      const ampm = timeColon[3]?.toLowerCase();
      if (ampm === "pm" && h !== 12) h += 12;
      if (ampm === "am" && h === 12) h = 0;
      if (h < 0 || h > 23 || m < 0 || m > 59) return null;
      i += timeColon[0].length;
      // Optional timezone after whitespace
      const tzMatch = src
        .slice(i)
        .match(new RegExp(`^\\s*(${TZ_PATTERN})\\b`, "i"));
      const tz = tzMatch ? tzMatch[1].toLowerCase() : null;
      if (tzMatch) i += tzMatch[0].length;
      tokens.push({ t: "time", minutes: h * 60 + m, tz });
      continue;
    }

    // Compact time: 930pm, 1530, 3pm
    const timeCompact = src.slice(i).match(/^(\d{1,4})\s*(am|pm)\b/i);
    if (timeCompact) {
      let raw = parseInt(timeCompact[1]);
      const ampm = timeCompact[2].toLowerCase();
      let h: number, m: number;
      if (raw < 100) {
        h = raw;
        m = 0;
      } else {
        h = Math.floor(raw / 100);
        m = raw % 100;
      }
      if (ampm === "pm" && h !== 12) h += 12;
      if (ampm === "am" && h === 12) h = 0;
      if (h < 0 || h > 23 || m < 0 || m > 59) return null;
      i += timeCompact[0].length;
      const tzMatch = src
        .slice(i)
        .match(new RegExp(`^\\s*(${TZ_PATTERN})\\b`, "i"));
      const tz = tzMatch ? tzMatch[1].toLowerCase() : null;
      if (tzMatch) i += tzMatch[0].length;
      tokens.push({ t: "time", minutes: h * 60 + m, tz });
      continue;
    }


    const numMatch = src.slice(i).match(/^(\d+(?:\.\d+)?)/);
    if (numMatch) {
      tokens.push({ t: "num", v: parseFloat(numMatch[1]) });
      i += numMatch[0].length;
      continue;
    }

    if ("+-*/".includes(src[i])) {
      tokens.push({ t: "op", op: src[i] as "+" | "-" | "*" | "/" });
      i++;
      continue;
    }

    // timezone as standalone token (for "->" target)
    const tzStandalone = src
      .slice(i)
      .match(new RegExp(`^(${TZ_PATTERN})\\b`, "i"));
    if (tzStandalone) {
      // push as a special kw with tz meaning. handled in eval
      const w = tzStandalone[1].toLowerCase();
      if (w === "utc") {
        tokens.push({ t: "kw", w: "utc" });
      } else {
        // encode as a synthetic time-zone token by reusing kw with the value
        tokens.push({ t: "kw", w: w as any });
      }
      i += tzStandalone[0].length;
      continue;
    }

    // unknown character
    return null;
  }

  return tokens;
}

type EvalResult = { value: TimeValue; tzConverted: boolean };

function evaluate(tokens: Token[]): EvalResult | null {
  if (!tokens.length) return null;

  let i = 0;
  let tzConverted = false;

  function peek(): Token | undefined {
    return tokens[i];
  }
  function consume(): Token {
    return tokens[i++];
  }

  function parsePrimary(): TimeValue | null {
    const tok = peek();
    if (!tok) return null;

    // "now" keyword
    if (tok.t === "kw" && tok.w === "now") {
      consume();
      const now = new Date();
      const mins = now.getHours() * 60 + now.getMinutes();
      return absTime(mins, localTzOffset());
    }

    if (tok.t === "time") {
      consume();
      const offset = tok.tz ? resolveOffset(tok.tz) : localTzOffset();
      return absTime(tok.minutes, offset);
    }

    if (tok.t === "dur") {
      consume();
      return durSeconds(tok.seconds);
    }

    if (tok.t === "num") {
      consume();
      return { kind: "dur", seconds: tok.v, scalar: true };
    }

    return null;
  }

  // parse a full expression chain left-to-right
  let left = parsePrimary();
  if (!left) return null;

  while (i < tokens.length) {
    const op = peek();
    if (!op || op.t !== "op") break;
    consume(); // eat operator

    // timezone conversion: left -> tz
    if (op.op === "->") {
      const tzTok = peek();
      if (!tzTok) return null;
      consume();

      const targetTz =
        tzTok.t === "kw"
          ? String(tzTok.w)
          : tzTok.t === "time"
            ? (tzTok.tz ?? "local")
            : null;

      if (!targetTz) return null;

      if (left.kind !== "time") return null;

      const srcOffset = left.tzOffset ?? localTzOffset();
      const dstOffset = resolveOffset(targetTz);
      const shiftedMins = left.minutes - srcOffset + dstOffset;
      left = absTime(shiftedMins, dstOffset);
      tzConverted = true;
      continue;
    }

    const right = parsePrimary();
    if (!right) return null;

    // combine
    if (op.op === "+") {
      if (left.kind === "time" && right.kind === "dur") {
        left = absTime(left.minutes + right.seconds / 60, left.tzOffset);
        continue;
      }
      if (left.kind === "dur" && right.kind === "time") {
        left = absTime(right.minutes + left.seconds / 60, right.tzOffset);
        continue;
      }
      if (left.kind === "dur" && right.kind === "dur") {
        left = durSeconds(left.seconds + right.seconds);
        continue;
      }
      return null;
    }

    if (op.op === "-") {
      if (left.kind === "time" && right.kind === "dur") {
        left = absTime(left.minutes - right.seconds / 60, left.tzOffset);
        continue;
      }
      if (left.kind === "time" && right.kind === "time") {
        // time difference -> duration
        let diff = (left.minutes - right.minutes) * 60;
        if (diff < 0) diff += 86400;
        left = durSeconds(diff);
        continue;
      }
      if (left.kind === "dur" && right.kind === "dur") {
        left = durSeconds(left.seconds - right.seconds);
        continue;
      }
      return null;
    }

    if (op.op === "*") {
      if (left.kind === "dur" && right.kind === "dur") {
        if (left.scalar) {
          left = durSeconds(left.seconds * right.seconds);
        } else if (right.scalar) {
          left = durSeconds(left.seconds * right.seconds);
        } else {
          return null; // two real durations
        }
        continue;
      }
      return null;
    }

    if (op.op === "/") {
      if (left.kind === "dur" && right.kind === "dur") {
        if (right.seconds === 0) return null;
        if (right.scalar) {
          left = durSeconds(left.seconds / right.seconds);
        } else {
          return null; // dividing by a real duration
        }
        continue;
      }
      return null;
    }

    return null;
  }

  return { value: left, tzConverted };
}

export function isTimeExpression(expr: string): boolean {
  const timePatterns = [
    /\d{1,2}:\d{2}/, // HH:MM
    /\d{1,4}\s*[ap]m\b/i, // 3pm, 930am
    /\d+[dhms]\b/i, // durations
    /\bnow\b/i, // now keyword
    /->/, // conversion
  ];
  return timePatterns.some((p) => p.test(expr));
}

export function evaluateTime(expr: string): string | null {
  const tokens = tokenise(expr.trim());
  if (!tokens || tokens.length === 0) return null;

  let implicitConvert = false;
  if (tokens.length === 1 && tokens[0].t === "time" && tokens[0].tz !== null) {
    const srcOffset = resolveOffset(tokens[0].tz);
    if (srcOffset !== localTzOffset()) {
      tokens.push({ t: "op", op: "->" });
      tokens.push({ t: "kw", w: "local" });
      implicitConvert = true;
    }
  }

  const res = evaluate(tokens);
  if (!res) return null;

  const { value, tzConverted } = res;

  if (value.kind === "time") {
    const timeStr = formatTime(value.minutes);
    if (tzConverted || implicitConvert) {
      return `${timeStr} ${localTzAbbr()}`;
    }
    return timeStr;
  }
  if (value.kind === "dur") {
    return formatDuration(value.seconds);
  }
  return null;
}