# -*- coding: utf-8 -*-
"""Single source of truth for MIPF October 2026 (syllabus .docx + website)."""

TITLE = "Mastering Infrastructure and Project Finance Boot Camp"
SHORT = "MIPF"
VENUE = "Lagos Business School, Pan-Atlantic University"
PLACE = "Ajah, Lagos"
DATES_LONG = "14th – 21st October 2026"

ADI = "Prof Bongo Adi"
MC = "Michelle Chikezie, LLB, LLM"
PG = "Promise Godbold"

# ---------------------------------------------------------------- readings
# kind: hosted  = file copied into website/materials (author's own work)
#       pack    = third-party / licensed: in the course folder & printed pack, NOT hosted on the site
#       web     = public link
R = {
 # hosted
 "primer":   dict(kind="hosted", t="Pre-read Primer: Infrastructure Finance Essentials", s="Prof Bongo Adi, LBS (adapted from the CIBN workshop)", f="MIPF_Day1_PreRead_Primer.docx"),
 "workbook": dict(kind="hosted", t="Day 1 Participant Workbook: Project Sahel Sun and the Credit Committee Case Pack", s="Prof Bongo Adi, LBS (adapted from the CIBN workshop)", f="MIPF_Day1_Participant_Workbook.docx"),
 "deck1":    dict(kind="hosted", t="Day 1 slide deck: Modules 1 & 2", s="Prof Bongo Adi, LBS (adapted from the CIBN workshop)", f="MIPF_Day1_Modules_1-2_Deck.pptx"),
 "sahel":    dict(kind="hosted", t="Sahel Sun Capital Stack Template (Excel)", s="Prof Bongo Adi, LBS", f="Sahel_Sun_Capital_Stack_Template.xlsx"),
 "trainstat":dict(kind="hosted", t="TrainStat Start Model (Excel), corrected and completed", s="MIPF modelling pack; see the change log on the model page", f="TrainStat_StartModel.xlsx"),
 # course folder (pack)
 "arg":      dict(kind="pack", t="Argentina Power: Don't Cry for Me Argentina (HBS 5-219-010) and Teaching Note", s="Harvard Business School case"),
 "chad":     dict(kind="pack", t="Chad-Cameroon Petroleum Development and Pipeline Project (HBS 9-202-010), Cases A & B, Teaching Notes and spreadsheet", s="Harvard Business School case"),
 "bp":       dict(kind="pack", t="BP Amoco (A): Policy Statement on the Use of Project Finance (HBS 9-201-054), with (B) and Teaching Note", s="Harvard Business School case"),
 "ajc":      dict(kind="pack", t="Australia-Japan Cable: Structuring the Project Company", s="Case and note"),
 "riskmap":  dict(kind="pack", t="Risk Mapping in Project Finance", s="Course note"),
 "reneg":    dict(kind="pack", t="Contract Renegotiation, Revision and Financial Restructuring", s="Course note"),
 "lending":  dict(kind="pack", t="Managing the Project Finance Lending Process and Negotiating Credit Enhancements", s="Course note"),
 "overview": dict(kind="pack", t="An Overview of Project Finance and Infrastructure Finance: 2009 Update", s="Pack reading"),
 "emerging": dict(kind="pack", t="An Introduction to Project Finance in Emerging Markets", s="Pack reading"),
 "esty":     dict(kind="pack", t="Overview of Project Finance (Esty, 2014)", s="Pack reading"),
 "yes":      dict(kind="pack", t="E. R. Yescombe, Principles of Project Finance", s="Book; chapters named per session"),
 "bodmer":   dict(kind="pack", t="E. Bodmer, Corporate and Project Finance Modeling", s="Book; chapters named per session"),
 "pignataro":dict(kind="pack", t="P. Pignataro, Financial Modeling and Valuation", s="Book"),
 "gatti":    dict(kind="pack", t="S. Gatti, Project Finance in Theory and Practice (Elsevier)", s="Book (reference copy in the course folder: Project Finance in Theory and Practice)"),
 "syndic":   dict(kind="pack", t="Loan Syndication (note)", s="Course note"),
 "termsheet":dict(kind="pack", t="Sample Term Sheet", s="Course document"),
 "ngppp":    dict(kind="pack", t="Overview of Nigeria's PPP Framework and PPP Status; Status of Nigeria PPP (World Bank)", s="Slides and report"),
 "srcfin":   dict(kind="pack", t="Sources of Finance for PPP Project Finance", s="Slides"),
 "contract": dict(kind="pack", t="LBS Contractual Framework for Project Finance", s="Slides"),
 "teach":    dict(kind="pack", t="Project Finance Teaching Note; Teaching Project Finance", s="Notes"),
 "bogoma":   dict(kind="pack", t="The City of Bogoma: Case Study and Bogoma Model Spreadsheet", s="Case and Excel model"),
 "thumann":  dict(kind="pack", t="Thumann, Energy Project Financing", s="Pack reading"),
 "exercises":dict(kind="pack", t="Exercises.xlsx; Exercise 14: Debt Sculpting; IRR and MIRR workbooks", s="Excel exercises"),
 # web
 "w_pppguide": dict(kind="web", t="PPP Reference Guide, Version 3", s="World Bank Group and partners", u="https://ppp.worldbank.org/public-private-partnership/library/ppp-reference-guide-3-0-full-version"),
 "w_risk":     dict(kind="web", t="Allocating Risks in Public-Private Partnership Contracts (interactive matrices)", s="Global Infrastructure Hub / World Bank PPP", u="https://ppp.worldbank.org/node/8649"),
 "w_ifcps":    dict(kind="web", t="IFC Performance Standards on Environmental and Social Sustainability (2012)", s="IFC", u="https://www.ifc.org/performancestandards"),
 "w_ep":       dict(kind="web", t="The Equator Principles (EP4)", s="Equator Principles Association", u="https://equator-principles.com"),
 "w_infracredit": dict(kind="web", t="InfraCredit: financial guarantee for local-currency infrastructure debt", s="InfraCredit Nigeria", u="https://infracredit.ng/our-products/our-financial-guarantee"),
 "w_icrc":     dict(kind="web", t="The ICRC 2025 PPP Guidelines: catalyst for private investment or another policy experiment? (commentary)", s="Mondaq, Nigeria", u="https://www.mondaq.com/nigeria/government-contracts-procurement-ppp/1694180/thought-leadership-the-icrc-2025-ppp-guidelines-catalyst-for-private-investment-or-another-policy-experiment"),
 "w_dscr":     dict(kind="web", t="What is the Debt Service Coverage Ratio (DSCR) in project finance?", s="Forvis Mazars Financial Modelling", u="https://financialmodelling.forvismazars.com/resources/debt-service-coverage-ratio-dscr/"),
 "w_sculpt":   dict(kind="web", t="Project finance transactions: debt sizing versus debt sculpting", s="Forvis Mazars Financial Modelling", u="https://financialmodelling.mazars.com/project-finance-transactions-and-debt-sizing-versus-debt-sculpting/"),
 "w_fast":     dict(kind="web", t="The FAST Standard (Flexible, Appropriate, Structured, Transparent) for financial modelling", s="FAST Standard Organisation", u="https://www.fast-standard.org"),
}

