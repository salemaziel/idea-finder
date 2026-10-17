const assert = require("node:assert/strict");
const { createServer } = require("node:http");
const { readFile } = require("node:fs/promises");
const path = require("node:path");
const test = require("node:test");
const { chromium } = require("playwright");

// Requirement: each tab has a unique URL. A user clicks each tab, opens its URL
// directly, reloads it, and uses Back/Forward. Pass when the URL and visible tab
// agree at every step; fail on a wrong URL, wrong content, or page error.

const uiDir = path.join(__dirname, "../ui");
const fixtureData = `
const PERSONA = {
  name: "Example Founder", location: "Example City", epigraph: "A test profile",
  interviewedOn: "Today", interviewLength: "One hour"
};
const ROLES = [{
  id: "researcher", label: "Researcher", shortLabel: "Researcher",
  sublabel: "Studies problems", intensity: "daily", goal: "Learn",
  practice: [], problems: { personal: [], researched: [] }, narratives: [],
  openQuestions: ["What needs research?"]
}];
const NETWORK = [{
  id: "friend", name: "Example Friend", relation: "Friend", roles: ["Researcher"],
  overlapsWith: ["researcher"], note: "Can help"
}];
const DISCOVERY_DOC = "# Example discovery document";
Object.assign(window, { PERSONA, ROLES, NETWORK, DISCOVERY_DOC });
`;

test("each tab has a direct URL and participates in browser history", { timeout: 60_000 }, async () => {
  const files = new Set([
    "Self-Map.html", "styles.css", "tweaks-panel.jsx", "map.jsx",
    "role-page.jsx", "tabs.jsx", "tab-routing.js", "app.jsx",
  ]);
  const server = createServer(async (request, response) => {
    const filename = new URL(request.url, "http://localhost").pathname.slice(1) || "Self-Map.html";
    if (filename === "data.jsx") {
      response.writeHead(200, { "Content-Type": "text/plain" });
      response.end(fixtureData);
      return;
    }
    if (!files.has(filename)) {
      response.writeHead(404).end();
      return;
    }
    try {
      const body = await readFile(path.join(uiDir, filename));
      const type = filename.endsWith(".html") ? "text/html" :
        filename.endsWith(".css") ? "text/css" : "text/plain";
      response.writeHead(200, { "Content-Type": type }).end(body);
    } catch {
      response.writeHead(500).end();
    }
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  let browser;
  try {
    browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    const errors = [];
    page.on("pageerror", (error) => errors.push(error.message));
    const base = `http://127.0.0.1:${server.address().port}/Self-Map.html`;
    const tabs = [
      ["Self-map", "#self-map", ".column-map"],
      ["Network", "#network", ".network"],
      ["Opportunities", "#opportunities", ".opportunities"],
      ["Open questions", "#open-questions", ".questions"],
      ["Full discovery doc", "#full-discovery-doc", ".discovery"],
    ];

    await page.goto(base, { waitUntil: "domcontentloaded" });
    await page.locator(".column-map").waitFor();
    for (const [label, hash, selector] of tabs) {
      await page.getByRole("link", { name: new RegExp(label, "i") }).first().click();
      await page.waitForURL(base + hash);
      await page.locator(selector).first().waitFor();
      assert.equal(await page.locator('nav a[aria-current="page"]').count(), 1);
    }

    await page.goBack();
    await page.locator(".questions").waitFor();
    assert.equal(new URL(page.url()).hash, "#open-questions");
    await page.goForward();
    await page.locator(".discovery").waitFor();
    assert.equal(new URL(page.url()).hash, "#full-discovery-doc");

    for (const [, hash, selector] of tabs) {
      await page.goto(base + hash, { waitUntil: "domcontentloaded" });
      await page.locator(selector).first().waitFor();
    }
    await page.reload();
    await page.locator(".discovery").waitFor();
    await page.goto(base + "#unknown", { waitUntil: "domcontentloaded" });
    await page.locator(".column-map").waitFor();

    await page.goto(base + "#network", { waitUntil: "domcontentloaded" });
    await page.locator(".network-overlap-link").first().click();
    await page.waitForURL(base + "#self-map");
    await page.locator(".role-page").first().waitFor();
    assert.deepEqual(errors, []);
  } finally {
    if (browser) await browser.close();
    await new Promise((resolve) => server.close(resolve));
  }
});
