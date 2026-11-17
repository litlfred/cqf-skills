# terminology answers

**TE-01.** `=` compares display and version too; use `~`. *Fail if* it blames the value set.

**TE-02.** `system-version` applies where the value set names no version; `force-system-version` overrides the value set's version (unsafe, per the spec); `check-system-version` returns an error instead of an expansion on a mismatch. All take `[system]|[version]`.

**TE-03.** No: the expansion uses `http://snomed.info/sct`; the OID form does not match. Fix the data or map it.

**TE-04.** Commit each ValueSet with its `expansion` (and expansion parameters). With flat tests, clinical-reasoning's IgRepository reads the whole project flat, so the ValueSets must be flat in `input/vocabulary/`; `input/vocabulary/valueset/` is read only when tests are grouped by type too. A ValueSet without an expansion is not expanded locally. *Fail if* it keeps `vocabulary/valueset/` with flat tests.

**TE-05.** Nothing in the CQL: in its default terminology mode the engine turns the retrieve into a `code:in=` search, which a local IG folder does not support. Set the retrieve terminology mode to in-memory or inline codes, or filter with `in` in a `where`.
