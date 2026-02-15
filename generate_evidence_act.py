"""
Generate Evidence Act Summary
=============================
Generates a PDF summary of the Indian Evidence Act, 1872.
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

# Text Content
EVIDENCE_ACT_TEXT = """
THE INDIAN EVIDENCE ACT, 1872
(Summary for Commercial Disputes)

PART I: RELEVANCY OF FACTS

Section 5. Evidence may be given of facts in issue and relevant facts.
- Evidence may be given in any suit or proceeding of the existence or non-existence of every fact in issue and of such other facts as are hereinafter declared to be relevant, and of no others.

Section 6. Relevancy of facts forming part of same transaction (Res Gestae).
- Facts which, though not in issue, are so connected with a fact in issue as to form part of the same transaction, are relevant, whether they occurred at the same time and place or at different times and places.

Section 34. Entries in books of account when relevant.
- Entries in books of account, including those maintained in an electronic form, regularly kept in the course of business, are relevant whenever they refer to a matter into which the Court has to inquire, but such statements shall not alone be sufficient evidence to charge any person with liability.
- *Crucial for Commercial Suits*: Ledgers and invoices must be corroborated.

Section 65A & 65B. Electronic Evidence.
- Special provisions as to evidence relating to electronic record.
- Any information contained in an electronic record which is printed on a paper, stored, recorded or copied in optical or magnetic media produced by a computer is deemed to be also a document.
- Section 65B Certificate is mandatory for admissibility of electronic records (Supreme Court in Arjun Panditrao Khotkar v. Kailash Kushanrao Gorantyal).

PART II: ON PROOF

Section 91. Evidence of terms of contracts, grants and other dispositions of property reduced to form of document.
- When the terms of a contract have been reduced to the form of a document, no evidence shall be given in proof of the terms of such contract, except the document itself.

Section 92. Exclusion of evidence of oral agreement.
- When the terms of any such contract have been proved, no evidence of any oral agreement or statement shall be admitted, as between the parties, for the purpose of contradicting, varying, adding to, or subtracting from its terms.
- *Exceptions*: Fraud, intimidation, illegality, want of due execution, distinct subsequent oral agreement.

PART III: BURDEN OF PROOF

Section 101. Burden of proof.
- Whoever desires any Court to give judgment as to any legal right or liability dependent on the existence of facts which he asserts, must prove that those facts exist.

Section 114. Court may presume existence of certain facts.
- The Court may presume the existence of any fact which it thinks likely to have happened, regard being had to the common course of natural events, human conduct and public and private business, in their relation to the facts of the particular case.
- Illustration (g): That evidence which could be and is not produced would, if produced, be unfavourable to the person who withholds it.

"""

def main():
    print("Generating Evidence Act Summary...")
    create_pdf("Book_Indian_Evidence_Act.pdf", "The Indian Evidence Act, 1872", EVIDENCE_ACT_TEXT)

if __name__ == "__main__":
    main()
