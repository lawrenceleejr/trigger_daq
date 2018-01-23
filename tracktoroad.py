# check which roads a track should be in

import ROOT, sys, math

# offsets in fw
v_off = 7
u_off = -6  

# flipped planes
flipped = [0, 3, 5, 6]

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
            m_roads.append(myroad_0)
            m_roads.append(myroad_1)
            #m_roads.append(myroad_2)
            #m_roads.append(myroad_3)
            m_roads.append(myroad_4)
            m_roads.append(myroad_5)
    return m_roads

def flip(ch, ib):
    if ib in flipped:
        return 512 - ch 
    else:
        return ch
    
def offset(strip, ib):
    if ib < 2 or ib > 5:
        return strip
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
    def contains_hit(self, ib, strip):
        iroad = -1
        if ib < 2 or ib > 5:
            iroad = self.iroadx
        elif ib == 2 or ib == 4:
            iroad = self.iroadu
        else:
            iroad = self.iroadv
        slow = 8 * iroad 
        shigh = 8 * (iroad + 1) 
        slow -= 0
        shigh += 4
        strip = offset(strip, ib)
        return strip >= slow and strip < shigh

def main():

    hits = []

    # event 1310
    hits.append(Hit(5, 7, 31))
    hits.append(Hit(2, 0, 15))
    hits.append(Hit(6, 7, 40))
    hits.append(Hit(1, 0, 25))
    hits.append(Hit(0, 7, 40))

    # event 1799
    # looks ok
#     hits.append(Hit(5, 6, 63))
#     hits.append(Hit(3, 6, 63))
#     hits.append(Hit(4, 1, 47))
#     hits.append(Hit(7, 1, 25))
#     hits.append(Hit(6, 6, 40))
#     hits.append(Hit(0, 6, 40))

#     # event 1095 # this is weird b/c it wraps around the boards tho
#     hits.append(Hit(5, 7, 23))
#     #hits.append(Hit(3, 7, 40))
#     hits.append(Hit(4, 0, 7))
#     hits.append(Hit(2, 0, 7))
#     #hits.append(Hit(7, 7, 47))
#     hits.append(Hit(6, 7, 40))
#     hits.append(Hit(1, 0, 25))
#     hits.append(Hit(0, 7, 40))

#     # event 1123 - 1126 # i think here there is a duplicate that doesn't make sense, 1126 + 1124
#     #hits.append(Hit(5, 6, 23))
#     hits.append(Hit(3, 6, 23))
#     #hits.append(Hit(4, 0, 7))
#     hits.append(Hit(2, 1, 7))
#     hits.append(Hit(7, 1, 25))
#     #hits.append(Hit(6, 7, 40))
#     hits.append(Hit(1, 1, 25))
#     hits.append(Hit(0, 6, 40))

#     # event 1048
#     hits.append(Hit(5, 6, 19))
#     hits.append(Hit(3, 6, 19))
#     #hits.append(Hit(4, 0, 7))
#     #hits.append(Hit(2, 1, 3))
#     hits.append(Hit(7, 1, 25))
#     #hits.append(Hit(6, 7, 40))
#     hits.append(Hit(1, 1, 25))
#     hits.append(Hit(0, 6, 40))


#     hits.append(Hit(7, 0, 25))
#     hits.append(Hit(6, 7, 40))
#     hits.append(Hit(5, 7, 47))
#     hits.append(Hit(4, 0, 31))
#     hits.append(Hit(3, 7, 47))
#     hits.append(Hit(2, 0, 31))
#     hits.append(Hit(1, 0, 25))
#     hits.append(Hit(0, 7, 40))

    my_roads = create_roads(512)

    for road in my_roads:
        if road.iroadx == 2 and road.iroadu == 0 and road.iroadv == 5:
            print "road: (%d,%d,%d)" %(road.iroadx,road.iroadu,road.iroadv)
        nx = 0
        nu = 0
        nv = 0
        road_good = True
        for hit in hits:
            strip = hit.ivmm * 64 + hit.ich 
            strip = flip(strip, hit.ib)
            if not road.contains_hit(hit.ib, strip):
                road_good = False
                break
        if road_good:
            print
            print "road: (%d,%d,%d)" %(road.iroadx,road.iroadu,road.iroadv)

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


if __name__ == "__main__":
    main()
