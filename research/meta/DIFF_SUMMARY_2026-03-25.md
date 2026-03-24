## Batch 1

MiroFish frontier tranche 180 deeper:

- re-run the anchored `180`-domain frontier tranche from March 24, 2026 under the deeper harness instead of the weaker medium harness
- save the deeper spec, run, diagnostic, ranked readout, and markdown export under `research/meta/`
- confirm that the broader slice now stays non-zero and materially improves over the medium `180`, with top ensemble adoption at `5.33%`, top retained adoption at `6.67%`, and benchmark median adoption at `1.63%`

## Batch 2

MiroFish frontier watchtower surface:

- add a dedicated `MiroFish Frontier` watchtower page alongside the existing portfolio page
- add a local comparison HTML surface under `research/meta/` and refresh `watchtower_latest`
- fix watchtower latest-artifact resolution so it selects the real newest frontier export by modification time instead of filename sort

## Batch 3

MiroFish frontier shortlist:

- add a shortlist builder and markdown exporter for frontier readouts
- extract a fast operator shortlist from the deeper `180` frontier checkpoint under `research/meta/`
- separate the current frontier surface into `winners`, `breakouts`, and `speculative` buckets so the best domains are easier to review without reopening another simulation run
