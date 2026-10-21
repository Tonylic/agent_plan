// nws.js: National Weather Service client for the home_weather tool. No dependencies: the caller
// passes fetch. It only ever contacts https://api.weather.gov, and it refuses redirects and any
// forecast URL that the points lookup returns on another host.
//
// API: https://www.weather.gov/documentation/services-web-api
//   GET /points/{lat},{lon}            -> properties.forecast (gridpoint URL), timeZone
//   GET /gridpoints/{wfo}/{x},{y}/forecast -> properties.periods (12-hour periods), updateTime
//   GET /alerts/active?point={lat},{lon}   -> features[].properties (event, headline, ends)
// NWS asks every client to send a User-Agent that names the app and a contact.

const API = "https://api.weather.gov";
const POINTS_TTL_MS = 24 * 60 * 60 * 1000; // a grid assignment changes very rarely
const FORECAST_TTL_MS = 10 * 60 * 1000;    // NWS refreshes forecasts about hourly
const TIMEOUT_MS = 8000;

/** Collapses whitespace, drops control characters and caps the length of text from the API. */
export function clip(value, max) {
  if (value === null || value === undefined) return "";
  const text = String(value).replace(/[\u0000-\u001f\u007f]+/g, " ").replace(/\s+/g, " ").trim();
  return text.length > max ? `${text.slice(0, max - 1)}…` : text;
}

/** NWS wants at most four decimals and no trailing zeros (it redirects otherwise). */
export function coord(value, min, max) {
  const n = Number(value);
  if (!Number.isFinite(n) || n < min || n > max) throw new Error(`coordinate out of range: ${value}`);
  return String(Number(n.toFixed(4)));
}

/** The human-readable forecast page for the same point, for the reply's source link. */
export function sourceUrl(latitude, longitude) {
  return `https://forecast.weather.gov/MapClick.php?lat=${coord(latitude, -90, 90)}&lon=${coord(longitude, -180, 180)}`;
}

function apiUrl(value) {
  let url;
  try { url = new URL(value); } catch { return null; }
  return url.protocol === "https:" && url.hostname === "api.weather.gov" ? url.href : null;
}

function number(value) {
  const n = Number(value);
  return value === null || value === undefined || !Number.isFinite(n) ? null : n;
}

export function createNwsClient({ userAgent, fetchImpl = (...args) => globalThis.fetch(...args),
                                  now = () => Date.now(),
                                  sleep = (ms) => new Promise((r) => setTimeout(r, ms)) }) {
  if (!userAgent || typeof userAgent !== "string") throw new Error("home-weather: userAgent is required");
  const cache = new Map(); // url -> { at, body }

  async function getJson(url, ttl, signal) {
    const hit = cache.get(url);
    if (hit && now() - hit.at < ttl) return hit.body;
    let lastError;
    for (let attempt = 0; attempt < 2; attempt++) {   // one retry: NWS returns brief 5xx at times
      if (attempt) await sleep(1000);
      const timeout = AbortSignal.timeout(TIMEOUT_MS);
      try {
        const res = await fetchImpl(url, {
          headers: { "User-Agent": userAgent, Accept: "application/geo+json" },
          redirect: "error",
          signal: signal ? AbortSignal.any([signal, timeout]) : timeout,
        });
        if (res.status === 200) {
          const body = await res.json();
          cache.set(url, { at: now(), body });
          return body;
        }
        lastError = new Error(`HTTP ${res.status} from api.weather.gov`);
        if (res.status < 500 && res.status !== 429) break;
      } catch (err) {
        if (signal?.aborted) throw err;
        lastError = err;
      }
    }
    throw lastError;
  }

  /** Forecast periods for the next `days` days (two 12-hour periods a day) and active alerts. */
  async function getForecast({ latitude, longitude, place, days = 2, signal }) {
    const lat = coord(latitude, -90, 90);
    const lon = coord(longitude, -180, 180);
    const points = await getJson(`${API}/points/${lat},${lon}`, POINTS_TTL_MS, signal);
    const forecastUrl = apiUrl(points?.properties?.forecast);
    if (!forecastUrl) throw new Error("points lookup returned no api.weather.gov forecast URL");
    const timeZone = clip(points?.properties?.timeZone, 64) || "America/New_York";
    const [forecast, alerts] = await Promise.all([
      getJson(forecastUrl, FORECAST_TTL_MS, signal),
      getJson(`${API}/alerts/active?point=${lat},${lon}`, FORECAST_TTL_MS, signal).catch(() => null),
    ]);
    const count = Math.min(14, Math.max(1, Math.trunc(days)) * 2);
    const periods = (Array.isArray(forecast?.properties?.periods) ? forecast.properties.periods : [])
      .slice(0, count)
      .map((p) => ({
        name: clip(p?.name, 40),
        isDaytime: Boolean(p?.isDaytime),
        temperature: number(p?.temperature),
        unit: p?.temperatureUnit === "C" ? "C" : "F",
        precipitationChance: number(p?.probabilityOfPrecipitation?.value),
        wind: clip(`${p?.windDirection ?? ""} ${p?.windSpeed ?? ""}`, 40),
        summary: clip(p?.shortForecast, 80),
        detail: clip(p?.detailedForecast, 300),
      }));
    if (!periods.length) throw new Error("the forecast had no periods");
    const updatedRaw = forecast?.properties?.updateTime ?? forecast?.properties?.generatedAt;
    const updatedDate = new Date(updatedRaw);
    const updated = Number.isNaN(updatedDate.getTime()) ? "unknown"
      : updatedDate.toLocaleString("en-US", { timeZone, dateStyle: "medium", timeStyle: "short" });
    return {
      place: clip(place, 80),
      source: "National Weather Service",
      sourceUrl: sourceUrl(lat, lon),
      updated,
      periods,
      alerts: alerts === null ? null
        : (Array.isArray(alerts?.features) ? alerts.features : []).slice(0, 5).map((f) => ({
            event: clip(f?.properties?.event, 80),
            severity: clip(f?.properties?.severity, 20),
            headline: clip(f?.properties?.headline, 200),
            ends: clip(f?.properties?.ends ?? f?.properties?.expires, 40),
          })),
    };
  }

  return { getForecast };
}

/** The text the model sees: one line per period, alerts first. */
export function formatText(r) {
  const lines = [
    `${r.source} forecast for ${r.place}, updated ${r.updated}.`,
    `Source link: ${r.sourceUrl}`,
    r.alerts === null ? "Active alerts: could not be checked."
      : r.alerts.length ? `Active alerts: ${r.alerts.map((a) => `${a.event} (${a.severity}): ${a.headline}`).join(" | ")}`
      : "Active alerts: none.",
  ];
  for (const p of r.periods) {
    const temp = p.temperature === null ? "" : ` ${p.isDaytime ? "High" : "Low"} ${p.temperature}°${p.unit}.`;
    const rain = p.precipitationChance === null ? "" : ` Chance of precipitation ${p.precipitationChance}%.`;
    const wind = p.wind ? ` Wind ${p.wind}.` : "";
    lines.push(`- ${p.name}: ${p.summary}.${temp}${rain}${wind} ${p.detail}`.replace(/\.\./g, "."));
  }
  return lines.join("\n");
}
