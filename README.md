# Linux I/O Scheduler Performance Analysis
## Does Scheduling Still Matter? A Comparative Study on HDD and SSD

### Overview
This repository contains the full experimental artifacts for a graduate-level research study comparing Linux I/O schedulers (`none` and `mq-deadline`) on HDD and SSD virtual disks within a virtualized environment.

### Research Questions
1. How do `none` and `mq-deadline` schedulers affect throughput (IOPS) in a virtualized Linux environment?
2. What is the impact on mean latency and throughput under random and mixed workloads?
3. How do queueing theory principles (Little's Law) explain the observed performance?

### Experimental Setup
- **Hypervisor**: Oracle VirtualBox 7.0
- **Guest OS**: Ubuntu 20.04.1 LTS (Mininet-VM)
- **Kernel**: 5.4.0-42-generic
- **Test Disks**:
  - SATA VDI (10 GB) - HDD (rotational=1)
  - NVMe VDI (25 GB) - SSD (rotational=0)
- **Benchmark Tool**: fio 3.16
- **Queue Depth**: 32
- **Block Size**: 4 KB

### Key Results
| Device | Scheduler | Workload | IOPS | Latency (ms) |
|--------|-----------|----------|------|--------------|
| SSD | none | randread | 16547.84 | 1.85 |
| HDD | none | randread | 9811.68 | 3.10 |

### Limitations
- Virtualized environment (not physical HDD/SSD)
- p99 not available in fio 3.16

### Author
Majed Al-Dahaq - Supervised by Dr. Wedad Al-Sorory