# ---------------------------------------------------------------- sessions
# Each session: dict(start,end,title,mode,fac,desc,cases,exercise,sheets,read,alt,note)
def S(start, end, title, mode="Lecture and Discussion", fac=ADI, desc="", exercise=None,
      sheets=None, read=None, alt=None, note=None, kind="session"):
    return dict(start=start, end=end, title=title, mode=mode, fac=fac, desc=desc, exercise=exercise,
                sheets=sheets or [], read=read or [], alt=alt or [], note=note, kind=kind)

def B(start, end, title):
    return dict(start=start, end=end, title=title, kind="break")

DAYS = [
# =============================================================== DAY 1
dict(n=1, date="Wednesday 14th October 2026", short="Wed 14 Oct", module=1,
 mtitle="The Infrastructure Challenge and Raison d'être of Project Finance",
 fac=ADI,
 blurb=("Day 1 follows one deal from structuring to credit committee: Project Sahel Sun, a 50 MW solar plant in Kano State. "
        "Nigeria's reference transaction, the Azura-Edo IPP, anchors every concept, and the Lekki concessions, the 2nd Niger Bridge and the "
        "Road Infrastructure Tax Credit Scheme show where structures succeed or stall. The Day 1 material is adapted from the LBS workshop built for the "
        "CIBN Centre for Financial Studies. The Harvard cases used in earlier editions are retained as alternative reading."),
 sessions=[
  S("09.00","10.00","Session 1.1: SPVs, Non-Recourse Lending and Cash-Flow-Based Finance",
    desc="Why banks cannot lend infrastructure from the balance sheet; the SPV and the recourse spectrum; lending against CFADS rather than assets; the contract web; the project life cycle and who is around the table. Azura-Edo IPP against a sponsor-financed corporate plant.",
    exercise="Exercise 1 (Workbook p.2): draw the corporate-finance and project-finance structures side by side and circle the one contract without which lenders would not lend.",
    read=["primer","deck1","workbook"], alt=["arg","overview","emerging"]),
  S("10.00","11.00","Session 1.2: Designing Layered Capital Stacks",
    desc="Senior debt, mezzanine and shareholder loans, equity; the cash-flow waterfall; sizing debt by the lower of the DSCR test and the gearing cap; sculpting; matching currency (US$ DFI loan with a guaranteed naira bond). Nigeria lens: CBN, InfraCorp, InfraCredit.",
    exercise="Exercise 2 (Workbook p.3 and Excel template): build the Sahel Sun capital stack: uses of funds, debt capacity at 1.35x, sources of funds.",
    read=["sahel","primer","w_infracredit"], alt=["chad","esty"]),
  B("11.00","11.30","Coffee Break"),
  S("11.30","12.30","Session 1.3: Appraising Deals with Cash-Flow Models",
    desc="Corporate model versus project-finance model; anatomy of a PF model; the ratios lenders watch (DSCR, LLCR); sensitivities. Lekki-Epe Expressway and Lekki Deep Sea Port: why one concession stalled on tariffs and the other reached completion.",
    exercise="The Bankability Checklist (Workbook p.4).",
    read=["deck1","workbook"], alt=["chad","bp"]),
  S("12.30","02.00","Session 2.1: Risk: Identify, Allocate, Mitigate",
    desc="What risk means to a lender; the risk management cycle; the golden rule of allocation; construction and completion, operating and resource (P50/P90), off-take and payment, currency and regulatory risk; stress-testing Sahel Sun.",
    exercise="Exercise 3 (Workbook p.5): complete the Risk Allocation Matrix for Sahel Sun; model answer in debrief.",
    read=["riskmap","w_risk","primer"], alt=["arg","bp"]),
  B("02.00","02.45","Lunch Break (working lunch: read the Credit Committee Case Pack, Workbook pp.7–9)"),
  S("02.45","03.30","Sessions 2.2 and 2.3: PPPs, Concessions and Blended Finance; ESG in Infrastructure Appraisal",
    desc="PPP and concession models; Nigeria's PPP framework; blended finance and the DFI toolkit; the 2nd Niger Bridge and the EO 007 tax-credit road scheme; ESG as a credit issue: IFC Performance Standards, Equator Principles and the Nigerian Sustainable Banking Principles. (Condensed for the full-day format.)",
    read=["w_pppguide","w_ifcps","w_ep","ngppp"], alt=["chad"],
    note="ESG session condensed from the CIBN 25-minute slot; the ESG checklist for Sahel Sun is in the deck."),
  S("03.30","04.30","Session 2.4: Negotiation and Credit Committee Simulation",
    mode="Case-study-led group session",
    desc="Anatomy of a term sheet; what each side asks for; the credit committee brief; the shock six months after financial close; testing the fixes; what a strong committee answer looks like.",
    exercise="Credit Committee decision form (Workbook p.9). Five questions to take back to your institution.",
    read=["workbook","termsheet"], alt=["bp","ajc"]),
 ]),
# =============================================================== DAY 2
dict(n=2, date="Thursday 15th October 2026", short="Thu 15 Oct", module=2,
 mtitle="Legal Fundamentals of Project and Infrastructure Finance",
 fac=MC,
 blurb=("Legal due diligence, security, negotiation and the allocation of risk in contract: the documents that make a project bankable, "
        "and the covenants that decide what happens when it is not."),
 sessions=[
  S("09.00","10.00","Course Introduction and Legal Due Diligence in Project Finance", fac=MC,
    desc="Orientation to the legal workstream; scope and process of legal due diligence; the project documents lenders' counsel review; conditions precedent.",
    read=["contract","yes","riskmap"], alt=["arg"],
    note="Yescombe: Ch. 7 (Project Documentation: the contractual framework)."),
  S("10.00","11.00","Security Agreements", fac=MC,
    desc="Security packages in limited-recourse lending; security over assets, accounts and contracts; direct agreements and step-in rights; intercreditor arrangements.",
    read=["yes","lending"], alt=["bp"],
    note="Yescombe: Ch. on Security Package and Lenders' Direct Agreements."),
  B("11.00","11.30","Coffee Break"),
  S("11.30","12.45","Negotiation and Risk Allocation", fac=MC,
    desc="How risk is negotiated between sponsor, lenders, contractors and offtakers; contract-by-contract allocation; change in law and force majeure; termination and compensation.",
    read=["riskmap","w_risk","yes"], alt=["arg","chad"]),
  S("12.45","02.00","Representations, Warranties and Covenants", fac=MC,
    desc="Representations and warranties at signing and drawdown; positive, negative and financial covenants; events of default and remedies; renegotiation and restructuring when covenants fail.",
    read=["reneg","yes","termsheet"], alt=["bp"]),
  B("02.00","02.45","Lunch Break"),
  S("02.45","03.30","Case-Study-Led Group Session", mode="Case-study-led group session", fac=MC,
    desc="Groups work a transaction fact pattern: identify the legal risks, the missing protections and the covenant package they would require as lenders' counsel.",
    exercise="Group deliverable: a one-page legal issues list and a proposed covenant package, presented in plenary.",
    read=["ajc","reneg"], alt=["chad","arg"]),
  S("03.30","04.30","Other Project Finance Issues and In-Class Assessment", fac=MC,
    mode="Lecture and In-class assessment",
    desc="Remaining legal topics (regulation, permits, dispute resolution, insurance); recap of the legal module; short in-class assessment.",
    exercise="In-class assessment on Day 2 content.",
    read=["w_pppguide","yes"]),
 ]),
# =============================================================== DAY 3
dict(n=3, date="Friday 16th October 2026", short="Fri 16 Oct", module=3,
 mtitle="Finance Fundamentals of Project and Infrastructure Finance",
 fac=PG,
 blurb=("From project contracts to bankability, capital structure, term loans and syndication; risk allocation viewed through the lender's model; "
        "and a first look at the TrainStat start model that anchors the modelling days."),
 sessions=[
  S("09.00","10.30","Introduction to Project Finance: Project Contracts and Bankability", fac=PG,
    desc="The contract chain (concession/PPA, EPC, O&M, supply, offtake) and what makes each bankable; value for money and bankability tests.",
    read=["contract","esty","yes"], alt=["bp","chad"],
    note="Yescombe: Ch. 2 (What is project finance?) and the chapter on Commercial Risks."),
  S("10.30","11.00","Project Capital Structure", fac=PG,
    desc="Debt-to-equity, sources and layers, cost of each layer, and how structure drives returns and DSCR.",
    read=["srcfin","yes","w_infracredit"], alt=["esty"]),
  B("11.00","11.30","Coffee Break"),
  S("11.30","02.00","Project Finance Term Loans and Syndication in Project Finance", fac=PG,
    desc="Term-loan mechanics: tenor, grace, repayment profiles, margins and fees, covenants; arranging and syndicating a project loan; roles of mandated lead arrangers, agents and DFIs.",
    exercise="Exercise: compare the three senior-debt repayment profiles (7.5, 10 and 15 years) on a simple annuity and a sculpted basis using Exercises.xlsx.",
    sheets=["Debt","InpS"], read=["syndic","lending","termsheet","exercises"], alt=["chad"]),
  B("02.00","02.45","Lunch Break"),
  S("02.45","04.30","Need for Appropriate Risk Allocation; General Risks and Mitigants; Project Finance Risks", fac=PG,
    desc="Why allocation drives financing terms; a catalogue of risks and mitigants across construction, operation, market, finance, political and force majeure; reading risk into the cash-flow model.",
    exercise="Exercise: map TrainStat's risks (demand, fare, O&M cost, interest rate, capex timing) to the model inputs that carry them.",
    sheets=["InpC","InpS"], read=["riskmap","w_risk","yes"], alt=["arg","bp"]),
  S("04.30","05.00","Financial Modelling in Project Finance: Preview of the TrainStat Start Model", mode="Demonstration", fac=PG,
    desc="Tour of the start model: workbook map, colour conventions, the scenario switch and the Track sheet. Set-up check so every laptop is ready for Day 4.",
    sheets=["InpC","InpS","Time","Track"], read=["trainstat","w_fast"]),
 ]),
# =============================================================== DAY 4
dict(n=4, date="Saturday 17th October 2026", short="Sat 17 Oct", module=4,
 mtitle="Financial Modelling for Projects I: The Operating Model",
 fac=PG,
 blurb=("Hands-on in Excel with the TrainStat start model: a 20-year, quarterly model of an international and domestic train service. "
        "Today: orientation, the financial statements, revenue, operating cost and tax. (Sunday 18th October is a rest day.)"),
 sessions=[
  S("09.00","10.00","Introduction to Financial Modelling for Projects; Understanding the Start Model; Review of the Case Study", mode="Lecture and Exercise", fac=PG,
    desc="Modelling standards (inputs, workings, outputs, checks; one formula per row); the start model's structure and timeline; the TrainStat case.",
    exercise="Exercise 4.1: trace the timeline. Set the first date, forecast length and months per period in InpC; follow the Time sheet and confirm the period counters and flags.",
    sheets=["InpC","InpS","Time","Esc","Track"], read=["trainstat","w_fast","bodmer"], alt=["bogoma"]),
  B("10.00","10.30","Coffee Break"),
  S("10.30","02.00","Linking the Financial Statements; Revenue Modelling", mode="Lecture and Exercise", fac=PG,
    desc="How inputs flow through the operating sheets into FinStat (income statement, cash flow cascade, balance sheet) and the model checks. Revenue: demand forecast from trains, arrivals per train, seats and occupancy; average fare; escalation; receivable days and cash received.",
    exercise="Exercise 4.2: rebuild OpRev from the inputs, one row at a time, then change the scenario switch and explain the revenue movement. Exercise 4.3: trace one revenue dollar from OpRev to the cash received line and the receivables balance.",
    sheets=["OpRev","FinStat","InpS","Esc"], read=["trainstat","bodmer","pignataro"], alt=["bogoma"]),
  B("02.00","02.45","Lunch Break"),
  S("02.45","05.00","Operating Cost Modelling; Financial Statement Modelling: Tax", mode="Lecture and Exercise", fac=PG,
    desc="Operating cost: fixed and variable handling cost per arrival, fixed O&M, the O&M sensitivity input, escalation, payable days. Tax: tax depreciation on a written-down-value basis, corporation tax, tax paid versus tax expense, deferred tax.",
    exercise="Exercise 4.4: build OpCost and the payables balance. Exercise 4.5: build the Tax sheet and reconcile tax paid to tax expense through the deferred tax balance.",
    sheets=["OpCost","Tax","FinStat"], read=["trainstat","bodmer"]),
 ]),
# =============================================================== DAY 5
dict(n=5, date="Monday 19th October 2026", short="Mon 19 Oct", module=4,
 mtitle="Financial Modelling for Projects II: Balance Sheet, Funding and Valuation",
 fac=PG,
 blurb=("Completing the three-statement start model: non-current assets, working capital, equity and debt; then scenarios, sensitivities, ratios and valuation, "
        "closing with a model review against the guide."),
 sessions=[
  S("09.00","10.00","Modelling Non-Current Assets and Working Capital", mode="Lecture and Exercise", fac=PG,
    desc="Opening non-current asset balance and useful life; capex by date and its depreciation; the NCA balance roll-forward; receivables and payables as working capital.",
    exercise="Exercise 5.1: build the NCA sheet: initial balance depreciation, capex depreciation, closing balance. Exercise 5.2: reconcile working capital to the cash flow cascade.",
    sheets=["NCA","OpRev","OpCost","FinStat"], read=["trainstat","bodmer"]),
  B("10.00","10.30","Coffee Break"),
  S("10.30","02.00","Modelling Equity and Debt; Scenario Analysis", mode="Lecture and Exercise", fac=PG,
    desc="Equity: share capital, redemption, dividends, retained cash and earnings. Debt: senior debt as a share of non-current assets, repayment profile selection (7.5, 10, 15 years), interest on a day-count basis. Scenarios: the scenario switch and name, storing and comparing runs on Track.",
    exercise="Exercise 5.3: build Equity and Debt; get the balance sheet check to zero. Exercise 5.4: run all scenarios and log the results on Track.",
    sheets=["Equity","Debt","InpC","InpS","Track","FinStat"], read=["trainstat","bodmer","w_dscr"]),
  B("02.00","02.45","Lunch Break"),
  S("02.45","05.00","Sensitivity and Ratio Analysis; Valuation; Model Guide and Review", mode="Lecture and Exercise", fac=PG,
    desc="Sensitivities on fare, occupancy, O&M and interest rate; credit and return ratios; shareholder cash flow, NPV and IRR against the required return; payback. Closing review of the model against a model guide.",
    exercise="Exercise 5.5: one-at-a-time sensitivity table on equity IRR. Exercise 5.6: peer review: swap models and run the check list.",
    sheets=["Val","FinStat","Track","InpC"], read=["trainstat","pignataro","w_fast","exercises"]),
 ]),
# =============================================================== DAY 6
dict(n=6, date="Tuesday 20th October 2026", short="Tue 20 Oct", module=4,
 mtitle="Project and Infrastructure Finance Modelling I: Construction and Funding",
 fac=PG,
 blurb=("We convert the operating start model into a project-finance model by adding a construction period, a funding plan and the cost of "
        "financing during construction."),
 sessions=[
  S("09.00","10.00","Introduction to Project Finance Modelling; Understanding the Start Model; Construction Period", mode="Lecture and Exercise", fac=PG,
    desc="What changes between a corporate-style model and a PF model: a construction phase before operations, funding-driven balance sheet, lender-driven ratios. Extending the Time sheet with a construction timeline and the construction/operations flags.",
    exercise="Exercise 6.1: extend the timeline: construction flag, operations start date, post-operations flag.",
    sheets=["Time","InpC"], read=["trainstat","yes","bodmer"], alt=["ajc"]),
  B("10.00","10.30","Coffee Break"),
  S("10.30","02.00","Sources and Uses of Funds; Sources of Finance; Finance Cost and Fees During Construction", mode="Lecture and Exercise", fac=PG,
    desc="Uses: construction cost, fees, IDC, reserve funding. Sources: senior debt, shareholder loan and equity with gearing targets. Upfront, commitment and agency fees; how fees are capitalised.",
    exercise="Exercise 6.2: build the Sources and Uses table and make it balance. Exercise 6.3: build the fee calculations and carry them into uses.",
    sheets=["InpC","NCA","Debt","Equity"], read=["srcfin","yes","trainstat"]),
  B("02.00","02.45","Lunch Break"),
  S("02.45","05.00","Opening Balances, Timelines and Interest During Construction", mode="Lecture and Exercise", fac=PG,
    desc="Opening balance sheet at financial close; construction-period timing; interest during construction and the circularity it creates; keeping the model balanced.",
    exercise="Exercise 6.4: compute IDC; resolve the circularity (iterative calculation versus algebraic solution) and re-run the checks.",
    sheets=["Debt","FinStat","Time"], read=["trainstat","bodmer","yes"]),
 ]),
# =============================================================== DAY 7
dict(n=7, date="Wednesday 21st October 2026", short="Wed 21 Oct", module=4,
 mtitle="Project and Infrastructure Finance Modelling II: Debt Sizing and Returns",
 fac=PG,
 blurb=("Drawdown, cover ratios, sculpting and sizing, reserve accounts and shareholder returns: the numbers a credit committee decides on."),
 sessions=[
  S("09.00","10.00","Construction Debt Drawdown Structure; DSCR, LLCR and PLCR", mode="Lecture and Exercise", fac=PG,
    desc="Drawing debt in line with spend and the gearing rule; defining CFADS; DSCR, LLCR and PLCR and how lenders use minimum and average tests.",
    exercise="Exercise 7.1: build the drawdown schedule. Exercise 7.2: compute CFADS, DSCR, LLCR and PLCR for the base case.",
    sheets=["Debt","FinStat","InpC"], read=["w_dscr","yes","exercises"]),
  B("10.00","10.30","Coffee Break"),
  S("10.30","02.00","Debt Sculpting and Debt Sizing; Blended Equity Rate of Return", mode="Lecture and Exercise", fac=PG,
    desc="Replacing the fixed repayment profiles with a sculpted profile: principal = CFADS ÷ target DSCR − interest; sizing debt as the present value of sculpted debt service, capped by gearing; blended equity return across shareholder loan and equity.",
    exercise="Exercise 7.3: sculpt and size the debt at a 1.35x DSCR; compare with the 7.5, 10 and 15-year profiles. Exercise 7.4: compute the blended equity IRR (Exercise 14: Debt Sculpting as the check).",
    sheets=["Debt","Val","InpS"], read=["w_sculpt","w_dscr","exercises","yes"]),
  B("02.00","02.45","Lunch Break"),
  S("02.45","05.00","Debt Service Reserve Account; Shareholder's Loan; Model Optimisation", mode="Lecture and Exercise", fac=PG,
    desc="DSRA: sizing, funding and release; shareholder-loan mechanics and its effect on cover ratios and returns; optimising gearing, tenor and DSCR against the equity IRR; final integrity checks.",
    exercise="Exercise 7.5: build the DSRA and shareholder loan. Exercise 7.6: optimise the structure to the highest equity IRR that keeps minimum DSCR at 1.30x and passes all checks.",
    sheets=["Debt","Equity","Val","Track"], read=["w_fast","trainstat","yes"]),
 ]),
]

