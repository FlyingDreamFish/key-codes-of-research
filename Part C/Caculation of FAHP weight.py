# -*- coding: utf-8 -*-

import numpy as np
import math

'''
Convert the judgment matrix of Analytic Hierarchy Process (AHP) (scale 1-9) into a fuzzy complementary judgment matrix (scale 0.1-0.9).
'''
def get_fuzzy_judgment_matrix(A):
    A=[[(math.log(a[i][j],243)+0.5) for j in range(len(a[i]))] for i in range(len(a))]
    A=np.array(A)
    return A
'''
Convert the fuzzy complementary judgment matrix into a fuzzy consistent judgment matrix.
'''
def get_ri(i,A):
    row_list = A.sum(axis=1)
    ri=row_list[i]
    return ri

if __name__ == '__main__':

    # The judgment matrix of Hazardousness, Sensitivity and Vulnerability
    a = np.array([[1, 3, 3],[1/3, 1, 1],[1/3, 1, 1]]) 

    # For Hazardousness: The judgment matrix of RMAX3 and Historical flood inundation frequency
    # a = np.array([[1, 1/2],[2, 1]])
    
    # For Sensitivity: The judgment matrix of Elevation,TWI, NDVI and Proximity level to river system
    # a = np.array([[1, 1/5, 3, 1/4],[5, 1, 7, 3],[1/3, 1/7, 1, 1/3],[4, 1/3, 3, 1]])
    
    # For Vulnerability : The judgment matrix of Population density, GDP and Land use
    # a = np.array([[1, 3, 1/3],[1/3, 1, 1/5],[3, 5, 1]])
    
    A=get_fuzzy_judgment_matrix(a)
    m=len(A)
    n=len(A[0])
    r=np.zeros(shape=(m,n))
    for i in range(m):
        for j in range(n):
            ri=get_ri(i,A)
            rj=get_ri(j,A)
            rij=(ri-rj)/(2*(n-1))+0.5
            r[i,j]=rij  
    RI=[0, 0, 0.58, 0.89, 1.12, 1.26, 1.36, 1.41, 1.46, 1.49, 1.52]
    R= np.linalg.matrix_rank(r)
    V,D=np.linalg.eig(r)
    list1 = list(V)
    B= np.max(list1)
    index = list1.index(B)
    C = D[:, index]
    CI=(B-n)/(n-1)
    CR=CI/RI[n-1]
    if CR<0.10:
        print("CI=", CI)
        print("CR=", CR)
        print('The comparison matrix A passes the consistency test, the weight vector Q is:')
        sum=np.sum(C)
    
        Q=C/sum
        print(Q)
    else:
        print("The comparison matrix A does not pass the consistency test, it is necessary to reconstruct the comparison matrix A.")