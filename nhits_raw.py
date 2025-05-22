import gaps_online as go
import numpy as np
from tqdm import tqdm
from pathlib import Path
import io
import go_pybindings as gop
from glob import glob
import argparse
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(prog = 'get RB moni', description = 'get and extract info from RBMoniData in .tof.gaps files')
parser.add_argument('path')

args = parser.parse_args()

run_path = Path(args.path)
files = np.array([str(f) for f in ((run_path.glob('*.tof.gaps')))])
f_nums = [int(file.split('.')[0].split('_')[-1]) for file in files]
files = files[np.argsort(f_nums)]

n_hits = []
for f in tqdm(files):
    reader = go.io.TofPacketReader(str(f))
    for pack in reader: 
        tof_packet = go.io.TofPacket()
        tof_packet.from_bytestream(pack.payload, 0)
        n_hits_one_event = int(len(tof_packet.hits))
        n_hits.append(n_hits_one_event)


plt.figure()
plt.hist(n_hits)
plt.show()

