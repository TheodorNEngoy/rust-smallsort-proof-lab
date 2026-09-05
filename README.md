# SmallSort proof calibration

Experimental, partial defensive verification of Rust's `sort4_stable` helper.
This repository is not an accepted contest submission or a claim of a reward.

The [5 September 2026 calibration](https://github.com/TheodorNEngoy/rust-smallsort-proof-lab/actions/runs/33961893993)
passed at commit `d9d39bc762427c141f99178de237ee425e5faa76`:
zero of 115 positive checks failed, both named output assertions were SUCCESS,
and the deliberate value-loss control failed at exactly its intended assertion.
Four unrelated helper-path checks were unreachable; neither output assertion was.
Positive solver time was about two seconds, and the complete hosted job took 5m39s.

The manually dispatched workflow checks out the exact `verify-rust-std` commit
`ad7590c3dbdfeb97f2b4c7254dc5f4787ca9e783` and appends a proof module without
changing the target implementation. It uses the contest's pinned Kani runner.

The candidate checks sorting and multiset preservation for four arbitrary `i32`
values under ordinary integer ordering. A separate deliberately failing control
must be rejected. Full SmallSort, other lengths/types, stability, and comparator
panic behavior are outside this calibration.

The workflow uses one standard Ubuntu runner in this public repository, has a
30-minute cap, and runs only on manual dispatch. No paid runner, saved Actions
cache, artifact upload, secret, or scheduled execution is configured. A passing
workflow establishes only the scoped result shown in its logs.
