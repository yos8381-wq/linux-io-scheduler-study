import os, json, csv, glob, statistics

RESULTS_DIR = os.path.expanduser('~/experiment_results/json')
OUTPUT_CSV = os.path.expanduser('~/experiment_summary.csv')

json_files = glob.glob(os.path.join(RESULTS_DIR, "*.json"))
data_by_config = {}

def get_p99(lat_ns_dict):
    try:
        pct = lat_ns_dict.get('percentile', {})
        if not pct:
            return 0
        for k in pct.keys():
            if k.startswith('99'):
                return pct[k]
        return 0
    except:
        return 0

for file_path in json_files:
    filename = os.path.basename(file_path).replace('.json', '')
    parts = filename.split('_')
    if len(parts) >= 4:
        dev_type = parts[0]
        sched = parts[1]
        workload = parts[2]
        key = (dev_type, sched, workload)
        try:
            with open(file_path, 'r') as f:
                res = json.load(f)
                job = res['jobs'][0]
                if workload in ['randread', 'read']:
                    iops = job['read']['iops']
                    bw = job['read']['bw']
                    lat_mean = job['read']['lat_ns']['mean'] / 1e6
                    lat_p99 = get_p99(job['read']['lat_ns']) / 1e6
                elif workload == 'randwrite':
                    iops = job['write']['iops']
                    bw = job['write']['bw']
                    lat_mean = job['write']['lat_ns']['mean'] / 1e6
                    lat_p99 = get_p99(job['write']['lat_ns']) / 1e6
                else:
                    iops = job['read']['iops'] + job['write']['iops']
                    bw = job['read']['bw'] + job['write']['bw']
                    lat_mean = (job['read']['lat_ns']['mean'] + job['write']['lat_ns']['mean']) / 2 / 1e6
                    lat_p99 = max(get_p99(job['read']['lat_ns']), get_p99(job['write']['lat_ns'])) / 1e6
                if key not in data_by_config:
                    data_by_config[key] = []
                data_by_config[key].append({
                    'IOPS': iops, 'Throughput_MBs': bw / 1024.0,
                    'Mean_Latency_ms': lat_mean, 'p99_Latency_ms': lat_p99
                })
        except Exception as e:
            pass

final_data = []
for (dev, sched, workload), runs in data_by_config.items():
    iops_values = [r['IOPS'] for r in runs]
    bw_values = [r['Throughput_MBs'] for r in runs]
    lat_values = [r['Mean_Latency_ms'] for r in runs]
    p99_values = [r['p99_Latency_ms'] for r in runs]
    final_data.append({
        'Device': dev, 'Scheduler': sched, 'Workload': workload, 'Runs': len(runs),
        'IOPS_median': round(statistics.median(iops_values), 2),
        'Throughput_MBs_median': round(statistics.median(bw_values), 2),
        'Mean_Latency_ms_median': round(statistics.median(lat_values), 3),
        'p99_Latency_ms_median': round(statistics.median(p99_values), 3),
    })

final_data.sort(key=lambda x: (x['Device'], x['Scheduler'], x['Workload']))

with open(OUTPUT_CSV, 'w', newline='') as f:
    fieldnames = ['Device', 'Scheduler', 'Workload', 'Runs', 'IOPS_median',
                  'Throughput_MBs_median', 'Mean_Latency_ms_median', 'p99_Latency_ms_median']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(final_data)

print(f"Summary: {OUTPUT_CSV}\n")
print("=" * 110)
print(f"{'Device':8} | {'Scheduler':15} | {'Workload':12} | {'IOPS':>10} | {'Throughput':>12} | {'Lat(ms)':>10} | {'p99(ms)':>10}")
print("=" * 110)
for row in final_data:
    print(f"{row['Device']:8} | {row['Scheduler']:15} | {row['Workload']:12} | "
          f"{row['IOPS_median']:>10} | {row['Throughput_MBs_median']:>12} | "
          f"{row['Mean_Latency_ms_median']:>10} | {row['p99_Latency_ms_median']:>10}")
print("=" * 110)

