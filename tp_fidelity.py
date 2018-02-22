"""

tp_fidelity.py -- a script to test self-consistency of the TP output.

1. Check if fitted slope matches offline slope.
2. Check if fit satisfies the occupancy requirements.
3. Check if all hits in the fit are in the GBT.
4. Check if the fit is missing any hits which should be there (IN PROGRESS. PRETTY HARD.)

run like:
> python tp_fidelity.py --fit fit.decode.dat --gbt gbt.decode.dat [ --ignore-slope ]

"""

lines_gbt_packet = 151
lines_fit_packet = 12

# VVUUXXXX
boardmap = [5, 3, 4, 2, 7, 6, 1, 0]

import os
import sys
verbose = "verbose" in sys.argv

pitch = 0.4
zboard = {0: 0.0, 1: 11.2, 6: 146.0, 7: 157.2} # mm
roadsize = 64

def main():

    ops = options()
    fname_gbt = ops.gbt
    fname_fit = ops.fit

    if not os.path.isfile(fname_gbt):
        fatal("Please provide --gbt decoded dat filename which exists. You gave: %s" % (fname_gbt))
    if not os.path.isfile(fname_fit):
        fatal("Please provide --fit decoded dat filename which exists. You gave: %s" % (fname_fit))

    # this is slow af with hella events
    # try making this less horrible
    lines_gbt = open(fname_gbt).readlines()
    lines_fit = open(fname_fit).readlines()

    gbtpks = parse_gbt(lines_gbt)
    fitpks = parse_fit(lines_fit)

    # first, check slopes and occupancy
    badslope = 0
    badoccup = 0
    for fitpk in fitpks:

        mxl_offline = fitpk.mxl_offline()

        if mxl_offline != fitpk.mxl and not ops.ignore_slope:
            if abs(int(mxl_offline, base=16) - int(fitpk.mxl, base=16)) == 1:
                # off by 1: probably just rounding
                pass
            else:
                badslope += 1
                print "Warning: fitter online slope doesnt match offline slope."
                print " - Fit number : %i" % (fitpks.index(fitpk))
                for (bo, vmm, ch) in fitpk.hits:
                    print " - Fit hit: %1s %1s %2s" % (bo, vmm, ch)
                print " - fitter  slope: %s" % (fitpk.mxl)
                print " - offline slope: %s" % (mxl_offline)

        if fitpk.nx() < 2 or fitpk.nu() + fitpk.nv() < 2:
            badoccup += 1
            print "Warning: fitter fails the occupancy requirements."
            print " - Fit number : %i" % (fitpks.index(fitpk))
            for (bo, vmm, ch) in fitpk.hits:
                print " - Fit hit: %1s %1s %2s" % (bo, vmm, ch)
            print " - NX: %s" % (fitpk.nx())
            print " - NU: %s" % (fitpk.nu())
            print " - NV: %s" % (fitpk.nv())


    # second, compare with GBT
    badfitter = 0
    for gbtpk in gbtpks:

        fits = []
        for fitpk in fitpks:
            if abs(fitpk.time - gbtpk.time) < 0.1 and fitpk.bcid in gbtpk.bcidsB:
                fits.append(fitpk)

        # first, check if there are any hits in the fit which arent in the GBT
        for fitpk in fits:
            if any([(bo, vmm, ch) not in gbtpk.hits and (vmm, ch) != (0, 0) for (bo, vmm, ch) in fitpk.hits]):
                badfitter += 1
                print
                print "GBT %i @ %s, BCIDs = %s..." % (gbtpks.index(gbtpk), gbtpk.time, 
                                                      " ".join([format(bc, "04X") for bc in gbtpk.bcidsB[:6]]))
                for hit in gbtpk.hits:
                    bo, vmm, ch = hit
                    print "%2s %3s %3s" % (bo, vmm, ch)
                print "FIT %i, BCID = %s" % (fitpks.index(fitpk), format(fitpk.bcid, "04X"))
                for hit in fitpk.hits:
                    bo, vmm, ch = hit
                    msg = "" if hit in gbtpk.hits or (vmm, ch) == (0, 0) else "<-- Not in GBT!"
                    print "%2s %3s %3s %s" % (bo, vmm, ch, msg)

        # second, check if there are hits in the GBT which should be used in the fit
        # actually, this gets pretty confusing. skip it for now.
        # used = {}
        # for hit in gbtpk.hits:
        #     global_strip = tp_strip(hit)
        #     road = int(global_strip) / int(roadsize)
        #     prob_noise = all([road not in fitpk.evaluate_roads() for fitpk in fits])
        #     gets_used  = any([hit in fitpk.hits for fitpk in fits])
        #     used[hit]  = gets_used or prob_noise
        # if not all(used.values()):
        #     print
        #     print "GBT %i" % (gbtpks.index(gbtpk))
        #     for hit in gbtpk.hits:
        #         bo, vmm, ch = hit
        #         msg = "" if used[hit] else "<-- Not in triggers!"
        #         print "%2s %3s %3s %s" % (bo, vmm, ch, msg)
        #     for fitpk in fits:
        #         print "FIT %i" % (fitpks.index(fitpk))
        #         for (bo, vmm, ch) in fitpk.hits:
        #             print "%2s %3s %3s" % (bo, vmm, ch)

    print
    print "  Found %i triggers and %i GBT packets" % (len(fitpks), len(gbtpks))
    print
    print "  %s%5i%s triggers have mismatched slope"       % (color.RED+color.BOLD, badslope,  color.END)
    print "  %s%5i%s triggers have low occupancy"          % (color.RED+color.BOLD, badoccup,  color.END)
    print "  %s%5i%s triggers have hits not in GBT packet" % (color.RED+color.BOLD, badfitter, color.END)
    print
    print "  Done! %s>^.^<%s" % (color.BLUE+color.BOLD, color.END)
    print
            

