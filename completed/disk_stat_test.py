# Simple script to gather some data about a disk to verify it's seen by the OS
# and is properly represented.  Defaults to sda if not passed a disk at run time

from pathlib import Path
import argparse
import subprocess
import time

ERROR = 1
OK = 0

parser = argparse.ArgumentParser(prog="disk_stat_test")
parser.add_argument("-d", "--disk")
args = parser.parse_args()
if args.disk:
    DISK = args.disk
else:
    DISK = "sda"

STATUS = 0


def error_msg(code, msg, items=[]):
    global STATUS
    if code != OK:
        print(f"ERROR: retval {code} : {msg}")
        if STATUS == OK:
            STATUS = code

        for item in items:
            print("output: ", item)


nvdimm = "pmem"
if nvdimm in DISK:
    print(f"Disk {DISK} appears to be an NVDIMM, skipping")
    exit(STATUS)

# Check /proc/partitions, exit with fail if disk isn't found
p = Path("/proc/partitions")
if DISK not in p.read_text():
    error_msg(ERROR, f"Disk {DISK} not found in /proc/partitions")

# Next, check /proc/diskstats
diskstats_p = Path("/proc/diskstats")
if DISK not in diskstats_p.read_text():
    error_msg(ERROR, f"Disk {DISK} not found in /proc/diskstats")
else:
    # Get some baseline stats for use later
    PROC_STAT_BEGIN = [
        line for line in diskstats_p.read_text().splitlines() if DISK in line
    ]

# Verify the disk shows up in /sys/block/
p = Path(f"/sys/block/{DISK}")
if not p.exists():
    error_msg(ERROR, f"Disk {DISK} not found in /sys/block")

# Verify there are stats in /sys/block/$DISK/stat
stat_p = Path(f"/sys/block/{DISK}/stat")
if not stat_p.exists() or stat_p.stat().st_size == 0:
    error_msg(ERROR, f"stat is either empty or nonexistant in /sys/block/{DISK}/")
else:
    # Get some baseline stats for use later
    SYS_STAT_BEGIN = stat_p.read_text()

# Generate some disk activity using hdparm -t
command = ["hdparm", "-t", f"/dev/{DISK}"]
result = subprocess.run(command)

# Sleep 5 to let the stats files catch up
time.sleep(5.0)

# Make sure the stats have changed:
PROC_STAT_END = [line for line in diskstats_p.read_text().splitlines() if DISK in line]
SYS_STAT_END = stat_p.read_text()

if PROC_STAT_BEGIN == PROC_STAT_END:
    error_msg(
        ERROR, "Stats in /proc/diskstats did not change", [PROC_STAT_BEGIN, PROC_STAT_END]
    )

if SYS_STAT_BEGIN == SYS_STAT_END:
    error_msg(
        ERROR,
        f"Stats in /sys/block/{DISK}/stat did not change",
        [SYS_STAT_BEGIN, SYS_STAT_END],
    )

if STATUS == 0:
    print(f"PASS: Finished testing stats for {DISK}")

exit(STATUS)
