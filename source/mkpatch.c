// mkpatch: block-matching binary diff. Output format (little endian):
//  "BBRP1\0" u32 oldSize u32 newSize u32 oldCrc u32 newCrc
//  ops: u8 type; type 1 = COPY: u32 srcOff u32 len ; type 2 = ADD: u32 len, bytes ; type 0 = END
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#define B 32
static uint8_t *rd(const char *p, size_t *n){FILE*f=fopen(p,"rb");if(!f){perror(p);exit(1);}fseek(f,0,2);*n=ftell(f);fseek(f,0,0);uint8_t*b=malloc(*n+1);fread(b,1,*n,f);fclose(f);return b;}
static uint32_t crc32(const uint8_t*d,size_t n){uint32_t c=~0u;for(size_t i=0;i<n;i++){c^=d[i];for(int k=0;k<8;k++)c=(c>>1)^(0xEDB88320u&-(c&1));}return ~c;}
#define HB 24
static uint32_t *head,*nxt;
static inline uint32_t hsh(const uint8_t*p){uint64_t h=0;for(int i=0;i<B;i++)h=h*1000003u+p[i];return (uint32_t)(h^(h>>29))&((1u<<HB)-1);}
// rolling: polynomial with base M over window B
#define M 1000003ull
int main(int argc,char**argv){
  if(argc<4){fprintf(stderr,"usage: mkpatch old new out\n");return 1;}
  size_t on,nn; uint8_t*o=rd(argv[1],&on),*n=rd(argv[2],&nn);
  FILE*out=fopen(argv[3],"wb");
  fwrite("BBRP1\0",1,6,out); uint32_t hdr[4]={(uint32_t)on,(uint32_t)nn,crc32(o,on),crc32(n,nn)}; fwrite(hdr,4,4,out);
  head=malloc(sizeof(uint32_t)<<HB); memset(head,0xff,sizeof(uint32_t)<<HB);
  size_t nb=on/B; nxt=malloc(sizeof(uint32_t)*(nb+1));
  // rolling hash values must match hsh() definition: use same polynomial computed incrementally
  uint64_t pw=1; for(int i=0;i<B-1;i++) pw*=M;
  for(size_t b=0;b<nb;b++){ uint64_t h=0; const uint8_t*p=o+b*B; for(int i=0;i<B;i++) h=h*M+p[i]; uint32_t k=(uint32_t)(h^(h>>29))&((1u<<HB)-1); nxt[b]=head[k]; head[k]=(uint32_t)b; }
  size_t i=0, addStart=0; uint64_t h=0; int hv=0; size_t copies=0, addBytes=0;
  #define FLUSH_ADD(end) do{ if((end)>addStart){ uint8_t t=2; uint32_t L=(uint32_t)((end)-addStart); fwrite(&t,1,1,out); fwrite(&L,4,1,out); fwrite(n+addStart,1,L,out); addBytes+=L; } }while(0)
  while(i+B<=nn){
    if(!hv){ h=0; for(int k=0;k<B;k++) h=h*M+n[i+k]; hv=1; }
    uint32_t key=(uint32_t)(h^(h>>29))&((1u<<HB)-1);
    size_t bestLen=0, bestSrc=0; int tries=0;
    for(uint32_t b=head[key]; b!=0xffffffffu && tries<16; b=nxt[b], tries++){
      size_t s=(size_t)b*B; if(memcmp(o+s,n+i,B)) continue;
      size_t L=B; while(s+L<on && i+L<nn && o[s+L]==n[i+L]) L++;
      if(L>bestLen){bestLen=L;bestSrc=s;}
    }
    if(bestLen>=B){
      // extend backwards into pending add region
      size_t s=bestSrc, st=i; while(st>addStart && s>0 && o[s-1]==n[st-1]){s--;st--;bestLen++;}
      FLUSH_ADD(st);
      uint8_t t=1; uint32_t so=(uint32_t)s, L=(uint32_t)bestLen; fwrite(&t,1,1,out); fwrite(&so,4,1,out); fwrite(&L,4,1,out); copies++;
      i=st+bestLen; addStart=i; hv=0; continue;
    }
    // roll by one
    if(i+B<nn){ h=(h - (uint64_t)n[i]*pw)*M + n[i+B]; } 
    i++;
  }
  FLUSH_ADD(nn);
  uint8_t e=0; fwrite(&e,1,1,out); fclose(out);
  fprintf(stderr,"%s: copies=%zu addBytes=%zu\n",argv[3],copies,addBytes);
  return 0;
}
