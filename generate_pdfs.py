"""
Generate Legal PDFs
===================
Since direct government PDF links are unstable, this script generates clean PDFs
containing the text of key commercial court legislations.
"""

from fpdf import FPDF
from pathlib import Path

# Configuration
DOWNLOAD_DIR = Path("data") # Directly to data folder for processing
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

# Text Content (Detailed summaries/text)
COMMERCIAL_COURTS_ACT_TEXT = """
THE COMMERCIAL COURTS ACT, 2015
(Act No. 4 of 2016)

An Act to provide for the constitution of Commercial Courts, Commercial Appellate Courts, Commercial Division and Commercial Appellate Division in the High Courts for adjudicating commercial disputes of specified value and matters connected therewith or incidental thereto.

CHAPTER I: PRELIMINARY

Section 2. Definitions:
(1) In this Act, unless the context otherwise requires,—
(c) "commercial dispute" means a dispute arising out of—
(i) ordinary transactions of merchants, bankers, financiers and traders such as those relating to mercantile documents, including enforcement and interpretation of such documents;
(ii) export or import of merchandise or services;
(iii) issues relating to admiralty and maritime law;
(iv) transactions relating to aircraft, aircraft engines, aircraft equipment and helicopters, including sales, leasing and financing of the same;
(v) carriage of goods;
(vi) construction and infrastructure contracts, including tenders;
(vii) agreements relating to immovable property used exclusively in trade or commerce;
(viii) franchising agreements;
(ix) distribution and licensing agreements;
(x) management and consultancy agreements;
(xi) joint venture agreements;
(xii) shareholders agreements;
(xiii) subscription and investment agreements pertaining to the service industry including outsourcing services and financial services;
(xiv) mercantile agency and mercantile usage;
(xv) partnership agreements;
(xvi) technology development agreements;
(xvii) intellectual property rights relating to registered and unregistered trademarks, copyright, patent, design, domain names, geographical indications and semiconductor integrated circuits;
(xviii) agreements for sale of goods or provision of services;
(xix) exploitation of oil and gas reserves or other natural resources including electromagnetic spectrum;
(xx) insurance and reinsurance;
(xxi) contracts of agency relating to any of the above; and
(xxii) such other commercial disputes as may be notified by the Central Government.

(i) "Specified Value", in relation to a commercial dispute, shall mean the value of the subject-matter in respect of a suit as determined in accordance with section 12 which shall not be less than three lakh rupees or such higher value, as may be notified by the Central Government.

CHAPTER II: COMMERCIAL COURTS, COMMERCIAL APPELLATE COURTS, COMMERCIAL DIVISIONS AND COMMERCIAL APPELLATE DIVISIONS

Section 3. Constitution of Commercial Courts:
(1) The State Government, may after consultation with the concerned High Court, by notification, constitute such number of Commercial Courts at District level, as it may deem necessary for the purpose of exercising the jurisdiction and powers conferred on those Courts under this Act:
Provided that with respect to the High Courts having ordinary original civil jurisdiction, the State Government may, after consultation with the concerned High Court, by notification, constitute Commercial Courts at the District Judge level:
Provided further that with respect to a territory over which the High Courts have ordinary original civil jurisdiction, the State Government may, by notification, specify such pecuniary value which shall not be less than three lakh rupees and not more than the pecuniary jurisdiction exercisable by the District Courts, as it may consider necessary.

CHAPTER III: SPECIFIED VALUE

Section 12. Determination of Specified Value:
(1) The Specified Value of the subject-matter of the commercial dispute in a suit, appeal or application shall be determined in the following manner:––
(a) where the relief sought in a suit or application is for recovery of money, the money sought to be recovered in the suit or application inclusive of interest, if any, computed up to the date of filing of the suit or application, as the case may be, shall be taken into account for determining such Specified Value;
(b) where the relief sought in a suit, appeal or application relates to movable property or to a right therein, the market value of the movable property as on the date of filing of the suit, appeal or application, as the case may be, shall be taken into account for determining such Specified Value.

CHAPTER IIIA: PRE-INSTITUTION MEDIATION AND SETTLEMENT

Section 12A. Pre-Institution Mediation and Settlement:
(1) A suit, which does not contemplate any urgent interim relief under this Act, shall not be instituted unless the plaintiff exhausts the remedy of pre-institution mediation in accordance with such manner and procedure as may be prescribed by rules made by the Central Government.
(2) The Central Government may, by notification, authorise the Authorities constituted under the Legal Services Authorities Act, 1987, for the purposes of pre-institution mediation.
(3) Notwithstanding anything contained in the Legal Services Authorities Act, 1987, the Authority authorised by the Central Government under sub-section (2) shall complete the process of mediation within a period of three months from the date of application made by the plaintiff under sub-section (1):
Provided that the period of mediation may be extended for a further period of two months with the consent of the parties.
(4) The period during which the parties remained occupied with the pre-institution mediation, such period shall not be computed for the purpose of limitation under the Limitation Act, 1963.
(5) If the parties to the commercial dispute arrive at a settlement, the same shall be reduced into writing and shall be signed by the parties to the dispute and the mediator.
"""


