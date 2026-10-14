# MIPF Model Prompt Book

Everything that builds the TrainStat financial model for the **Mastering Infrastructure and Project Finance Boot Camp**, Lagos Business School, 14 to 21 October 2026.

| File | What it is |
|---|---|
| `MIPF_Model_Prompt_Book.qmd` | The prompt book (Quarto source). 24 build blocks, each with specification, five prompts (tutor, formula generator, script builder, replica, auditor), checkpoints, options and failure modes; options atlas; diagnostics; verification protocol; defect catalogue; appendices. |
| `MIPF_Model_Prompt_Book.html` | The rendered, self-contained book. |
| `mipf_model_builder.html` | The interactive app (open in any browser, works offline). Runs the whole 84-quarter model, shows statements, ratios, checks and charts, compares scenarios, explores options and generates prompts tailored to your inputs. |
| `src/engine.js` | The model engine (start model and project-finance model). A line-by-line port of the Python replicas that were verified against Microsoft Excel. |
| `src/blocks.py`, `src/templates.py` | The hand-authored content: block definitions and the prompt templates. |
| `src/gen_promptbook.py`, `src/build_app.py`, `src/gen_numbers.js`, `src/export_inputs.py` | Generators. |
| `data/` | `inputs.json` (all three scenarios), `atlas_start.json` and `atlas_pf.json` (every row of every sheet), `numbers.json` (every figure quoted in the book), `promptbook.json` (content for the app). |
| `test/` | `test_engine.js` (89 workbook reference values for all three scenarios), `test_options.js` (2,160 option combinations, every integrity check must pass), `test_book.py` (consistency of the book and app data). |

## Rebuild

```bash
cd promptbook
python3 src/export_inputs.py data      # needs the verified workbooks (optional; data/ is included)
node src/gen_numbers.js                # recompute every figure quoted in the book
python3 src/gen_promptbook.py .        # writes the QMD and data/promptbook.json
python3 src/build_app.py .             # writes mipf_model_builder.html
quarto render MIPF_Model_Prompt_Book.qmd
bash run_tests.sh
```

## Verification

1. Workbooks: the final build (day-count correction, facility rule, automatic calculation) was recalculated in Microsoft Excel for Mac on 10 October 2026 for Base, Downside and Upside: values equal the engine to 6 decimals, Cover reads ALL CHECKS PASSED, zero error cells; it was also verified by a full formula evaluation of every cell.
2. Python replica: agrees with Excel to 6 decimals.
3. This JavaScript engine: reproduces the same reference values (`node test/test_engine.js`; the same list runs on the app's Verify tab) and satisfies the integrity checks for 2,160 option combinations (`node test/test_options.js`).

## Contacts

Prof Bongo Adi, Lagos Business School. +234 706 164 8699. badi@lbs.edu.ng. bongo.adi@fulbrightmail.org.
