# -*- coding: utf-8 -*-

import os
import pandas as pd
import urllib2
import json

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
FTH      = ['FTH1']
FTL      = ['FTL']
FTH_ALL  = ['FTH1', 'FTH1P14', 'FTH1P20', 'FTHL17' ]
FTL_ALL  = ['FTL', 'FTLP17']
FERRITIN = FTH_ALL + FTL_ALL + ['FTMT']
TF       = ['TF']
HFE      = ['HFE']
HFE2     = ['HFE2']
SLC25    = ['SLC25A37']
SLC40    = ['SLC40A1']
BIOBANK  = TF + FTH + HFE + SLC25

BTBD9 = ['BTBD9']

TCA = ['ACLY', 'ACO1', 'ACO2', 'CS', 'DLAT', 'DLD', 'DLST', 'FH', 'IDH1', 'IDH2', 'IDH3A', 'IDH3B',
      'IDH3G', 'LOC283398', 'LOC642502', 'MDH1', 'MDH2', 'OGDH', 'OGDHL', 'PC',  'PCK1',  'PCK2',
     'PDHA1', 'PDHA2', 'PDHB', 'SDHA', 'SDHB', 'SDHC', 'SDHD', 'SUCLA2', 'SUCLG1', 'SUCLG2']

ACO1 = ['ACO1']
ACO2 = ['ACO2']
ACO =  ACO1+ ACO2


### HOSEKEEPING

HOUSEKEEPING = ['AAMP', 'AARS', 'ABLIM1', 'ACTB', 'ACTG1', 'AES', 'AGPAT1', 'ALDOA', 'ANP32B', 'ANXA11', 'ANXA2',
                'AP3S1', 'APEX1', 'APLP2', 'ARAF', 'ARF1', 'ARF3', 'ARF4', 'ARHGAP1', 'ARHGDIB', 'ARL6IP1', 'ARPC2',
                'ATF4', 'ATIC', 'ATOX1', 'ATP5A1', 'ATP5B', 'ATP5C1', 'ATP5F1', 'ATP5G1', 'ATP5G2', 'ATP5G3', 'ATP5O',
                'ATP6V1F', 'B2M', 'BCAP31', 'BCLAF1', 'BECN1', 'BRD2', 'BTG2', 'BUD31', 'C1QBP', 'CALM2', 'CANX',
                'CAP1', 'CAPN2', 'CAPNS1', 'CAPZA1', 'CASC3', 'CAST', 'CCND2', 'CCNI', 'CCR9', 'CCT4', 'CD151',
                'CD164', 'CD34', 'CD3E', 'CD63', 'CD74', 'CD81', 'CES2', 'CETN2', 'CFL1', 'CHI3L2', 'CHKB', 'CIRBP',
                'CLIC1', 'CLTA', 'CLTC', 'CLU', 'COMT', 'COPA', 'COPS6', 'COX10', 'COX4I1', 'COX6A1', 'COX6B1',
                'COX6C', 'COX7A2', 'COX7C', 'COX8A', 'CSNK2B', 'CST3', 'CSTB', 'CTDSP2', 'CTNNB1', 'CYB5R3',
                'DAZAP2', 'DCTN2', 'DDB1', 'DDT', 'DDX39B', 'DDX5', 'DHPS', 'DSTN', 'DUSP1', 'DVL3', 'DYNLL1',
                'ECHS1', 'EEF1A1', 'EEF1B2', 'EEF1D', 'EEF1G', 'EEF2', 'EIF1', 'EIF3E', 'EIF3F', 'EIF4A1', 'EIF4A2',
                'EIF4A3', 'EIF4G2', 'EIF4H', 'ENO1', 'ERH', 'ESD', 'EZR', 'FAM193A', 'FAS', 'FBL', 'FCGRT', 'FHL1',
                'FKBP1A', 'FKBP4', 'FLNA', 'FMOD', 'FNTA', 'FTH1', 'FTL', 'FUCA1', 'FUS', 'FYN', 'GAPDH', 'GDI2',
                'GLUL', 'GNAS', 'GNB1', 'GNB2L1', 'GPS1', 'GPS2', 'GPX1', 'GPX4', 'GSTO1', 'GSTP1', 'GUSB', 'H2AFZ',
                'H3F3B', 'HDAC1', 'HINT1', 'HLA-A', 'HLA-DOA', 'HLA-DPA1', 'HLA-DQB1', 'HLA-DRA', 'HLA-E', 'HMGB1',
                'HMGN2', 'HNRNPA1', 'HNRNPC', 'HNRNPF', 'HNRNPK', 'HNRNPL', 'HSP90AA1', 'HSP90AB1', 'HSPB1', 'HSPD1',
                'HTRA1', 'HYAL2', 'IFITM1', 'ILK', 'IQGAP1', 'IRAK1', 'ISG20', 'ITGB1', 'ITPK1', 'JOSD1', 'JUNB',
                'JUND', 'KARS', 'KAT6A', 'LAMP1', 'LASP1', 'LDHA', 'LDHB', 'LGALS1', 'LGALS3', 'LTA4H', 'MARCKS',
                'MAZ', 'MDH1', 'MGP', 'MGST2', 'MLF2', 'MLH1', 'MORF4L2', 'MPRIP', 'MSN', 'MT2A', 'MYH9',
                'NACA', 'NAP1L1', 'NCL', 'NCOR2', 'NCSTN', 'NDRG1', 'NDUFA12', 'NDUFA4', 'NDUFV2', 'NEDD8', 'NEFL',
                'NFIB', 'NFKBIA', 'NONO', 'NPC2', 'NPM1', 'OAZ1', 'OS9', 'PABPC1', 'PARP1', 'PAX6', 'PCBP2', 'PDLIM1',
                'PEBP1', 'PFDN5', 'PFN1', 'PGAM1', 'PGK1', 'PHB2', 'PI4KA', 'PIM1', 'PLP2', 'POLR2L', 'PPIA', 'PRDX1',
                'PRDX6', 'PSAP', 'PSD', 'PSEN1', 'PSMB2', 'PSMB3', 'PSMB4', 'PSMB5', 'PSMB6', 'PSMC1', 'PSMD2', 'PSMD7',
                'PSMD8', 'PSME1', 'PTDSS1', 'PTMA', 'PTP4A2', 'PTPN6', 'QARS', 'RAC1', 'RBPMS', 'RER1', 'RFTN1',
                'RHOA', 'RPA2', 'RPL10A', 'RPL11', 'RPL12', 'RPL13', 'RPL13A', 'RPL14', 'RPL17', 'RPL18',
                'RPL19', 'RPL21', 'RPL23', 'RPL24', 'RPL27', 'RPL27A', 'RPL28', 'RPL29', 'RPL3', 'RPL31', 'RPL32',
                'RPL34', 'RPL35', 'RPL35A', 'RPL36A', 'RPL36AL', 'RPL37A', 'RPL38', 'RPL39', 'RPL4', 'RPL6',
                'RPL7', 'RPL7A', 'RPL8', 'RPL9', 'RPLP0', 'RPLP1', 'RPLP2', 'RPN2', 'RPS10', 'RPS11', 'RPS14', 'RPS15',
                'RPS15A', 'RPS16', 'RPS17', 'RPS18', 'RPS19', 'RPS2', 'RPS21', 'RPS23', 'RPS25', 'RPS26', 'RPS27A',
                'RPS28', 'RPS29', 'RPS3', 'RPS3A', 'RPS5', 'RPS6', 'RPS7', 'RPS8', 'RPS9', 'RPSA', 'S100A10', 'SARS',
                'SCN1B', 'SEC61B', 'SEPT2', 'SEPW1', 'SERPINA3', 'SERPINB6', 'SET', 'SF1', 'SF3B2', 'SLC25A3',
                'SLC25A5', 'SLC25A6', 'SLC6A8', 'SNRNP70', 'SNRPD2', 'SOD1', 'SON', 'SPTBN1', 'SQSTM1', 'SRP14',
                'SSB', 'SSR2', 'STAT3', 'STMN1', 'STOM', 'SURF1', 'TAGLN2', 'TAX1BP1', 'TCEA1', 'TMBIM6', 'TMED10',
                'TMSB10', 'TMSB4X', 'TPR', 'TPT1', 'TRAF4', 'TRIM28', 'TUBB', 'TXN', 'TXNIP', 'UBA1', 'UBA52',
                'UBC', 'UBE2C', 'UBE2D3', 'UQCRB', 'UQCRH', 'USP11', 'VDAC2', 'VIM', 'VPS72', 'WARS', 'XBP1', 'XPO1',
                'YBX1', 'YWHAB', 'YWHAH', 'YWHAQ', 'YWHAZ', 'ZFP36', 'ZNF91']

                #housekeeping genes not in AHBA
                # 'DARC', 'MTRNR2L8',  'RPL18A', 'RPL41', 'UBB',

