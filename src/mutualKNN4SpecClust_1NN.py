# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 04:52:07 2017

@author: Yifeng Tao
"""

# Generate mutual kNN graph.

import numpy as np
import numpy.linalg as linalg
from collections import defaultdict as dd
import matplotlib.pyplot as plt
from random import shuffle
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import pandas as pd
from sklearn.manifold import TSNE
import colorsys
import math
import copy

itertime = 20
KM = np.array([5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100])
#KM = np.array([40])
classsize = np.zeros([0,], dtype=float)
enrich = np.zeros([len(KM),],dtype = float)
enrich_ctrl = np.zeros([len(KM),],dtype = float)

def _get_colors(num_colors):
    colors=[]
    for i in np.arange(0., 360., 360. / num_colors):
        hue = i/360.
        lightness = (50 + np.random.rand() * 10)/100.
        saturation = (90 + np.random.rand() * 10)/100.
        colors.append(colorsys.hls_to_rgb(hue, lightness, saturation))
    return colors




    
kNN = 20
sga2sgaAaff = dd(set)
sgaAsga2aff = dd(int)
set_gene = set()
path = 'sga2sgaAff_baseline_brca.txt'
f = open(path, 'r')
pathout = 'out.txt'
fo = open(pathout, 'w')
next(f)
for line in f:
    l = line.strip().split('\t')
    sga1, sga2, aff = l[0], l[1], int(l[2])
    sga2sgaAaff[sga1].add((sga2, aff))
    set_gene.add(sga1)
    set_gene.add(sga2)
f.close()

set_gene = list(set_gene)

for sga in set_gene:
    context = sga2sgaAaff[sga]
    context = list(context)    
    # shuffle
    
    for i in range(kNN):
        shuffle(context)
    
        Maff = 0.0
        Mgene = 'helloword'
        for line in context:
            sgacontext, aff = line[0], line[1]
            if aff > Maff:
                Maff = aff
                Mgene = sgacontext
        sgaAsga2aff[(sga, Mgene)] = aff
        #sgaAsga2aff[(Mgene, sga)] = aff
        #print sga, Mgene, Maff
        context.remove((Mgene, Maff))
        if len(context) == 0: break
    
    #sgaAsga2aff[(sga1, sga2)] = aff

    #print >> fo, l

gene2id = dd()
id2gene = dd()

k = 0
for g in set_gene:
    gene2id[g] = k
    id2gene[k] = g
    k += 1


len_gene = len(set_gene)
W = np.zeros([len_gene, len_gene], float)
for i in range(len_gene):
    for j in range(len_gene):
        W[i][j] = sgaAsga2aff[(id2gene[i], id2gene[j])]*sgaAsga2aff[(id2gene[j], id2gene[i])]
   



path = 'sga2sgaAff_baseline_mukNN_'+str(kNN)+'_brca.txt'
f = open(path, 'w')
print >> f, 'Source\tTarget\tWeight'
for line in sgaAsga2aff.keys():
        sga1, sga2 = line[0], line[1]
        overlap = sgaAsga2aff[(sga1, sga2)]*sgaAsga2aff[(sga2, sga1)]
        #sga2, overlap = line[0], line[1]
        if overlap == 0: continue
        if sga1 == sga2: continue
        #TODO:1
        #print >> f, sga1 + '\t' + sga2 + '\t' + str(overlap)    
        print >> f, sga1 + '\t' + sga2 + '\t' + str(math.sqrt(overlap))
        #print >> f, sga1 + '\t' + sga2 + '\t' + overlap
f.close()






sga2sgaAaff = dd(set)
set_gene = set()

path = 'sga2sgaAff_baseline_mukNN_'+str(kNN)+'_brca.txt'
f = open(path, 'r')
next(f)
for line in f:
    l = line.strip().split('\t')
    sga1, sga2, aff = l[0], l[1], float(l[2])
    sga2sgaAaff[sga1].add((sga2, aff))
    set_gene.add(sga1)
    set_gene.add(sga2)
f.close()

set_gene = list(set_gene)

gene2id = dd()
id2gene = dd()

k = 0
for g in set_gene:
    gene2id[g] = k
    id2gene[k] = g
    k += 1


len_gene = len(set_gene)
W = np.zeros([len_gene, len_gene], float)
for i in range(len_gene):
    for j in range(len_gene):
        # TODO:2            
        #W[i][j] = sgaAsga2aff[(id2gene[i], id2gene[j])]*sgaAsga2aff[(id2gene[j], id2gene[i])]
        W[i][j] = math.sqrt(sgaAsga2aff[(id2gene[i], id2gene[j])]*sgaAsga2aff[(id2gene[j], id2gene[i])])

D = W.sum(axis=0)
Dinv = np.diag(1.0/D)

D = np.diag(D);
L =  D - W
#L = D - W;
L = np.dot(Dinv,L)

#print 2

lambda0, V0 = linalg.eig(L)

#print 3
#L = diag(1./sum(W))*L;
#[V0, lambda0] = eig(L);
ordr =lambda0.argsort()
lam = lambda0[ordr]
#V = V0
V = V0[:,ordr]



gene2goid = dd(set)
path = 'gene2goId.txt'
f = open(path, 'r')
#next(f)
for line in f:
    l = line.strip().split('\t')
    g, goid = l[0], l[1]
    gene2goid[g].add(goid)
f.close()



km = 40
#km = 50
X = V[:,0:km]

sga2sgaAaff = dd(set)

W = X
M = 0
for id1 in range(len_gene):
    #g1 = id2gene[id1]
    for id2 in range(len_gene):
        #g2 = id2gene[id2]
        d = W[id1,:] - W[id2,:]
        d =  np.linalg.norm(d)
        M = max(d, M)
        
for id1 in range(len_gene):
    g1 = id2gene[id1]
    for id2 in range(len_gene):
        g2 = id2gene[id2]
        d = W[id1,:] - W[id2,:]
        d =  M - np.linalg.norm(d)
        
        sga2sgaAaff[g1].add((g2, d))

def getsgaAsga2pp():
    set_pathway = set()
    sgaAsga2pp = dd(float)
    path = '../src/pp/sgaAsga2pp.txt'
    f = open(path, 'r')
    for line in f:
        l = line.strip().split('\t')
        sga1, sga2, prob = l[0], l[1], float(l[2])
        sgaAsga2pp[(sga1, sga2)] = prob
        set_pathway.add(sga1)
        set_pathway.add(sga2)
    
    f.close()
    return sgaAsga2pp, set_pathway

sgaAsga2pp, set_pathway = getsgaAsga2pp()
avgacc = 0
for trial in range(10):
    count_total = 0
    count_true = 0
    for sga in set_gene:
        if sga not in sga2sgaAaff.keys(): continue
        count_total += 1
        NNgene = 'helloworld'
        NNdist = 0.0
        Context = list(sga2sgaAaff[sga])
        shuffle(Context)
        for line in Context:
            sgaContext, aff = line[0], line[1]
            if sgaContext == sga: continue
            if aff > NNdist:
                NNdist = aff
                NNgene = sgaContext
        #print sga, NNgene, NNdist
        thd = 0.001
        if sgaAsga2pp[(sga, NNgene)] == 0.0: continue
        if sgaAsga2pp[(sga, NNgene)] <= thd:
            count_true += 1
#        ovlp = gene2goid[sga].intersection(gene2goid[NNgene])
#        ovlp = len(ovlp)
#        metric = 'one'
#        if metric == 'one':
#            if ovlp > 0:
#                count_true += 1
#        elif metric == 'total':
#            count_true += ovlp
#        elif metric == 'jaccard':
#            count_true += 1.0*ovlp/len(gene2goid[sga].union(gene2goid[NNgene]))
            
            
    acc = 1.0*count_true/count_total
    avgacc += acc
    # Omit if necessary
    #print '\tcancer:'+cancer+'\ttrial:'+str(trial)+'\taccuracy:'+str(acc)
print 'cancer:brca\tavgacc:'+str(1.0*avgacc/10)+'\t\t#checked_genes:'+str(count_total)


'''
kmeans = KMeans(n_clusters=km).fit(X)
y = kmeans.labels_



len_gene = len(set_gene)

total_u = 0.0
total_d = 0.0
within_u = 0.0
within_d = 0.0
for i in range(len_gene):
    g1 = id2gene[i]
    for j in range(len_gene):
        g2 = id2gene[j]
        l1 = y[i]
        l2 = y[j]
        total_d += 1
        if len(gene2goid[g1].intersection(gene2goid[g2])) > 0:
            total_u += 1
        if y[i] == y[j]:
            within_d += 1
            if len(gene2goid[g1].intersection(gene2goid[g2])) > 0:
                within_u += 1
#print within_d, total_d, within_u, total_u
print km, 1.0*within_u/within_d*total_d/total_u



pca = PCA(n_components=2)
Xnew = pca.fit_transform(X)
h = Xnew[:,0]
v = Xnew[:,1]


df = pd.DataFrame(dict(x=h, y=v, label=y))

groups = df.groupby('label')

plt.figure(figsize=(8, 8))
#fig, ax = plt.subplots()
for name, group in groups:
    plt.plot(group.x, group.y, marker='o', linestyle='', markersize = 5, label=name)
#ax.legend()
plt.xlim(-1,1)
plt.ylim(-1,1)




model = TSNE(n_components=2)
#np.set_printoptions(suppress=True)
Xnew = model.fit_transform(X)
h = Xnew[:,0]
v = Xnew[:,1]



df = pd.DataFrame(dict(x=h, y=v, label=y))

groups = df.groupby('label')


fig, ax = plt.subplots(figsize=(8, 8))




gene2degree = dd(float)
for i in range(len(set_gene)):
    sga1 = set_gene[i]
    for line in sga2sgaAaff[sga1]:
        sga2, aff = line[0], line[1]
        sga1id = gene2id[sga1]
        sga2id = gene2id[sga2]
        gene2degree[sga1] += aff
        gene2degree[sga2] += aff
        ax.plot([h[sga1id], h[sga2id]], [v[sga1id], v[sga2id]], marker='.', linestyle='-', color = [0.7, 0.7, 0.7] )

Mval = 0
for g in gene2degree.keys():
    degree = gene2degree[g]
    if degree > Mval: Mval = degree

Mval = math.sqrt(Mval)
for g in gene2degree.keys():
    degree = gene2degree[g]
    gene2degree[g] = math.sqrt(degree)/Mval



RGB_tuples = _get_colors(km)


for i in range(len(set_gene)):
    sga1 = set_gene[i]
    sga1id = gene2id[sga1]
    ax.plot(h[sga1id], v[sga1id], marker='o', linestyle='', markersize = int(20*gene2degree[sga1])+5, color = RGB_tuples[y[sga1id]])


    
    
    
threshold = 300

blacklist = set()
path = 'degree_SGA_SGA_.txt'
f = open(path, 'r')
next(f)
for line in f:
    l = line.strip().split('\t')
    sga, degree = l[0], int(l[1])
    if degree > threshold: blacklist.add(sga)
f.close()

    


plt.title('t-SNE of spectral clustering (k = '+str(km)+')')
#plt.xlim(-1,1)
#plt.ylim(-1,1)

plt.figure()
plt.plot(lam)
plt.ylabel('labmda')
plt.xlabel('k')
plt.title('SGA in BRCA')
plt.ylim((0,2))

enrich = enrich/itertime
enrich_ctrl = enrich_ctrl/itertime
plt.figure()
plt.plot(KM, enrich, color='r')
plt.plot(KM, enrich_ctrl, color='b')
plt.xlabel('k')
plt.ylabel('enrichment')

plt.title('averaged over '+str(itertime)+' replications')

np.save('enrichment_baseline_mukNN_'+str(kNN)+'_brca', enrich)
np.save('enrichment_baseline_mukNN_'+str(kNN)+'_ctrl_brca', enrich_ctrl)

np.save('classsize_40_baseline_mukNN_'+str(kNN)+'_brca',classsize)
#classsize
plt.figure()
plt.hist(classsize, bins = 200)
'''
print 'Done!'












