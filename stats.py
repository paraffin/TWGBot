#!/usr/bin/python2

import numpy as np
import scipy.stats as st
import matplotlib.pyplot as plt
import os, operator, string, __builtin__


def plot_wcts(GI):
    for member in GI.members:
        wcts = member.countwords()
        logcts = np.log10(wcts)
        logcts = logcts[np.isfinite(logcts)]
        plt.cla()
        plt.hist(logcts)
        plt.title(member.name)
        plt.draw()
        plt.show()

def plot_human_vs_wolf_wcts(GI):
    for member in GI.members:
        humancounts = member.countwords('human')
        wolfcounts = member.countwords('wolf')
        if len(humancounts) > 0 and len(wolfcounts) > 0:
            loghum = np.log10(humancounts)
            logwol = np.log10(wolfcounts)
            loghum = loghum[np.isfinite(loghum)]
            logwol = logwol[np.isfinite(logwol)]
            plt.subplot(211)
            plt.hist(loghum,bins=15,range=(0,3))
            plt.xlim(0,3)
            plt.title(member.name)
            plt.subplot(212)
            plt.hist(logwol,bins=15,range=(0,3))
            plt.xlim(0,3)
            plt.draw()
            plt.show()

def plot_all_human_vs_wolf_wcts(GI):
    humancounts = np.array([])
    wolfcounts = np.array([])
    for member in GI.members:
        hcs = member.countwords('human')
        wcs = member.countwords('wolf')
        humancounts = np.concatenate([humancounts,hcs])
        wolfcounts = np.concatenate([wolfcounts,wcs])
    loghum = np.log10(humancounts)
    logwol = np.log10(wolfcounts)
    loghum = loghum[np.isfinite(loghum)]
    logwol = logwol[np.isfinite(logwol)]
    plt.subplot(211)
    plt.hist(loghum,bins=15,range=(0,3))
    plt.xlim(0,3)
    plt.title("humans vs wolves")
    plt.subplot(212)
    plt.hist(logwol,bins=15,range=(0,3))
    plt.xlim(0,3)
    plt.draw()
    plt.show()

def plot_use_rates(GI):
    """
    Goal:
        Want to figure out how players vary word use rates per game.

    Method:
        For each member, do a word count for each game as wolf or human.
        Compute the mean and std of use rates for each word
        For each game, find how many stddevs the use rate is from the mean
        Histogram stddevs
    """
    Ns = []
    ps = []
    for member in GI.members:
        all_words = count_word_uses(member,dict(),'human')
        all_words = count_word_uses(member,all_words,'wolf')
        sum_allwords = 0
        for k,v in all_words.iteritems():
            sum_allwords += v
        sigs = []
        for player in member.players:
            if player.alignment in ['human','wolf']:
                pwords = {}
                for post in player.posts:
                    count_word_uses_in_post(post,pwords)
                sum_words = 0
                for k,v in pwords.iteritems():
                    sum_words += v
                for k,v in pwords.iteritems():
                    if k in all_words and v > 10:
                        n1 = float(v)
                        N1 = float(sum_words)
                        n2 = float(all_words[k])
                        N2 = float(sum_allwords)
                        p = compare_uses((n1,N1),(n2,N2))+1e-15
                        sig = st.norm.ppf(1-p)
                        #print(p,n1,N1,n2,N2)
                        sigs.append(sig*cmp(n1/N1,n2/N2))
                        #sigs.append(sig)
        if len(sigs) > 20:
            #print(sigs)
            sigs = np.array(sigs)
            sigs = sigs[np.isfinite(sigs)]
            k2, pval = st.normaltest(sigs)
            print(len(sigs))
            print(pval)
            plt.hist(sigs)
            plt.draw()
            plt.show()
            plt.cla()
            Ns.append(len(sigs))
            ps.append(pval)
    plt.scatter(Ns,ps)
    plt.show()

