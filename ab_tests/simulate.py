import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as st
import tqdm

from ab_tests import data_generator as dg
from ab_tests import stattests as ab


UPLIFT_REL = 0.1
USERS_NUM = 10000
EXPERIMENTS_NUM = 100
BOOTSTRAP_NUM = 10000
PARAMS_CLICKS = {'mean': 1, 'sigma': 0.5, 'sample_size': USERS_NUM}
PARAMS_CTRS_OLD = {
    'beta': 100,
    'success_rate': 0.02,
    'sample_size': 10000,
}
PARAMS_CTRS_NEW = {
    'beta': 100,
    'success_rate': 0.02 * (1 + UPLIFT_REL),
    'sample_size': 10000,
}

# Generate data for views and clicks
views = np.empty((USERS_NUM, EXPERIMENTS_NUM))
ctrs_old = np.empty((USERS_NUM, EXPERIMENTS_NUM))
ctrs_new = np.empty((USERS_NUM, EXPERIMENTS_NUM))
clicks_old = np.empty((USERS_NUM, EXPERIMENTS_NUM))
clicks_new_up = np.empty((USERS_NUM, EXPERIMENTS_NUM))
clicks_new_same = np.empty((USERS_NUM, EXPERIMENTS_NUM))
for i in tqdm.tqdm(range(EXPERIMENTS_NUM)):
    cur_views = dg.generate_views(**PARAMS_CLICKS)
    cur_ctrs_old = dg.generate_ctrs(**PARAMS_CTRS_OLD)
    cur_ctrs_new = dg.generate_ctrs(**PARAMS_CTRS_NEW)
    cur_clicks_old = dg.generate_clicks(cur_views, cur_ctrs_old)
    cur_clicks_new_up = dg.generate_clicks(cur_views, cur_ctrs_new)
    cur_clicks_new_same = dg.generate_clicks(cur_views, cur_ctrs_old)

    views[:, i] = cur_views
    ctrs_old[:, i] = cur_ctrs_old
    ctrs_new[:, i] = cur_ctrs_new
    clicks_old[:, i] = cur_clicks_old
    clicks_new_up[:, i] = cur_clicks_new_up
    clicks_new_same[:, i] = cur_clicks_new_same

# Test hypothesis for mean clicks
p_values_ttest = []
p_values_mwtest = []
fpr = [i / EXPERIMENTS_NUM for i in range(EXPERIMENTS_NUM)]
for i in range(EXPERIMENTS_NUM):
    p_values_ttest.append(
        st.ttest_ind(clicks_old[:, i], clicks_new_same[:, i]).pvalue,
    )
    p_values_mwtest.append(
        st.mannwhitneyu(clicks_old[:, i], clicks_new_same[:, i]).pvalue,
    )
p_values_ttest.sort()
p_values_mwtest.sort()
power_threshold_ttest = len(
    list(filter(lambda x: x <= 0.05, p_values_ttest)),
) - 1
power_threshold_mwtest = len(
    list(filter(lambda x: x <= 0.05, p_values_mwtest)),
) - 1
print(f'T-test Power under 0.05 p-value: {fpr[power_threshold_ttest]}')
print(f'MW-test Power under 0.05 p-value: {fpr[power_threshold_mwtest]}')
plt.plot(p_values_ttest, fpr, label='ttest')
plt.plot(p_values_mwtest, fpr, label='mwtest')
plt.legend(loc='best')
plt.show()

# Test hypothesis for CTRs
userCTR_old = clicks_old / views
userCTR_new_up = clicks_new_up / views
userCTR_new_same = clicks_new_same / views
p_values_ctrs_mwtest = []
for exp_num in range(EXPERIMENTS_NUM):
    tmp_ctrs_old = np.empty((BOOTSTRAP_NUM, 1))
    tmp_ctrs_new_up = np.empty((BOOTSTRAP_NUM, 1))
    tmp_ctrs_new_same = np.empty((BOOTSTRAP_NUM, 1))
    for trial in range(BOOTSTRAP_NUM):
        weights = ab.poisson_bootstrap(USERS_NUM)
        wviews = weights * views[:, exp_num]
        tmp_ctrs_old[trial] = np.nansum(wviews * userCTR_old[:, exp_num]) / np.nansum(wviews)
        tmp_ctrs_new_up[trial] = np.nansum(wviews * userCTR_new_up[:, exp_num]) / np.nansum(wviews)
        tmp_ctrs_new_same[trial] = np.nansum(wviews * userCTR_new_same[:, exp_num]) / np.nansum(wviews)

    p_values_ctrs_mwtest.append(st.mannwhitneyu(tmp_ctrs_old[:, 0], tmp_ctrs_new_same[:, 0]).pvalue)

p_values_ctrs_mwtest.sort()
power_threshold_mwtest = len(
    list(filter(lambda x: x <= 0.05, p_values_ctrs_mwtest)),
) - 1
print(f'MW-test for CTR Power under 0.05 p-value: {fpr[power_threshold_mwtest]}')
plt.plot(p_values_ctrs_mwtest, fpr, label='mwtest')
plt.legend(loc='best')
plt.show()
