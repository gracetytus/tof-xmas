import gaps_online as go
from tqdm import tqdm
from pathlib import Path
import go_pybindings as gop
from glob import glob
import argparse
import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(prog = 'compare number of hits for event ids identified to exist in binary files but not on tofcpu')
parser.add_argument('-bd', '--binary_dir', default = '', help = 'path to binary files that are telemetered from FCU')
parser.add_argument('-s', '--start_time', type=int, default = -1, help = 'start time for binary search')
parser.add_argument('-e', '--end_time', type=int, default = -1, help = 'end time for binary search')
parser.add_argument('-id', '--run_id', default = 0, help = 'the run id being compared')

args = parser.parse_args()

if __name__ == '__main__':
    suspicious_evt_ids = [208033, 208481, 208762, 208581, 207880, 209453, 207727, 207316, 207799, 207897, 208474, 207614]
    suspicious_evt_ids.sort()
    suspicious_evt_nhits = []
    binary_files = go.io.get_telemetry_binaries(args.start_time, args.end_time, data_dir=args.binary_dir)
    for f in tqdm(binary_files, desc = 'reading binary files'):
        treader = go.io.TelemetryPacketReader(str(f))
        for pack in treader:
            if int(pack.header.packet_type) in [90, 190, 191]:
                packet_type = int(pack.header.packet_type)
                binary_ev = go.events.MergedEvent()
                binary_ev.from_telemetrypacket(pack)
                binary_evt_id = binary_ev.event_id
                if binary_evt_id in suspicious_evt_ids:
                    tof_hits = binary_ev.tof.hits
                    n_hits = len(tof_hits)
                    suspicious_evt_nhits.append((packet_type, binary_evt_id, n_hits))
                else: continue
    suspicious_evt_nhits.sort(key=lambda x: x[1])
    output_filename = f'run_{args.run_id}_suspicious_events.txt'
    with open(output_filename, 'w') as f:
        print(f'Run {args.run_id}', file=f)
        for i in range(len(suspicious_evt_nhits)):
            print(f'Event {suspicious_evt_nhits[i][1]} of packet type {suspicious_evt_nhits[i][0]} has {suspicious_evt_nhits[i][2]} hits', file=f)
    
    hits_only = [entry[2] for entry in suspicious_evt_nhits]
    plt.hist(hits_only)
    plt.xlim((-5, 5))
    plt.savefig('nhits_missing_tof_evts.pdf')