def print_word_compares(GI):
    for member in GI.members:
        wolfwords = count_word_uses(member,dict(),'wolf')
        humawords = count_word_uses(member,dict(),'human')
        sum_wolfwords = 0
        for k,v in wolfwords.iteritems():
            sum_wolfwords += v
        sum_humawords = 0
        for k,v in humawords.iteritems():
            sum_humawords += v
        wolfps = {}
        humaps = {}
        for player in member.players:
            if player.alignment in ['human','wolf']:
                pwords = {}
                for post in player.posts:
                    count_word_uses_in_post(post,pwords)
                sum_words = 0
                for k,v in pwords.iteritems():
                    sum_words += v
                for k,v in pwords.iteritems():
                    if player.alignment == 'wolf' and k in humawords and v > 10:
                        p = compare_uses((v,sum_words),(humawords[k],sum_humawords))
                        if k in wolfps:
                            wolfps[k].append(p)
                        else:
                            wolfps[k] = [p]
                    elif player.alignment == 'human' and k in wolfwords and v > 10:
                        p = compare_uses((v,sum_words),(wolfwords[k],sum_wolfwords))
                        if k in humaps:
                            humaps[k].append(p)
                        else:
                            humaps[k] = [p]
        tops = {}
        for k,v in wolfps.iteritems():
            if k in humaps:
                tops[k] = (v,humaps[k])
        cmpfnc = lambda x,y:cmp(np.mean(np.concatenate([x[0],x[1]])),np.mean(np.concatenate([y[0],y[1]])))
        sortops = sorted(tops.iteritems(),key=operator.itemgetter(1),cmp=cmpfnc)
        for i in range(min(len(sortops),10)):
            print(sortops[i])
        raw_input()


def print_word_uses(GI):
    for member in GI.members:
        wolfwords = count_word_uses(member,dict(),'wolf')
        humawords = count_word_uses(member,dict(),'human')
        topwolf = sorted(wolfwords.iteritems(), key=operator.itemgetter(1), reverse=True)
        tophuma = sorted(humawords.iteritems(), key=operator.itemgetter(1), reverse=True)
        print(member.name)
        print('Top human words')
        print(tophuma[:10])
        print('Top wolf words')
        print(topwolf[:10])
        raw_input()

def print_diffs_word_uses_all(GI):
    wolfwords = {}
    humawords = {}
    for member in GI.members:
        count_word_uses(member,wolfwords,'wolf')
        count_word_uses(member,humawords,'human')
    if len(wolfwords) > 0 and len(humawords) > 0:
        normwolf = normalize_word_uses(wolfwords)
        normhuma = normalize_word_uses(humawords)
        diffs = {}
        for k,v in normhuma.iteritems():
            if k in normwolf:
                vwolf = normwolf[k]
                abs_diff = np.abs(v[0] - vwolf[0])
                #err = np.sqrt((v[1]/v[0])**2 + (vwolf[1]/vwolf[0])**2)
                err = np.sqrt(v[1]**2 + vwolf[1]**2)
                sig_diff = abs_diff/err
                if sig_diff > 0.0:
                    diffs[k] = (sig_diff, (v[0],v[1]), (vwolf[0],vwolf[1]))
        topdiffs = sorted(diffs.iteritems(),cmp=lambda x,y:cmp(x[0],y[0]),key=operator.itemgetter(1),reverse=True)
        print('Top word differences')
        for i in range(min(25,len(topdiffs))):
            word = topdiffs[i][0]
            print('Word: %s' % (word))
            print('\tUse rate by humans:\t%f +/- %f pct. (N = %d)' % (100.0*normhuma[word][0],100.0*normhuma[word][1],humawords[word]))
            print('\tUse rate by wolves:\t%f +/- %f pct. (N = %d)' % (100.0*normwolf[word][0],100.0*normwolf[word][1],wolfwords[word]))
            print('\tSignificance:\t%3f' % (topdiffs[i][1][0]))
            print('\tP-value:\t %f' % (st.norm.sf(topdiffs[i][1][0])*2))

