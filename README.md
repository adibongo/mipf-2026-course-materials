# MIPF October 2026: course materials

Mastering Infrastructure and Project Finance Boot Camp, Lagos Business School, Pan-Atlantic University, 14 to 21 October 2026 (Sunday 18th is a rest day). Open enrolment.

Course director: **Prof Bongo Adi** · +234 706 164 8699 · badi@lbs.edu.ng · bongo.adi@fulbrightmail.org

Everything here is branded with the LBS logo, the MIPF hex and the bongo.ai hex.

This repository is the public home of the participants' course materials. The readings (books, papers, templates) are not stored here; the website's Readings page links to them.

## What is in this folder

| Folder / file | What it is | Audience |
|---|---|---|
| `syllabus/MIPF_October_2026_Course_Syllabus.docx` | Course syllabus in the 2024/2025 format, merged with the 2026 curriculum | Participants |
| `website/` | Static participant website (open `index.html`): timetable, day pages, readings, model guide, faculty, practical information | Participants |
| `decks/` | Eight **participants' edition** tutorial decks (543 slides): Excel foundations, Day 1 companion, Days 2 to 7. Exercises are intact; answer callouts, answer slides, answer keys and speaker notes are withheld and reviewed in class. The 101-slide Day 1 deck (adapted from the CIBN workshop) is in `website/materials/`, also without speaker notes. | Participants |
| `models/` | Excel models: the corrected start model (Days 4 to 5), the complete project finance model (Days 6 to 7), and the original supplied file | Facilitators; start model also on the website |
| `promptbook/` | **Model Prompt Book** (QMD and rendered HTML): everything that builds the model, with prompts for five build paths, checkpoints, options and failure modes; and the **MIPF Model Builder** (interactive HTML app). See `promptbook/README.md` | Everyone |
| `build/` | Python scripts that generate the syllabus, website and decks from one content file (`mipf_data.py`) and the models | Maintainers |

## Day 1 (CIBN-derived) materials

The Day 1 deck, participant workbook, pre-read primer and the Sahel Sun capital-stack template were adapted from the CIBN workshop and are rebranded for MIPF: CIBN references replaced, LBS logo, MIPF hex and bongo.ai hex added, contact block in every file, speaker notes removed from the deck. The template's formulas are unchanged; results were checked in Microsoft Excel (debt 37.40, minimum DSCR 1.35x, LLCR 1.35x, sponsor IRR 10.25%). The adaptation scripts are `src/rebrand_sahel_template.py` and `src/rebrand_day1_docs.py`.

## Models

* `TrainStat_StartModel.xlsx`: the supplied start model, **corrected and completed**. Corrections: about 1.2 million ghost cells out to column XFD removed (file 6.0 MB to 0.4 MB), tax now deducts interest (deferred tax and retained earnings end at zero), check totals extended from column BY to the full timeline CO, empty Track sheet built with stored Base/Downside/Upside runs, broken names and external links repaired, scenarios made coherent, unused O&M sensitivity linked, placeholder rows wired to inputs, DSCR block, Cover and Dashboard added. Full list on the Cover sheet.
* `TrainStat_PF_Model_Complete.xlsx`: adds the Day 6 and 7 extension: Constr (construction, uses and sources, interest during construction), Sculpt (debt capacity, sizing, sculpted repayments), DSRA, SHL (shareholder loan) and Ratios (DSCR, LLCR, PLCR).
* `original/TrainStat_StartModel_original.xlsx`: the file as supplied, kept for reference.

## Verification

Both models were recalculated in **Microsoft Excel for Mac on 10 October 2026** for all three scenarios (Base, Downside, Upside): every check is zero, Cover reads ALL CHECKS PASSED, no cell returns an error. They also agree to about 9 significant figures with a full formula evaluation and with an independent Python/JavaScript replica.

Base case (start model): shareholder NPV 17,609 and XIRR 33.72%. Base case (project finance model): debt sized 72,154 at a 2.25x target DSCR (71.4% gearing), minimum DSCR 2.30x, blended sponsor IRR 43.03% measured from COD (34.71% when each construction-period contribution is dated when it is paid; see the retained conventions in the Prompt Book).

Corrections made in the delivered workbooks (full list on each Cover sheet): ghost cells removed, tax deducts interest, check ranges extended, Track built, names repaired, scenarios coherent, O&M sensitivity wired, placeholders wired, DSCR block, **day count corrected (Time row 30 +1)**, **facility = ROUNDUP(MIN(capacity, gearing cap x cost))**, Dashboard DSCR guard, Cover status covers the construction checks, Track uses the named tolerance, and the workbooks are saved in **Automatic** calculation mode (the original was Manual).

Retained and documented: all sponsor funding is dated at COD in Val; tax losses are refunded in cash; no lock-up and no DSRA draw.

## Rebuilding

```
python3 build/build_docx.py <out-folder>     # syllabus
python3 build/build_site.py <out-folder>     # website
python3 build/models/build_stage1.py <out.xlsx>   # corrected start model (formulas)
python3 build/models/build_final.py start|pf <out.xlsx>   # add Cover, Dashboard, PF extension
```

The scripts expect the logo folder and model data paths used on the authoring machine; edit the paths at the top of each script.

## Notes

* Harvard (HBS) cases, Yescombe, Bodmer and other third-party readings are **not** stored here; the website lists them as course-pack items.
* Statute references in the Day 2 deck summarise public commentary and must be confirmed against current text with Nigerian counsel.
* The participants' decks are published as files. The scripts that generate them are held by the course director because they embed the exercise answers.
