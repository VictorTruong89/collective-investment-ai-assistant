# Filing fixtures — the documents golden `extraction` cases are established from

A golden `extraction` case's `input_ref` names a file **in this directory**. `F5` `CT-5.2` calls it
*"the fixture"*: the document whose text contains the answer.

★ **Why the document lives in the repo rather than being fetched.** An extraction case's whole claim
is *"the filing says X"*. If the filing is re-fetched at test time the case measures the fetch as
well as the extraction, and it breaks when a vendor reorganises a URL — ⚠ a regression suite that
reds for reasons unrelated to the code teaches people to ignore red, which destroys it permanently
(`F5` `D5`, the same reasoning that keeps live calls out of CI).

## How to add one

1. Get the filing **from EDGAR**, not from a data vendor —
   `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&ticker=<TICKER>&type=10-Q`.
   ⚠⚠ **Not from FMP.** FMP is a *subject* of these tests; a fixture taken from it would let the
   thing under test supply its own input (`F5` `D2`, in the input direction).
2. Save the text as `<TICKER>_<FY><Q>_<FORM>.txt` — e.g. `MU_FY2025Q3_10Q.txt`.
   ★ Plain text, not PDF: a fixture a reviewer cannot `grep` cannot be checked.
3. ✏ **Keep the WHOLE document** *(revised 2026-09-05, on first real use — the earlier advice here
   said "trim to the statements you cite", and that was wrong.)* Three reasons: a trimmed fixture no
   longer **is** the filing; a second case about a different item (guidance, share count, debt
   ladder) would force a re-fetch; and the trimming itself is an editorial choice made by whoever
   prepared it. ★ A converted 10-Q is ~200 KB of text and greps fine.
   ⚠ Convert HTML → text **mechanically**, and say so in the header. Keep table column headers
   intact — they are usually where the trap is: *"Quarter Ended"* beside *"Nine Months Ended"*.
4. **Put a provenance header at the top** — filer, CIK, form, period, filing date, accession, the
   exact source URL, retrieval date, and how it was converted. ★ `source` in the golden case points
   a reader here; this header is what lets them get back to the original.
5. Record the case in `tests_src/fixtures/golden/extraction.yaml`.

## ⚠ What not to do

- ✗ **Do not edit a fixture to make a test pass.** That is the one move that converts this whole
  directory from evidence into decoration.
- ✗ **Do not replace a fixture when a filing is restated.** Add a *second* fixture and a *second*
  case; both stand. Editing the first back-fills history and destroys what was knowable when.