# ---------------------------------------------------------------- narrative
INTRO = [
 "Greetings, and welcome to Lagos Business School’s Boot Camp on Mastering Infrastructure and Project Finance! We are delighted that you are joining us for what will be an engaging and rewarding training experience.",
 "This document provides an overview of the boot camp, key objectives, module contents and information on the faculty team that will be leading you for the next 7 days to ensure that your participation in the boot camp is a fruitful and rewarding one.",
]
OBJECTIVE = ("The objective of this course is to equip participants with the skills required to fully understand the practical techniques, skills, and processes required in planning, analysing, structuring, negotiating, and ultimately completing successful project-backed financings. By presenting effective financial model design techniques, analysing case studies of project financing models, and participating in developing a model from scratch, participants in this program will learn how to design and structure project financing models, how to review and critique project financing models, as well as how to strengthen the structure and how to negotiate infrastructure project financings.")
OVERVIEW = [
 "Project Finance is a highly technical and complex field that has evolved with PPPs, especially as a limited-recourse facility.  Project companies provide a particularly powerful laboratory in which to study the determinants and implications of various structural attributes because they are, as newly created companies, less influenced by the vagaries of history (Esty, 2002).  Moreover, the size of the investments (75% of projects cost more than $100 million) and the time it takes to structure them (one to five years) ensures that managers have the opportunity and the economic incentive to make careful, value-enhancing structural decisions.  As a rapidly developing field of practice in connection with the rolling out of PPPs in Nigeria, a grave need has been established to update the skills of investment professionals and financial analysts involved in infrastructure projects across the country.",
 "Delivered by internationally certified and recognised experts in LBS and the PPP domain of practice, this boot camp is designed to assist participants in fully understanding the practical techniques, skills, and spreadsheet models needed to analyse, structure, negotiate, and ultimately complete successful project-backed financings. By presenting effective financial model design techniques and analysing case studies of project financing models, participants in this program will learn how to design and structure project financing models, review and critique project financing models, as well as how to negotiate and structure infrastructure project financing.",
 "This boot camp is delivered in 4 modules over seven teaching days (14th–21st October 2026, with Sunday 18th October as a rest day). Below is an overview of the areas covered in the 4 modules.",
]
MODULES_INTRO = [
 "This Project Finance Bootcamp is designed to provide participants with a comprehensive understanding of project finance modelling in an infrastructure project context.  It encompasses the key principles, practices, and strategies in procurement, contracting, deal structuring, financing, debt sculpting, legal framework, risk management, and demonstration of skills learned in modelling practice.  Most of these are driven by real-life case studies and a single running Excel model.",
 "All of these aspects are covered under four essential components of infrastructure project finance: The infrastructure challenge and the raison d’être of Project Finance, legal fundamentals of Project Finance, Finance Fundamentals of Project Finance, and Project Finance Modelling.",
]
MODULES = [
 ("The Infrastructure Challenge and Raison d’être of Project Finance (Day 1)",
  "Project finance, as a limited recourse lending, was first used to fund maritime voyages in ancient Greece and Rome.  In modern times, it was employed in the development of the Panama Canal and was widely used in the US oil and gas industry in the early 20th century. However, the structured approach to project finance, as it is known today, is particularly devoted to high-risk infrastructure projects.  This first-day module sets the stage for the program by introducing participants to the relevant context of project finance and illustrating its structure, risks and negotiation using one running case (a 50 MW solar plant) and Nigerian transactions such as the Azura-Edo IPP and the Lekki concessions."),
 ("Legal Fundamentals of Project Finance (Day 2)",
  "In the Legal Fundamentals Module, participants will gain an understanding of the legal aspects of project finance, including contract negotiation, regulatory compliance, and dispute resolution. They will also learn about the role of the various legal and regulatory bodies in project finance and how to navigate the legal complexities involved."),
 ("Finance Fundamentals of Project Finance (Day 3)",
  "In the finance fundamentals component, participants will gain an understanding of the financial and economic aspects of project finance, including project finance structuring, risk appraisal, allocation and management. They will also learn how to analyse project economics and evaluate project feasibility."),
 ("Project Finance Modelling (Days 4–7)",
  "Participants will learn how to develop financial models for projects and analyse project risk, including the assessment of cash flows, discount rates, and sensitivities using Excel.  Working from the TrainStat start model, they will first complete a three-statement operating model (Days 4–5) and then extend it into a full project finance model with construction, funding, cover ratios, debt sculpting and sizing, reserve accounts and shareholder returns (Days 6–7)."),
]
CASES_LINE = "Each of the modules leverages exciting and, at the same time, technically rigorous case studies to drive learning."
CAPSTONE = ("Following the boot camp, participants are expected to develop their first project finance model case by extending the TrainStat model they have built, applying their own assumptions and structure. This capstone project will integrate all the various dimensions of the learning covered in the boot camp to demonstrate mastery of the subject.  The submission of the capstone project is expected to be within 2 weeks after the boot camp.  The reason for this is also to inculcate the important role of mentoring, which is one of the major objectives of the boot camp.  Participants become team members of our evolving project finance expert forum in Nigeria and Africa.")
CLOSING = "Overall, participants can expect to leave the Infrastructure Project Finance Bootcamp with a comprehensive understanding of project finance, including the skills, knowledge, and practical experience to navigate and succeed in this exciting field."
PROFILE = ("This boot camp is designed specifically for financial analysts, investment bankers, consultants, and transaction advisers, as well as chairpersons, directors, commissioners and managers of parastatals currently involved or intending to engage in PPPs through project financing; chairpersons, directors and managers of private companies who are intending or are presently engaged in PPPs. It is an open-enrolment programme.")

