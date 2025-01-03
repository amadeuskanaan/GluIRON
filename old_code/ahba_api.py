import json
import urllib2
import os
from tables import open_file
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn import preprocessing
#from alleninf.api import get_probes_from_genes
from alleninf.data import get_values_at_locations
from alleninf.api import get_mni_coordinates_from_wells#
from alleninf.analysis import fixed_effects, approximate_random_effects, bayesian_random_effects
import statsmodels.formula.api as smf
import math
from variables.variables import *
from AHBA.genesets import *
from AHBA.genesets_iron import *
from sklearn.decomposition import TruncatedSVD, PCA
api_url        = "http://api.brain-map.org/api/v2/data/query.json"




def get_probes_from_genes(gene_names):
    if not isinstance(gene_names, list):
        gene_names = [gene_names]
    # in case there are white spaces in gene names
    gene_names = ["'%s'" % gene_name for gene_name in gene_names]

    api_query = "?criteria=model::Probe"
    api_query += ",rma::criteria,[probe_type$eq'DNA']"
    api_query += ",products[abbreviation$eq'HumanMA']"
    api_query += ",gene[acronym$eq%s]" % (','.join(gene_names))
    api_query += ",rma::options[only$eq'probes.id','name']"

    data = json.load(urllib2.urlopen(api_url + api_query))

    d = {probe['id']: probe['name'] for probe in data['msg']}

    if not d:
        print 'Gene %s not available'%gene_name#
        # raise Exception("Could not find any probes for %s gene. Check "
        #                "http://help.brain-map.org/download/attachments/2818165/HBA_ISH_GeneList.pdf?version=1&modificationDate=1348783035873 "
        #                "for list of available genes." % gene_name)
        pass
    else:
        return d


def return_probe_expression(gene_probes_dict, geneset_name):
    dfs = []
    genes = gene_probes_dict.keys()

    if not os.path.isfile(os.path.join(ahba_dir, 'AHBA/AHBA_%s.csv' % geneset_name)):

        print 'Fetching normalized gene expression values for:', genes
        print ''
        for gene in genes:
            probe_ids = ["'%s'" % probe_id for probe_id in gene_probes_dict[gene].keys()]
            print 'Probe IDs for Gene %s = %s' % (gene, probe_ids)

            api_query = api_url + "?criteria=service::human_microarray_expression[probes$in%s]" % (','.join(probe_ids))
            data = json.load(urllib2.urlopen(api_query))
            print api_query

            cols = ['top_struct', 'struct_name', 'struct_id', 'donor_names', 'coords_native']
            probe_cols = ['%s_' % gene + str(i) for i in gene_probes_dict[gene].values()]
            cols = cols + probe_cols
            well_ids = [str(sample["sample"]["well"]) for sample in data["msg"]["samples"]]
            df = pd.DataFrame(index=well_ids, columns=cols)

            df['top_struct'] = [sample["top_level_structure"]["name"] for sample in data["msg"]["samples"]]
            df['struct_id'] = [sample["structure"]["id"] for sample in data["msg"]["samples"]]
            df['struct_name'] = [sample["structure"]["name"] for sample in data["msg"]["samples"]]
            df['donor_names'] = [sample["donor"]["name"] for sample in data["msg"]["samples"]]
            df['coords_native'] = [sample["sample"]["mri"] for sample in data["msg"]["samples"]]

            for i, probe_id in enumerate(gene_probes_dict[gene].values()):
                df['%s_%s' % (gene, probe_id)] = [float(expression_value) for expression_value in
                                                  data["msg"]["probes"][i]["expression_level"]]

            dfs.append(df)

        # concat all probe expression dataframes
        df = pd.concat(dfs, axis=1).T.groupby(level=0).first().T
        df.to_csv(os.path.join(ahba_dir, 'PROBES/PROBES_%s.csv' % geneset_name))

        # decompose probe expression values
        all_probes = ['%s_'%gene + str(i) for gene in gene_probes_dict.keys() for i in gene_probes_dict[gene].values()]

        # Need to simplify Dataframe by averaging all probes for every gene
        #split dataframe in probes and metadata
        df_probes     = df.iloc[:, :-5]
        df_metadata   = df.iloc[:, -5:]
        probes_unique = [s.split('_')[0] for s in df_probes.T.index.values]
        df_probes_mu  = df_probes.astype(float).T.groupby(probes_unique).mean().T

        df = pd.concat([df_probes_mu, df_metadata], axis=1)
        if len(set(probes_unique)) > 1:
            df['Mean'] = df[list(set(probes_unique))].mean(axis=1)
            df['Median'] = df[list(set(probes_unique))].median(axis=1)
            pca_genes = PCA()
            pca_genes.fit(np.array(np.asarray([df[gene] for gene in genes])))
            pca_probes = PCA()
            pca_probes.fit(np.array(np.asarray([df_probes[probe] for probe in all_probes])))
            try:
                df['SVD1g'] = pca_genes.components_[0, :]
                df['SVD1p'] = pca_probes.components_[0, :]
            except:
                print 'No SVD1'
            try:
                df['SVD2g'] = pca_genes.components_[1, :]
                df['SVD2p'] = pca_probes.components_[1, :]
            except:
                print 'No SVD2'
            try:
                df['SVD3g'] = pca_genes.components_[2, :]
                df['SVD3p'] = pca_probes.components_[2, :]
            except:
                print 'No SVD3'

            # print 'PC explained variance:', pca.explained_variance_ratio_
            #df['PC_EV'] = pca.explained_variance_ratio_[0]#, pca.explained_variance_ratio_[1], pca.explained_variance_ratio_[2],


            #package_directory = '/Users/kanaan/SCR/Github/alleninf/alleninf'
        package_directory = '/scr/malta1/Software/anaconda/envs/awesome/lib/python2.7/site-packages/alleninf'
        mni = pd.read_csv(os.path.join(package_directory, "data", "corrected_mni_coordinates.csv"),
                          header=0, index_col=0)
        mni.index = mni.index.map(unicode)
        df_concat = pd.concat([df, mni], axis=1).to_csv(os.path.join(ahba_dir, 'AHBA_%s.csv' % geneset_name))

        return df_concat
    return pd.read_csv(os.path.join(ahba_dir, 'AHBA/AHBA_%s.csv' % geneset_name), index_col=0)