#Eisenberg E, Levanon EY. Human housekeeping genes, revisited. Trends Genet 2013; 29: 569–574.
HOUSEKEEPING_EISENBERG = ['C1orf43', 'CHMP2A', 'EMC7', 'GPI', 'PSMB2', 'PSMB4', 'RAB7A', 'REEP5', 'SNRPD3', 'VCP', 'VPS29']
# SHORT_HOUSEKEEPING = ['ACTB','GAPDH', 'HPRT1', 'B2M']
# SHORT_HOUSEKEEPING = ['ACTB','ALDOA', 'G6PD', 'GAPDH', 'B2M', 'PFKP', 'PGK1', 'PGAM1', 'TUBA1A', 'VIM', 'LDHA'] #  'HRPT',


rich = pd.read_excel(os.path.join('/scr/malta1/Github/GluIRON/AHBA/Richiardi_Data_File_S2.xlsx'))
AHBA_GENELIST = list(rich.gene_symbol)




# url ='http://api.brain-map.org/api/v2/data/Gene/query.json?criteria=products[abbreviation$eq%27HumanMA%27]&only=id,acronym,entrez_id,homologene_id&num_rows=all&order=id'
# ahba_all = json.load(urllib2.urlopen(url))
# ahba20k = [i['acronym'] for i in ahba_all['msg'] if i['entrez_id']]


french = pd.read_table(os.path.join('/scr/malta1/Github/GluIRON/AHBA/AHBA_French2015.tsv'),index_col = 0)
AHBA_GENELIST_FRENCH = [gene for gene in list(french.index)]