FACULTY = [
 dict(name="Prof. Bongo Adi", role="Academic Director", short="Prof Bongo Adi", bio=[
  "Prof Bongo Adi holds a full-time faculty position in the Economics and Business Intelligence department of Lagos Business School, Pan-Atlantic University, Nigeria. He is a development economist, data Scientist, PPP & Project Finance expert and management consultant working in the infrastructure, economic development and Policy field for the last 20 years – with expertise in managing teams, teaching & learning facilitation, PPPs, Project Finance, poverty research, econometric modelling, monitoring and evaluation of programs including the development of M&E plans, methodologies and indicators in multi-country large scale development projects; survey design and execution; randomised control trials; use of propensity score matching and other evaluation tools; technical report writing and promoting research uptake. His expertise has seen him lead and manage exciting and complex projects on multi-state randomised control experiments in health, evaluation of CCT in education, Infrastructure reforms and PPPs, project finance, market sounding for PPP studies, Willingness-To-Pay studies, Multi-sectoral Computable General Equilibrium modelling, macroeconomics modelling and forecasting, econometrics modelling and analysis, economic development strategies, including SME development and Finance. He has sound expertise in managing large grants within development aid contexts.",
  "Prof Adi holds a PhD in Regional Science and Development Economics and an M.Sc in Economic Development and Policy Management under the Joint Japan/World Bank Graduate Scholarship of the University of Tsukuba, Japan. He did postdoctoral training in Data Mining at the National Agricultural Research Centre in Japan. He is a recipient of the Japan Society for the Promotion of Science (JSPS) fellowship. His research has been presented at numerous international conferences and workshops and published in top-ranked international journals.",
  "Prof. Bongo Adi has consulted for the World Bank on project design, preparation and appraisal. His current research interests include electricity market design, private-public partnerships, and the political economy of mega projects.  He is a regular Economist and Business analyst on Channels TV, CNBC Africa and CNN.  He maintains a column tagged bongonomics in the Businessday newspaper."]),
 dict(name="Michelle Chikezie, LLB, LLM", role="Legal Fundamentals (Partner, G. Elias)", short="Michelle Chikezie", bio=[
  "Michelle Chikezie is a Partner at G. Elias, one of Nigeria’s leading business law firms, where she advises on complex transactions spanning capital markets, structured finance, project finance, venture capital, and private equity. She regularly represents multinational banks, pan-African financial institutions, telecommunications companies, and other leading corporates on cross-border transactions, Eurobond issuances, corporate restructurings, and other significant matters. She has been recognised as a “Next Generation Partner” by The Legal 500 and a “Rising Star Partner” by IFLR1000. Michelle is dual-qualified to practise law in Nigeria and New York State.",
  "She has contributed to major industry forums like the African Private Capital Association (AVCA) Conference and the Africa Prosperity Summit, where she has shared insights on local fund domiciliation, regulatory frameworks, private capital, and market liquidity. Michelle graduated with First Class Honours from the Nigerian Law School, ranking among the top 0.2% nationally. She holds an LL.B. from the University of Lagos, an LL.M. from New York University School of Law, and a Master of International Public Policy in International Economics and Finance from Johns Hopkins SAIS."]),
 dict(name="Promise Godbold", role="Finance Fundamentals and Project Finance Modelling", short="Promise Godbold", bio=[
  "Promise is a highly accomplished project finance expert with over 8 years of experience delivering comprehensive project finance modelling solutions and advisory and training services to clients and businesses across Africa and beyond. He has a proven track record in providing project finance transactions worth 100 million dollars, making him a valuable asset to his clients and students alike.",
  "As an Associate Chartered Accountant, Financial Modelling and Valuation Analyst, Promise brings a wealth of expertise and knowledge to the table. He has delivered a series of project finance and financial modelling solutions across various industries, showcasing his versatility and adaptability.",
  "Promise is deeply committed to sustainability, infrastructure, and development finance. He is focused on providing innovative solutions that align with these values and make a positive impact on communities and the environment. His most recent high-net-worth project finance modelling and advisory were delivered for Utilita Energy and Tourba Energy ( a Sierra Leonean Energy Company).",
  "He has a strong focus on projects in the sustainability, infrastructure, and development finance sectors and is deeply passionate about preparing professionals for the future of work."]),
]

