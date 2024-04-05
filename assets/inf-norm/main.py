import matplotlib.pyplot as plt
import numpy as np

import time

def twod(xs, xf, cb, overlay_polytope = False, show_box = False):
    pts = []

    for i in range(10000):
        x = (np.random.rand(2)-0.5) * 10

        d = np.linalg.norm(xs - x, np.inf) + np.linalg.norm(x - xf, np.inf)
        if d <= cb:
            pts.append(x)

    plt.figure()
    plt.scatter(*np.array(pts).T)
    plt.axis('equal')

    m = (xs + xf) / 2

    mins = np.min(np.array(pts), axis=0)
    maxs = np.max(np.array(pts), axis=0)

    if show_box:
        plt.plot([mins[0], mins[0]], [mins[1], maxs[1]], linewidth=2, color='black', ls='--')
        plt.plot([mins[0], maxs[0]], [maxs[1], maxs[1]], linewidth=2, color='black', ls='--')

        plt.plot([maxs[0], maxs[0]], [mins[1], maxs[1]], linewidth=2, color='black', ls='--')
        plt.plot([mins[0], maxs[0]], [mins[1], mins[1]], linewidth=2, color='black', ls='--')

    x = np.linspace(-3, 3, 20)

    if overlay_polytope:
        dim = 2

        A = np.zeros((4*dim + 2*dim, dim))
        d = np.zeros(4*dim + 2*dim)
        cnt = 0

        for i in range(dim):
            for j in range(dim):
                if j == i:
                    continue

                a = xs[i]
                b = xf[j]

                A[cnt*4, i] = 1
                A[cnt*4, j] = 1
                d[cnt*4] = cb + a + b

                A[cnt*4 + 1, i] =  1
                A[cnt*4 + 1, j] = -1
                d[cnt*4 + 1] = cb + a - b

                A[cnt*4 + 2, i] = -1
                A[cnt*4 + 2, j] =  1
                d[cnt*4 + 2] = cb - a + b

                A[cnt*4 + 3, i] = -1
                A[cnt*4 + 3, j] = -1
                d[cnt*4 + 3] = cb - a - b

                cnt += 1

        for i in range(dim):
            A[cnt*4+i*dim, i] = 1
            d[cnt*4+i*dim] = cb/2 + m[i]

            A[cnt*4+i*dim+1, i] = -1
            d[cnt*4+i*dim+1] = cb/2 - m[i]

        pts = []

        for i in range(10000):
            x = (np.random.rand(2)-0.5) * 10

            tmp = A@ x
            if (tmp < d).all():
                pts.append(x)

        plt.scatter(*np.array(pts).T, alpha=0.5)

    plt.scatter(xs[0], xs[1])
    plt.scatter(xf[0], xf[1])

def threed():
    xs = np.array([-1, -2, 0])
    xf = np.array([1, 2, 1])
    cb = 5

    pts = []

    for i in range(100000):
        x = np.random.rand(3) * 10 - 5

        d = np.linalg.norm(x - xs, np.inf) + np.linalg.norm(x - xf, np.inf)
        if d < cb:
            pts.append(x)

    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(projection='3d')

    ax.plot([xs[0], xf[0]], [xs[1], xf[1]], [xs[2], xf[2]], linewidth=5)

    ax.scatter(*np.array(pts).T, alpha = 0.5)
    ax.scatter(xs[0], xs[1], xs[2])
    ax.scatter(xf[0], xf[1], xf[2])

    plt.axis('equal')

    if False:
        dim = 3

        N = 4*dim*(dim-1) + 2*dim
        A = np.zeros((N, dim))
        d = np.zeros(N)
        cnt = 0

        for i in range(dim):
            for j in range(dim):
                if j == i:
                    continue

                a = xs[i]
                b = xf[j]

                A[cnt*4, i] = 1
                A[cnt*4, j] = 1
                d[cnt*4] = cb + a + b

                A[cnt*4 + 1, i] =  1
                A[cnt*4 + 1, j] = -1
                d[cnt*4 + 1] = cb + a - b

                A[cnt*4 + 2, i] = -1
                A[cnt*4 + 2, j] =  1
                d[cnt*4 + 2] = cb - a + b

                A[cnt*4 + 3, i] = -1
                A[cnt*4 + 3, j] = -1
                d[cnt*4 + 3] = cb - a - b

                cnt += 1

        for i in range(dim):
            A[cnt*4+i*2, i] = 1
            d[cnt*4+i*2] = cb/2

            A[cnt*4+i*2+1, i] = -1
            d[cnt*4+i*2+1] = cb/2

        pts = []

        for i in range(100000):
            x = np.random.rand(3) * 10 - 5

            tmp = A@ x
            if (tmp < d).all():
                pts.append(x)

        ax.scatter(*np.array(pts).T, alpha = 1)

