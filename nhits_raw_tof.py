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
    reader = go.io.TofPacketReader(str(f), filter = go.io.TofPacketType.TofEvent)
    #if you don't include the filter, will need something like:
    # if pack.packet_type == TofEvent()
    # after the 'for pack in reader ...event.from_tofpacket'
    for pack in reader: 
        event = go.events.TofEvent()
        event.from_tofpacket(pack)
        
        hits = len(event.hits)
        n_hits.append(hits)



plt.figure()
plt.hist(n_hits, histtype = 'step', bins = 50)
plt.title('n hits per event for .tof.gaps data')
plt.ylabel('multiplicity')
plt.xlabel('number of hits')
plt.minorticks_on()
plt.xlim(0, 100)
plt.set_yscale('log')
plt.savefig('nhits_tof_data.pdf')

