#include "stdio.h"
#include "stdint.h"
#include "verilated.h"
#include "build/VIntDivRem4.h"
#include "../divider_input/cpp_input.dat"

inline void cycle(VIntDivRem4 *model)
{
  model->eval();
  model->clk = 0;
  model->eval();
  model->clk = 1;
  model->eval();
}

int main(int argc, char **argv)
{
  if (argc != 3)
  {
    printf("Please give exactly 2 arguments for (1)trace and (2)ncycle\n");
    return 1;
  }
  int trace;
  sscanf(argv[1], "%d", &trace);

  long long ncycle;
  sscanf(argv[2], "%lld", &ncycle);

  VIntDivRem4 *idiv = new VIntDivRem4();

  // Reset the model
  idiv->reset = 1;
  cycle(idiv);
  idiv->reset = 0;
  cycle(idiv);

  long long time = 0, passed = 0;
  int ans0, ans1, ans2, ans3;

  for (long long time=0; time<ncycle; ++time)
  {
    idiv->resp_rdy = 1;
    idiv->req_val  = 1;

    int idx = time % num_inputs;

    idiv->req_msg[0] = inp[idx][0];
    idiv->req_msg[1] = inp[idx][1];
    idiv->req_msg[2] = inp[idx][2];
    idiv->req_msg[3] = inp[idx][3];

    if (idiv->req_rdy)
    {
      ans0 = oup[idx][0];
      ans1 = oup[idx][1];
      ans2 = oup[idx][2];
      ans3 = oup[idx][3];
    }

    cycle(idiv);

    if (trace)
    {
      printf("req_rdy: %d resp_val: %d\n", idiv->req_rdy, idiv->resp_val);
    }

    if (idiv->resp_val)
    {
      if ( idiv->resp_msg[0] != ans0 || idiv->resp_msg[1] != ans1 ||
           idiv->resp_msg[2] != ans2 || idiv->resp_msg[3] != ans3 )
      {
        printf("Test Failed\n");
        return 1;
      }
      passed += 1;
    }
  }

  printf("[%lld passed] idiv", passed );

  return 0;
}
