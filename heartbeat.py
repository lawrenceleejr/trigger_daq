import os
import subprocess
import sys
import time

def main():

    ops = options()
    if not os.path.isfile(ops.f):
        fatal("%s does not exist" % (ops.f))

    print
    print " Input     :: %s" % (ops.f)
    print " Output    :: %s" % ("heartbeat.pdf")
    print " Sleeptime :: %s" % (ops.s)
    print " N(lines)  :: %s" % (ops.l)
    print
    print " Slam Ctrl+C to exit."
    print

    lines_to_parse = "-n %s" % (ops.l)
    sleeptime      = int(ops.s)
    fin            = ops.f

    fname = "heartbeat.dat"
    fout  = open(fname, "w")
    start = time.time()

    nparse = 0
    while True:

        cmd = "tail"
        popen = subprocess.Popen([cmd, lines_to_parse, fin],
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        lines, errors = popen.communicate()
        lines = lines.split("\n")

        lines_time = filter(lambda line: "TIME" in line,        lines)
        lines_trig = filter(lambda line: line.startswith("A3"), lines)
        if len(lines_time) < 2:
            continue

        line_earl = lines_time[0] .strip()
        line_late = lines_time[-1].strip()

        _, timelo = line_earl.split()
        _, timehi = line_late.split()
        timelo = float(timelo)/pow(10, 9) - start
        timehi = float(timehi)/pow(10, 9) - start
        rate = len(lines_trig) / (float(timehi) - float(timelo))

        days = 60*60*24
        fout.write("%s %s %s\n" % (timelo/days, timehi/days, rate))
        fout.flush()

        os.system("root -l -q -b heartbeat.C > /dev/null")
        nparse += 1
        time.sleep(sleeptime)

def options():
    import argparse
    parser = argparse.ArgumentParser(usage=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    mmtp = "/data/mm_2016/work/mmtp_test_22.dat"
    parser.add_argument("-s", default="60",   help="Sleep time between measurements")
    parser.add_argument("-f", default=mmtp,   help="Raw FIT file to read")
    parser.add_argument("-l", default="1000", help="Number of lines to read")
    return parser.parse_args()

def fatal(msg):
    sys.exit("Fatal error: %s" % msg)

if __name__ == "__main__":
    main()
