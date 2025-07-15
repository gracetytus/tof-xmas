import gaps-onlnine as go
from tqdm import tqdm
from pathlib import Path
import go_pybindings as gop
from glob import glob
import argparse
import numpy as np


def count_missing_entries(sorted_list):
    missing_count = 0
    for i in range(1, len(sorted_list)):
        diff = sorted_list[i] - sorted_list[i - 1]
        if diff > 1:
            missing_count += diff - 1
    return missing_count

parser = argparse.ArgumentParser(prog = 'compare number of evt. ids in raw .tof.gaps files with number of evt. ids in binary files')
parser.add_argument('-rd', '--raw_dir', default='', help = 'path to .tof.gaps files')
parser.add_argument('-bd', '--binary_dir', default = '', help = 'path to binary files that are telemetered from FCU')
parser.add_argument('-s', '--start_time', default = -1, help = 'start time for binary search')
parser.add_argument('-e', '--end_time', default = -1, help = 'end time for binary search')
parser.add_argyment('-id', '--run_id', default = 0, help = 'the run id being compared')

args = parser.parse_args()

if __name__ == '__main__':
    binary_event_ids = []
    binary_files = go.io.get_telemetry_binaries(args.start_time, args.end_time, data_dir=args.binary_dir)
    for f in tqdm(binary_files, desc = 'reading binary files'):
        treader = go.io.TelemetryPacketReader(str(f))
        for pack in treader:
            if int(pack.header.packet_type) in [90, 190, 191]:
                binary_ev = go.events.MergedEvent()
                binary_ev.from_telemetrypacket(pack)
                binary_evt_id = binary_ev.tof.event_id
                binary_event_ids.append(binary_evt_id)

    
    tof_event_ids = []
    tof_run_path = Path(args.raw_dir)
    tof_files = np.array([str(f) for f in ((run_path.glob('*.tof.gaps')))])
    tof_f_nums = [int(file.split('.')[0].split('_')[-1]) for file in tof_files]
    tof_files = tof_files[np.argsort(tof_f_nums)]

    for f in tqdm(tof_files, desc = 'reading raw .tof.gaps files'):
        reader = go.io.TofPacketReader(str(f), filter = go.io.TofPacketType.TofEvent)
        for pack in reader: 
            tof_ev = go.events.TofEvent()
            tof_ev.from_tofpacket.pack()
            tof_event_id = tof_ev.event_id
            tof_event_ids.append(tof_event_id)

    binary_event_ids.sort()
    tof_event_ids.sort()

    num_binary_events = len(binary_event_ids)
    num_tof_events = len(tof_event_ids)
    
    num_missing_binary_events = count_missing_entries(binary_event_ids)
    num_missing_tof_events = count_missing_entries(tof_event_ids)

    print(f'Run {args.run_id}: \n')
    print(f'{num_binary_events} binary events found (processed by FCU) \n')
    print(f'{num_tof_events} tof events found (stored on TOFCPU) \n')
    print(f'After sorting, {num_missing_binary_events} binary events are not found and {num_missing_tof_events} tof events are not found')



