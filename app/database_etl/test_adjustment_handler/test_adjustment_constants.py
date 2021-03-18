# Bastos 2020 in BMJ provided a SR&MA of serological test diagnostic accuracy
# https://www.bmj.com/content/370/bmj.m2516
# we use their provided Se and Sp figures when independent evaluations are not available in our data
# and infer their distributions from the total number of samples provided

bastos_estimates_raw = {
    'ELISA': {
        'se': {
            '50': 75.6,
            '2.5': 84.3,
            '97.5': 90.9,
            'n': 766
        },
        'sp': {
            '50': 97.6,
            '2.5': 93.2,
            '97.5': 99.4,
            'n': 1109
        }
    },
    'LFIA': {
        'se': {
            '50': 66.0,
            '2.5': 49.3,
            '97.5': 79.3,
            'n': 2660
        },
        'sp': {
            '50': 96.6,
            '2.5': 94.3,
            '97.5': 98.2,
            'n': 2874
        }
    },
    'CLIA': {
        'se': {
            '50': 97.8,
            '2.5': 46.2,
            '97.5': 100,
            'n': 375
        },
        'sp': {
            '50': 97.8,
            '2.5': 62.9,
            '97.5': 99.9,
            'n': 2804
        }
    }
}

# rescale seroprevalence data from percentages to proportion
bastos_estimates = {test_type: {
    char: {prop: value / 100 if prop != 'n' else value for prop, value in char_di.items()}
    for char, char_di in test_type_di.items()}
    for test_type, test_type_di in bastos_estimates_raw.items()}

testadj_model_code = """
data {
    int<lower = 0> n_prev_obs;
    int<lower = 0> y_prev_obs;
    int<lower = 0> n_se;
    int<lower = 0> y_se;
    int<lower = 0> n_sp;
    int<lower = 0> y_sp;
}
parameters {
    real<lower = 0, upper = 1> prev;
    real<lower = 0, upper = 1> sens;
    real<lower = 0, upper = 1> spec;
}
model {
    real prev_obs;
    
    prev_obs = prev * sens + (1 - prev) * (1 - spec);
    y_prev_obs ~ binomial(n_prev_obs, prev_obs);
    y_se ~ binomial(n_se, sens);
    y_sp ~ binomial(n_sp, spec);
}
"""

jeffries_model_code = """
data {
    int<lower = 0> n_prev_obs;
    int<lower = 0> y_prev_obs;
    int<lower = 0> n_se;
    int<lower = 0> y_se;
    int<lower = 0> n_sp;
    int<lower = 0> y_sp;
}
parameters {
    real<lower = 0, upper = 1> prev;
    real<lower = 0, upper = 1> sens;
    real<lower = 0, upper = 1> spec;
}
model {
    real prev_obs;    
    prev ~ beta(0.5, 0.5); // imposes jeffries prior on true prevalence

    prev_obs = prev * sens + (1 - prev) * (1 - spec);
    y_prev_obs ~ binomial(n_prev_obs, prev_obs);
    y_se ~ binomial(n_se, sens);
    y_sp ~ binomial(n_sp, spec);
}
"""

fixed_sens_spec_model_code = """
data {
    int<lower = 0> n_prev_obs;
    int<lower = 0> y_prev_obs;
    int<lower = 0> n_se;
    int<lower = 0> y_se;
    int<lower = 0> n_sp;
    int<lower = 0> y_sp;
}
transformed data {
    real sens = y_se * 1.0 / n_se; // fix the sensitivity
    real spec = y_sp * 1.0 / n_sp; // fix the specificity 
}
parameters {
    real<lower = 0, upper = 1> prev;
}
model {
    real prev_obs;
    
    prev_obs = prev * sens + (1 - prev) * (1 - spec);
    y_prev_obs ~ binomial(n_prev_obs, prev_obs);
}
"""