def get_expression_df(genes, geneset_name):
    gene_probes = {}

    print '##########################################################################################################'
    print '##########################    Downloading AHBA for data for geneset %s      ##############################'%geneset_name
    print '##########################################################################################################'

    for gene in genes:
        probes  = get_probes_from_genes(gene)
        if probes:
            gene_probes[gene] = probes
        else:
            pass #print 'Gene %s has no probes' %gene

    return_probe_expression(gene_probes, geneset_name)
    #return df


genesets = ['IRON', 'IRON_D', 'DA_jellen', 'DA_jellen2', 'DA_metabolism', 'DA_receptor', 'DA_receptor_sig', 'DA_tranmission', 'DA_transport',
            'ANMC', 'GLU', 'GABA', 'FTH', 'TF','FTH_ALL', 'FTL_ALL', 'FERRITIN']


# get_expression_df(IRON_HOMEOSTASIS.keys()  , 'IRON_HOMEOSTASIS')
# get_expression_df(IRON_D.keys()            , 'IRON_D')
# get_expression_df(IRON_ION_HOMEOSTASIS     , 'IRON_ION_HOMEOSTASIS')
# get_expression_df(IRON_ION_BINDING         , 'IRON_ION_BINDING')
# get_expression_df(IRON_ION_IMPORT          , 'IRON_ION_IMPORT')
# get_expression_df(IRON_TRANSPORT1          , 'IRON_TRANSPORT1')
# get_expression_df(IRON_TRANSPORT2          , 'IRON_TRANSPORT2')
# get_expression_df(IRON_RESPONSE            , 'IRON_RESPONSE')
# get_expression_df(DA_jellen             , 'DA_jellen')
# get_expression_df(DA_jellen2            , 'DA_jellen2')
# get_expression_df(DA_metabolism.keys()  , 'DA_metabolism')
# get_expression_df(DA_receptor_bind      , 'DA_receptor')
# get_expression_df(DA_receptor_sig       , 'DA_receptor_sig')
# get_expression_df(DA_tranmission        , 'DA_tranmission')
# get_expression_df(DA_transport          , 'DA_transport')
# get_expression_df(ANMC                  , 'ANMC')
# get_expression_df(GLU_metabolism        , 'GLU')
# get_expression_df(GABA_metabolism       , 'GABA')
# get_expression_df(GLU_GABA              , 'GLU_GABA')
# get_expression_df(TF                    , 'TF')
# get_expression_df(FTH                   , 'FTH')
# get_expression_df(FTL                   , 'FTL')
# get_expression_df(HFE                   , 'HFE')
# get_expression_df(HFE2                  , 'HFE2')
# get_expression_df(SLC25                 , 'SLC25')
# get_expression_df(BIOBANK               , 'BIOBANK')
# get_expression_df(FTH_ALL               , 'FTH_ALL')
# get_expression_df(FTL_ALL               , 'FTL_ALL')
# get_expression_df(FERRITIN              , 'FERRITIN')
# get_expression_df(BTBD9                 , 'BTBD9')
# get_expression_df(TCA                   , 'TCA')
# get_expression_df(ACO1                  , 'ACO1')
# get_expression_df(ACO2                  , 'ACO2')
# get_expression_df(ACO                   , 'ACO')
# get_expression_df(HOUSEKEEPING          , 'HOUSEKEEPING')
# get_expression_df(HOUSEKEEPING_EISENBERG, 'HOUSEKEEPING_EISENBERG')