def initial_plot():
    cb = 7
    xs = np.array([0, 1])
    xf = np.array([2, -1])
    twod(xs, xf, cb)
    plt.savefig('img1.png', dpi=300, bbox_inches='tight')

    cb = 5
    xs = np.array([1, 2])
    xf = np.array([-1, -2])
    twod(xs, xf, cb)
    plt.savefig('img2.png', dpi=300, bbox_inches='tight')

def second_plot():
    cb = 7
    xs = np.array([0, 1])
    xf = np.array([2, -1])
    twod(xs, xf, cb, show_box=True)
    plt.savefig('img1_box.png', dpi=300, bbox_inches='tight')

    cb = 5
    xs = np.array([1, 2])
    xf = np.array([-1, -2])
    twod(xs, xf, cb, show_box=True)
    plt.savefig('img2_box.png', dpi=300, bbox_inches='tight')

def third_plot():
    cb = 7
    xs = np.array([0, 1])
    xf = np.array([2, -1])
    twod(xs, xf, cb, overlay_polytope=True)
    plt.savefig('img1_poly.png', dpi=300, bbox_inches='tight')

    cb = 5
    xs = np.array([1, 2])
    xf = np.array([-1, -2])
    twod(xs, xf, cb, overlay_polytope=True)
    plt.savefig('img2_poly.png', dpi=300, bbox_inches='tight')

def rejection_sampling(bounds, xs, xf, cb, N=1):
    mean = (bounds[:, 0] + bounds[:, 1]) / 2
    w = bounds[:,1] - bounds[:, 0]

    pts = []
    num_attempts = 0
    while True:
        num_attempts += 1
        x = (np.random.rand(bounds.shape[0]) - 0.5) * w + mean

        d = np.linalg.norm(xs - x, np.inf) + np.linalg.norm(x - xf, np.inf)
        if d <= cb:
            pts.append(x)

            if len(pts) >= N:
                return pts

def batch_rejection_sampling(bounds, xs, xf, cb, N=1, batch_size=1):
    mean = (bounds[:, 0] + bounds[:, 1]) / 2
    w = bounds[:,1] - bounds[:, 0]

    pts = []
    num_attempts = 0
    while True:
        num_attempts += 1
        x = (np.random.rand(bounds.shape[0], batch_size) - 0.5) * w[:, None] + mean[:, None]

        d = np.linalg.norm(xs[:, None] - x, np.inf, axis=0) + np.linalg.norm(x - xf[:, None], np.inf, axis=0)
        cmp = (d <= cb)
        masked = x[:, cmp]
        pts_to_use = min(masked.shape[1], N - len(pts))

        pts.extend(list(masked[:, :pts_to_use].T))

        if len(pts) >= N:
            return pts

def rejection_sampling_with_box(bounds, xs, xf, cb, N=1):
    cost_min = -cb/2 + (xs + xf) / 2
    cost_max =  cb/2 + (xs + xf) / 2

    mins = np.maximum(bounds[:, 0], cost_min)
    maxs = np.minimum(bounds[:, 1], cost_max)

    mean = (mins + maxs) / 2
    w = maxs - mins

    pts = []
    num_attempts = 0
    while True:
        num_attempts += 1
        x = (np.random.rand(bounds.shape[0]) - 0.5) * w + mean

        d = np.linalg.norm(xs - x, np.inf) + np.linalg.norm(x - xf, np.inf)
        if d <= cb:
            pts.append(x)

            if len(pts) >= N:
                return pts

def batch_rejection_sampling_with_box(bounds, xs, xf, cb, N=1, batch_size=1):
    cost_min = -cb/2 + (xs + xf) / 2
    cost_max =  cb/2 + (xs + xf) / 2

    mins = np.maximum(bounds[:, 0], cost_min)
    maxs = np.minimum(bounds[:, 1], cost_max)

    mean = (mins + maxs) / 2
    w = maxs - mins

    pts = []
    num_attempts = 0
    while True:
        num_attempts += 1
        effective_batch_size = batch_size
        #effective_batch_size = min(N - len(pts), batch_size)
        x = (np.random.rand(bounds.shape[0], effective_batch_size) - 0.5) * w[:, None] + mean[:, None]

        d = np.linalg.norm(xs[:, None] - x, np.inf, axis=0) + np.linalg.norm(x - xf[:, None], np.inf, axis=0)
        cmp = (d <= cb)
        masked = x[:, cmp]
        pts_to_use = min(masked.shape[1], N - len(pts))

        pts.extend(list(masked[:, :pts_to_use].T))

        if len(pts) >= N:
            return pts

def tmp():
    bounds = np.array([[-1, 5],
                       [-2, 3]])
    xs = np.array([0, 0])
    xf = np.array([2, 1])
    cb = 4

    pts = []
    #pts = batch_rejection_sampling(bounds, xs, xf, cb, 1000, 100)
    pts = batch_rejection_sampling_with_box(bounds, xs, xf, cb, 1000, 10)
    #for _ in range(1000):
    #    #pt = rejection_sampling_with_box(bounds, xs, xf, cb)
    #    pt = rejection_sampling(bounds, xs, xf, cb)
    #    pts.append(pt)

    plt.figure()
    plt.scatter(*np.array(pts).T)
    plt.axis('equal')

