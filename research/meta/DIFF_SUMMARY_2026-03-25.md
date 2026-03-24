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

## Batch 4

MiroFish frontier shortlist watchtower surface:

- update the `MiroFish Frontier` watchtower page to render the saved deeper `180` shortlist before the full frontier export
- fix the shortlist-artifact resolver so the page chooses the shortlist export instead of the similarly named shortlist note
- refresh `research/meta/watchtower_latest/` so the repo-local dashboard shows the current frontier winners first

## Batch 5

MiroFish frontier localhost shortlist surface:

- update the repo-local `MIROFISH_FRONTIER_CHECKPOINTS_2026-03-25.html` page to render the saved deeper `180` shortlist above the checkpoint comparison
- keep the existing deeper `90` / medium `180` / deeper `180` comparison intact below the shortlist
- make the local host view show the currently chosen chips immediately instead of forcing the user to scan the full checkpoint comparison first
