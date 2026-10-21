// Tests for plugins/home-weather. Run from the repo root:  node --test tests/home-weather/
// The fixtures are trimmed real api.weather.gov responses (5 Oct 2026) with a fictional grid and
// coordinates. The last test loads index.js the way OpenClaw does, with the installed OpenClaw's SDK.
import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { clip, coord, createNwsClient, formatText, sourceUrl } from "../../plugins/home-weather/nws.js";

const here = path.dirname(new URL(import.meta.url).pathname);
const fixture = (name) => JSON.parse(fs.readFileSync(path.join(here, "fixtures", name), "utf8"));
const LAT = 40.1234, LON = -75.5;
const POINTS = `https://api.weather.gov/points/${LAT},${LON}`;
const FORECAST = "https://api.weather.gov/gridpoints/TST/10,20/forecast";
const ALERTS = `https://api.weather.gov/alerts/active?point=${LAT},${LON}`;

function fakeFetch(routes) {
  const calls = [];
  const fn = async (url, init) => {
    calls.push({ url, init });
    const route = routes[url];
    if (!route) return { status: 404, json: async () => ({}) };
    const r = typeof route === "function" ? route(calls.filter((c) => c.url === url).length) : route;
    return { status: r.status ?? 200, json: async () => r.body };
  };
  fn.calls = calls;
  return fn;
}
const ok = (body) => ({ status: 200, body });
const standard = (alerts = "alerts-none.json") => ({
  [POINTS]: ok(fixture("points.json")), [FORECAST]: ok(fixture("forecast.json")), [ALERTS]: ok(fixture(alerts)),
});
const client = (fetchImpl, extra = {}) =>
  createNwsClient({ userAgent: "test-agent (test@example.com)", fetchImpl, sleep: async () => {}, ...extra });

test("formats today, tonight and tomorrow with highs, lows, rain chance and the source link", async () => {
  const f = fakeFetch(standard());
  const r = await client(f).getForecast({ latitude: LAT, longitude: LON, place: "Hometown, State", days: 2 });
  assert.equal(r.periods.length, 4);
  const text = formatText(r);
  assert.match(text, /National Weather Service forecast for Hometown, State, updated Oct 5, 2026, 9:10 AM\./);
  assert.match(text, /- Today: Mostly Sunny\. High 69°F\. Chance of precipitation 0%\. Wind NW 14 to 18 mph\./);
  assert.match(text, /- Tonight: Mostly Clear\. Low 44°F\./);
  assert.match(text, /Active alerts: none\./);
  assert.ok(text.includes(`Source link: https://forecast.weather.gov/MapClick.php?lat=${LAT}&lon=${LON}`));
});

test("days limits the periods (two per day)", async () => {
  const r = await client(fakeFetch(standard())).getForecast({ latitude: LAT, longitude: LON, place: "X Y", days: 1 });
  assert.deepEqual(r.periods.map((p) => p.name), ["Today", "Tonight"]);
});

test("lists active alerts", async () => {
  const r = await client(fakeFetch(standard("alerts-one.json"))).getForecast({ latitude: LAT, longitude: LON, place: "X Y" });
  assert.match(formatText(r), /Active alerts: Wind Advisory \(Moderate\): Wind Advisory issued/);
});

test("a failed alerts lookup does not lose the forecast", async () => {
  const routes = standard(); routes[ALERTS] = { status: 500, body: {} };
  const r = await client(fakeFetch(routes)).getForecast({ latitude: LAT, longitude: LON, place: "X Y" });
  assert.equal(r.alerts, null);
  assert.match(formatText(r), /Active alerts: could not be checked\./);
});

test("refuses a forecast URL that is not on api.weather.gov", async () => {
  const routes = standard();
  routes[POINTS] = ok({ properties: { forecast: "https://evil.example/gridpoints/TST/10,20/forecast" } });
  await assert.rejects(client(fakeFetch(routes)).getForecast({ latitude: LAT, longitude: LON, place: "X Y" }),
                       /no api.weather.gov forecast URL/);
  routes[POINTS] = ok({ properties: { forecast: "http://api.weather.gov/gridpoints/TST/10,20/forecast" } });
  await assert.rejects(client(fakeFetch(routes)).getForecast({ latitude: LAT, longitude: LON, place: "X Y" }));
});

test("sends the User-Agent, refuses redirects, and only ever calls api.weather.gov", async () => {
  const f = fakeFetch(standard());
  await client(f).getForecast({ latitude: LAT, longitude: LON, place: "X Y" });
  assert.equal(f.calls.length, 3);
  for (const c of f.calls) {
    assert.equal(new URL(c.url).origin, "https://api.weather.gov");
    assert.equal(c.init.headers["User-Agent"], "test-agent (test@example.com)");
    assert.equal(c.init.redirect, "error");
  }
});

