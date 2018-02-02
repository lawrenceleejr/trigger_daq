# check which roads a track should be in

import ROOT, sys, math

# offsets in fw
v_off = 71
u_off = 58  
x_off = 64

# flipped planes
flipped = [0, 3, 5, 6]
ips = [123, 125, 109, 106, 126, 122, 124, 119][::-1]


def parse_config(line):
    info = line.split()
    nice_info = info[3].strip("[]")
    nhits = len(nice_info.split("),"))
    my_hits = []
    for j in range(nhits):
        (ip,vmm,ch) = nice_info.split("),")[j].strip("()").split(",")
        ib = ips.index(int(ip))
        my_hits.append(Hit(ib, int(vmm), int(ch)))
    return my_hits

def create_roads(nstrips):
    if (nstrips % 8 != 0):
        print "number of strips isn't divis. by 8!"
        sys.exit(1)
    nroad = nstrips / 8
    m_roads = []
    for i in range(nroad):
        m_roads.append(Road(i,i,i))
        nuv = 4; #1, uv factor for 20 cm chamber
        for uv in range(1, nuv+1):
            if (i-uv < 0):
                continue
            myroad_0 = Road(i, i+uv,   i-uv)
            myroad_1 = Road(i, i-uv,   i+uv)
            myroad_2 = Road(i, i+uv-1, i-uv)
            myroad_3 = Road(i, i-uv,   i+uv-1)
            myroad_4 = Road(i, i-uv+1, i+uv)
            myroad_5 = Road(i, i+uv,   i-uv+1)
            if uv != 4:
                m_roads.append(myroad_0)
                m_roads.append(myroad_1)
                #m_roads.append(myroad_2)
                # m_roads.append(myroad_3)
                # m_roads.append(myroad_4) #nathan doesn't have these right now
                # m_roads.append(myroad_5)
            m_roads.append(myroad_2)
            m_roads.append(myroad_3)
            m_roads.append(myroad_4)
            m_roads.append(myroad_5)
    return m_roads

def flip(ch, ib):
    if ib in flipped:
        return 511 - ch 
    else:
        return ch
    
def offset(strip, ib):
    if ib < 2 or ib > 5:
        return strip + x_off
    elif ib == 5 or ib == 3:
        return strip + v_off
    else:
        return strip + u_off


class Hit(object):
    
    def __init__(self, ib, vmm, ch):
        self.ivmm = vmm
        self.ich = ch
        self.ib = ib

    
class Road(object):

    def __init__(self, iroadx, iroadu, iroadv):
        self.iroadx = iroadx
        self.iroadu = iroadu
        self.iroadv = iroadv
        self.margin_boards = []
    def contains_hit(self, ib, strip):
        iroad = -1
        if ib < 2 or ib > 5:
            iroad = self.iroadx
        elif ib == 2 or ib == 4:
            iroad = self.iroadu
        else:
            iroad = self.iroadv
        strip = offset(strip, ib)

        slow = 8 * iroad 
        shigh = 8 * (iroad + 1) 
        
        if strip >= slow and strip < shigh:
            return True

        slow -= 0
        shigh += 4
        if strip >= slow and strip < shigh:
            self.margin_boards.append(ib)
            return True

def main():

    events = []

    hits = []

    lines_scan = open("scan_config_mm.txt").readlines()
    for i in range(len(lines_scan)-1):
        print
        print color.BLUE + "TRACK %d"%(i) + color.END
        print lines_scan[i].split()[3:]
        hits = parse_config(lines_scan[i])
        process_hits(hits)

    # if you want to add events by hand

    if 1123 in events:
        # i think here there is a duplicate that doesn't make sense, 1126 + 1124
        print
        print color.BLUE + "event 1123" + color.END
        #hits.append(Hit(5, 6, 23))
        hits.append(Hit(3, 6, 23))
        #hits.append(Hit(4, 1, 7))
        hits.append(Hit(2, 1, 7))
        hits.append(Hit(7, 1, 25))
        #hits.append(Hit(6, 6, 40))
        hits.append(Hit(1, 1, 25))
        hits.append(Hit(0, 6, 40))
        process_hits(hits)
    hits = []

def process_hits(hits):

    my_roads = create_roads(512)

    for road in my_roads:
        if road.iroadx == 2 and road.iroadu == 0 and road.iroadv == 5:
            print "road: (%d,%d,%d)" %(road.iroadx,road.iroadu,road.iroadv)
        nx = 0
        nu = 0
        nv = 0
        road_good = True
        for hit in hits:
            #print hit.ivmm, hit.ich, hit.ib
            strip = hit.ivmm * 64 + hit.ich - 1
            strip = flip(strip, hit.ib)
            if not road.contains_hit(hit.ib, strip):
                road_good = False
                break
            else:
                if hit.ib < 2 or hit.ib > 5:                                                                                             
                    nx += 1                                                                                                              
                elif hit.ib == 2 or hit.ib == 4:                                                                                         
                    nu += 1                                                                                                              
                elif hit.ib == 3 or hit.ib == 5:                                                                                         
                    nv += 1 
        if road_good and nx > 2 and (nu + nv) > 2: 
            print
            print "road: (%d,%d,%d)" %(road.iroadx,road.iroadu,road.iroadv)
            print "margin", road.margin_boards
#             if road.contains_hit(hit.ib, strip):
#                 if hit.ib < 2 or hit.ib > 5:
#                     nx += 1
#                 elif hit.ib == 2 or hit.ib == 4:
#                     nu += 1
#                 elif hit.ib == 3 or hit.ib == 5:
#                     nv += 1

#             if nx > 1 and (nu + nv) > 1:
#                 print
#                 print "road: (%d,%d,%d)" %(road.iroadx,road.iroadu,road.iroadv)
#                 print "nx:%d, nu:%d, nv:%d" %(nx,nu,nv)

class color:
    BLUE      = "\033[94m"
    GREEN     = "\033[92m"
    YELLOW    = "\033[93m"
    RED       = "\033[91m"
    END       = "\033[0m"
    BOLD      = "\033[1m"
    UNDERLINE = "\033[4m"

if __name__ == "__main__":
    main()
