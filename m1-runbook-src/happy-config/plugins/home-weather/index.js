// home-weather: one agent tool, home_weather, that returns the National Weather Service forecast
// for the fixed home location in this plugin's config (plugins.entries.home-weather.config, written
// by scripts/gen-family.mjs from family.json5). The model can only choose how many days; it cannot
// pick a place or a URL. Loaded through plugins.load.paths from ~/.config/happy/plugins/home-weather,
// where happy-deploy installs it. Search results stay the fallback for other places.
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { wrapWebContent } from "openclaw/plugin-sdk/provider-web-search";
import { clip, createNwsClient, formatText, sourceUrl } from "./nws.js";

export default definePluginEntry({
  id: "home-weather",
  name: "Home Weather",
  description: "National Weather Service forecast for the family's home town.",
  register(api) {
    const cfg = api.pluginConfig ?? {};
    const client = createNwsClient({ userAgent: cfg.userAgent });
    api.registerTool({
      name: "home_weather",
      label: "Home Weather",
      description:
        `Official National Weather Service forecast for home (${clip(cfg.place, 80)}): high or low, ` +
        "sky, chance of precipitation and wind for each 12-hour period, plus active weather alerts and " +
        "the source link. Use it for any weather question about home. For other places use web_search.",
      parameters: {
        type: "object",
        properties: {
          days: {
            type: "integer",
            minimum: 1,
            maximum: 7,
            description: "Days to include, 1-7. Default 2 (today, tonight and tomorrow).",
          },
        },
        additionalProperties: false,
      },
      async execute(_toolCallId, params, signal) {
        const days = Number.isInteger(params?.days) ? Math.min(7, Math.max(1, params.days)) : 2;
        try {
          const result = await client.getForecast({
            latitude: cfg.latitude, longitude: cfg.longitude, place: cfg.place, days, signal,
          });
          api.logger?.info?.(`home_weather: served ${result.periods.length} periods (days=${days}), NWS updated ${result.updated}`);
          return {
            content: [{ type: "text", text: wrapWebContent(formatText(result), "home_weather") }],
            details: result,
          };
        } catch (err) {
          if (signal?.aborted) throw err;
          const reason = clip(err?.message ?? err, 160);
          api.logger?.warn?.(`home_weather failed: ${reason}`);
          return {
            content: [{
              type: "text",
              text: `The National Weather Service forecast could not be fetched (${reason}). ` +
                `Say so plainly and give this link: ${sourceUrl(cfg.latitude, cfg.longitude)}`,
            }],
            details: { error: reason },
          };
        }
      },
    });
  },
});
