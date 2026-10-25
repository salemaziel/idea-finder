const TAB_HASHES = Object.freeze({
  map: "#self-map",
  network: "#network",
  opportunities: "#opportunities",
  questions: "#open-questions",
  discovery: "#full-discovery-doc",
});

function tabFromHash(hash) {
  return Object.keys(TAB_HASHES).find((tab) => TAB_HASHES[tab] === hash) || "map";
}

if (typeof module !== "undefined") {
  module.exports = { TAB_HASHES, tabFromHash };
}
