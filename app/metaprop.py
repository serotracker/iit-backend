import requests
import pandas as pd
from math import log, sqrt, asin, exp, sin, cos, pi
from numpy import sign

Z_975 = 1.96
SP_ZERO_BLACKLIST = ['untransformed', 'logit']
MIN_DENOMINATOR = 250
pd.options.mode.chained_assignment = None

url = 'https://iit-backend.com/airtable_scraper/records'
response = requests.get(url)

if response.status_code == 200:
    data = pd.DataFrame(response.json()['records'])

def calcTransformPrevalence(p, N, method):
    if method == 'untransformed': 
        return p
    elif method == 'logit': 
        return log(p / (1 - p))
    elif method == 'arcsin': 
        return asin(sqrt(p))
    elif method == 'double_arcsin_approx': 
        n = N * p
        return asin(sqrt(n / (N + 1))) + asin(sqrt((n + 1) / (N + 1)))
    elif method == 'double_arcsin_precise':
        n = N * p
        return 0.5 * (asin(sqrt(n / (N + 1))) + asin(sqrt((n + 1) / (N + 1))))

def calcTransformVariance(p, N, method):
    if method == 'untransformed': 
        return p * (1 - p) / N
    elif method == 'logit': 
        return 1 / (N * p) + 1 / (N * (1- p))
    elif method == 'arcsin': 
        return 1 / (4 * N)
    elif method == 'double_arcsin_approx': 
        return 1 / (N + 0.5)
    elif method == 'double_arcsin_precise': 
        return 1 / (4 * N + 2)

def backTransformPrevalence(t, n, method):
    if method == 'untransformed': 
        if t < 0: 
            return 0
        elif t > 1: 
            return 1
        else: 
            return t
    elif method == 'logit': 
        return exp(t) / (exp(t) + 1)
    elif method == 'arcsin': 
        if t < 0: 
            return 0
        elif t > pi / 2: 
            return 1
        else:
            return sin(t) ** 2
    elif method == 'double_arcsin_approx': 
        if t < 0: 
            return 0
        elif t > pi: 
            return 1
        else:
            return sin(t / 2) ** 2
    elif method == 'double_arcsin_precise': 
        if t < 0: 
            return 0
        elif t > pi / 4: 
            return 1
        else:
            return 0.5 * (1 - sign(cos(t)) * sqrt(1 - (sin(2 * t) + (sin(2 * t) - 2 * sin(2 * t)) / n) ** 2))

def metaprop(records, method = 'arcsin'):
    filteredRecords = records[(records['SERUM_POS_PREVALENCE'].notna()) &
                            (records['DENOMINATOR'].notna()) &
                            (records['DENOMINATOR'] >= MIN_DENOMINATOR) &
                            (records['SERUM_POS_PREVALENCE'] != 0 if method in SP_ZERO_BLACKLIST else True)]
    
    n_studies = filteredRecords.shape[0]
    if n_studies == 0: 
        return None 
    
    filteredRecords['TRANSFORMED_PREVALENCE'] = filteredRecords.apply(lambda row: calcTransformPrevalence(row['SERUM_POS_PREVALENCE'], 
                                                                                                          row['DENOMINATOR'], 
                                                                                                          method),
                                                                     axis = 1)
    filteredRecords['TRANSFORMED_VARIANCE'] = filteredRecords.apply(lambda row: calcTransformVariance(row['SERUM_POS_PREVALENCE'], 
                                                                                                          row['DENOMINATOR'], 
                                                                                                          method),
                                                                     axis = 1)
    filteredRecords['INVERSE_VARIANCE'] = 1 / filteredRecords['TRANSFORMED_VARIANCE']
    filteredRecords['PREVALENCE_OVER_VARIANCE'] = filteredRecords['TRANSFORMED_PREVALENCE'] / filteredRecords['TRANSFORMED_VARIANCE']
    filteredRecords['INVERSE_DENOMINATOR'] = 1 / filteredRecords['DENOMINATOR']
    
    N_sum = sum(filteredRecords['DENOMINATOR'])
    weight_sum = sum(filteredRecords['INVERSE_VARIANCE'])
    weighted_variance_sum = sum(filteredRecords['PREVALENCE_OVER_VARIANCE'])
    variance_sum = sum(filteredRecords['TRANSFORMED_VARIANCE'])
    inverse_n_sum = sum(filteredRecords['INVERSE_DENOMINATOR'])
    
    trans_pooled_prevalence = weighted_variance_sum / weight_sum
    trans_conf_inter = [trans_pooled_prevalence - Z_975 * sqrt(variance_sum),
                       trans_pooled_prevalence + Z_975 * sqrt(variance_sum)]
    
    overall_n = n_studies / inverse_n_sum
    
    pooled_prevalence = backTransformPrevalence(trans_pooled_prevalence, overall_n, method)
    conf_inter = [backTransformPrevalence(i, overall_n, method) for i in trans_conf_inter]
    conf_inter = [max(conf_inter[0], 0), min(conf_inter[1], 1)]
    error = [abs(pooled_prevalence - i) for i in conf_inter]
    
    return {
        'seroprevalence_percent': pooled_prevalence * 100,
        'error_percent': [i * 100 for i in error],
        'total_N': N_sum,
        'n_studies': n_studies
    }

def groupBy(records, factor):
    options = {item for sublist in data[factor] for item in sublist}
    records.dropna(subset = [factor], inplace = True)
    return {name: records[records[factor].apply(lambda x: name in x)] for name in options}

{name: metaprop(records) for name, records in groupBy(data, 'COUNTRY').items()}