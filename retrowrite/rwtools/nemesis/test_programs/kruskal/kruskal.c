#include <stdlib.h>
#include <stdio.h>

static int find(int x, int par[])
{
  if (par[x] != x)
  {
    return find(par[x], par);
  }

  return x;
}


int kruskal(int g[], int mst[], int par[], int len)
{
  for (int i=0; i < len; ++i)
    {
      mst[i] = -1;
      par[i] = i;
    }

    int idx = 0;

    // originally `i < len` but this caused segmentation fault (?)
    for (int i=1; i < len-1; i += 2)
    {
      int src = find(g[i], par);
      int tgt = find(g[i + 1], par);

      if (src != tgt)
      {
        mst[++idx] = src;
        mst[++idx] = tgt;
        par[src] = tgt;
      }
    }

    mst[0] = idx / 2 + 1;

    int ret = 0;
    for (int i = 0; i < len; i++){
        ret += mst[i];
        ret += par[i];
    }
    return ret;
}

int main(int argc, char  *argv[]){
    if (argc != 2){
        printf("incorrect number of args: %i \n", argc);
    }

    /* 5 vertices, 7 edges */
    int g1[] = {0, 1, 0, 2, 0, 3, 0, 4, 1, 2, 2, 3, 3, 4};

    /* 7 vertices, 7 edges */
    int g2[] = {0, 1, 0, 2, 0, 3, 0, 4, 0, 5, 0, 6, 0, 7};


    int arg = atoi(argv[1]);

    int mst[sizeof(g1)];
    int par[sizeof(g1)];

    switch (arg) {
        case 1:
            return kruskal(g1, mst, par, sizeof(g1)/sizeof(g1[0]));
        case 2:
            return kruskal(g2, mst, par, sizeof(g2)/sizeof(g2[0]));
    }
    return 0;
}
