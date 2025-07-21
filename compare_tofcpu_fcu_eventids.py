import gaps_online as go
from tqdm import tqdm
from pathlib import Path
import go_pybindings as gop
from glob import glob
import argparse
import numpy as np
import matplotlib.pyplot as plt


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
parser.add_argument('-s', '--start_time', type = int, default = -1, help = 'start time for binary search')
parser.add_argument('-e', '--end_time', type = int, default = -1, help = 'end time for binary search')
parser.add_argument('-id', '--run_id', default = 0, help = 'the run id being compared')

args = parser.parse_args()

if __name__ == '__main__':
    binary_event_ids = []
    binary_event_ids_no_tof = []
    boring_event_ids = []
    interesting_event_ids = []
    track_trig_event_ids = []
    evts_no_trkr_hits = 0
    binary_files = go.io.get_telemetry_binaries(args.start_time, args.end_time, data_dir=args.binary_dir)
    for f in tqdm(binary_files, desc = 'reading binary files'):
        treader = go.io.TelemetryPacketReader(str(f))
        for pack in treader:
            if int(pack.header.packet_type) in [90, 190, 191]:
                binary_ev = go.events.MergedEvent()
                binary_ev.from_telemetrypacket(pack)
                binary_evt_id = binary_ev.tof.event_id
                binary_event_ids.append(binary_evt_id)
                tracker_hits = len(binary_ev.tracker_v2)
                if tracker_hits == 0: evts_no_trkr_hits +=1 
                if int(pack.header.packet_type) == 90:
                    boring_event_ids.append(binary_evt_id)
                elif int(pack.header.packet_type) == 190:
                    interesting_event_ids.append(binary_evt_id)
                elif int(pack.header.packet_type) == 191:
                    track_trig_event_ids.append(binary_evt_id)

            if int(pack.header.packet_type) == 192:
                binary_ev_no_tof = go.events.MergedEvent()
                binary_ev_no_tof.from_telemetrypacket(pack)
                binary_evt_id_no_tof = binary_ev_no_tof.event_id
                binary_event_ids_no_tof.append(binary_evt_id_no_tof)

    print(evts_no_trkr_hits)
    tof_event_ids = []
    tof_run_path = Path(args.raw_dir)
    tof_files = np.array([str(f) for f in ((tof_run_path.glob('*.tof.gaps')))])
    tof_f_nums = [int(file.split('.')[0].split('_')[-1]) for file in tof_files]
    tof_files = tof_files[np.argsort(tof_f_nums)]

    for f in tqdm(tof_files, desc = 'reading raw .tof.gaps files'):
        reader = go.io.TofPacketReader(str(f), filter = go.io.TofPacketType.TofEvent)
        for pack in reader: 
            tof_ev = go.events.TofEvent()
            tof_ev.from_tofpacket(pack)
            tof_event_id = tof_ev.event_id
            tof_event_ids.append(tof_event_id)

    binary_event_ids.sort()
    binary_event_ids_no_tof.sort() 
    tof_event_ids.sort()
    
    num_binary_events = len(binary_event_ids)
    num_tof_events = len(tof_event_ids)
    num_binary_events_no_tof = len(binary_event_ids_no_tof)
    num_interesting_events = len(interesting_event_ids)
    num_boring_events = len(boring_event_ids)
    num_track_trig_events = len(track_trig_event_ids)

    num_missing_binary_events = count_missing_entries(binary_event_ids)
    num_missing_tof_events = count_missing_entries(tof_event_ids)

    set_binary_event_ids_no_tof = set(binary_event_ids_no_tof)
    set_tof_event_ids = set(tof_event_ids)
    set_interesting_events = set(interesting_event_ids)
    set_boring_events = set(boring_event_ids)
    set_track_trig_events = set(track_trig_event_ids)
    set_binary_event_ids = set(binary_event_ids)

    intersection = set_binary_event_ids_no_tof & set_tof_event_ids
    count_in_both = len(intersection)

    only_in_tof_data = set_tof_event_ids - set_binary_event_ids
    count_tof_only = len(only_in_tof_data)
    
    intersect_interesting_evt_w_tof = set_interesting_events & set_tof_event_ids
    intersect_boring_evt_w_tof = set_boring_events & set_tof_event_ids
    intersect_track_evt_w_tof = set_track_trig_events & set_tof_event_ids
    
    percent_interesting_evts_in_tof = (len(intersect_interesting_evt_w_tof) / num_interesting_events) * 100
    percent_boring_evts_in_tof = (len(intersect_boring_evt_w_tof) / num_boring_events) * 100
    percent_track_evts_in_tof = (len(intersect_track_evt_w_tof) / num_track_trig_events) * 100

    only_in_boring_bin = set_boring_events - set_tof_event_ids
    only_in_track_bin = set_track_trig_events - set_tof_event_ids

    print(f'Run {args.run_id}: \n')
    print(f'{num_binary_events} binary events found (processed by FCU)')
    print(f'{num_tof_events} tof events found (stored on TOFCPU)')
    print(f'After sorting, {num_missing_binary_events} binary events are not found and {num_missing_tof_events} tof events are not found \n')
    print(f'{count_in_both} MergedEvents with no TOF data (packet 192) BUT event id exists on TOFCPU')
    print(f'{count_tof_only} events which occur only on the TOFCPU and are not contained in ANY MergedEvent')

    print(f'{percent_interesting_evts_in_tof}% interesting events from binaries present on TOFCPU')
    print(f'{percent_boring_evts_in_tof}% boring events from binaries present on TOFCPU')
    #print(f'event ids missing from tof are:  {only_in_boring_bin}')
    print(f'{percent_track_evts_in_tof}% track trigger only events from binaries present on TOFCPU')
    #print(f'event ids missing from tof are: {only_in_track_bin}')
    
    print(len(only_in_tof_data))
    list_tof_only = list(only_in_tof_data)
    list_tof_only.sort()
    np.savetxt('tof_only_event_ids.txt', list_tof_only, fmt='%d')

    #plt.plot(list_tof_only)
    #plt.savefig('tof_only_event_ids.pdf')