# ---------------------------------------------------------------- TrainStat model map (read from the workbook)
MODEL = dict(
 facts=[("Horizon","20 years, modelled quarterly (4 periods a year)"),
        ("Start date","1 July 2021 timeline; acquisition / opening balance (financial close) at 31 Dec 2021; construction quarters are added on Day 6"),
        ("Revenue drivers","Trains, arrivals per train, seats (350 domestic, 150 international), occupancy and an average fare of US$7.15 per passenger"),
        ("Operating cost","Handling: fixed US$4.5m a year plus US$550 per arrival; O&M fixed US$3.3m a year; a +10% O&M sensitivity input"),
        ("Working capital","Receivable days 25; payable days 35"),
        ("Non-current assets","US$100m opening balance (15-year life); capex of US$0.5–2.0m a year 2023–2029 (5-year life)"),
        ("Senior debt","60% of non-current assets in the start model; all-in rate 6.5%; 360-day count; repayment profiles (7.5, 10, 15 years, and a sculpted profile added on Day 7) chosen by a switch"),
        ("Tax","5% tax depreciation on written-down value; 30% corporation tax; interest is tax deductible; deferred tax unwinds to zero by the end"),
        ("Valuation","Shareholder required return 25.25%; NPV and IRR of shareholder cash flow"),
        ("Scenarios","Switch on InpC: Base; Downside (fare −10%, O&M +10%); Upside (fare +10%). The Track sheet stores key outputs of each run for comparison")],
 sheets=[("InpC","Constants and scenario switch","Time, escalation, revenue, cost, asset, debt, tax and valuation constants"),
         ("InpS","Time-series inputs","Trains, arrivals, occupancy and the three debt repayment profiles by period"),
         ("Time","Timeline","Time ruler, flags and period counters"),
         ("Esc","Escalation","CPI inflation rates and indices"),
         ("OpRev","Operating revenue","Demand forecast, revenue, cash received, receivables"),
         ("OpCost","Operating cost","Handling and O&M cost, escalation, payables"),
         ("Tax","Tax","Tax depreciation, tax paid, tax expense, deferred tax"),
         ("NCA","Non-current assets","Capex, accounting depreciation, asset balance"),
         ("Debt","Senior debt","Repayment profile, interest, balance"),
         ("Equity","Equity and distributions","Share capital, dividends, retained cash and earnings"),
         ("FinStat","Financial statements","Income statement, cash flow payment cascade, balance sheet, checks"),
         ("Val","Valuation","Discount factors, shareholder cash flow, NPV, IRR"),
         ("Track","Scenario tracking","Key outputs saved per run for comparison"),
         ("Temp","Scratch","Working area")],
)

