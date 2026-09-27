import { useEffect, useRef, useState } from 'react';
import RefineFrame from './components/RefineFrame';

const INSTALL_COMMAND = 'npx reigns-work install';

// The hero background resolves once on load: queued → generating → refining → complete.
const SEQUENCE = [
  ['queued', 900],
  ['generating', 1800],
  ['refining', 1600],
  ['complete', 0]
];

const LABELS = {
  queued: 'Watching',
  generating: 'Checking',
  refining: 'Refining',
  complete: 'All clear',
  error: 'Lost the trail'
};

function useStatusSequence() {
  const [index, setIndex] = useState(0);
  useEffect(() => {
    if (index >= SEQUENCE.length - 1) return undefined;
    const id = setTimeout(() => setIndex(i => i + 1), SEQUENCE[index][1]);
    return () => clearTimeout(id);
  }, [index]);
  return SEQUENCE[index][0];
}

const COMPANIONS = [
  {
    id: 'mamu',
    name: 'Mamu',
    art: '/mamu.svg',
    scene: 'sunset',
    tagline: 'The wild west trailblazer',
    body:
      "Mamu is a wild west horse who loves nothing more than riding off into the sunset. Saddle up, and Mamu will keep you on the trail all the way out to the great frontier: a finished project, an aced test, or a better life."
  },
  {
    id: 'mia',
    name: 'Mia',
    art: '/mia.svg',
    scene: 'stars',
    tagline: 'The southern stargazer',
    body:
      "Mia is a southern girl who loves every activity there is, but her favorite comes after dark: watching the stars. She'll trace the constellations with you toward the same frontier: a finished project, an aced test, or a better life."
  }
];

// Fixed star positions for Mia's night sky, as [left %, top %, size px].
const STARS = [
  [8, 14, 3], [18, 38, 2], [27, 10, 2], [36, 26, 3], [62, 12, 2], [72, 30, 3],
  [84, 16, 2], [91, 40, 3], [12, 62, 2], [88, 64, 2], [50, 8, 2], [78, 52, 2]
];

// Heat stages, matching engine/app/heat.py (LEVEL_BOUNDS) and the companion's expressions.
const STAGES = [
  {
    id: 'calm',
    level: '0',
    title: 'Calm',
    heat: 'Heat 0–10',
    body: name => `Everything checks out. Claude's answers line up with the evidence, so ${name} just keeps a quiet eye on the chat.`
  },
  {
    id: 'curious',
    level: '1',
    title: 'Curious',
    heat: 'Heat 11–30',
    body: name => `Something couldn't be confirmed either way. The orange ? badge counts the unverified claims. ${name} wants a second look, but nothing is wrong yet.`
  },
  {
    id: 'concerned',
    level: '2',
    title: 'Concerned',
    heat: 'Heat 31–55',
    body: () => 'Unverified claims are piling up, or Claude gave in the moment you pushed back. Cue the side-eye: take its answers with a grain of salt.'
  },
  {
    id: 'alarmed',
    level: '3',
    title: 'Alarmed',
    heat: 'Heat 56–80',
    body: () => "Claude said something the evidence contradicts: a likely hallucination. Up goes the red flag. Reigns shows what it found and offers a Fix it prompt that asks Claude to recheck."
  },
  {
    id: 'meltdown',
    level: '4',
    title: 'Meltdown',
    heat: 'Heat 81–100',
    body: () => 'Several likely hallucinations. The conversation has gone off the rails, so Reigns suggests starting fresh, carrying over only what holds up.'
  },
  {
    id: 'recovered',
    level: 'R',
    title: 'Recovered',
    heat: 'After a verified fix',
    body: name => `Claude's next reply fixed the flagged claim and Reigns checked it. Heat drops and ${name} does a happy little hop.`
  }
];

