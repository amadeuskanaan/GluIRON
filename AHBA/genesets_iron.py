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

IRON_HOMEOSTASIS = {
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



########################################################################################################################
########################################################################################################################

# Gene Set: GO_CELLULAR_IRON_ION_HOMEOSTASIS

# http://software.broadinstitute.org/gsea/msigdb/geneset_page.jsp?geneSetName=GO_CELLULAR_IRON_ION_HOMEOSTASIS&keywords=iron
# Any process involved in the maintenance of an internal steady state of iron ions at the level of a cell.

IRON_ION_HOMEOSTASIS = ['ABCB6', 'ABCB7', 'ABCG2', 'ACO1', 'ALAS2', 'BMP6', 'CP', 'CYBRD1',  'FLVCR1', 'FTH1',  'FTHL17',
                        'FTL', 'FTMT', 'FXN', 'GDF2', 'HAMP', 'HEPH', 'HFE', 'HFE2', 'HIF1A', 'HMOX1', 'HMOX2', 'HPX', 'IREB2', 'ISCU', 'LCN2',
                        'LTF', 'MYC', 'NDFIP1', 'NUBP1', 'SCARA5', 'SLC11A1', 'SLC11A2', 'SLC22A17', 'SLC40A1', 'SLC46A1', 'SMAD4', 'SOD1',
                        'SRI', 'TF', 'TFR2', 'TFRC', 'TMPRSS6', 'TTC7A'] # not available 'FAM132B', 'FTH1P19',

########################################################################################################################
########################################################################################################################


#Gene Set: GO_IRON_ION_BINDING

#http://software.broadinstitute.org/gsea/msigdb/geneset_page.jsp?geneSetName=GO_IRON_ION_BINDING&keywords=iron
# > Interacting selectively and non-covalently with iron (Fe) ions.

IRON_ION_BINDING = ['ACO2', 'ACP5', 'AGMO', 'ALKBH1', 'ALKBH2', 'ALKBH3', 'ALKBH8', 'ALOX12', 'ALOX12B', 'ALOX15', 'ALOX15B',
                    'ALOX5', 'ALOXE3', 'AOX1', 'BBOX1', 'C14orf169',  'CALR', 'CDO1', 'CH25H', 'CYGB',
                    'CYP11A1', 'CYP11B1', 'CYP11B2', 'CYP17A1', 'CYP19A1', 'CYP1A1', 'CYP1A2', 'CYP1B1', 'CYP20A1', 'CYP21A2',
                    'CYP24A1', 'CYP26A1', 'CYP26B1', 'CYP26C1', 'CYP27A1', 'CYP27B1', 'CYP27C1', 'CYP2A13', 'CYP2A6', 'CYP2A7',
                    'CYP2B6', 'CYP2C18', 'CYP2C19', 'CYP2C8', 'CYP2C9', 'CYP2D6', 'CYP2E1', 'CYP2F1', 'CYP2G1P',
                    'CYP2J2', 'CYP2R1', 'CYP2S1', 'CYP2U1', 'CYP2W1', 'CYP39A1', 'CYP3A4', 'CYP3A43', 'CYP3A5', 'CYP3A7',
                    'CYP46A1', 'CYP4A11', 'CYP4A22', 'CYP4B1', 'CYP4F11', 'CYP4F12', 'CYP4F2', 'CYP4F22',  'CYP4F8',
                    'CYP4V2', 'CYP4X1', 'CYP4Z1', 'CYP4Z2P', 'CYP51A1', 'CYP7A1', 'CYP7B1', 'CYP8B1', 'DNAJC24', 'EGLN1',
                    'EGLN2', 'EGLN3', 'ETHE1', 'FA2H', 'FBXL5', 'FDX1', 'FECH', 'FTH1',  'FTHL17', 'FTL', 'FTMT',
                    'FTO', 'FXN', 'HAAO', 'HBA1', 'HBA2', 'HBB', 'HBD', 'HBE1', 'HBG1', 'HBG2', 'HBM', 'HBQ1', 'HBZ', 'HEPH',
                    'HIF1AN', 'ISCA1', 'ISCA2', 'ISCU',  'JMJD6', 'KDM3A', 'LCN2',
                    'LTF', 'MFI2', 'MIOX', 'MSMO1', 'MTRR', 'NDOR1', 'NFU1', 'NOS1', 'NOS2', 'NOS3', 'NT5E', 'OGFOD1', 'OGFOD2',
                    'P4HA1', 'P4HA2', 'P4HA3', 'P4HTM', 'PAH',  'PHF2', 'PHF8', 'PLOD1', 'PLOD2', 'PLOD3', 'POR', 'PPEF1',
                    'PPEF2', 'PTGIS',  'SCD', 'SNCA', 'TBXAS1', 'TET1', 'TET2', 'TF', 'TH', 'TMLHE', 'TPH1', 'TPH2',
                    'TYW1', 'TYW1B', 'TYW5', 'UROD', 'XDH']
#not available 'C17orf101', 'C5orf4', 'CYP2D7P1', 'CYP4F3', 'FTH1P19', 'JHDM1D', 'LEPRE1',  'LEPREL1', 'LEPREL2', 'PDF', 'SC5DL',


########################################################################################################################
########################################################################################################################

# Gene Set: GO_IRON_ION_IMPORT

# http://software.broadinstitute.org/gsea/msigdb/geneset_page.jsp?geneSetName=GO_IRON_ION_IMPORT&keywords=iron
# > The directed movement of iron ions into a cell or organelle.

IRON_ION_IMPORT = ['HFE', 'MFI2', 'PICALM', 'SLC11A2', 'STEAP1', 'STEAP1B', 'STEAP2', 'STEAP3', 'STEAP4', 'TF', 'TFR2', 'TFRC']



########################################################################################################################
########################################################################################################################

# Gene Set: GO_IRON_COORDINATION_ENTITY_TRANSPORT
# http://software.broadinstitute.org/gsea/msigdb/geneset_page.jsp?geneSetName=GO_IRON_COORDINATION_ENTITY_TRANSPORT&keywords=iron
#> The directed movement of an iron coordination entity into, out of or within a cell, or between cells, by means of some agent such as a transporter or pore.

IRON_TRANSPORT1 = ['ABCB6', 'ABCB7', 'ABCG2', 'FLVCR1', 'FLVCR2', 'HPX', 'HRG', 'LCN2',
                   'SLC22A17', 'SLC46A1', 'SLC48A1'] # not available 'ACCN3',



########################################################################################################################
########################################################################################################################



#Gene Set: REACTOME_IRON_UPTAKE_AND_TRANSPORT
#> Genes involved in Iron uptake and transport
# http://www.reactome.org/content/detail/917937

# http://software.broadinstitute.org/gsea/msigdb/geneset_page.jsp?geneSetName=REACTOME_IRON_UPTAKE_AND_TRANSPORT&keywords=iron

IRON_TRANSPORT2 = ['ABCG2', 'ATP6V0A2', 'ATP6V0A4', 'ATP6V0B', 'ATP6V0C', 'ATP6V0D1', 'ATP6V0D2', 'ATP6V0E1', 'ATP6V1A',
                             'ATP6V1B1', 'ATP6V1B2', 'ATP6V1C1', 'ATP6V1C2', 'ATP6V1D', 'ATP6V1E1', 'ATP6V1E2', 'ATP6V1F', 'ATP6V1G1',
                             'ATP6V1G2', 'ATP6V1G3', 'ATP6V1H', 'CP', 'CYBRD1', 'FLVCR1', 'FTH1', 'FTL', 'HEPH', 'HMOX1', 'HMOX2',
                             'MCOLN1', 'SLC40A1', 'SLC46A1', 'STEAP3', 'TCIRG1', 'TF', 'TFRC']



# Gene Set: GO_RESPONSE_TO_IRON_ION

#http://software.broadinstitute.org/gsea/msigdb/geneset_page.jsp?geneSetName=GO_RESPONSE_TO_IRON_ION&keywords=iron
# > Any process that results in a change in state or activity of a cell or an organism (in terms of movement,
# secretion, enzyme production, gene expression, etc.) as a result of an iron ion stimulus.

IRON_RESPONSE = ['ABAT', 'ABCG2', 'ACO1', 'ALAD', 'APBB1', 'ATP7A', 'B2M', 'BCL2', 'BMP6', 'C1QA', 'CCNB1', 'CCND1',
                 'CPOX', 'CYBRD1', 'CYP1A1', 'DRD2', 'FXN', 'GSK3B', 'HAMP', 'HFE', 'HMOX1', 'LCT', 'MDM2', 'PAWR',
                 'PDX1', 'SLC11A2', 'SLC40A1', 'SLC6A3', 'SNCA', 'TF', 'TFAP2A', 'TFF1', 'TFR2', 'TFRC', 'UROD']

########################################################################################################################
########################################################################################################################