SCHEDULE_NOTE = ("Timings follow the 2026 curriculum. Sunday 18th October is a rest day. "
                 "Coffee and lunch breaks are shown in the timetable.")

# ---------------------------------------------------------------- tutorial decks attached to sessions
DECKS = {
 "d1":  dict(t="Day 1 deck: Modules 1 and 2 (adapted from the CIBN workshop)", f="materials/MIPF_Day1_Modules_1-2_Deck.pptx", n=101),
 "d1c": dict(t="Day 1 companion: glossary, numbers primer and case frames", f="materials/decks/MIPF_Day1_Companion_Deck.pptx", n=26),
 "xl":  dict(t="Excel foundations for project finance modelling", f="materials/decks/MIPF_Excel_Foundations_Deck.pptx", n=50),
 "d2":  dict(t="Day 2 deck: legal fundamentals", f="materials/decks/MIPF_Day2_Legal_Fundamentals_Deck.pptx", n=65),
 "d3":  dict(t="Day 3 deck: finance fundamentals", f="materials/decks/MIPF_Day3_Finance_Fundamentals_Deck.pptx", n=48),
 "d4":  dict(t="Day 4 deck: the operating model", f="materials/decks/MIPF_Day4_Operating_Model_Deck.pptx", n=116),
 "d5":  dict(t="Day 5 deck: assets, funding and valuation", f="materials/decks/MIPF_Day5_Funding_Valuation_Deck.pptx", n=109),
 "d6":  dict(t="Day 6 deck: construction and funding", f="materials/decks/MIPF_Day6_PF_Construction_Deck.pptx", n=52),
 "d7":  dict(t="Day 7 deck: debt sizing, sculpting and returns", f="materials/decks/MIPF_Day7_Sizing_Returns_Deck.pptx", n=77),
}
# (day, session number among non-break sessions) -> [(deck, first slide, last slide, what)]
SESSION_DECKS = {
 (1,1): [("d1",8,27,"Session 1.1"), ("d1c",3,10,"glossary and infrastructure basics")],
 (1,2): [("d1",28,46,"Session 1.2"), ("d1c",11,15,"numbers primer")],
 (1,3): [("d1",48,59,"Session 1.3")],
 (1,4): [("d1",61,73,"Session 2.1")],
 (1,5): [("d1",74,90,"Sessions 2.2 and 2.3")],
 (1,6): [("d1",91,99,"Session 2.4"), ("d1c",16,26,"case frames for the alternative readings")],
 (2,1): [("d2",1,18,"introduction, vocabulary and legal due diligence")],
 (2,2): [("d2",19,26,"security agreements")],
 (2,3): [("d2",27,33,"negotiation and risk allocation")],
 (2,4): [("d2",34,42,"representations, warranties and covenants")],
 (2,5): [("d2",43,46,"case-study-led group session")],
 (2,6): [("d2",47,65,"other project finance issues and assessment")],
 (3,1): [("d3",1,10,"contracts and bankability")],
 (3,2): [("d3",11,16,"capital structure")],
 (3,3): [("d3",17,32,"term loans and syndication")],
 (3,4): [("d3",33,42,"risk allocation, risks and mitigants")],
 (3,5): [("d3",43,48,"preview of the TrainStat model"), ("xl",1,50,"Excel foundations (read before Day 4)")],
 (4,1): [("d4",1,19,"modelling, the case and the workbook tour"), ("xl",1,50,"Excel foundations")],
 (4,2): [("d4",20,78,"Time, Esc, linking the statements and revenue")],
 (4,3): [("d4",79,116,"operating cost and tax")],
 (5,1): [("d5",1,25,"non-current assets and working capital")],
 (5,2): [("d5",26,78,"debt, equity, the statements, scenarios and Track")],
 (5,3): [("d5",79,109,"sensitivity, ratios, valuation and review")],
 (6,1): [("d6",1,16,"from the start model to a PF model; the construction timeline")],
 (6,2): [("d6",17,37,"uses and sources of funds; fees and interest")],
 (6,3): [("d6",38,52,"opening balances and interest during construction")],
 (7,1): [("d7",1,16,"drawdown structure; DSCR, LLCR and PLCR")],
 (7,2): [("d7",17,57,"debt capacity, sizing, sculpting and the blended return")],
 (7,3): [("d7",58,77,"DSRA and optimisation (the shareholder-loan build, slides 43 to 57, is revisited)")],
}
DAY_DECKS = {1:["d1","d1c"], 2:["d2"], 3:["d3","xl"], 4:["d4","xl"], 5:["d5"], 6:["d6"], 7:["d7"]}

