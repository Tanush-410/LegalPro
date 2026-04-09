"""
Complete Case Type Reference with Full Names and Descriptions
Used for mapping abbreviations to full names for the website
"""

CASE_TYPES = {
    # Writ Petitions & Appeals
    "WP": {
        "full_name": "Writ Petition",
        "description": "A petition to the court requesting relief against governmental action, requesting orders/directions on matters of public importance or fundamental rights violations",
        "category": "Writ & Constitutional"
    },
    "WA": {
        "full_name": "Writ Appeal",
        "description": "An appeal against a decision made in a Writ Petition, challenging the lower court's judgment on constitutional matters",
        "category": "Writ & Constitutional"
    },
    
    # Civil Appeals
    "CA": {
        "full_name": "Civil Appeal",
        "description": "An appeal against a judgment or order from a lower court in civil matters, seeking reversal or modification",
        "category": "Civil Matters"
    },
    "FAO": {
        "full_name": "First Appeal (Original Side)",
        "description": "Appeal against a judgment passed by the High Court in original jurisdiction",
        "category": "Civil Matters"
    },
    "FA": {
        "full_name": "First Appeal",
        "description": "Appeal against a judgment from a District Court or lower court in civil proceedings",
        "category": "Civil Matters"
    },
    "SAO": {
        "full_name": "Second Appeal (Original)",
        "description": "Second appeal on questions of law from High Court's original jurisdiction decisions",
        "category": "Civil Matters"
    },
    "RSA": {
        "full_name": "Regular Second Appeal",
        "description": "Second appeal on pure questions of law against District Court judgments",
        "category": "Civil Matters"
    },
    "SAM": {
        "full_name": "Second Appeal (Miscellaneous)",
        "description": "Second appeal on mixed questions of law and fact in miscellaneous matters",
        "category": "Civil Matters"
    },
    
    # Civil Petitions & Motions
    "CP": {
        "full_name": "Civil Petition",
        "description": "A petition seeking relief in civil matters not covered by specific appeal procedures",
        "category": "Civil Matters"
    },
    "CCP": {
        "full_name": "Civil Contempt Petition",
        "description": "Petition alleging breach of court orders or contempt of court in civil matters",
        "category": "Court Procedures"
    },
    "CMP": {
        "full_name": "Civil Miscellaneous Petition",
        "description": "Petition for relief in miscellaneous civil matters, including applications for stay, bail, or interim relief",
        "category": "Court Procedures"
    },
    "CP(IB)": {
        "full_name": "Civil Petition (Insolvency & Bankruptcy)",
        "description": "Petition related to insolvency proceedings, bankruptcy, and debt recovery matters",
        "category": "Commercial & Insolvency"
    },
    
    # Criminal Matters
    "CRIM": {
        "full_name": "Criminal Petition",
        "description": "Petition seeking relief in criminal matters, including bail applications or challenging criminal proceedings",
        "category": "Criminal Matters"
    },
    "CRA": {
        "full_name": "Criminal Appeal",
        "description": "Appeal against a criminal conviction or sentence from a lower court, seeking acquittal or reduction of sentence",
        "category": "Criminal Matters"
    },
    "CC": {
        "full_name": "Criminal Contempt",
        "description": "Petition alleging contempt of court or breach of court orders in criminal proceedings",
        "category": "Criminal Matters"
    },
    "MCC": {
        "full_name": "Miscellaneous Criminal Case",
        "description": "Miscellaneous criminal matters including applications for stay, bail, or other relief",
        "category": "Criminal Matters"
    },
    
    # Special Cases
    "CAVEAT": {
        "full_name": "Caveat (Anticipatory Plea)",
        "description": "An application filed in anticipation of a case being filed against you, requesting notice before any order is passed",
        "category": "Special Cases"
    },
    "SLP(C)": {
        "full_name": "Special Leave Petition (Civil)",
        "description": "Petition seeking permission to appeal against a judgment that is normally not appealable",
        "category": "Special Cases"
    },
    "SLP(CR)": {
        "full_name": "Special Leave Petition (Criminal)",
        "description": "Criminal petition seeking permission to appeal beyond normal appellate procedures",
        "category": "Special Cases"
    },
    
    # Arbitration & Disputes
    "ARB": {
        "full_name": "Arbitration Case",
        "description": "Cases related to arbitration agreements and disputes between parties referred to arbitration",
        "category": "Arbitration & ADR"
    },
    "ARBO": {
        "full_name": "Arbitration (Original)",
        "description": "Original arbitration matter filed directly in the High Court",
        "category": "Arbitration & ADR"
    },
    
    # Appeals & Revisions
    "APO": {
        "full_name": "Appeal (Original)",
        "description": "Appeal from a court decision filed in the High Court's original jurisdiction",
        "category": "Civil Matters"
    },
    "RP": {
        "full_name": "Review Petition",
        "description": "Application to review and reconsider a previous judgment of the court",
        "category": "Court Procedures"
    },
    "RPA": {
        "full_name": "Review Petition (Appeal)",
        "description": "Review petition seeking reconsideration of an appellate judgment",
        "category": "Court Procedures"
    },
    
    # Tax & Financial
    "ITA": {
        "full_name": "Income Tax Appeal",
        "description": "Appeal against assessment, valuation, or order of Income Tax Officer or appellate authority",
        "category": "Tax & Financial"
    },
    "CTA": {
        "full_name": "Central Excise Appeal",
        "description": "Appeal against Central Excise duty assessment or disputes",
        "category": "Tax & Financial"
    },
    "EXCZL": {
        "full_name": "Excise Appeal",
        "description": "Appeal against excise duties or alcohol licensing issues",
        "category": "Tax & Financial"
    },
    "C.A.": {
        "full_name": "Customs Appeal",
        "description": "Appeal against customs duties, import/export decisions",
        "category": "Tax & Financial"
    },
    "VAT": {
        "full_name": "Value Added Tax Appeal",
        "description": "Appeal against VAT assessment or orders by tax authorities",
        "category": "Tax & Financial"
    },
    
    # Labour & Service Matters
    "LCA": {
        "full_name": "Labour Court Appeal",
        "description": "Appeal against Labor Court judgment in labour law and service matters",
        "category": "Labour & Service"
    },
    "WLI": {
        "full_name": "Workers' Compensation & Insurance",
        "description": "Cases related to worker compensation, gratuity, and service benefits disputes",
        "category": "Labour & Service"
    },
    
    # Land & Property
    "LEASE": {
        "full_name": "Lease & Property Matters",
        "description": "Cases involving lease agreements, property disputes, and landlord-tenant matters",
        "category": "Land & Property"
    },
    "LAND": {
        "full_name": "Land Dispute",
        "description": "Disputes over land ownership, boundaries, and property rights",
        "category": "Land & Property"
    },
    
    # Environmental & Administrative
    "ENVIR": {
        "full_name": "Environmental Matter",
        "description": "Cases involving environmental violations, pollution, and environmental protection laws",
        "category": "Environmental & Administrative"
    },
    "ADMIN": {
        "full_name": "Administrative Case",
        "description": "Cases challenging administrative decisions or government actions",
        "category": "Environmental & Administrative"
    },
    
    # Commercial & Corporate
    "COMM": {
        "full_name": "Commercial Dispute",
        "description": "Cases involving commercial contracts, business disputes, and trade matters",
        "category": "Commercial & Insolvency"
    },
    "CORP": {
        "full_name": "Corporate Petition",
        "description": "Cases involving company law, corporate governance, and shareholder disputes",
        "category": "Commercial & Insolvency"
    },
    
    # Family & Matrimonial
    "MATRI": {
        "full_name": "Matrimonial Case",
        "description": "Cases involving marriage, divorce, maintenance, and family law matters",
        "category": "Family Law"
    },
    "FAM": {
        "full_name": "Family Petition",
        "description": "Petitions in family law matters including guardianship and custody",
        "category": "Family Law"
    },
    
    # Other Civil Matters
    "MISC": {
        "full_name": "Miscellaneous Case",
        "description": "Miscellaneous civil matters not covered under specific case types",
        "category": "Miscellaneous"
    },
}

def get_case_type_info(case_type_abbrev):
    """Get full name and description for a case type"""
    case_type_upper = case_type_abbrev.upper().strip()
    
    if case_type_upper in CASE_TYPES:
        return CASE_TYPES[case_type_upper]
    
    # Return default if not found
    return {
        "full_name": case_type_abbrev,
        "description": "Legal case - see case details for more information",
        "category": "General"
    }

def get_all_case_types():
    """Get list of all case type abbreviations"""
    return sorted(CASE_TYPES.keys())

def get_case_types_by_category():
    """Group case types by category"""
    categories = {}
    for abbrev, info in CASE_TYPES.items():
        category = info['category']
        if category not in categories:
            categories[category] = []
        categories[category].append({
            'abbrev': abbrev,
            'full_name': info['full_name'],
            'description': info['description']
        })
    return categories
