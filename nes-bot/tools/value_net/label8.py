"""Rollout-averaged value labels: for each board, K greedy rollouts of H placements on random NES piece
sequences; label = mean discounted points (tetris = 1.0, gamma G), death = -D.
Usage: label.py IN.npz OUT.npz  (IN has 'boards' packed (n,25); env K H G D BELOW WFILE WORKERS)"""
import os, sys, json, multiprocessing as mp, numpy as np
NES = os.environ.get('NESBOT', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')); sys.path.insert(0, NES)
from nes_original import sim
from numba import njit
K = int(os.environ.get('K', 16)); H = int(os.environ.get('H', 60)); G = float(os.environ.get('G', .98)); D = float(os.environ.get('D', 10))
BELOW = int(os.environ.get('BELOW', 9))
W = json.load(open(os.environ.get('WFILE', NES+'/nes_original/weights/tetris-playout12-b9-vnet-ff-start.json')))
ALT = sim.pad_weights(W['alt_weights']); BURN = sim.pad_weights(W['burn_weights'])
R = np.array([0, 40, 100, 300, 1200]) / 1200.

@njit(cache=True)
def rollout(board0, seed, K, H, G, D, below, alt, burn, R):
    np.random.seed(seed)
    states = np.zeros((sim.MAX_CANDIDATES, 9), np.int64); scratch = np.zeros(sim.N_FEATURES)
    total = 0.
    for k in range(K):
        st = np.random.randint(1, 65535); cnt = 0; last = 0
        board = board0.copy(); das = 0; acc = 0.; disc = 1.
        for t in range(H):
            for _ in range(30 + np.random.randint(0, 20)): st = sim._lfsr(st)
            st, cnt, p = sim._draw(st, cnt, last); last = p
            rows = 0
            for r in range(20):
                if board[r].any():
                    rows = 20 - r; break
            if rows <= below: w = alt; well = 9
            else: w = burn; well = -1
            before = board.sum()
            nb, das, dead, v, part = sim._greedy(board, p, das, 29, 2, 0, well, w, states, scratch)
            if dead:
                acc += disc * (-D); break
            c = (before + 4 - nb.sum()) // 10
            acc += disc * R[c]; disc *= G; board = nb
        total += acc
    return total / K

def work(args):
    bits, s0 = args
    out = np.zeros(len(bits))
    for i in range(len(bits)):
        b = np.unpackbits(bits[i])[:200].reshape(20, 10).astype(np.bool_)
        out[i] = rollout(b, s0 + i, K, H, G, D, BELOW, ALT, BURN, R)
    return out

if __name__ == '__main__':
    z = np.load(sys.argv[1]); B = z['boards']; n = len(B); step = 2000
    jobs = [(B[i:i+step], 1000003 * (i // step + 1) + 7) for i in range(0, n, step)]
    with mp.get_context('spawn').Pool(int(os.environ.get('WORKERS', 4))) as pool:
        ys = []
        for j, y in enumerate(pool.imap(work, jobs)):
            ys.append(y); print(j, len(jobs), round(float(y.mean()), 3), flush=True)
    np.savez_compressed(sys.argv[2], boards=B, y=np.concatenate(ys))