function Stages({ character }) {
  const { name } = COMPANIONS.find(c => c.id === character);
  return (
    <div className="stages" key={character}>
      <div className="stages-head">
        <h3>
          How {name} reacts
        </h3>
        <p>
          Reigns scores each reply for trouble. That score is the <strong>heat</strong>: it rises with
          unverified claims, caving to pushback and likely hallucinations, and cools with clean answers,
          verified fixes and time. {name}'s face shows where it stands.
        </p>
      </div>
      <ol className="stage-list">
        {STAGES.map(stage => (
          <li key={stage.id} className={`stage stage--${stage.id}`}>
            <div className="stage-art">
              <img src={`/stages/${character}-${stage.id}.svg`} alt={`${name} looking ${stage.title.toLowerCase()}`} />
            </div>
            <div className="stage-label">
              <span>{stage.level}</span> {stage.title}
            </div>
            <p className="stage-heat">{stage.heat}</p>
            <p className="stage-body">{stage.body(name)}</p>
          </li>
        ))}
      </ol>
    </div>
  );
}

function CompanionCard({ name, art, scene, tagline, body, selected, onSelect }) {
  return (
    <button
      type="button"
      className={`companion companion--${scene}`}
      aria-pressed={selected}
      aria-controls="stages"
      onClick={onSelect}
    >
      <div className="companion-scene">
        {scene === 'sunset' ? (
          <div className="sun" aria-hidden="true" />
        ) : (
          <div className="sky" aria-hidden="true">
            {STARS.map(([x, y, size], i) => (
              <span
                key={i}
                className="star"
                style={{ left: `${x}%`, top: `${y}%`, width: size, height: size, animationDelay: `${(i % 5) * 0.6}s` }}
              />
            ))}
          </div>
        )}
        <div className="ground" aria-hidden="true" />
        <img src={art} alt={`${name}, the Reigns companion`} className="companion-art" />
      </div>
      <div className="companion-body">
        <p className="companion-tag">{tagline}</p>
        <h3>{name}</h3>
        <p>{body}</p>
        <span className="companion-cta">{selected ? `Showing ${name}'s moods ↓` : `See ${name}'s moods`}</span>
      </div>
    </button>
  );
}

const FLOW = [
  {
    title: 'Extract',
    body: "Claude's reply is broken into individual claims: facts, numbers, papers, links, packages, code calls."
  },
  {
    title: 'Triage',
    body: 'Each claim gets a risk level. Opinions and small talk are skipped; specific names, dates and citations go straight to checking.'
  },
  {
    title: 'Check',
    body: 'Claims are routed to the detectors built for them, which search real sources in parallel.'
  },
  {
    title: 'Decide',
    body: 'The results merge into one verdict per claim, and the heat score moves your companion up or down.'
  }
];

const DETECTORS = [
  {
    name: 'Reference Auditor',
    catches: 'Fake papers & dead links',
    how: 'Looks up cited papers in Crossref, Semantic Scholar and OpenAlex, opens links, and checks packages exist on PyPI or npm.'
  },
  {
    name: 'Claim Verifier',
    catches: 'Wrong dates, numbers & names',
    how: 'Searches the web and Wikipedia, then a judge compares the claim to the sources and must quote the exact line that settles it.'
  },
  {
    name: 'Consistency Probe',
    catches: 'Made-up niche facts',
    how: "When no search can settle it, the same question is asked 5 fresh times. Real knowledge repeats; invented answers scatter."
  },
  {
    name: 'Code API Checker',
    catches: 'Functions that don\u2019t exist',
    how: 'Reads Python code without running it and checks every function and argument against the real library.'
  },
  {
    name: 'Pushback Detector',
    catches: 'Caving under pressure',
    how: 'When you push back without new evidence, it checks whether Claude flipped its answer just to agree with you.'
  },
  {
    name: 'Source Faithfulness',
    catches: 'Summaries that drift',
    how: "Checks every point in a summary against the document you pasted, and flags anything that isn't in it."
  },
  {
    name: 'Memory Consistency',
    catches: 'Forgetting what you said',
    how: 'Remembers your constraints and setup, like "I\u2019m on Python 3.8", and flags replies that contradict them.'
  }
];

const VERDICTS = [
  ['green', 'Supported', 'Real sources confirm it.'],
  ['amber', 'Unverified', "Couldn't be confirmed either way. Worth a second look."],
  ['red', 'Likely hallucination', 'Evidence contradicts it, or it was clearly invented.']
];

