# -*- coding: utf-8 -*-

##################################################################################################
# Iron
##################################################################################################

IRON_D = {
    # Clardy et al. (2006). Acute and chronic effects of developmental iron deficiency
    # on mRNA expression patterns in the brain. Journal of Neural Transmission, 71, 173–96.
    # http://www.ncbi.nlm.nih.gov/pubmed/17447428
    'THRSP': 'thyroid hormone responsive protein',
    'TF': 'transferrin',
    'MAL': 'mal, T-cell differentiation protein',
    'KLK6': 'kallikrein-related peptidase 6',
    'HOMER1': 'homer homolog 1 (Drosophila), neuronal immediate early gene',
    'MOBP': 'myelin-associated oligodendrocytic basic protein',
    'APOD': 'apolipoprotein D',
    'MOG': 'myelin oligodendrocyte glycoprotein',
    'CRYAB': 'crystallin, alpha B',
    'APOC1': 'apolipoprotein C-I',
    'CA2': 'carbonic anhydrase II',
    'RASGRP1': 'RAS guanyl releasing protein 1',
    'STMN4': 'stathmin-like 4',
    'LYZ': 'lysozyme',
    'GSTM1': 'glutathione S-transferase mu 1',
    'CTSS': 'cathepsin S',
    'DCK': 'deoxycytidine kinase',
    # ''          :  'Rattus norvegicus Nclone10 mRNA',
    # 'Af6'       :  'afadin',
    # ''           :  'Rattus norvegicus retroviral-like ovarian specific transcript 30-1 mRNA',
    # ''          :  'Rat troponin-c mRNA'
    # 'Rnf28'      :  'ring finger protein 28',
    # 'LOC309574' :  'olfactory receptor',
    # ''           :  'Rattus norvegicus similar to S-100 protein, alpha chain (LOC295214), mRNA',
    # ''           :  'Rat PMSG-induced ovarian mRNA, 3’sequence, N1'
}

IRON = {
    # http://amp.pharm.mssm.edu/Harmonizome/gene_set/Iron+Homeostasis(Mus+musculus)/Wikipathways+Pathways
    'FTH1': 'ferritin heavy polypeptide 1',
    'FTL': 'ferritin light polypeptide',
    'HFE': 'hemochromatosis',
    'HFE2': 'hemochromatosis type 2 (juvenile)',
    'IL1A': 'interleukin 1, alpha',
    'IL6': 'interleukin 6',
    'IL6R': 'interleukin 6 receptor',
    'IREB2': 'iron-responsive element binding protein 2',
    'SLC40A1': 'solute carrier family 40 (iron-regulated transporter), member 1',
    'TF': 'transferrin',
    'TFR2': 'transferrin receptor 2',
    'TNF': 'tumor necrosis factor',
                            }

##################################################################################################
# Dopamine
##################################################################################################

DA_metabolism = {
# http://amp.pharm.mssm.edu/Harmonizome/gene_set/Dopamine+metabolism(Homo+sapiens)/Wikipathways+Pathways
    'COMT': 'catechol-O-methyltransferase',
    'DDC': 'dopa decarboxylase (aromatic L-amino acid decarboxylase)',
    'MAOA': 'monoamine oxidase A',
    'MAOB': 'monoamine oxidase B',
    'NQO1': 'NAD(P)H dehydrogenase, quinone 1',
    'PPP2CA': 'protein phosphatase 2, catalytic subunit, alpha isozyme',
    'PPP2CB': 'protein phosphatase 2, catalytic subunit, beta isozyme',
    'PRKACA': 'protein kinase, cAMP-dependent, catalytic, alpha',
    'PRKACB': 'protein kinase, cAMP-dependent, catalytic, beta',
    'PRKACG': 'protein kinase, cAMP-dependent, catalytic, gamma',
    # 'SOD1': 'superoxide dismutase 1, soluble',
    'TH': 'tyrosine hydroxylase',
    'TYR': 'tyrosinase ',
}