def benchmark_times(N=100):
    batch_size = 100

    colormap = {
        "rejection": "tab:blue",
        "box": "tab:orange",
        "rejection_batch": "tab:green",
        "box_batch": "tab:red",
    }

    fig, axes = plt.subplots(nrows=1, ncols=3, sharey=True, figsize=(8, 4))

    for i, cb in enumerate([4, 6, 8]):
        timings = {"rejection": [],
                   "box": [],
                   "rejection_batch": [],
                   "box_batch": [],
                  }

        ticks = {"rejection": [],
                   "box": [],
                   "rejection_batch": [],
                   "box_batch": [],
                  }

        dims = np.arange(2, 15)
        for dim in dims:
            print(dim)

            bounds = np.array([[-4, 4]]*dim)
            xs = np.array([-1]*dim)
            xf = np.array([1]*dim)

            if dim < 8:
                start = time.time()
                pts = rejection_sampling(bounds, xs, xf, cb, N)
                end = time.time()
                duration = end - start
                timings["rejection"].append(duration)
                ticks["rejection"].append(dim)
                print('no box', end - start)

            if dim < 12:
                start = time.time()
                pts = batch_rejection_sampling(bounds, xs, xf, cb, N, batch_size)
                end = time.time()
                duration = end - start
                timings["rejection_batch"].append(duration)
                ticks["rejection_batch"].append(dim)
                print('batch no box', end - start)

            start = time.time()
            pts = rejection_sampling_with_box(bounds, xs, xf, cb, N)
            end = time.time()
            duration = end - start
            timings["box"].append(duration)
            ticks["box"].append(dim)
            print('box:', end - start)

            start = time.time()
            pts = batch_rejection_sampling_with_box(bounds, xs, xf, cb, N, batch_size)
            end = time.time()
            duration = end - start
            timings["box_batch"].append(duration)
            ticks["box_batch"].append(dim)
            print('batch box:', end - start)

        linestyle='-'
        if cb == 6:
            linestyle = '--'
        elif cb == 8:
            linestyle = ":"

        axes[i].set_title("Bound: " + str(cb))
        for k, e in timings.items():
            axes[i].semilogy(ticks[k], np.array(e)/N, label=k, color=colormap[k], linestyle=linestyle)
        axes[i].set_ylabel("t [s]")
        axes[i].set_xlabel("dim")
        plt.legend()

    plt.savefig('comp_times_log.png', dpi=300, bbox_inches='tight')

def cost_bound_ablation(N=1000):
    batch_size = 100

    dim = 6

    plt.figure()
    timings = {"rejection": [],
               "box": [],
               "rejection_batch": [],
               "box_batch": [],
              }

    cbs = np.arange(4, 12)
    for cb in cbs:
        bounds = np.array([[-4, 4]]*dim)
        xs = np.array([-1]*dim)
        xf = np.array([1]*dim)
        #xf[0] = 1

        start = time.time()
        pts = rejection_sampling(bounds, xs, xf, cb, N)
        end = time.time()
        duration = end - start
        timings["rejection"].append(duration)
        print('no box', end - start)

        start = time.time()
        pts = batch_rejection_sampling(bounds, xs, xf, cb, N, batch_size)
        end = time.time()
        duration = end - start
        timings["rejection_batch"].append(duration)
        print('batch no box', end - start)

        start = time.time()
        pts = rejection_sampling_with_box(bounds, xs, xf, cb, N)
        end = time.time()
        duration = end - start
        timings["box"].append(duration)
        print('box:', end - start)

        start = time.time()
        pts = batch_rejection_sampling_with_box(bounds, xs, xf, cb, N, batch_size)
        end = time.time()
        duration = end - start
        timings["box_batch"].append(duration)
        print('batch box:', end - start)

    for k, e in timings.items():
        plt.semilogy(cbs, np.array(e)/N, label=k)
    plt.legend()

    plt.xlabel('c_b')
    plt.ylabel('t [s]')

    plt.savefig('cost_bound_ablation.png', dpi=300, bbox_inches='tight')

def test():
    cb = 5

    #xs = np.array([2, -1])
    #xf = np.array([-2, 1])
    #twod(xs, xf, cb)

    #xs = np.array([-1, -3])
    #xf = np.array([1, 3])
    #twod(xs, xf, cb)

    xs = np.array([0, 1])
    xf = np.array([2, -1])
    twod(xs, xf, 7)

    xs = np.array([1, 2])
    xf = np.array([-1, -2])
    twod(xs, xf, cb)

    threed()

if __name__ == "__main__":
    #initial_plot()
    #second_plot()
    #third_plot()

    #benchmark_times()
    cost_bound_ablation()

    plt.show()
