"""
Conversion pack for April 2020 release
"""

CONVERSIONS = {
    # Renamed items, extracted via diff file
    "Adaptive Invulnerability Field I": "Adaptive Invulnerability Shield Hardener I",
    "Gistum C-Type Adaptive Invulnerability Field": "Gistum C-Type Adaptive Invulnerability Shield Hardener",
    "Adaptive Invulnerability Field II": "Adaptive Invulnerability Shield Hardener II",
    "Explosive Deflection Field I": "Anti-Explosive Shield Hardener I",
    "Kinetic Deflection Field I": "Anti-Kinetic Shield Hardener I",
    "EM Ward Field I": "Anti-EM Shield Hardener I",
    "Thermal Dissipation Field I": "Anti-Thermal Shield Hardener I",
    "Explosive Deflection Field II": "Anti-Explosive Shield Hardener II",
    "Kinetic Deflection Field II": "Anti-Kinetic Shield Hardener II",
    "EM Ward Field II": "Anti-EM Shield Hardener II",
    "Thermal Dissipation Field II": "Anti-Thermal Shield Hardener II",
    "Gistum B-Type Adaptive Invulnerability Field": "Gistum B-Type Adaptive Invulnerability Shield Hardener",
    "Gistum A-Type Adaptive Invulnerability Field": "Gistum A-Type Adaptive Invulnerability Shield Hardener",
    "Pithum A-Type Adaptive Invulnerability Field": "Pithum A-Type Adaptive Invulnerability Shield Hardener",
    "Pithum B-Type Adaptive Invulnerability Field": "Pithum B-Type Adaptive Invulnerability Shield Hardener",
    "Pithum C-Type Adaptive Invulnerability Field": "Pithum C-Type Adaptive Invulnerability Shield Hardener",
    "Limited Kinetic Deflection Field I": "Compact Anti-Kinetic Shield Hardener",
    "Limited 'Anointed' EM Ward Field": "Compact Anti-EM Shield Hardener",
    "Limited Adaptive Invulnerability Field I": "Compact Adaptive Invulnerability Shield Hardener",
    "Limited Explosive Deflection Field I": "Compact Anti-Explosive Shield Hardener",
    "Limited Thermal Dissipation Field I": "Compact Anti-Thermal Shield Hardener",
    "Dread Guristas EM Ward Field": "Dread Guristas Anti-EM Shield Hardener",
    "Dread Guristas Thermal Dissipation Field": "Dread Guristas Anti-Thermal Shield Hardener",
    "Dread Guristas Explosive Deflection Field": "Dread Guristas Anti-Explosive Shield Hardener",
    "Dread Guristas Kinetic Deflection Field": "Dread Guristas Anti-Kinetic Shield Hardener",
    "Dread Guristas Adaptive Invulnerability Field": "Dread Guristas Adaptive Invulnerability Shield Hardener",
    "Domination EM Ward Field": "Domination Anti-EM Shield Hardener",
    "Domination Thermal Dissipation Field": "Domination Anti-Thermal Shield Hardener",
    "Domination Explosive Deflection Field": "Domination Anti-Explosive Shield Hardener",
    "Domination Kinetic Deflection Field": "Domination Anti-Kinetic Shield Hardener",
    "Domination Adaptive Invulnerability Field": "Domination Adaptive Invulnerability Shield Hardener",
    "Kaikka's Modified Kinetic Deflection Field": "Kaikka's Modified Anti-Kinetic Shield Hardener",
    "Thon's Modified Kinetic Deflection Field": "Thon's Modified Anti-Kinetic Shield Hardener",
    "Vepas's Modified Kinetic Deflection Field": "Vepas's Modified Anti-Kinetic Shield Hardener",
    "Estamel's Modified Kinetic Deflection Field": "Estamel's Modified Anti-Kinetic Shield Hardener",
    "Kaikka's Modified EM Ward Field": "Kaikka's Modified Anti-EM Shield Hardener",
    "Thon's Modified EM Ward Field": "Thon's Modified Anti-EM Shield Hardener",
    "Vepas's Modified EM Ward Field": "Vepas's Modified Anti-EM Shield Hardener",
    "Estamel's Modified EM Ward Field": "Estamel's Modified Anti-EM Shield Hardener",
    "Kaikka's Modified Explosive Deflection Field": "Kaikka's Modified Anti-Explosive Shield Hardener",
    "Thon's Modified Explosive Deflection Field": "Thon's Modified Anti-Explosive Shield Hardener",
    "Vepas's Modified Explosive Deflection Field": "Vepas's Modified Anti-Explosive Shield Hardener",
    "Estamel's Modified Explosive Deflection Field": "Estamel's Modified Anti-Explosive Shield Hardener",
    "Kaikka's Modified Thermal Dissipation Field": "Kaikka's Modified Anti-Thermal Shield Hardener",
    "Thon's Modified Thermal Dissipation Field": "Thon's Modified Anti-Thermal Shield Hardener",
    "Vepas's Modified Thermal Dissipation Field": "Vepas's Modified Anti-Thermal Shield Hardener",
    "Estamel's Modified Thermal Dissipation Field": "Estamel's Modified Anti-Thermal Shield Hardener",
    "Kaikka's Modified Adaptive Invulnerability Field": "Kaikka's Modified Adaptive Invulnerability Shield Hardener",
    "Thon's Modified Adaptive Invulnerability Field": "Thon's Modified Adaptive Invulnerability Shield Hardener",
    "Vepas's Modified Adaptive Invulnerability Field": "Vepas's Modified Adaptive Invulnerability Shield Hardener",
    "Estamel's Modified Adaptive Invulnerability Field": "Estamel's Modified Adaptive Invulnerability Shield Hardener",
    "Caldari Navy Kinetic Deflection Field": "Caldari Navy Anti-Kinetic Shield Hardener",
    "Caldari Navy Explosive Deflection Field": "Caldari Navy Anti-Explosive Shield Hardener",
    "Caldari Navy Thermal Dissipation Field": "Caldari Navy Anti-Thermal Shield Hardener",
    "Caldari Navy Adaptive Invulnerability Field": "Caldari Navy Adaptive Invulnerability Shield Hardener",
    "Caldari Navy EM Ward Field": "Caldari Navy Anti-EM Shield Hardener",
    "Gist C-Type Kinetic Deflection Field": "Gist C-Type Anti-Kinetic Shield Hardener",
    "Pith C-Type Kinetic Deflection Field": "Pith C-Type Anti-Kinetic Shield Hardener",
    "Gist C-Type Explosive Deflection Field": "Gist C-Type Anti-Explosive Shield Hardener",
    "Pith C-Type Explosive Deflection Field": "Pith C-Type Anti-Explosive Shield Hardener",
    "Gist C-Type Thermal Dissipation Field": "Gist C-Type Anti-Thermal Shield Hardener",
    "Pith C-Type Thermal Dissipation Field": "Pith C-Type Anti-Thermal Shield Hardener",
    "Gist C-Type EM Ward Field": "Gist C-Type Anti-EM Shield Hardener",
    "Pith C-Type EM Ward Field": "Pith C-Type Anti-EM Shield Hardener",
    "Gist B-Type EM Ward Field": "Gist B-Type Anti-EM Shield Hardener",
    "Pith B-Type EM Ward Field": "Pith B-Type Anti-EM Shield Hardener",
    "Gist B-Type Thermal Dissipation Field": "Gist B-Type Anti-Thermal Shield Hardener",
    "Pith B-Type Thermal Dissipation Field": "Pith B-Type Anti-Thermal Shield Hardener",
    "Gist B-Type Explosive Deflection Field": "Gist B-Type Anti-Explosive Shield Hardener",
    "Pith B-Type Explosive Deflection Field": "Pith B-Type Anti-Explosive Shield Hardener",
    "Gist B-Type Kinetic Deflection Field": "Gist B-Type Anti-Kinetic Shield Hardener",
    "Pith B-Type Kinetic Deflection Field": "Pith B-Type Anti-Kinetic Shield Hardener",
    "Gist A-Type Kinetic Deflection Field": "Gist A-Type Anti-Kinetic Shield Hardener",
    "Pith A-Type Kinetic Deflection Field": "Pith A-Type Anti-Kinetic Shield Hardener",
    "Gist A-Type Explosive Deflection Field": "Gist A-Type Anti-Explosive Shield Hardener",
    "Pith A-Type Explosive Deflection Field": "Pith A-Type Anti-Explosive Shield Hardener",
    "Gist A-Type Thermal Dissipation Field": "Gist A-Type Anti-Thermal Shield Hardener",
    "Pith A-Type Thermal Dissipation Field": "Pith A-Type Anti-Thermal Shield Hardener",
    "Gist A-Type EM Ward Field": "Gist A-Type Anti-EM Shield Hardener",
    "Pith A-Type EM Ward Field": "Pith A-Type Anti-EM Shield Hardener",
    "Gist X-Type EM Ward Field": "Gist X-Type Anti-EM Shield Hardener",
    "Pith X-Type EM Ward Field": "Pith X-Type Anti-EM Shield Hardener",
    "Gist X-Type Thermal Dissipation Field": "Gist X-Type Anti-Thermal Shield Hardener",
    "Pith X-Type Thermal Dissipation Field": "Pith X-Type Anti-Thermal Shield Hardener",
    "Gist X-Type Explosive Deflection Field": "Gist X-Type Anti-Explosive Shield Hardener",
    "Pith X-Type Explosive Deflection Field": "Pith X-Type Anti-Explosive Shield Hardener",
    "Gist X-Type Kinetic Deflection Field": "Gist X-Type Anti-Kinetic Shield Hardener",
    "Pith X-Type Kinetic Deflection Field": "Pith X-Type Anti-Kinetic Shield Hardener",
    "'Nugget' Kinetic Deflection Field": "'Nugget' Anti-Kinetic Shield Hardener",
    "'Desert Heat' Thermal Dissipation Field": "'Desert Heat' Anti-Thermal Shield Hardener",
    "'Posse' Adaptive Invulnerability Field": "'Posse' Adaptive Invulnerability Shield Hardener",
    "'Poacher' EM Ward Field": "'Poacher' Anti-EM Shield Hardener",
    "'Snake Eyes' Explosive Deflection Field": "'Snake Eyes' Anti-Explosive Shield Hardener",
    "Civilian Thermal Dissipation Field": "Civilian Anti-Thermal Shield Hardener",
    "Civilian EM Ward Field": "Civilian Anti-EM Shield Hardener",
    "Civilian Explosive Deflection Field": "Civilian Anti-Explosive Shield Hardener",
    "Civilian Kinetic Deflection Field": "Civilian Anti-Kinetic Shield Hardener"
}
