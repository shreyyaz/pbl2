"""
Generate Legal Book (Synthetic)
===============================
Generates a PDF representing a "Legal Book" on Interpretation of Statutes and Legal Maxims.
This serves as a core reference for the AI to make legal decisions.
"""

from fpdf import FPDF
from pathlib import Path

# Configuration
DOWNLOAD_DIR = Path("data")
DOWNLOAD_DIR.mkdir(exist_ok=True)

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, self.title, 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

def create_pdf(filename, title, text):
    pdf = PDF()
    pdf.title = title
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    
    # Process text to handle encoding
    text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 5, text)
    
    filepath = DOWNLOAD_DIR / filename
    pdf.output(str(filepath))
    print(f"✅ Generated: {filepath}")

# Text Content for the "Book"
LEGAL_BOOK_TEXT = """
PRINCIPLES OF STATUTORY INTERPRETATION & LEGAL MAXIMS
For Commercial Courts

CHAPTER 1: INTERPRETATION OF COMMERCIAL CONTRACTS

1. Contra Proferentem Rule
   - Ambiguity in a contract is resolved against the party who drafted it.
   - In commercial contracts between sophisticated parties, this rule applies with less rigor (Supreme Court of India).

2. Business Efficacy Test
   - Courts imply terms into a contract only if necessary to give 'business efficacy' to the contract.
   - The term must be so obvious that it goes without saying (The Moorcock Case).

3. Textualism vs Contextualism
   - Modern commercial interpretation considers the 'matrix of fact' or surrounding circumstances.
   - However, the plain meaning of words (Literal Rule) is the primary guide.

CHAPTER 2: KEY LEGAL MAXIMS FOR COMMERCIAL DISPUTES

1. Vigilantibus non dormientibus jura subveniunt
   - "The law assists those who are vigilant, not those who sleep over their rights."
   - Application: Limitation Act. Delays in filing commercial suits (Section 2(c), Commercial Courts Act) can be fatal.
   - Delay and Laches: Unexplained delay is a ground to deny equitable relief (e.g., Injunctions).

2. Ubberima Fides
   - "Utmost Good Faith".
   - Application: Insurance contracts and some partnership agreements.
   - Non-disclosure of material facts voids the contract.

3. Pacta Sunt Servanda
   - "Agreements must be kept."
   - The sanctity of contracts is paramount. Courts will enforce agreed terms unless illegal or contrary to public policy.
   - Exceptions: Force Majeure (frustration of contract).

4. Nemo Judex In Causa Sua
   - "No one should be a judge in their own cause."
   - Application: Arbitration. An arbitrator with a conflict of interest is ineligible (Section 12(5), Arbitration Act).

5. Audi Alteram Partem
   - "Listen to the other side."
   - Principles of Natural Justice. No order created without hearing the affected party.

CHAPTER 3: DECISION MAKING FRAMEWORK FOR JUDGES

When adjudicating a commercial dispute, the Court should:
1. Identify the 'Commercial Dispute' under Section 2(1)(c).
2. Check for Pre-Institution Mediation compliance (Section 12A).
   - If no urgent interim relief is sought, mediation is mandatory. Patil Automation v. Rakheja Engineers (2022) SC.
   - Non-compliance leads to rejection of plaint.
3. Determine 'Specified Value' (Section 2(1)(i)).
   - Must be > 3 Lakhs.
4. Case Management Hearing (Order XV-A, CPC).
   - Framing of issues at the first hearing.
   - Setting strict timelines for trial.

"""

def main():
    print("Generating synthetic Legal Book...")
    create_pdf("Book_Legal_Maxims_Interpretation.pdf", "Principles of Statutory Interpretation", LEGAL_BOOK_TEXT)

if __name__ == "__main__":
    main()
