export default function Home() {
  return (
    <main className="home-shell">
      <section className="home-hero">
        <p className="home-eyebrow">Graduate training · AI from foundations to practice</p>
        <h1>AI: From Rules to<br /><em>Real-World Agents</em></h1>
        <p className="home-lead">
          A student-facing course with an interactive presentation and four practical,
          reproducible labs.
        </p>
        <div className="home-actions">
          <a className="home-primary" href="/story_deck/">Open the presentation <span>→</span></a>
          <a href="/labs/">Open the student lab kit <span>→</span></a>
        </div>
      </section>
      <section className="home-map" aria-label="Course progression">
        <article><span>01</span><div><b>Understand</b><p>History, learning, transformers, and agents</p></div></article>
        <article><span>02</span><div><b>Ground</b><p>Sources, evidence, uncertainty, and verification</p></div></article>
        <article><span>03</span><div><b>Build</b><p>Extraction, retrieval, analysis tools, and voice</p></div></article>
        <article><span>04</span><div><b>Evaluate</b><p>Interface, evidence, and human responsibility</p></div></article>
      </section>
      <footer className="home-footer">
        <p>Course-authored materials · fictional lab data · presenter notes included</p>
      </footer>
    </main>
  );
}