DA_receptor_bind = {
# http://software.broadinstitute.org/gsea/msigdb/geneset_page.jsp?geneSetName=GO_DOPAMINE_RECEPTOR_BINDING&keywords=dopamine
    'GNA13': 'guanine nucleotide binding protein',
    'DLG4': 'discs, large homolog 4 (Drosophila)',
    'DNM1': 'dynamin 1',
    'DNM2': 'dynamin 2',
    'DRD1': 'dopamine receptor D1',
    'DRD3': 'dopamine receptor D3',
    'GNA12': 'guanine nucleotide binding protein',
    'GNAS': 'GNAS complex locus',
    'ARRB2': 'arrestin, beta 2',
    'ATP1A3': 'ATPase, Na+/K+ transporting, alpha 3 polypep...',
    'PALM': 'paralemmin',
    'CLIC6': 'chloride intracellular channel 6',
    'PTPN11': 'protein tyrosine phosphatase, non-receptor t...',
    'PPP1R1B': 'protein phosphatase 1, regulatory (inhibitor...',
    'DNAJC14': 'DnaJ (Hsp40) homolog, subfamily C, member 14',
    'CAV2': 'caveolin 2',
    'SLC9A3R1': 'solute carrier family 9 (sodium/hydrogen exc...'
}

DA_receptor_sig = ['ADCY5', 'ADCY6', 'ARRB2', 'CALY',  # 'D4S234E',
                          'DRD1', 'DRD2', 'DRD3',
                          'DRD4', 'DRD5', 'FLNA', 'GNA11',
                          'GNA14', 'GNA15', 'GNAI3', 'GNAL', 'GNAO1',
                          'GNAQ', 'GNAS', 'GNB1', 'GNG2',
                          'GPR21', 'GPR52', 'GSK3A', 'GSK3B', 'HMP19', 'KLF16',
                          'OPRM1', 'RGS9', 'SLC9A3R1']
DA_transport = [
    # GO_DOPAMINE_TRANSPORT
    # > The directed movement of dopamine into, out of or within a cell, or between cells, by means of some agent such as a transporter or pore. Dopamine is a catecholamine neurotransmitter and a metabolic precursor of noradrenaline and adrenaline.
    # http://software.broadinstitute.org/gsea/msigdb/geneset_page.jsp?geneSetName=GO_DOPAMINE_TRANSPORT&keywords=dopamine
    'CHRM5', 'DRD1', 'PARK2', 'PARK7', 'SLC18A2',
    'SLC22A1', 'SLC22A2', 'SLC22A3', 'SLC6A2', 'SLC6A3', 'SNCA'
                       ]

DA_tranmission = [  # http://genesetdb.auckland.ac.nz/genesearch2.php
    # GO_DOPAMINE_RECEPTOR_SIGNALING_PATHWAY', '> The series of molecular signals
    # generated as a consequence of a dopamine receptor binding to one of its physiological ligands.',
    # http://software.broadinstitute.org/gsea/msigdb/geneset_page.jsp?geneSetName=GO_DOPAMINE_RECEPTOR_SIGNALING_PATHWAY&keywords=dopamine
    'CDK5', 'CRH', 'CRHBP', 'DRD1', 'DRD2', 'DRD3', 'DRD4', 'DRD5', 'RASD2', 'TH']

DA_jellen = ['SLC4A1', 'ALAS2', 'HBB', 'CXCL12', 'RSAD2', 'TFRC', 'GYPA', 'ACER2', 'AHSP', 'C10orf10', 'E2F2', 'UBE2L6'
                # missing 'APOL11B'
                ]
DA_jellen2 = ['HBB', 'CXCL12']

##################################################################################################
# GLUGABA
##################################################################################################


ANMC = [  # de Leeuw, C.,etal (2015). Involvement of astrocyte metabolic coupling
    # in Tourette syndrome pathogenesis. European Journal of Human Genetics,
    # 23(August 2014), 1–4. https://doi.org/10.1038/ejhg.2015.22
    'ME1', 'ALDH5A1', 'GBE1', 'GALM', 'PYGL', 'CPS1', 'PFKFB3',
    'PYGB', 'IDH2', 'ENO1', 'PPP1R1A', 'MDH2', 'CS', 'PYGM', 'PGM3',
    'PHKG1', 'SLC3A2', 'PFKFB4', 'KHK', 'LDHB', 'PCK2', 'SLC2A8',
    'PGM2', 'GPT', 'AKR1B1', 'NANS', 'PDK4', 'OGDHL', 'DHTKD1',
    'PFKM', 'PGM1', 'PC', 'AGL'
]

