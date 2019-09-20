import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
import sys

from meld.util.utility import *
from meld.util.pytorch_complex import *

import lib_complex as cp

np_dtype = np.float32

class MultiChannelMRI(nn.Module):
    def __init__(self, ndim=2, alpha=1e-2, mu=1e-2, testFlag=False, device='cpu'):
        super(MultiChannelMRI,self).__init__()
    
        assert ndim == 2, '3D not yet supported!'

        self.ndim = ndim
        
        self.truth = None
        self.maps = None
        self.mask = None
        self.ksp = None
        self.adjoint = None
        
        # parameters
        self.alpha = nn.Parameter(torch.from_numpy(np.asarray([alpha]).astype(np_dtype))).to(device)
        self.mu = nn.Parameter(torch.from_numpy(np.asarray([mu]).astype(np_dtype))).to(device)
        self.testFlag = testFlag
        if testFlag:
            self.alpha.requires_grad_(False)

    def batch(self, imgs, maps, mask, ksp):

        self.truth, self.maps, self.mask, self.ksp = imgs, maps, mask, ksp
        self.adjoint = self.model_adjoint(self.ksp) # setup 

        return self.adjoint
        
    def forward(self, x, max_iter=10, eps=1e-4, device='cpu'):
        # initialize with adjoint
        return conjgrad(self.adjoint * 0., 
                        self.adjoint + self.mu * x, 
                        self.model_reg_normal, 
                        max_iter = max_iter,
                        eps = eps) 

    def reverse(self, x, device='cpu'):
        pass
    
    def model(self, x, device='cpu'):
        return sense_forw(x, self.maps, self.mask, ndim=self.ndim)

    def model_adjoint(self, x, device='cpu'):
        return sense_adj(x, self.maps, self.mask, ndim=self.ndim)

    def model_normal(self, x, device='cpu'):
        return sense_normal(x, self.maps, self.mask, ndim=self.ndim)
    
    def model_reg_normal(self, x, device='cpu'):
        return x * self.mu + self.model_normal(x, device = device)
    
    def loss(self, x):
        return (1/2) * torch.sum((self.ksp - self.model(x))**2)
        
    def nrmse(self, x, truth):
        with torch.no_grad():
            return ((x - truth).pow(2).sum() / truth.pow(2).sum()).sqrt()

def maps_forw(img, maps, ndim=2):
    return cp.zmul(img[:,None,...], maps)

def maps_adj(cimg, maps, ndim=2):
    return torch.sum(cp.zmul(cp.zconj(maps), cimg), 1, keepdim=False)

def fft_forw(x, ndim=2):
    return torch.fft(x, signal_ndim=ndim, normalized=True)

def fft_adj(x, ndim=2):
    return torch.ifft(x, signal_ndim=ndim, normalized=True)

def mask_forw(y, mask, ndim=2):
    return y * mask[:,None,:,:,None]

def sense_forw(img, maps, mask, ndim=2):
    return mask_forw(fft_forw(maps_forw(img, maps)), mask, ndim)

def sense_adj(ksp, maps, mask, ndim=2):
    return maps_adj(fft_adj(mask_forw(ksp, mask)), maps)

def sense_normal(img, maps, mask, ndim=2):
    return maps_adj(fft_adj(mask_forw(fft_forw(maps_forw(img, maps)), mask)), maps)


# conjugate gradient algorithm
def dot(x1, x2):
    return torch.sum(x1*x2)

def ip(x):
    return dot(x, x)

def dot_batch(x1, x2):
    return torch.sum(x1*x2, dim=list(range(1, len(x1.shape))))

def ip_batch(x):
    return dot_batch(x, x)


def conjgrad(x, b, Aop_fun, max_iter=50, l2lam=0., eps=1e-4, verbose=True):
    ''' batched conjugate gradient descent. assumes the first index is batch size '''

    # explicitly remove r from the computational graph
    r = b.new_zeros(b.shape, requires_grad=False)

    # the first calc of the residual may not be necessary in some cases...
    if l2lam > 0:
        r = b - (Aop_fun(x) + l2lam * x)
    else:
        r = b - Aop_fun(x)
    p = r

    rsnot = ip_batch(r)
    rsold = rsnot
    rsnew = rsnot

    eps_squared = eps ** 2

    reshape = (-1,) + (1,) * (len(x.shape) - 1)
    for i in range(max_iter):
        
        if rsnew.max() < eps:
            # print this value...
            print('Hit eps after', i)
            break

        if l2lam > 0:
            Ap = Aop_fun(p) + l2lam * p
        else:
            Ap = Aop_fun(p)
        pAp = dot_batch(p, Ap)

        alpha = (rsold / pAp).reshape(reshape)

        x = x + alpha * p
        r = r - alpha * Ap

        rsnew = ip_batch(r)

        beta = (rsnew / rsold).reshape(reshape)

        rsold = rsnew

        p = beta * p + r

    return x