test("retries once on a 5xx, not on a 4xx", async () => {
  const routes = standard();
  routes[FORECAST] = (n) => (n === 1 ? { status: 503, body: {} } : ok(fixture("forecast.json")));
  const f = fakeFetch(routes);
  await client(f).getForecast({ latitude: LAT, longitude: LON, place: "X Y" });
  assert.equal(f.calls.filter((c) => c.url === FORECAST).length, 2);

  const routes2 = standard(); routes2[FORECAST] = { status: 404, body: {} };
  const f2 = fakeFetch(routes2);
  await assert.rejects(client(f2).getForecast({ latitude: LAT, longitude: LON, place: "X Y" }), /HTTP 404/);
  assert.equal(f2.calls.filter((c) => c.url === FORECAST).length, 1);
});

test("caches the forecast for ten minutes and the grid for a day", async () => {
  let t = 0;
  const f = fakeFetch(standard());
  const c = client(f, { now: () => t });
  await c.getForecast({ latitude: LAT, longitude: LON, place: "X Y" });
  await c.getForecast({ latitude: LAT, longitude: LON, place: "X Y" });
  assert.equal(f.calls.length, 3);
  t = 11 * 60 * 1000;
  await c.getForecast({ latitude: LAT, longitude: LON, place: "X Y" });
  assert.equal(f.calls.filter((x) => x.url === POINTS).length, 1);
  assert.equal(f.calls.filter((x) => x.url === FORECAST).length, 2);
});

test("coordinates: four decimals, no trailing zeros, range-checked", () => {
  assert.equal(coord(40.12340, -90, 90), "40.1234");
  assert.equal(coord(-75.5000, -180, 180), "-75.5");
  assert.equal(coord(40.123456, -90, 90), "40.1235");
  assert.throws(() => coord(91, -90, 90));
  assert.throws(() => coord("x", -90, 90));
  assert.equal(sourceUrl(40.1, -75), "https://forecast.weather.gov/MapClick.php?lat=40.1&lon=-75");
});

test("clip removes control characters and caps the length", () => {
  assert.equal(clip("a\u0000b\n\nc", 10), "a b c");
  assert.equal(clip("x".repeat(20), 5), "xxxx…");
  assert.equal(clip(undefined, 5), "");
});

test("requires a User-Agent", () => {
  assert.throws(() => createNwsClient({ fetchImpl: async () => ({}) }), /userAgent is required/);
});

test("index.js registers home_weather and returns wrapped NWS text (OpenClaw SDK)", async (t) => {
  const sdk = "/opt/homebrew/lib/node_modules/openclaw";
  if (!fs.existsSync(path.join(sdk, "package.json"))) return t.skip("OpenClaw not installed here");
  // Load the plugin from a temp copy whose node_modules/openclaw points at the installed OpenClaw,
  // as the gateway's loader resolves openclaw/plugin-sdk/* for a plugin.
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "home-weather-"));
  for (const f of ["index.js", "nws.js", "package.json", "openclaw.plugin.json"]) {
    fs.copyFileSync(path.join(here, "../../plugins/home-weather", f), path.join(dir, f));
  }
  fs.mkdirSync(path.join(dir, "node_modules"));
  fs.symlinkSync(sdk, path.join(dir, "node_modules", "openclaw"));
  const entry = (await import(path.join(dir, "index.js"))).default;
  const register = () => {          // each registration has its own client and cache
    const tools = [];
    entry.register({
      pluginConfig: { place: "Hometown, State", latitude: LAT, longitude: LON, userAgent: "test-agent (test@example.com)" },
      logger: { warn() {}, info() {}, debug() {}, error() {} },
      registerTool: (tool) => tools.push(tool),
    });
    return tools;
  };
  const tools = register();
  assert.deepEqual(tools.map((x) => x.name), ["home_weather"]);
  const manifest = JSON.parse(fs.readFileSync(path.join(dir, "openclaw.plugin.json"), "utf8"));
  assert.deepEqual(manifest.contracts.tools, ["home_weather"]);

  const realFetch = globalThis.fetch;
  globalThis.fetch = fakeFetch(standard());
  try {
    const out = await tools[0].execute("call-1", { days: 1 }, undefined);
    const text = out.content[0].text;
    assert.match(text, /EXTERNAL_UNTRUSTED_CONTENT/);
    assert.match(text, /- Today: Mostly Sunny\. High 69°F\./);
    assert.doesNotMatch(text, /Tuesday/);
    globalThis.fetch = fakeFetch({});   // every URL 404s
    const failed = await register()[0].execute("call-2", {}, undefined);
    assert.match(failed.content[0].text, /could not be fetched \(HTTP 404 from api\.weather\.gov\)\. Say so plainly/);
  } finally {
    globalThis.fetch = realFetch;
    fs.rmSync(dir, { recursive: true, force: true });
  }
});
