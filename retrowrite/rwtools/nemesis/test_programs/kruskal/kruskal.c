
static int find(int x, int par[]) 
{
  if (par[x] != x)
  {
    return find(par[x], par);
  }

  return x;
}

void
kruskal(int g[], int mst[], int par[], int len)
{
  for (int i=0; i < len; ++i)
  {
    mst[i] = -1;
    par[i] = i;
  }

  int idx = 0;

  for (int i=1; i < len; i += 2)
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
}

int main(){
  /* 5 vertices, 7 edges */
  int g1[] = {0, 1, 0, 2, 0, 3, 0, 4, 1, 2, 2, 3, 3, 4}; 

  /* 7 vertices, 7 edges */
  // int g2[] = {0, 1, 0, 2, 0, 3, 0, 4, 0, 5, 0, 6, 0, 7};
  
  int mst[sizeof(g1)];
  int par[sizeof(g1)];
  kruskal(g1, mst, par, sizeof(g1)/sizeof(g1[0]));
}
