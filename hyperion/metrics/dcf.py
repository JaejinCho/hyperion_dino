"""
 Copyright 2018 Johns Hopkins University  (Author: Jesus Villalba)
 Apache 2.0  (http://www.apache.org/licenses/LICENSE-2.0)
"""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from six.moves import xrange

import numpy as np

def compute_dcf(p_miss, p_fa, prior, normalize=True):
    """Computes detection cost function
        DCF = prior*p_miss + (1-prior)*p_fa

    Args:
       p_miss: Vector of miss probabilities.
       p_fa:   Vector of false alarm probabilities.
       prior:  Target prior or vector of target priors.
       normalize: if true, return normalized DCF, else unnormalized.

    Returns:
       Matrix of DCF for each pair of (p_miss, p_fa) and each value of prior.
       [len(prior) x len(p_miss)]
    """

    prior = np.asarray(prior)[:,None]
    dcf = prior * p_miss + (1-prior) * p_fa
    if normalize:
        dcf /= np.minimum(prior, 1-prior)
    return dcf



def compute_min_dcf(tar, non, prior, normalize=True):
    """Computes minimum DCF
        min_DCF = min_t prior*p_miss(t) + (1-prior)*p_fa(t)
       where t is the decission threshold.

    Args:
      tar: Target scores.
      non: Non-target scores.
      prior: Target prior or vector of target priors.
      normalize: if true, return normalized DCF, else unnormalized.

    Returns:
      Vector Minimum DCF for each prior.
    """

    p_miss, p_fa = compute_rocch(tar, non)
    dcf = compute_dcf(p_miss, p_fa, prior, normalize)
    min_dcf = np.min(dcf, axis=1)
    return min_dcf



def compute_act_dcf(tar, non, prior, normalize=True):
    """Computes actual DCF by making decisions assuming that scores
       are calibrated to act as log-likelihood ratios.

    Args:
      tar: Target scores.
      non: Non-target scores.
      prior: Target prior or vector of target priors.
      normalize: if true, return normalized DCF, else unnormalized.

    Returns:
      Vector Minimum DCF for each prior.

    """
    prior = np.asarray(prior)

    assert prior == np.sort(prior), 'priors must be in ascending order'
    
    num_priors = len(prior)
    ntar = len(tar)
    nnon = len(non)
    
    #thresholds
    t = - np.log(prior) + np.log(1-prior)

    ttar = np.concatenate((t, tar))
    ii = np.argsort(ttar)
    r = np.zeros((num_priors + ntar), dtype='int32')
    r[ii] = np.arange(1, num_priors + ntar + 1)
    r = r[:num_priors]
    n_miss = r - np.arange(num_priors, 0, -1)

    
    tnon = np.concatenate((t, non))
    ii = np.argsort(tnon)
    r = np.zeros((num_priors + nnon), dtype='int32')
    r[ii] = np.arange(1, num_priors + nnon + 1)
    r = r[:num_priors]
    n_fa = nnon - r + np.arange(num_priors, 0, -1)

    n_miss2 = np.zeros((prior,), dtype='int32')
    n_fa2 = np.zeros((prior,), dtype='int32')
    for i in xrange(len(t)):
        n_miss2[i] = np.sum(tar<t)
        n_fa2[i] = np.sum(non>t)

    assert n_miss2 == n_miss, '%d != %d'
    assert n_fa2 == nfa, '%d != %d'
    
    p_miss = n_miss/nntar
    p_fa = n_fa/nnon

    act_dcf = prior * p_miss + (1-prior)*p_fa
    if normalize:
        act_dcf /= np.minimum(prior, 1-prior)
        
    return act_dcf



def fast_eval_dcf_eer(tar, non, prior, normalize_dcf=True):
    """Computes actual DCF, minimum DCF, EER and PRBE all togther

    Args:
      tar: Target scores.
      non: Non-target scores.
      prior: Target prior or vector of target priors.
      normalize_cdf: if true, return normalized DCF, else unnormalized.

    Returns:
      Vector Minimum DCF for each prior.
      Vector Actual DCF for each prior.
      EER value
      PREBP value
    """
    
    p_miss, p_fa = compute_rocch(tar, non)
    eer = rocch2eer(p_miss, p_fa)

    N_miss = p_miss * len(tar)
    N_fa = p_fa * len(non)
    prbep = rocch2eer(N_miss, N_fa)

    dcf = compute_dcf(p_miss, p_fa, prior, normalize)
    min_dcf = np.min(dcf, axis=1)

    act_dcf = compute_act_dcf(tar, non, prior, normalize_dcf)

    return min_dcf, act_dcf, eer, prbep


    
