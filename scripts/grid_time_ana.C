#!/usr/bin/env root.exe

TTree* t = new TTree("a","a");
t->ReadFile("ts_warm_bore/timing_data/ts_warm_bore.711_1010.s1_sim.txt");
t->Draw("totwall/3600.");
