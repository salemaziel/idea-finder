/* app.jsx — root component. Owns active tab, selected role, question answers,
   and tweak state. */

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "tone": "cream",
  "showHints": true
}/*EDITMODE-END*/;

// Persist answers to localStorage and POST each new answer to the server so
// it is appended to discovery.md under ## QUESTION ANSWERS.
const LS_KEY = "self-map-answers";

function loadAnswers() {
  try { return JSON.parse(localStorage.getItem(LS_KEY) || "{}"); }
  catch { return {}; }
}

function persistAnswer(roleId, idx, text) {
  const role = ROLES.find((r) => r.id === roleId);
  if (!role) return;
  fetch("/save-answer", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      roleLabel: role.label,
      question:  role.openQuestions[idx],
      answer:    text,
    }),
  }).catch((err) => console.warn("save-answer:", err));
}

function App() {
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);
  const [tab, setTab] = React.useState(() => tabFromHash(window.location.hash));
  const [selectedId, setSelectedId] = React.useState(null);
  const [answers, setAnswers] = React.useState(loadAnswers); // { questionKey: { kind:'answer'|'skip', text? } }
  const [docOpen, setDocOpen] = React.useState(false);

  React.useEffect(() => {
    const syncTab = () => setTab(tabFromHash(window.location.hash));
    window.addEventListener("hashchange", syncTab);
    return () => window.removeEventListener("hashchange", syncTab);
  }, []);

  // Mirror answers to localStorage whenever they change.
  React.useEffect(() => {
    localStorage.setItem(LS_KEY, JSON.stringify(answers));
  }, [answers]);

  // Apply tone to <html> so the CSS variable set switches.
  React.useEffect(() => {
    document.documentElement.dataset.tone = t.tone;
  }, [t.tone]);

  // Close role page when switching to a different tab.
  React.useEffect(() => {
    if (tab !== "map") setSelectedId(null);
  }, [tab]);

  // ESC returns from a role page to the map.
  React.useEffect(() => {
    const onKey = (e) => {
      if (e.key === "Escape" && selectedId) setSelectedId(null);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [selectedId]);

  const selectedRole = ROLES.find((r) => r.id === selectedId) || null;
  const selectedIdx = selectedRole ? ROLES.findIndex((r) => r.id === selectedRole.id) : -1;
  const prevRoleId = selectedIdx > 0 ? ROLES[selectedIdx - 1].id : null;
  const nextRoleId = selectedIdx >= 0 && selectedIdx < ROLES.length - 1 ? ROLES[selectedIdx + 1].id : null;

  // Derive the CSS accent so children that need to set inline accent (svg
  // strokes, narrative pill borders) read the live value.
  const accent =
    t.tone === "linen" ? "oklch(0.480 0.090 220)" :
    t.tone === "slate" ? "oklch(0.760 0.090 75)" :
    "oklch(0.520 0.115 40)";

  const openQuestionCount = ROLES.reduce(
    (n, r) => n + r.openQuestions.filter((_, i) => !answers[`${r.id}-${i}`]).length,
    0
  );

  const onSelectRole = (id) => {
    window.location.hash = TAB_HASHES.map;
    setTab("map");
    setSelectedId(id);
  };

  const tabs = [
    { key: "map", label: "Self-map" },
    { key: "network", label: "Network", count: NETWORK.length },
    { key: "opportunities", label: "Opportunities" },
    { key: "questions", label: "Open questions", count: openQuestionCount },
    { key: "discovery", label: "Full discovery doc" },
  ];

  return (
    <div className="app">
      <header className="topbar">
        <div className="topbar-brand">
          <b>Self</b><span>&nbsp;a personal cartography</span>
        </div>
        <div className="topbar-meta">
          <span>Subject · {PERSONA.name}</span>
          <span>Interviewed · {PERSONA.interviewedOn}</span>
        </div>
      </header>

      <nav className="nav" aria-label="Primary">
        {tabs.map((x, i) => (
          <a
            key={x.key}
            href={TAB_HASHES[x.key]}
            className={`nav-btn ${tab === x.key ? "is-active" : ""}`}
            aria-current={tab === x.key ? "page" : undefined}
          >
            <span>{String(i + 1).padStart(2, "0")} · {x.label}</span>
            {x.count != null && <span className="nav-btn-count">{x.count}</span>}
          </a>
        ))}
      </nav>

      <main className="main">
        {tab === "map" && !selectedRole && (
          <SelfMap
            roles={ROLES}
            persona={PERSONA}
            selectedId={selectedId}
            onSelect={setSelectedId}
          />
        )}

        {tab === "map" && selectedRole && (
          <RolePage
            role={selectedRole}
            onBack={() => setSelectedId(null)}
            onPrev={prevRoleId ? () => setSelectedId(prevRoleId) : null}
            onNext={nextRoleId ? () => setSelectedId(nextRoleId) : null}
            accent={accent}
          />
        )}

        {tab === "network" && (
          <NetworkTab
            persona={PERSONA}
            network={NETWORK}
            roles={ROLES}
            onSelectRole={onSelectRole}
          />
        )}

        {tab === "opportunities" && (
          <OpportunitiesTab roles={ROLES} accent={accent} />
        )}

        {tab === "questions" && (
          <QuestionsTab
            roles={ROLES}
            answers={answers}
            onAnswer={(k, text) => {
              setAnswers((prev) => ({ ...prev, [k]: { kind: "answer", text } }));
              // k is "${roleId}-${idx}" — decode and ship to server
              const dash = k.lastIndexOf("-");
              persistAnswer(k.slice(0, dash), parseInt(k.slice(dash + 1), 10), text);
            }}
            onSkip={(k) =>
              setAnswers((prev) => ({ ...prev, [k]: { kind: "skip" } }))
            }
            accent={accent}
          />
        )}

        {tab === "discovery" && (
          <DiscoveryDocTab persona={PERSONA} doc={DISCOVERY_DOC} />
        )}
      </main>

      <footer className="footer">
        <span>SELF · cartography of a person</span>
        <span>{ROLES.length} roles · {NETWORK.length} in close circle · {openQuestionCount} open questions</span>
      </footer>

      <DiscoveryDoc
        open={docOpen}
        onClose={() => setDocOpen(false)}
        persona={PERSONA}
        doc={DISCOVERY_DOC}
      />

      <TweaksPanel title="Tweaks">
        <TweakSection label="Palette">
          <TweakRadio
            label="Tone"
            value={t.tone}
            options={[
              { value: "cream", label: "Cream" },
              { value: "linen", label: "Linen" },
              { value: "slate", label: "Slate" },
            ]}
            onChange={(v) => setTweak("tone", v)}
          />
        </TweakSection>

        <TweakSection label="Source material" />
        <TweakButton
          label="Open discovery document"
          onClick={() => setDocOpen(true)}
        />
        <div style={{
          marginTop: 8,
          fontSize: 11,
          lineHeight: 1.5,
          color: "rgba(41,38,27,.55)",
        }}>
          The transcribed interview the map was built from. Mocked here as a
          single document — in production this would be the actual file {PERSONA.name}
          and the interviewer worked through together.
        </div>
      </TweaksPanel>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