# ---------------------------------------------------------------- OneDrive links for non-Harvard readings
import urllib.parse as _up, os as _os
ONEDRIVE_BASE = "https://d.docs.live.net/72139f47f6570099/"   # change here if the shared folder link changes
_MI = "Mastering Infrastructure Project Finance 2023/"
_PF = _MI + "Project Finance Materials/"
_DOC = "Documents/Project Finance Materials/"
_OD = {
 "riskmap": [("Risk Mapping in Project Finance (PDF)", _MI + "MIPF Bootcamp 2025/Risk_Mapping_in_Project_Finance.pdf")],
 "reneg": [("Contract Renegotiation, Revision and Financial Restructuring (PDF)", _MI + "MIPF Bootcamp 2025/Contract_Renegotiation__Revision___Financial_Restructuring.pdf")],
 "lending": [("Managing the PF Lending Process and Negotiating Credit Enhancements (PDF)", _MI + "MIPF Bootcamp 2025/Managing_the_Project_Finance_Lending_Process___Negotiating_Credit_Enhancements.pdf")],
 "overview": [("An Overview of Project Finance and Infrastructure Finance, 2009 update (PDF)", _DOC + "An Overview of Project Finance and Infrastructure Finance - 2009 Update.pdf")],
 "emerging": [("An Introduction to Project Finance in Emerging Markets (PDF)", _DOC + "An introduction to project finance in emerging markets.pdf")],
 "esty": [("Overview of Project Finance, Esty 2014 (PDF)", _DOC + "Overview of Project Finance - Esty 2014.pdf")],
 "yes": [("Yescombe, Principles of Project Finance (PDF)", _PF + "E R Yescombe - Principles of Project Finance.pdf")],
 "bodmer": [("Bodmer, Corporate and Project Finance Modeling (PDF)", _PF + "Corporate and Project Finance Modeling Ed Bodimer.pdf")],
 "pignataro": [("Pignataro, Financial Modeling and Valuation (PDF)", _PF + "paul-pignataro-financial-modeling-and-valuation-investment-banking_compressed.pdf")],
 "gatti": [("Gatti, Project Finance in Theory and Practice (PDF)", _PF + "Project Finance in Theory and Practice - Designing, Structuring, and Financing Private and Public Projects ( PDFDrive ).pdf")],
 "syndic": [("Loan syndication (PDF)", _PF + "loan syndication.pdf")],
 "termsheet": [("Sample term sheet (Word)", _PF + "Term Sheet.docx")],
 "ngppp": [("Overview of Nigeria's PPP framework and PPP status (PowerPoint)", _PF + "PPP/Overview of Nigeria’s PPP Framework and PPP Status.pptx"), ("Status of Nigeria PPP, World Bank (PDF)", _PF + "Status of Nigeria PPP - World Bank.pdf")],
 "srcfin": [("Sources of Finance for PPP Project Finance (PowerPoint)", _PF + "PPP/Sources of Finance for PPP Project Finance.pptx")],
 "contract": [("LBS contractual framework for project finance (PowerPoint)", _DOC + "LBS contractual framework for project finance.pptx")],
 "teach": [("Project Finance Teaching Note (PDF)", _DOC + "Project Finance Teaching Note.pdf"), ("Teaching Project Finance (PDF)", _PF + "PF Bootcamp Materials/Teaching Project Finance.pdf")],
 "bogoma": [("Bogoma model spreadsheet (Excel)", _PF + "Bogoma Model Spreadsheet.xlsx"), ("The City of Bogoma case study (Word)", _PF + "The City of Bogoma - Case Study (1).doc")],
 "thumann": [("Thumann, Energy Project Financing (PDF)", _PF + "Thumann_Energy_Project_Financing.pdf")],
 "exercises": [("Exercises (Excel)", _DOC + "Exercises.xlsx"), ("Exercise 14: Debt sculpting (Excel)", _DOC + "Exercise 14 - Debt Sculpting.xls"), ("IRR (Excel)", _DOC + "IRR.xlsx"), ("MIRR (Excel)", _DOC + "MIRR.xlsx")],
}
_ROOT = "/Users/adibongo/Library/CloudStorage/OneDrive-Personal/"
for _k, _lst in _OD.items():
    R[_k]["od"] = [(lab, ONEDRIVE_BASE + _up.quote(p, safe="/")) for lab, p in _lst]
    R[_k]["od_ok"] = all(_os.path.exists(_ROOT + p) for lab, p in _lst)
HARVARD = {"arg", "chad", "bp", "ajc"}