def parse_gbt(lines_gbt):

    packets = []

    for (il, lgbt) in enumerate(lines_gbt):
        
        if not "Event" in lgbt:
            continue

        _, _, _, time_s, _, time_ns = lgbt.split()

        time = float(time_s) + float(time_ns)/pow(10, 9)

        gbtpk = GBTPacket(time)

        lpks = lines_gbt[il+1 : il+lines_gbt_packet]

        for (ilpk, lpk) in enumerate(lpks):
            lpk = lpk.split()
            if any([tag in "".join(lpk) for tag in ["Event"]]):
                continue
            if "BCID:" in lpk:
                bcid = lpk[1]
                if len(gbtpk.bcidsA) == len(gbtpk.bcidsB):
                    gbtpk.bcidsA.append(int(bcid))
                else:
                    gbtpk.bcidsB.append(int(bcid))
                continue
            if len(lpk) == 1:
                continue
            # 0-4: ADDC1
            # 5-9: ADDC2
            add4 = (ilpk % 10)/5 == 0
            gbtpk.add(lpk, add4)

        if verbose:
            for hit in gbtpk.hits:
                print "gbt", len(packets), hit

        gbtpk.pad()
        packets.append(gbtpk)

    return packets

def parse_fit(lines_fit):

    packets = []

    for il,lfit in enumerate(lines_fit):

        if not "Event" in lfit:
            continue
        _, _, _, time_s, _, time_ns = lfit.split()

        time = float(time_s) + float(time_ns)/pow(10, 9)

        fitpk = FitPacket(time)

        lpks = lines_fit[il+1 : il+lines_fit_packet]
        for lpk in lpks:
            lpk = lpk.split()
            if any([tag in "".join(lpk) for tag in ["cntr"]]):
                continue
            if "BCID:" in lpk:
                fitpk.header = lpk[0]
                fitpk.bcid = int(lpk[2])
                continue
            if "mx_local" in lpk:
                fitpk.mxl = lpk[1]
                continue
            fitpk.add(lpk)

        if verbose:
            for hit in fitpk.hits:
                print "fit", len(packets), hit

        packets.append(fitpk)

    return packets

class GBTPacket(object):
    def __init__(self, time):
        self.time  = time
        self.hits  = []
        self.bcidsA = []
        self.bcidsB = []

    def add(self, tup, add4):
        bo, vmm_chs = tup[0], tup[1:]
        if add4:
            bo = int(bo)+4
        for vmm_ch in vmm_chs:
            vmm,ch = vmm_ch.split(",")
            self.hits.append((int(bo), int(vmm), int(ch)))
        self.hits.sort()

    def pad(self):
        for ibo in xrange(8):
            if not any([ibo==bo for (bo, vmm, ch) in self.hits]):
                self.hits.append((ibo, 0, 0))
        self.hits.sort()