DA_allen = { #http://human.brain-map.org/microarray/search/show?exact_match=false&search_term=dopamine&search_type=gene
            'CDNF': 'cerebral dopamine neurotrophic factor',
            'DBH' : 'dopamine beta-hydroxylase (dopamine beta-monooxygenase)',
            'DRD1': 'dopamine receptor D1',
            'DRD2': 'dopamine receptor D2',
            'DRD3': 'dopamine receptor D3',
            'DRD4': 'dopamine receptor D4',
            'SLC6A3': 'solute carrier family 6 (neurotransmitter transporter, dopamine), member 3'
}

# get_expression_df(DA_allen.keys(), 'DA_allen')
# get_expression_df(DAT1, 'DAT1')
# get_expression_df(DRD_ALL, 'DRD_ALL')
# get_expression_df(['DRD1'], 'DRD1')
# get_expression_df(['DRD2'], 'DRD2')
# get_expression_df(['DRD3'], 'DRD3')
# get_expression_df(['DRD4'], 'DRD4')

# print len(AHBA_GENELIST_FRENCH)
# get_expression_df(AHBA_GENELIST_FRENCH    , 'GENELIST_FRENCH')
# get_expression_df(HOUSEKEEPING          , 'HOUSEKEEPING')
#
# get_expression_df(['TH'], 'TH')
# get_expression_df(['MAOA'], 'MAOA')
# get_expression_df(['MAOB'], 'MAOB')
# get_expression_df(['GAD1'], 'GAD1')
# get_expression_df(['GAD2'], 'GAD2')
# get_expression_df(['GLUD1'], 'GLUD1')
# get_expression_df(['GLUD2'], 'GLUD2')
# get_expression_df(['GLUD'], 'GLUD')
# get_expression_df(['IDH1'], 'IDH1')
# get_expression_df(['IDH2'], 'IDH2')
# get_expression_df(['IDH3A'], 'IDH3A')
# get_expression_df(['IDH3B'], 'IDH3B')
# get_expression_df(['IDH3G'], 'IDH3G')
# get_expression_df(['IDH3'], 'IDH3')
# get_expression_df(['IDH'], 'IDH')

# get_expression_df(NT_transport, 'NT_transport')
# get_expression_df(NT_receptor, 'NT_receptor')
# get_expression_df(NT_exo, 'NT_exo')
# get_expression_df(GABA_receptor, 'GABA_receptor')
# get_expression_df(GABA_sig, 'GABA_sig')
# get_expression_df(GLU_sec, 'GLU_sec')
# get_expression_df(NT_REG_NEG_T, 'NT_REG_NEG_T')
# get_expression_df(NT_REG_POS_GLU, 'NT_REG_POS_GLU')
# get_expression_df(NT_uptake, 'NT_uptake')
# get_expression_df(NT_REG_DA, 'NT_REG_DA')
# get_expression_df(NT_REG_GABA, 'NT_REG_GABA')
get_expression_df(NT_REG_GLU, 'NT_REG_GLU')
# get_expression_df(DA_cycling, 'DA_cycling')


