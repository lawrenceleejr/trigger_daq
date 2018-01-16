# generates straight down tracks in the middle of the plane

# pick your nominal x plane track
ivmm = 1
ich = 36

# offsets in fw
v_off = 7
u_off = -6  

# flipped planes
flipped = [0, 3, 5, 6]

def flip(ch, ib):
    if ib in flipped:
        return 512 - ch 
    else:
        return ch +1
    
def offset(strip, ib):
    if ib < 2 or ib > 5:
        return strip
    elif ib == 5 or ib == 3:
        return strip - v_off
    else:
        return strip - u_off

def main():
    for ib in reversed(range(8)):
        strip = ivmm * 64 + ich - 1
        print "board", ib, ": ",
        strip = offset(strip, ib)
        strip = flip(strip, ib)
        vmm = (strip/64)%8 
        ch = strip%64
        print vmm,",", ch
    


if __name__ == "__main__":
    main()