class FitPacket(object):
    def __init__(self, time):
        self.time     = time
        self.hits     = []
        self.bcid     = None
        self.mxl      = None
        self.header   = None

    def add(self, tup):
        vmm, ch = tup
        self.hits.append((boardmap[len(self.hits)], int(vmm), int(ch)))
        self.hits.sort()

    def nx(self):
        return sum([bo in [0, 1, 6, 7] and (vmm,ch) != (0,0) for (bo, vmm, ch) in self.hits])

    def nu(self):
        return sum([bo in [2, 4]       and (vmm,ch) != (0,0) for (bo, vmm, ch) in self.hits])

    def nv(self):
        return sum([bo in [3, 5]       and (vmm,ch) != (0,0) for (bo, vmm, ch) in self.hits])

    def mxl_offline(self):
        # collect hits
        xs, zs = [], []
        for (bo, vmm, ch) in self.hits:

            if not bo in [0, 1, 6, 7]:
                continue
            if (vmm, ch) == (0, 0):
                continue

            # convert to global strip number
            vmm_ch = tp_strip([bo, vmm, ch])
            vmm_ch = vmm_ch * pitch
            xs.append(vmm_ch)
            zs.append(zboard[bo])

        # calculate slope
        mxl_offline = slope(xs, zs)
        mxl_offline = int(mxl_offline*pow(2, 14))
        if mxl_offline < 0:
            mxl_offline += pow(2, 16)
        mxl_offline = format(mxl_offline, "04X")
        return mxl_offline
        
    def evaluate_roads(self):
        """ In testing. """
        roads = []

        roads_satisfied = {}
        for bo in xrange(8):
            roads_satisfied[bo] = []

        for (bo, vmm, ch) in self.hits:
            if (vmm, ch) == (0, 0):
                continue
            global_strip = tp_strip((bo, vmm, ch))
            road = int(global_strip) / int(roadsize)
            roads_satisfied[bo].append(road)
            roads_satisfied[bo].append(road+1)
            roads_satisfied[bo].append(road-1)
            
        roads_hit = []
        for key in roads_satisfied:
            roads_hit.extend(roads_satisfied[key])
        roads_hit = sorted(list(set(roads_hit)))

        for road in roads_hit:
            horiz_ok = all([road in roads_satisfied[0] or road in roads_satisfied[1],
                            road in roads_satisfied[6] or road in roads_satisfied[7]])
            stereo_ok = any([all([road in roads_satisfied[2] or road in roads_satisfied[4],   # 1U1V
                                  road in roads_satisfied[3] or road in roads_satisfied[5]]),
                             road in roads_satisfied[2] and road in roads_satisfied[4],       # 2U
                             road in roads_satisfied[3] and road in roads_satisfied[5]])      # 2V
            if horiz_ok and stereo_ok:
                roads.append(road)

        return roads


class color:
    BLUE      = "\033[94m"
    GREEN     = "\033[92m"
    YELLOW    = "\033[93m"
    RED       = "\033[91m"
    END       = "\033[0m"
    BOLD      = "\033[1m"
    UNDERLINE = "\033[4m"

def tp_strip(hit):
    bo, vmm, ch = hit
    vmm_ch = vmm*64 + ch - 1
    if bo in [0, 3, 5, 6]:
        vmm_ch = 511 - vmm_ch
    if bo in [0, 1, 6, 7]:
        vmm_ch += 64
    elif bo in [2, 4]:
        vmm_ch += 58
    else:
        vmm_ch += 71
    return int(vmm_ch)

def avg(li):
    return float(sum(li)) / len(li)

def slope(xs, zs):
    if len(xs) != len(zs): return -100
    if len(xs) == 1:       return -101
    return sum([x * ((z - avg(zs)) / (sum([zj*zj for zj in zs]) - len(zs)*pow(avg(zs), 2))) for (x,z) in zip(xs, zs)])

def fatal(message):
    sys.exit("Error in %s: %s" % (__file__, message))

def options():
    import argparse
    parser = argparse.ArgumentParser(usage=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--gbt", default="mmtp_test_21.decode.dat", help="Input GBT decoded dat file")
    parser.add_argument("--fit", default="mmtp_test_22.decode.dat", help="Input FIT decoded dat file")
    parser.add_argument("--ignore-slope", action="store_true", default=False, help="Disable slope check, if desired")
    return parser.parse_args()


if __name__ == "__main__":
    main()
