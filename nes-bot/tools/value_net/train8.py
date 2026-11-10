"""Train the MLP value net on rollout-averaged labels. Usage: train8.py OUT.npz *-lab.npz (env HID EPOCHS LR)"""
import os, sys, copy, numpy as np, torch, torch.nn as nn
HID = int(os.environ.get('HID', 128)); EPOCHS = int(os.environ.get('EPOCHS', 30)); LR = float(os.environ.get('LR', 1e-3))
torch.set_num_threads(4)
def inputs(bits):
    b = bits.reshape(-1, 20, 10).astype(np.float32)
    top = np.where(b.any(1), b.argmax(1), 20)
    return np.concatenate([b.reshape(-1, 200), (20-top).astype(np.float32)/20.], 1)
X, Y, blk = [], [], []
for f in sys.argv[2:]:
    z = np.load(f); bits = np.unpackbits(z['boards'], axis=1)[:, :200]
    X.append(inputs(bits)); Y.append(z['y']); blk.append(np.arange(len(z['y'])) // 1000 + 1000*len(blk))
X = torch.tensor(np.concatenate(X)); Y = torch.tensor(np.concatenate(Y), dtype=torch.float32); blk = np.concatenate(blk)
print('samples', len(Y), 'mean', round(Y.mean().item(), 3), 'std', round(Y.std().item(), 3), flush=True)
val = torch.tensor(blk % 10 == 0); tr = torch.nonzero(~val).squeeze(1)
net = nn.Sequential(nn.Linear(210, HID), nn.ReLU(), nn.Linear(HID, HID), nn.ReLU(), nn.Linear(HID, 1))
opt = torch.optim.Adam(net.parameters(), LR); sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, EPOCHS)
best, keep = float('inf'), None
for ep in range(EPOCHS):
    order = tr[torch.randperm(len(tr))]
    for i in range(0, len(order), 512):
        idx = order[i:i+512]; loss = ((net(X[idx]).squeeze(1)-Y[idx])**2).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    sched.step()
    with torch.no_grad(): mse = ((net(X[val]).squeeze(1)-Y[val])**2).mean().item()
    if mse < best: best, keep = mse, copy.deepcopy(net.state_dict())
    print(ep, 'val mse', round(mse, 4), 'R2', round(1-mse/Y[val].var().item(), 3), flush=True)
np.savez(sys.argv[1], **{n: keep[k].double().numpy() for n, k in (('W1','0.weight'),('b1','0.bias'),('W2','2.weight'),('b2','2.bias'),('W3','4.weight'),('b3','4.bias'))})
