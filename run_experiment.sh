#!/bin/bash
# I/O Scheduler Experiment - HDD + SSD (Virtual Disks)

HDD_DEV="sdb"
SSD_DEV="nvme0n1"
HDD_MOUNT="/mnt/test_hdd"
SSD_MOUNT="/mnt/test_ssd"
RUNTIME=30
SIZE="100M"
IODEPTH=32
BS="4k"
RUNS=3
RESULTS_DIR="$HOME/experiment_results"

mkdir -p $RESULTS_DIR/json

SCHEDULERS=("none" "mq-deadline")
WORKLOADS=("randread" "randwrite" "read" "randrw")

echo "=========================================="
echo "Starting Experiment: $(date)"
echo "HDD: /dev/$HDD_DEV  |  SSD: /dev/$SSD_DEV"
echo "=========================================="

run_test() {
    local DEV=$1
    local DEV_TYPE=$2
    local MOUNT=$3
    local SCHED=$4
    local WORKLOAD=$5
    local RUN=$6
    
    echo $SCHED | sudo tee /sys/block/$DEV/queue/scheduler > /dev/null 2>&1
    sudo sh -c "echo 3 > /proc/sys/vm/drop_caches"
    sleep 1
    
    local OUT="$RESULTS_DIR/json/${DEV_TYPE}_${SCHED}_${WORKLOAD}_run${RUN}.json"
    local RW_OPT="--rw=$WORKLOAD"
    if [ "$WORKLOAD" == "randrw" ]; then
        RW_OPT="--rw=randrw --rwmixread=70"
    fi
    
    echo "[$DEV_TYPE] $SCHED / $WORKLOAD / run $RUN"
    
    sudo fio --name=${DEV_TYPE}_${SCHED}_${WORKLOAD}_run${RUN} \
        --ioengine=libaio --direct=1 --bs=$BS --iodepth=$IODEPTH \
        --size=$SIZE --runtime=$RUNTIME --time_based --percentile_list=99 \
        --filename=$MOUNT/testfile $RW_OPT \
        --output-format=json --output=$OUT 2>&1 | tail -1
}

for SCHED in "${SCHEDULERS[@]}"; do
    for WORKLOAD in "${WORKLOADS[@]}"; do
        for RUN in $(seq 1 $RUNS); do
            run_test "$HDD_DEV" "HDD" "$HDD_MOUNT" "$SCHED" "$WORKLOAD" "$RUN"
            run_test "$SSD_DEV" "SSD" "$SSD_MOUNT" "$SCHED" "$WORKLOAD" "$RUN"
        done
    done
done

echo "=========================================="
echo "Experiment Complete: $(date)"
echo "Results: $RESULTS_DIR/json"
echo "=========================================="