ARBITRATION_ACT_TEXT = """
THE ARBITRATION AND CONCILIATION ACT, 1996
(As Amended in 2015, 2019 and 2021)

An Act to consolidate and amend the law relating to domestic arbitration, international commercial arbitration and enforcement of foreign arbitral awards as also to define the law relating to conciliation and for matters connected therewith or incidental thereto.

PART I: ARBITRATION

Section 2. Definitions:
(1) In this Part, unless the context otherwise requires,—
(a) "arbitration" means any arbitration whether or not administered by permanent arbitral institution;
(b) "arbitration agreement" means an agreement referred to in section 7;
(c) "arbitral award" includes an interim award;
(e) "Court" means— 
(i) in the case of an arbitration other than international commercial arbitration, the principal Civil Court of original jurisdiction in a district, and includes the High Court in exercise of its ordinary original civil jurisdiction, having jurisdiction to decide the questions forming the subject-matter of the arbitration if the same had been the subject-matter of a suit, but does not include any Civil Court of a grade inferior to such principal Civil Court, or any Court of Small Causes;
(ii) in the case of international commercial arbitration, the High Court in exercise of its ordinary original civil jurisdiction, having jurisdiction to decide the questions forming the subject-matter of the arbitration if the same had been the subject-matter of a suit, and in other cases, a High Court having jurisdiction to hear appeals from decrees of courts subordinate to that High Court.

Section 7. Arbitration agreement:
(1) In this Part, "arbitration agreement" means an agreement by the parties to submit to arbitration all or certain disputes which have arisen or which may arise between them in respect of a defined legal relationship, whether contractual or not.
(2) An arbitration agreement may be in the form of an arbitration clause in a contract or in the form of a separate agreement.
(3) An arbitration agreement shall be in writing.
(4) An arbitration agreement is in writing if it is contained in—
(a) a document signed by the parties;
(b) an exchange of letters, telex, telegrams or other means of telecommunication including communication through electronic means which provide a record of the agreement; or
(c) an exchange of statements of claim and defence in which the existence of the agreement is alleged by one party and not denied by the other.

Section 11. Appointment of arbitrators:
(1) A person of any nationality may be an arbitrator, unless otherwise agreed by the parties.
(2) Subject to sub-section (6), the parties are free to agree on a procedure for appointing the arbitrator or arbitrators.
(6) Where, under an appointment procedure agreed upon by the parties,—
(a) a party fails to act as required under that procedure; or
(b) the parties, or the two appointed arbitrators, fail to reach an agreement expected of them under that procedure; or
(c) a person, including an institution, fails to perform any function entrusted to him or it under that procedure,
a party may request the Supreme Court or, as the case may be, the High Court or any person or institution designated by such Court to take the necessary measure, unless the agreement on the appointment procedure provides other means for securing the appointment.

Section 29A. Time limit for arbitral award:
(1) The award in matters other than international commercial arbitration shall be made by the arbitral tribunal within a period of twelve months from the date of completion of pleadings under sub-section (4) of section 23.
Provided that the award in the matter of international commercial arbitration may be made as expeditiously as possible and endeavour may be made to dispose of the matter within a period of twelve months from the date of completion of pleadings under sub-section (4) of section 23.

Section 34. Application for setting aside arbitral award:
(1) Recourse to a Court against an arbitral award may be made only by an application for setting aside such award in accordance with sub-section (2) and sub-section (3).
(2) An arbitral award may be set aside by the Court only if—
(a) the party making the application furnishes proof that—
(i) a party was under some incapacity; or
(ii) the arbitration agreement is not valid under the law to which the parties have subjected it or, failing any indication thereon, under the law for the time being in force; or
(iii) the party making the application was not given proper notice of the appointment of an arbitrator or of the arbitral proceedings or was otherwise unable to present his case; or
(iv) the arbitral award deals with a dispute not contemplated by or not falling within the terms of the submission to arbitration, or it contains decisions on matters beyond the scope of the submission to arbitration; or
(v) the composition of the arbitral tribunal or the arbitral procedure was not in accordance with the agreement of the parties.
"""

def main():
    print("generating synethetic pdfs because direct links failed...")
    create_pdf("Commercial_Courts_Act_2015.pdf", "The Commercial Courts Act, 2015", COMMERCIAL_COURTS_ACT_TEXT)
    create_pdf("Arbitration_Act_1996.pdf", "The Arbitration and Conciliation Act, 1996", ARBITRATION_ACT_TEXT)

if __name__ == "__main__":
    main()
