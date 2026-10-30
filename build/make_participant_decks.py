# -*- coding: utf-8 -*-
"""Make the participants' edition of every tutorial deck from the facilitator edition.

Withheld in the participants' edition: speaker notes (they carry the answers and the
facilitator's cues), the "CHECK YOUR ANSWER" callouts of exercises, the "Answer and why"
slides and the answer-key tables. Slide numbers do not change, so the session slide ranges
on the website stay valid.

usage: python3 make_participant_decks.py <facilitator_dir> <participant_dir>
"""
import sys, os, glob, re
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

SRC, DST = sys.argv[1], sys.argv[2]
os.makedirs(DST, exist_ok=True)
GOLD = RGBColor.from_string("A8700F")
INK = RGBColor.from_string("1A2233")

CHECK = ("WHEN YOU ARE DONE:  compare your result with a neighbour. Your facilitator then confirms the answer "
         "and the reasoning in the room.")
CHECK_MODEL = CHECK + " Checkpoints for each model block are in the Model Prompt Book."


def set_text(shape, text):
    """Replace the text of a shape but keep the formatting of its first run."""
    tf = shape.text_frame
    p0 = tf.paragraphs[0]
    runs = p0.runs
    if runs:
        runs[0].text = text
        for r in runs[1:]: r._r.getparent().remove(r._r)
    else:
        p0.text = text
    for p in tf.paragraphs[1:]: p._p.getparent().remove(p._p)


def txt(sh): return sh.text_frame.text if sh.has_text_frame else ""


def add_body(slide, text, y=2.2, h=1.4, size=20):
    tb = slide.shapes.add_textbox(Inches(0.7), Inches(y), Inches(11.9), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    r = tf.paragraphs[0].add_run(); r.text = text
    r.font.size = Pt(size); r.font.name = "Calibri"; r.font.color.rgb = INK
    return tb


stats = {}
for f in sorted(glob.glob(os.path.join(SRC, "*.pptx"))):
    name = os.path.basename(f).replace("_Facilitator", "")
    prs = Presentation(f)
    c = dict(notes=0, checks=0, answers=0, tables=0, blurbs=0)
    for idx, s in enumerate(prs.slides):
        if s.has_notes_slide and s.notes_slide.notes_text_frame.text.strip():
            s.notes_slide.notes_text_frame.text = ""; c["notes"] += 1
        shapes = list(s.shapes)
        texts = [txt(sh) for sh in shapes]
        kicker = next((t for t in texts if t.strip().upper() in ("ANSWERS", "CHECK YOUR UNDERSTANDING")), "")
        # 1. exercise check callouts
        for sh in shapes:
            if sh.has_text_frame and sh.text_frame.text.startswith("CHECK YOUR ANSWER:"):
                set_text(sh, CHECK_MODEL if re.search(r"Day[4-7]_", name) else CHECK); c["checks"] += 1
        # 2. "Answer and why" slides
        if any(t == "Answer and why" for t in texts):
            for sh in shapes:
                t = txt(sh)
                if t == "Answer and why": set_text(sh, "Discuss, then compare")
                elif t.startswith("ANSWER:"): set_text(sh, "Agree your answer with a neighbour. Your facilitator will reveal it and explain why.")
            # the explanation box is the tallest remaining text box below the answer line
            body = [sh for sh in shapes if sh.has_text_frame and sh.top > Inches(3.4) and sh.top < Inches(4.0) and len(txt(sh)) > 40]
            for sh in body: set_text(sh, "Write your answer and one sentence of reasoning. The reasoning matters more than the letter.")
            c["answers"] += 1
        # 3. answer-key tables
        if kicker.strip().upper() == "ANSWERS":
            msg = "Your facilitator will take you through the model answers, the reasoning behind each one and the points most often missed. Compare them with your own work and note the gaps."
            callout = False
            for sh in shapes:
                if sh.shape_type == 19:  # table
                    sh._element.getparent().remove(sh._element); c["tables"] += 1
                elif sh.has_text_frame and txt(sh).startswith(("Model answers", "Assessment answer key")):
                    set_text(sh, "Debrief with your facilitator")
                elif sh.has_text_frame and txt(sh).startswith("Score out of"):
                    set_text(sh, msg); callout = True
                elif sh.has_text_frame and txt(sh).upper() == "ANSWERS":
                    set_text(sh, "DEBRIEF")
            if not callout: add_body(s, msg, y=1.9, h=1.4)
            else:  # the callout sat below the table: bring it up into the freed space
                for sh in shapes:
                    if abs(sh.top - Inches(3.0)) < Inches(0.05) and sh.shape_type != 19: sh.top = Inches(2.0)
        # 4. section blurb
        for sh in shapes:
            if sh.has_text_frame and "answers on the following slides" in txt(sh):
                set_text(sh, txt(sh).replace("answers on the following slides", "answers reviewed together in class")); c["blurbs"] += 1
        # 5. cover badge
        if idx == 0:
            tb = s.shapes.add_textbox(Inches(0.6), Inches(1.95), Inches(9.0), Inches(0.35))
            r = tb.text_frame.paragraphs[0].add_run()
            r.text = "PARTICIPANT EDITION  ·  exercise answers and facilitator notes are withheld"
            r.font.size = Pt(12); r.font.bold = True; r.font.name = "Calibri"; r.font.color.rgb = RGBColor.from_string("D99A2B")
    prs.core_properties.title = (prs.core_properties.title or name.replace(".pptx", "")) + " (participant edition)"
    out = os.path.join(DST, name)
    prs.save(out); stats[name] = c
    print(name, c)
