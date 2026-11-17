# terminology answers

**TE-01.** `=` compares display and version too; use `~`. *Fail if* it blames the value set.

**TE-02.** `system-version` (default when the value set does not fix one) and `force-system-version` (overrides); `check-system-version` errors on mismatch.

**TE-03.** No: the expansion uses `http://snomed.info/sct`; the OID form does not match. Fix the data or map it.

**TE-04.** Commit expanded ValueSets (with expansion parameters) under `input/vocabulary/valueset/` and point the tooling at them.