def print_diffs_word_uses_members(GI):
    all_diffs =[]
    for member in GI.members:
        wolfwords = {}
        humawords = {}
        count_word_uses(member,wolfwords,'wolf')
        count_word_uses(member,humawords,'human')
        sum_wolfwords = 0
        sum_humawords = 0
        for k,v in wolfwords.iteritems():
            sum_wolfwords += v
        for k,v in humawords.iteritems():
            sum_humawords += v
        normhuma = normalize_word_uses(humawords)
        normwolf = normalize_word_uses(wolfwords)
        if len(wolfwords) > 0 and len(humawords) > 0:
            diffs = {}
            for k,v in humawords.iteritems():
                if k in wolfwords:
                    if v > 10 and wolfwords[k] > 10:
                        n1 = float(v)
                        n2 = float(wolfwords[k])
                        N1 = float(sum_humawords)
                        N2 = float(sum_wolfwords)
                        p = compare_uses((n1,N1),(n2,N2))
                        sig_diff = st.norm.ppf(1-p)
                        #abs_diff = np.abs(v[0] - vwolf[0])
                        #err = np.sqrt((v[1]/v[0])**2 + (vwolf[1]/vwolf[0])**2)
                        #err = np.sqrt(v[1]**2 + vwolf[1]**2)
                        #sig_diff = abs_diff/err
                        if sig_diff > 0.0:
                            diffs[k] = (sig_diff, (n1/N1,n1/np.sqrt(n1), (n2/N2,n2/np.sqrt(n2))))
            all_diffs.append(diffs)
            topdiffs = sorted(diffs.iteritems(),cmp=lambda x,y:cmp(x[0],y[0]),key=operator.itemgetter(1),reverse=True)
            print('Top word differences for %s' % (member.name))
            for i in range(min(15,len(topdiffs))):
                word = topdiffs[i][0]
                print('Word: %s' % (word))
                print('\tUse rate by humans:\t%f +/- %f pct. (N = %d)' % (100.0*normhuma[word][0],100.0*normhuma[word][1],humawords[word]))
                print('\tUse rate by wolves:\t%f +/- %f pct. (N = %d)' % (100.0*normwolf[word][0],100.0*normwolf[word][1],wolfwords[word]))
                print('\tSignificance:\t%3f' % (topdiffs[i][1][0]))
                print('\tP-value:\t %f' % (st.norm.sf(topdiffs[i][1][0])*2))
            raw_input()
    common_diffs = {}
    for diffdict in all_diffs:
        for word,v in diffdict.iteritems():
            if word not in common_diffs:
                common_diffs[word] = ([v[0]],[v[1]],[v[2]])
            else:
                common_diffs[word][0].append(v[0])
                common_diffs[word][1].append(v[1])
                common_diffs[word][2].append(v[2])
    top_commdiffs = sorted(common_diffs.iteritems(),cmp=lambda x,y:cmp(np.mean(np.abs(x[0])),np.mean(np.abs(y[0]))),key=operator.itemgetter(1),reverse=True)
    return top_commdiffs

def compare_uses(r1,r2):
    """
    Given r1,r2 = (n,N), compute the significance of the difference between two use rates.
    Assume n's are Poisson RV's, calculate probability of getting n2 uses out of N2 words
    given null hypothesis of mu2 = (n1/N1)*N2 and vice-versa.
    
    """
    n1 = float(r1[0])
    N1 = float(r1[1])
    n2 = float(r2[0])
    N2 = float(r2[1])
    mu1 = n2*N1/N2
    mu2 = n1*N2/N1
    if n1 >= mu1:
        p1 = st.poisson.sf(n1,mu1)
    else:
        p1 = st.poisson.cdf(n1,mu1)
    if n2 >= mu2:
        p2 = st.poisson.sf(n2,mu2)
    else:
        p2 = st.poisson.cdf(n2,mu2)
    p = p1 + p2
    return p



def compare_use_rates(r1,r2):
    """
    Find how significant the difference between two usage rates is.
    r1,r2 = (frac,sigma)
    returns sig_diff
    """
    abs_diff = r1[0] - r2[0]
    err = np.sqrt(r1[1]**2 + r2[1]**2)
    sig_diff = abs_diff/err
    return sig_diff

def normalize_word_uses(dict):
    rv = {}
    total_words = 0
    for k,v in dict.iteritems():
        total_words += v
    for k,v in dict.iteritems():
        if v > 10:
            frac = float(v)/float(total_words)
            sigma = frac/np.sqrt(v)
            rv[k] = (frac, sigma)
    return rv

def count_word_uses(member,dict=dict(),alignment='any'):
    for player in member.players:
        if alignment == 'any':
            for post in player.posts:
                count_word_uses_in_post(post,dict)
        elif alignment == player.alignment:
            for post in player.posts:
                count_word_uses_in_post(post,dict)
    return dict

def count_word_uses_in_post(post,dict):
    post.stripquotes()
    words = post.soup.text.split()
    for word in words:
        w = word.encode('ascii','ignore')
        w2 = __builtin__.str(w)
        w2 = w2.lower()
        w2 = w2.translate(None,string.punctuation)
        if w2 in dict:
            dict[w2] += 1
        else:
            dict[w2] = 1

def merge_dicts(d1, d2, merge_fn=lambda x,y:x+y):
    result = dict(d1)
    for key,value in d3.iteritems():
        if key in result:
            result[key] = merge_fn(result[key],value)
        else:
            result[key] = value
    return result
