const assert = require("node:assert/strict");
const test = require("node:test");
const { TAB_HASHES, tabFromHash } = require("../ui/tab-routing.js");

test("each tab has a unique URL and resolves from its URL", () => {
  const entries = Object.entries(TAB_HASHES);
  assert.equal(entries.length, 5);
  assert.equal(new Set(entries.map(([, hash]) => hash)).size, entries.length);

  for (const [tab, hash] of entries) {
    assert.match(hash, /^#[a-z-]+$/);
    assert.equal(tabFromHash(hash), tab);
  }
});

test("missing or unknown URLs show the self-map", () => {
  assert.equal(tabFromHash(""), "map");
  assert.equal(tabFromHash("#unknown"), "map");
});
