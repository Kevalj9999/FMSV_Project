
============================================================
// TARGET: mem_data
============================================================

property p_mem_ctl_to_mem_data;
  @(posedge clk) disable iff (reset)
  mem_ctl |-> (mem_data != $past(mem_data));
endproperty
assert property (p_mem_ctl_to_mem_data);

property p_mem_cnt_to_mem_data;
  @(posedge clk) disable iff (reset)
  mem_cnt |-> (mem_data != $past(mem_data));
endproperty
assert property (p_mem_cnt_to_mem_data);

property p_mem_addr_to_mem_data;
  @(posedge clk) disable iff (reset)
  mem_addr |-> (mem_data != $past(mem_data));
endproperty
assert property (p_mem_addr_to_mem_data);

property p_stability_mem_data;
  @(posedge clk) disable iff (reset)
  !mem_ctl |-> (mem_data == $past(mem_data));
endproperty
assert property (p_stability_mem_data);

property p_multi_dependency_mem_data;
  @(posedge clk) disable iff (reset)
  (mem_ctl && mem_cnt) |-> (mem_data != $past(mem_data));
endproperty
assert property (p_multi_dependency_mem_data);


============================================================
// TARGET: per_addr
============================================================

property per_en_to_per_addr;
  @(posedge clk) disable iff (reset)
  per_en |-> (per_addr != $past(per_addr));
endproperty
assert property (per_en_to_per_addr);

property per_we_to_per_addr;
  @(posedge clk) disable iff (reset)
  per_we |-> (per_addr != $past(per_addr));
endproperty
assert property (per_we_to_per_addr);

property stable_per_addr;
  @(posedge clk) disable iff (reset)
  !per_en |-> (per_addr == $past(per_addr));
endproperty
assert property (stable_per_addr);

property multi_dependency_per_addr;
  @(posedge clk) disable iff (reset)
  (per_en && per_we) |-> (per_addr != $past(per_addr));
endproperty
assert property (multi_dependency_per_addr);


============================================================
// TARGET: dmem_cen
============================================================

property pmem_cen_to_dmem_cen;
  @(posedge clk) disable iff (reset)
  pmem_cen |-> (dmem_cen != $past(dmem_cen));
endproperty
assert property (pmem_cen_to_dmem_cen);

property pmem_din_to_dmem_cen;
  @(posedge clk) disable iff (reset)
  pmem_din |-> (dmem_cen != $past(dmem_cen));
endproperty
assert property (pmem_din_to_dmem_cen);

property stable_dmem_cen;
  @(posedge clk) disable iff (reset)
  !pmem_cen |-> (dmem_cen == $past(dmem_cen));
endproperty
assert property (stable_dmem_cen);

property multi_dependency_dmem_cen;
  @(posedge clk) disable iff (reset)
  (pmem_cen && pmem_din) |-> (dmem_cen != $past(dmem_cen));
endproperty
assert property (multi_dependency_dmem_cen);


============================================================
// TARGET: dma_en
============================================================

property per_en_to_dma_en;
  @(posedge clk) disable iff (reset)
  per_en |-> (dma_en != $past(dma_en));
endproperty
assert property (per_en_to_dma_en);

property dma_wkup_to_dma_en;
  @(posedge clk) disable iff (reset)
  dma_wkup |-> (dma_en != $past(dma_en));
endproperty
assert property (dma_wkup_to_dma_en);

property stability_dma_en;
  @(posedge clk) disable iff (reset)
  !per_en |-> (dma_en == $past(dma_en));
endproperty
assert property (stability_dma_en);

property stability_dma_en_wkup;
  @(posedge clk) disable iff (reset)
  !dma_wkup |-> (dma_en == $past(dma_en));
endproperty
assert property (stability_dma_en_wkup);

property multi_dependency;
  @(posedge clk) disable iff (reset)
  (per_en && dma_wkup) |-> (dma_en != $past(dma_en));
endproperty
assert property (multi_dependency);


============================================================
// TARGET: dmem_addr
============================================================

property dmem_cen_to_dmem_addr;
  @(posedge clk) disable iff (reset)
  dmem_cen |-> (dmem_addr != $past(dmem_addr));
endproperty
assert property (dmem_cen_to_dmem_addr);

property not_dmem_cen_stability;
  @(posedge clk) disable iff (reset)
  !dmem_cen |-> (dmem_addr == $past(dmem_addr));
endproperty
assert property (not_dmem_cen_stability);

property dmem_cen_and_dmem_addr_to_pmem_cen;
  @(posedge clk) disable iff (reset)
  (dmem_addr && dmem_cen) |-> (pmem_cen != $past(pmem_cen));
endproperty
assert property (dmem_cen_and_dmem_addr_to_pmem_cen);


============================================================
// TARGET: pmem_addr
============================================================

property pmem_cen_to_pmem_addr_change;
  @(posedge clk) disable iff (reset)
  pmem_cen |-> (pmem_addr != $past(pmem_addr));
endproperty
assert property (pmem_cen_to_pmem_addr_change);

property pmem_cen_stability;
  @(posedge clk) disable iff (reset)
  !pmem_cen |-> (pmem_addr == $past(pmem_addr));
endproperty
assert property (pmem_cen_stability);

property pmem_addr_stability;
  @(posedge clk) disable iff (reset)
  !pmem_addr |-> (pmem_cen == $past(pmem_cen));
endproperty
assert property (pmem_addr_stability);


============================================================
// TARGET: pmem_cen
============================================================

property pmem_addr_to_pmem_cen;
  @(posedge clk) disable iff (reset)
  (pmem_addr != $past(pmem_addr)) |-> (pmem_cen != $past(pmem_cen));
endproperty
assert property (pmem_addr_to_pmem_cen);

property pmem_cen_stability;
  @(posedge clk) disable iff (reset)
  !pmem_cen |-> (pmem_cen == $past(pmem_cen));
endproperty
assert property (pmem_cen_stability);

property pmem_addr_and_pmem_cen;
  @(posedge clk) disable iff (reset)
  (pmem_addr && pmem_cen) |-> (pmem_cen != $past(pmem_cen));
endproperty
assert property (pmem_addr_and_pmem_cen);


============================================================
// TARGET: cpu_en
============================================================

property p1;
  @(posedge clk) disable iff (reset)
  wkup |-> (cpu_en != $past(cpu_en));
endproperty
assert property (p1);

property p2;
  @(posedge clk) disable iff (reset)
  !wkup |-> (cpu_en == $past(cpu_en));
endproperty
assert property (p2);


============================================================
// TARGET: dmem_wen
============================================================

property pmem_wen_to_dmem_wen;
  @(posedge clk) disable iff (reset)
  pmem_wen |-> (dmem_wen != $past(dmem_wen));
endproperty
assert property (pmem_wen_to_dmem_wen);

property stable_dmem_wen;
  @(posedge clk) disable iff (reset)
  !pmem_wen |-> (dmem_wen == $past(dmem_wen));
endproperty
assert property (stable_dmem_wen);

