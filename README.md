# SmallSort proof calibration

Experimental, partial defensive verification of Rust's SmallSort helpers. This
repository is not an accepted contest submission or a claim of a reward.

## Recorded results

- [Functional calibration passed](https://github.com/TheodorNEngoy/rust-smallsort-proof-lab/actions/runs/33962527486)
  at commit `2fd1f98762fca6dd63d95a84356b94fd18c7341c`: actual `sort4_stable`
  and `sort8_stable` with arbitrary i32 inputs and ordinary integer ordering.
  Sortedness and multiset preservation assertions were explicitly successful;
  zero of 115 and 186 checks failed respectively. Each had four unrelated
  unreachable checks. The deliberately false preservation control was rejected.
  Eight-element solver time was 35.14189 seconds; the complete job took 8m0s.
- Those successful runs **did not enable automatic uninitialized-read checks**.
  They are correctness results under their recorded flags, not complete memory
  safety proofs or coverage of every Rust undefined-behavior rule.
- [The explicit initialization experiment did not pass](https://github.com/TheodorNEngoy/rust-smallsort-proof-lab/actions/runs/33963822038)
  at `9be91c2415117fa2e170620739bf4b19b4a18552`. With `-Z uninit-checks`,
  pinned Kani rejects the attempted raw-pointer/union interaction. Both positive
  postconditions were unreachable; later eight-element and control steps were
  skipped. An earlier array-of-unions representation was also unsupported.
  This is a verifier modeling limitation, not evidence of a sorting defect.

The current files preserve that instrumentation experiment. Use the immutable
successful commit above for the previously verified functional harness.
No further run is scheduled. Resume only with a supported verification approach
that retains initialization checks, then establish successful detector-control
and reachable positive results before expanding scope.

## Reproduction and limits

The manually dispatched workflow checks out exact `verify-rust-std` commit
`ad7590c3dbdfeb97f2b4c7254dc5f4787ca9e783`, checks the source blob and appends a
verification module without changing target runtime logic. It uses the contest's
pinned Kani runner. No target stubs or output-initialization assumptions are added.

Full public-entrypoint contracts, wider lengths, generic types, distinguishable-key
stability and comparator-panic behavior remain outside the established results.
Award availability and eligibility have not been confirmed.

The workflow uses one standard Ubuntu runner in this public repository, a
30-minute cap and manual dispatch only. It configures no paid runner, saved
Actions cache, artifact upload, secrets or schedule. The result-gate regression
checks run locally with `python3 -B test_check_result.py`.