const FINDINGS = [
  ['red', 'Completed in 1899', 'Claim Verifier', '\u00b7 Wikipedia: completed March 1889'],
  ['green', '330 metres tall', 'Claim Verifier', '\u00b7 matches Wikipedia'],
  ['amber', 'Night watchman Henri Morel', 'Consistency Probe', '\u00b7 5 re-asks gave 4 different names'],
  ['red', 'Lemoine & Duval (2014)', 'Reference Auditor', '\u00b7 no such paper in 3 databases']
];

const MEMORY = [
  {
    collection: 'cases',
    title: 'Past verdicts',
    body: 'Claims confirmed right or wrong by real evidence are saved with vector embeddings. When a new claim looks familiar, Atlas Vector Search hands the judge the closest past cases.'
  },
  {
    collection: 'feedback',
    title: 'False positives',
    body: "Click \u201cI disagree\u201d on a flag and Reigns records which detector raised it and how confident it was, so mistakes aren't forgotten."
  },
  {
    collection: 'detector_calibration',
    title: 'Self-tuning detectors',
    body: "If too many of a detector's recent red flags get disagreed with, Reigns raises that detector's bar. False alarms fade out on their own."
  }
];

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    } catch {
      setCopied(false);
    }
  };
  return (
    <button type="button" className="copy" onClick={copy} aria-label="Copy install command">
      {copied ? 'Copied' : 'Copy'}
    </button>
  );
}

