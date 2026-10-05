# Methodology Notes — TVB-20 Prototype

## What is this?

The CIII / TVB-20 tool in the parent repo is a **standalone educational
prototype**. It can be run, tested, and deployed independently of any
specific research project.

## Educational framing

The tool illustrates one core idea from introductory financial education:

> A small monthly contribution, when combined with compound interest over
> enough years, can grow far beyond its principal sum.

This is sometimes called the *time value of money* or *the power of
compounding*. It is a standard topic in personal-finance and
introductory-economics courses.

## Why a "diagnostic" angle?

Many introductory financial-education materials present the compound
formula and ask the student to *trust* the result. This tool instead
asks the student to *estimate* first, then reveals the gap. The pedagogical
hypothesis is that this *prediction-error* loop is more memorable than a
purely expository lesson.

This is an exploratory hypothesis. The tool itself does not measure
whether the approach actually improves outcomes.

## Caveats and limitations

- The 8% annual return is **not** an investment recommendation.
  It is a teaching number high enough to make the compounding effect
  visible within a classroom-friendly horizon (under 18 years).
- Classification thresholds (MOP $60k / $120k / $200k) are calibrated to
  the default scenario (MOP 300/mo × 18y × 8%). If the user changes the
  scenario, the thresholds remain the same and may no longer be meaningful.
  Future versions could make thresholds scenario-aware.
- The app does not validate that inputs are *realistic*. A negative
  PMT or an absurdly high annual return will produce a valid-looking
  number. Use the slider responsibly.

## What the tool is *not*

- Not an investment recommendation engine.
- Not a financial-planning tool.
- Not a regulated financial service.
- Not a substitute for qualified financial advice.

## Privacy

The tool collects nothing. Inputs exist only in the running session memory
and are discarded when the session ends. There is no analytics, no login,
no telemetry, and no external API call.

## How to extend

Possible educational extensions:

- Add **risk-aware** projections showing percentile bands, not just point estimates.
- Add a **reverse calculator — what monthly contribution reaches a target?
- Add a **multi-scenario compare** view: low / mid / high rate side by side.
- Localise the UI strings into multiple languages.
- Add a **teacher dashboard** view (still local, still no data leaves the machine).

Possible code extensions:

- Replace Streamlit with a plain HTML/JS bundle for offline-rendering use case.
- Move the `classify_estimate` thresholds into a JSON config so they can be edited without code changes.
- Add a **batch CSV import** mode for teachers who want to run the tool offline over a class set of paper-form responses.

## Why MIT?

MIT was chosen because:

- It allows maximum reuse (good for educational tools).
- It is the most common license in the Streamlit / scientific-Python community.
- It does not impose copyleft on derivative codebases.

## Contributing back

We do welcome issues and pull requests for:

- Better educational explanations.
- Accessibility improvements.
- Additional language support.
- Additional scenario parameters.

We do **not** welcome pull requests that:

- Add user tracking, analytics, or telemetry of any kind.
- Add login / authentication requirements.
- Add any external API call.
- Add any data persistence.
- Convert this into a financial-product promotion tool.

The privacy guarantee is the project's main design constraint.

## Versioning

We follow semantic versioning.

- 1.x.y — additive changes (new scenarios, language packs)
- 1.x.0 — minor behavior changes (new defaults)
- 2.0.0 — breaking changes (API or scenario defaults)

## Maintenance

This is a personal portfolio project. Maintenance is best-effort.
Security issues are welcome via GitHub Issues.