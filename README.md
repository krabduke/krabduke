
## Keenan

Liceo scientifico student in Rome. I build quantitative research infrastructure,
multi-agent LLM systems, and FPV hardware — mostly because each one keeps
turning out to need the others.

### K2 Capital Management

A personal quantitative research platform, and the thing most of my other work
feeds into. It runs a multi-agent pipeline that produces a daily intelligence
brief: separate agents cover geopolitics, macro, equities, and crypto, a writer
assembles the draft, and a formatter enforces structure before it publishes to
a vault and a site.

The parts that were actually hard:

- **Local inference where it fits.** Classification and formatting run on local
  models; only synthesis calls out. That decision is a cost model, not a
  preference, and it shapes the whole architecture.
- **Structured output from small models.** They emit JSON wrapped in prose,
  fenced in markdown, with trailing commas. Getting reliable structure out of
  them needs a validation and repair loop, not better prompting.
- **Taxonomy drift.** Three systems — pipeline, vault, and site — each grew
  their own idea of what a theme is, and they disagree in ways that only
  surface at publish time.

### What else is here

Perpetuals trading research on Hyperliquid, a Polymarket short-horizon data
pipeline, and FPV builds including a parametric frame designed in OpenSCAD.

### Small tools

Standalone utilities extracted from the above, each with tests and a README
that says what it cannot do:

| | |
|---|---|
| [papertrade](https://github.com/krabduke/papertrade) | Backtest engine that fills at the next bar's open, so a strategy cannot act on information it did not have |
| [truncated-loss](https://github.com/krabduke/truncated-loss) | Does cutting losses short help? Measured across paths, not asserted |
| [funding-basis](https://github.com/krabduke/funding-basis) | Perp funding normalised across venues that settle on different schedules |
| [calibration](https://github.com/krabduke/calibration) | Is your 70% actually 70%? Brier score and reliability diagrams |
| [schema-guard](https://github.com/krabduke/schema-guard) | Force any model to return schema-valid JSON, or fail with the history |
| [blackbox](https://github.com/krabduke/blackbox) | Betaflight log analysis with a hand-rolled radix-2 FFT |
| [ais-decode](https://github.com/krabduke/ais-decode) | Decode AIS ship broadcasts; detect chokepoint transits |
| [secretscan](https://github.com/krabduke/secretscan) | Find credentials in a repo's history before it goes public |

Everything above is standard library only. `git clone` and run it.

### Elsewhere

Model UN (RIMUN, THIMUN). Reading mostly history and market microstructure.

