import struct, sys, zlib
def apply(old, patch):
    assert patch[:6]==b'BBRP1\0'
    on,nn,oc,nc=struct.unpack_from('<4I',patch,6)
    assert len(old)==on and zlib.crc32(old)==oc, 'source mismatch'
    out=bytearray(); p=22
    while True:
        t=patch[p]; p+=1
        if t==0: break
        if t==1: s,L=struct.unpack_from('<2I',patch,p); p+=8; out+=old[s:s+L]
        else: L,=struct.unpack_from('<I',patch,p); p+=4; out+=patch[p:p+L]; p+=L
    assert len(out)==nn and zlib.crc32(out)==nc, 'output mismatch'
    return bytes(out)
for n in ['he0','(a)','(b)']:
    o=open(f'/root/bbgame/baseball 2001.{n}','rb').read(); pa=open(f'patch_{n}.bin','rb').read()
    r=apply(o,pa); print(n, r==open(f'/root/bbmod/baseball 2001.{n}','rb').read())