# uniform_sens_spec_model_code = """
# data {
#     int<lower = 0> n_prev_obs;
#     int<lower = 0> y_prev_obs;
#     int<lower = 0> n_se;
#     int<lower = 0> y_se;
#     int<lower = 0> n_sp;
#     int<lower = 0> y_sp;
# }
# transformed data {
#     real sens_reported = y_se * 1.0 / n_se;
#     real spec_reported = y_sp * 1.0 / n_sp;
# }
# parameters {
#     real<lower = 0, upper = 1> prev;
#     real<lower = 0, upper = 1> sens;
#     real<lower = 0, upper = 1> spec;
# }
# model {
#     real prev_obs;
#
#     prev_obs = prev * sens + (1 - prev) * (1 - spec);
#     y_prev_obs ~ binomial(n_prev_obs, prev_obs);
#     sens ~ uniform(sens_reported - 0.01, sens_reported + 0.01);
#     spec ~ uniform(spec_reported - 0.01, spec_reported + 0.01);
# }
# """

jeffries_fixed_sens_spec_model_code = """
data {
    int<lower = 0> n_prev_obs;
    int<lower = 0> y_prev_obs;
    int<lower = 0> n_se;
    int<lower = 0> y_se;
    int<lower = 0> n_sp;
    int<lower = 0> y_sp;
}
transformed data {
    real sens = y_se * 1.0 / n_se; // fix the sensitivity
    real spec = y_sp * 1.0 / n_sp; // fix the specificity 
}
parameters {
    real<lower = 0, upper = 1> prev;
}
model {
    real prev_obs; 
    prev ~ beta(0.5, 0.5); // imposes jeffries prior on true prevalence

    prev_obs = prev * sens + (1 - prev) * (1 - spec);
    y_prev_obs ~ binomial(n_prev_obs, prev_obs);
}
"""

# considering explicit transformations per http://avehtari.github.io/BDA_R_demos/demos_rstan/rstan_demo.html#3_Binomial_model
# section 3.1 
reparametrized_model_code = """
data {
    int<lower = 0> n_prev_obs;
    int<lower = 0> y_prev_obs;
    int<lower = 0> n_se;
    int<lower = 0> y_se;
    int<lower = 0> n_sp;
    int<lower = 0> y_sp;
}
parameters {
    real logit_prev;
    real logit_sens;
    real logit_spec;
}
transformed parameters{
    real<lower = 0, upper = 1> prev;
    real<lower = 0, upper = 1> sens;
    real<lower = 0, upper = 1> spec;

    prev = inv_logit(logit_prev);
    sens = inv_logit(logit_sens);
    spec = inv_logit(logit_spec);
}
model {
    real prev_obs;
    real logit_prev_obs;
    
    logit_prev ~ normal(0, 1.5);
    logit_sens ~ normal(0, 1.5);
    logit_spec ~ normal(0, 1.5);    
    
    prev_obs = prev * sens + (1 - prev) * (1 - spec);
    logit_prev_obs = logit(prev_obs);

    y_prev_obs ~ binomial_logit(n_prev_obs, logit_prev_obs);
    y_se ~ binomial_logit(n_se, logit_sens);
    y_sp ~ binomial_logit(n_sp, logit_spec);
}
"""

reparametrized_fixed_sens_spec_model_code = """
data {
    int<lower = 0> n_prev_obs;
    int<lower = 0> y_prev_obs;
    int<lower = 0> n_se;
    int<lower = 0> y_se;
    int<lower = 0> n_sp;
    int<lower = 0> y_sp;
}
transformed data {
    real sens = y_se * 1.0 / n_se; // fix the sensitivity
    real spec = y_sp * 1.0 / n_sp; // fix the specificity 
}
parameters {
    real logit_prev;
}
transformed parameters{
    real<lower = 0, upper = 1> prev;
    prev = inv_logit(logit_prev);
}
model {
    real prev_obs;
    real logit_prev_obs;
    
    logit_prev ~ normal(0, 1.5);   
    
    prev_obs = prev * sens + (1 - prev) * (1 - spec);
    logit_prev_obs = logit(prev_obs);

    y_prev_obs ~ binomial_logit(n_prev_obs, logit_prev_obs);
}
"""