GLU_metabolism = {
# http://software.broadinstitute.org/gsea/msigdb/cards/REACTOME_GLUTAMATE_NEUROTRANSMITTER_RELEASE_CYCLE
    'UNC13B': 'unc-13 homolog B (C. elegans)',
    'RIMS1': 'regulating synaptic membrane exocytosis 1',
    'GLS2': 'glutaminase 2 (liver, mitochondrial)',
    'GLS': 'glutaminase',
    'SLC38A2': 'solute carrier family 38, member 2',
    'SLC17A7': 'solute carrier family 17 (sodium-dependent in...',
    'RAB3A': 'RAB3A, member RAS oncogene family',
    'SLC1A1': 'solute carrier family 1 (neuronal/epithelial ...',
    'SLC1A6': 'solute carrier family 1 (high affinity aspart...',
    'SLC1A7': 'solute carrier family 1 (glutamate transporte...',
    'SNAP25': 'synaptosomal-associated protein, 25kDa',
    'STX1A': 'syntaxin 1A (brain)',
    'STXBP1': 'syntaxin binding protein 1',
    'VAMP2': 'vesicle-associated membrane protein 2 (synapt...',
    'SYT1': 'synaptotagmin I'}

GABA_metabolism = {  # http://software.broadinstitute.org/gsea/msigdb/cards/BIOCARTA_GABA_PATHWAY
    'GPHN': 'gephyrin',
    'GABARAP': 'GABA(A) receptor-associated protein',
    'DNM1': 'dynamin 1',
    'GABRA1': 'gamma-aminobutyric acid (GABA) A receptor, al...',
    'GABRA2': 'gamma-aminobutyric acid (GABA) A receptor, al...',
    'GABRA3': 'gamma-aminobutyric acid (GABA) A receptor, al...',
    'GABRA4': 'gamma-aminobutyric acid (GABA) A receptor, al...',
    'GABRA5': 'gamma-aminobutyric acid (GABA) A receptor, al...',
    'GABRA6': 'gamma-aminobutyric acid (GABA) A receptor, al...',
    'SRC': 'v-src sarcoma (Schmidt-Ruppin A-2) viral onco...'
}

GLU_GABA = {
    'UNC13B': 'unc-13 homolog B (C. elegans)',
    'RIMS1': 'regulating synaptic membrane exocytosis 1',
    'GLS2': 'glutaminase 2 (liver, mitochondrial)',
    'GLS': 'glutaminase',
    'SLC38A2': 'solute carrier family 38, member 2',
    'SLC17A7': 'solute carrier family 17 (sodium-dependent in...',
    'RAB3A': 'RAB3A, member RAS oncogene family',
    'SLC1A1': 'solute carrier family 1 (neuronal/epithelial ...',
    'SLC1A6': 'solute carrier family 1 (high affinity aspart...',
    'SLC1A7': 'solute carrier family 1 (glutamate transporte...',
    'SNAP25': 'synaptosomal-associated protein, 25kDa',
    'STX1A': 'syntaxin 1A (brain)',
    'STXBP1': 'syntaxin binding protein 1',
    'VAMP2': 'vesicle-associated membrane protein 2 (synapt...',
    'SYT1': 'synaptotagmin I',
    'GPHN': 'gephyrin',
    'GABARAP': 'GABA(A) receptor-associated protein',
    'DNM1': 'dynamin 1',
    'GABRA1': 'gamma-aminobutyric acid (GABA) A receptor, al...',
    'GABRA2': 'gamma-aminobutyric acid (GABA) A receptor, al...',
    'GABRA3': 'gamma-aminobutyric acid (GABA) A receptor, al...',
    'GABRA4': 'gamma-aminobutyric acid (GABA) A receptor, al...',
    'GABRA5': 'gamma-aminobutyric acid (GABA) A receptor, al...',
    'GABRA6': 'gamma-aminobutyric acid (GABA) A receptor, al...',
    'SRC': 'v-src sarcoma (Schmidt-Ruppin A-2) viral onco...'
}


## OTHER
TF       = ['TF']
FTH      = ['FTH1']
FTL      = ['FTL']
HRE      = ['HFE']
HRE2     = ['HFE2']
SLC25    = ['SLC25A37']
SLC40    = ['SLC40A1']
BIOBANK  = TF + FTH + HRE + SLC25