export default function App() {
  const status = useStatusSequence();
  const [character, setCharacter] = useState('mia');
  const stagesRef = useRef(null);

  const selectCharacter = id => {
    setCharacter(id);
    const el = stagesRef.current;
    if (el && el.getBoundingClientRect().top > window.innerHeight * 0.6) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <>
      <header className="nav">
        <a href="#top" className="brand">
          <img src="/logo.svg" alt="" className="brand-mark" />
          <span>Reigns</span>
        </a>
        <nav>
          <a href="#install">Install</a>
          <a href="#companions">Companions</a>
          <a href="#detection">How it works</a>
          <a href="#install" className="nav-cta">Get Reigns</a>
        </nav>
      </header>

      <main id="top">
        <section className="hero">
          <RefineFrame
            status={status}
            width={4000}
            radius={0}
            background="#FFF3D1"
            color="#3B2412"
            stageDuration={500}
            labels={LABELS}
            hideAfter={1600}
            className="hero-bg"
          >
            <img src="/warmtone.jpg" alt="" />
          </RefineFrame>
          <div className="hero-scrim" aria-hidden="true" />

          <div className="hero-copy">
            <p className="eyebrow">For macOS · Works with Claude</p>
            <h1>
              Get a <em>Clearer Picture</em>
            </h1>
            <p className="lede">
              Reigns is a small desktop companion that sits beside your Claude chats, spots
              hallucinations as they happen, and helps you steer the conversation back on course.
            </p>
            <div className="hero-actions">
              <a href="#install" className="btn btn-primary">Install in one line</a>
              <code className="hero-cmd">{INSTALL_COMMAND}</code>
            </div>
          </div>
        </section>

        <section id="install" className="install">
          <div className="install-head">
            <p className="eyebrow">Get started</p>
            <h2>Install from your terminal</h2>
            <p>One command sets up Reigns on your Mac. No account, no config.</p>
          </div>

          <div className="terminal">
            <div className="terminal-bar">
              <span className="dot" />
              <span className="dot" />
              <span className="dot" />
              <span className="terminal-title">Terminal</span>
            </div>
            <div className="terminal-body">
              <div className="line">
                <span className="prompt">$</span>
                <code>{INSTALL_COMMAND}</code>
                <CopyButton text={INSTALL_COMMAND} />
              </div>
            </div>
          </div>

          <ol className="steps">
            <li>
              <span>1</span>
              <div>
                <h3>Open Terminal</h3>
                <p>Needs Node 18 or newer.</p>
              </div>
            </li>
            <li>
              <span>2</span>
              <div>
                <h3>Run the command</h3>
                <p>Reigns installs and launches itself.</p>
              </div>
            </li>
            <li>
              <span>3</span>
              <div>
                <h3>Chat as usual</h3>
                <p>Reigns watches quietly and speaks up when something's off.</p>
              </div>
            </li>
          </ol>
        </section>

        <section id="companions" className="companions">
          <div className="section-head">
            <p className="eyebrow">Meet your guides</p>
            <h2>Take The Reigns</h2>
            <p>Pick the companion who rides alongside you. Both keep an eye on your chats and nudge you back on course. Tap one to see their moods.</p>
          </div>
          <div className="companion-grid">
            {COMPANIONS.map(c => (
              <CompanionCard key={c.id} {...c} selected={character === c.id} onSelect={() => selectCharacter(c.id)} />
            ))}
          </div>
          <div id="stages" ref={stagesRef} className="stages-anchor">
            <Stages character={character} />
          </div>
        </section>


        <section id="detection" className="course">
          <div className="section-head">
            <p className="eyebrow">Under the hood</p>
            <h2>How Reigns spots a hallucination</h2>
            <p>
              Every time Claude replies, Reigns pulls out the claims it makes and checks each one
              against the real world, in seconds, while you keep chatting.
            </p>
          </div>

          <ol className="flow">
            {FLOW.map((step, i) => (
              <li key={step.title}>
                <span className="flow-num">{i + 1}</span>
                <h3>{step.title}</h3>
                <p>{step.body}</p>
              </li>
            ))}
          </ol>

          <div className="detectors">
            <div className="detectors-head">
              <h3>Seven specialists, one verdict</h3>
              <p>Each kind of claim goes to the detector built for it. They run side by side.</p>
            </div>
            <div className="detector-grid">
              {DETECTORS.map(d => (
                <article key={d.name} className="detector">
                  <p className="detector-catches">{d.catches}</p>
                  <h4>{d.name}</h4>
                  <p>{d.how}</p>
                </article>
              ))}
            </div>
          </div>

          <div className="course-demo">
            <div className="course-copy">
              <h3>Green, amber, red</h3>
              <p>
                Every claim ends up with one color, highlighted right on Claude's reply. Reigns follows
                one strict rule: <strong>a claim only turns red when independent evidence backs it up.</strong>{' '}
                When in doubt, it's amber.
              </p>
              <ul className="verdicts">
                {VERDICTS.map(([tone, name, desc]) => (
                  <li key={tone}>
                    <span className={`tone tone--${tone}`} />
                    <div>
                      <strong>{name}</strong>
                      <p>{desc}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
            <figure className="prompt-card reply-card">
              <figcaption>
                <img src="/mia.svg" alt="" />
                <span>Claude's reply, checked</span>
              </figcaption>
              <p className="reply">
                The Eiffel Tower was <mark className="hl hl--red">completed in 1899</mark> for the
                World's Fair. It stands <mark className="hl hl--green">330 metres tall</mark>, and its
                first night watchman was <mark className="hl hl--amber">a man named Henri Morel</mark>.
                For the engineering story, see{' '}
                <mark className="hl hl--red">Lemoine &amp; Duval (2014), “Iron Lattices of Paris”</mark>.
              </p>
              <ul className="findings">
                {FINDINGS.map(([tone, claim, detector, result]) => (
                  <li key={claim}>
                    <span className={`tone tone--${tone}`} />
                    <div>
                      <strong>{claim}</strong>
                      <p>
                        <span className="finding-detector">{detector}</span> {result}
                      </p>
                    </div>
                  </li>
                ))}
              </ul>
            </figure>
          </div>

          <div className="memory">
            <div className="memory-head">
              <p className="eyebrow">Powered by MongoDB Atlas</p>
              <h3>Sharper with every ride</h3>
              <p>
                Reigns remembers how past claims were settled and where it was wrong, so its detectors
                get more accurate the more you use it.
              </p>
            </div>
            <div className="memory-grid">
              {MEMORY.map(item => (
                <article key={item.title} className="memory-card">
                  <code>{item.collection}</code>
                  <h4>{item.title}</h4>
                  <p>{item.body}</p>
                </article>
              ))}
            </div>
            <p className="privacy">
              No conversation text, pasted documents or names are ever stored in the database. Only the
              short, normalized claim and the outcome. Your chats stay on your Mac.
            </p>
          </div>
        </section>
      </main>

      <footer className="footer">
        <span className="brand small">
          <img src="/logo-light.svg" alt="" className="brand-mark" />
          Reigns
        </span>
        <span>Made for people who double-check.</span>
      </footer>
    </>
  );
}
