import json
import urllib2
import os
from tables import open_file
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn import preprocessing
from alleninf.api import get_probes_from_genes
from alleninf.data import get_values_at_locations
from alleninf.api import get_mni_coordinates_from_wells#
from alleninf.analysis import fixed_effects, approximate_random_effects, bayesian_random_effects
import statsmodels.formula.api as smf
import math
from variables.variables import *
from AHBA.genesets import *
from sklearn.decomposition import TruncatedSVD, PCA
api_url        = "http://api.brain-map.org/api/v2/data/query.json"


def return_probe_expression(gene_probes_dict, geneset_name):
    dfs = []
    genes = gene_probes_dict.keys()

    if not os.path.isfile(os.path.join(ahba_dir, 'AHBA_%s.csv' % geneset_name)):

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

        # decompose probe expression values
        all_probes = ['%s_' % gene + str(i) for gene in gene_probes_dict.keys() for i in
                      gene_probes_dict[gene].values()]


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
            pca = PCA(n_components=3)
            pca.fit(np.array(np.asarray([df[gene] for gene in genes])))
            df['PC1'] = pca.components_[0, :]
            if  pca.components_[1, :].any():
                df['PC2'] = pca.components_[1, :]
            if len(genes) > 3:
                df['PC3'] = pca.components_[2, :]
            print 'PC explained variance:', pca.explained_variance_ratio_
            #df['PC_EV'] = pca.explained_variance_ratio_[0]#, pca.explained_variance_ratio_[1], pca.explained_variance_ratio_[2],


            #package_directory = '/Users/kanaan/SCR/Github/alleninf/alleninf'
        package_directory = '/scr/malta1/Software/anaconda/envs/awesome/lib/python2.7/site-packages/alleninf'
        mni = pd.read_csv(os.path.join(package_directory, "data", "corrected_mni_coordinates.csv"),
                          header=0, index_col=0)
        mni.index = mni.index.map(unicode)
        df_concat = pd.concat([df, mni], axis=1).to_csv(os.path.join(ahba_dir, 'AHBA_%s.csv' % geneset_name))

        return df_concat
    return pd.read_csv(os.path.join(ahba_dir, 'AHBA_%s.csv' % geneset_name), index_col=0)

def get_expression_df(genes, geneset_name):
    gene_probes = {}
    for gene in genes:
        gene_probes[gene] = get_probes_from_genes(gene)

    return_probe_expression(gene_probes, geneset_name)
    #return df


genesets = ['IRON', 'IRON_D', 'DA_jellen', 'DA_jellen2', 'DA_metabolism', 'DA_receptor', 'DA_receptor_sig', 'DA_tranmission', 'DA_transport',
            'ANMC', 'GLU', 'GABA', 'FTH', 'TF','FTH_ALL', 'FTL_ALL', 'FERRITIN']


# get_expression_df(IRON.keys()           , 'IRON')
# get_expression_df(IRON_D.keys()         , 'IRON_D')
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
# get_expression_df(HOUSEKEEPING          , 'HOUSEKEEPING')
# get_expression_df(FTH_ALL               , 'FTH_ALL')
# get_expression_df(FTL_ALL               , 'FTL_ALL')
# get_expression_df(FERRITIN              , 'FERRITIN')
# get_expression_df(AHBA_GENELIST           , 'GENELIST')
get_expression_df(ahba20k                 , 'ahba20k')

