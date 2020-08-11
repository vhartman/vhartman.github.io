from scipy.optimize import minimize

import numpy as np
import matplotlib.pyplot as plt

import data as d


def ls(x, y):
    print "doing least squares"

    def fun(beta, x, y):
        res = np.sum((beta[0] + beta[1]*x - y)**2)
        return res

    res = minimize(fun, np.array([0, 0]), (x, y))
    return res.x

def lts(x, y, h):
    print "doing least trimmed squares"

def lms(x, y, h):
    print "doing least median squares"

def lhs(x, y):
    print "doing least huber squares"

    def fun(beta, x, y):
        def huber_cost(u, M = 1.3):
            L = np.zeros_like(u)
            for i in range(len(u)):
                if (abs(u[i]) < M):
                    L[i] = 0.5*u[i]**2
                else:
                    L[i] = M * (abs(u[i]) - 0.5 * M)
            return L

        res = np.sum(huber_cost(beta[0] + beta[1]*x - y))
        return res

    res = minimize(fun, np.array([0, 0]), (x, y))
    return res.x

def las(x, y):
    print "doing least absoulute"

    def fun(beta, x, y):
        res = np.sum(abs(beta[0] + beta[1]*x - y))
        return res

    res = minimize(fun, np.array([0, 0]), (x, y))
    return res.x

def lss(x, y):
    print "doing least saturated squares"

    def fun(beta, x, y):
        def saturated_cost(u, M = 1.3):
            L = np.zeros_like(u)
            for i in range(len(u)):
                if (abs(u[i]) < M):
                    L[i] = 0.5*u[i]**2
                else:
                    L[i] = 0.5*M **2
            return L

        res = np.sum(saturated_cost(beta[0] + beta[1]*x - y))
        return res

    res = minimize(fun, np.array([0, 0]), (x, y))
    return res.x

def lws(x, y):
    print "doing least weird shit"

    def fun(beta, x, y):
        res = np.sum((abs(beta[0] + beta[1]*x - y))**0.5)
        return res

    res = minimize(fun, np.array([0, 0]), (x, y))
    return res.x

def plot_model(x, y, betas):
    for beta in betas:
        plt.plot(x, beta[0] + beta[1]*x)
    
    plt.plot(x, y, 'x')

if __name__ == "__main__":
    x, y, xwo, ywo = d.get(0.5, 1, 0.3)

    beta_ls = ls(x, y)
    beta_ls_wo = ls(xwo, ywo)

    beta_lhs = lhs(x, y)
    beta_las = las(x, y)
    beta_lws = lws(x, y)

    print "LS: ",  beta_ls
    print "LSO: ",  beta_ls_wo

    print "LHS: ",  beta_lhs
    print "LAS: ",  beta_las
    print "LWS: ",  beta_lws

    plt.hist(x*beta_lws[1] + beta_lws[0] - y, 100)
    plt.show()

    plot_model(x, y, (beta_ls, beta_ls_wo, beta_lhs, beta_las, beta_lws))
    plt.legend(['LS', 'LS_WO', 'LHS', 'LAS', 'LWS'])

    plt.show()    


