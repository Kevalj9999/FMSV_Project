
============================================================
// TARGET: mem_data
============================================================

property p_mem_ctl_to_mem_data;
  @(posedge clk) disable iff (reset)
  mem_ctl |-> (mem_data != $past(mem_data));
endproperty
assert property (p_mem_ctl_to_mem_data);

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

property p_multi_dependency;
  @(posedge clk) disable iff (reset)
  (mem_ctl && mem_addr) |-> (mem_data != $past(mem_data));
endproperty
assert property (p_multi_dependency);


============================================================
// TARGET: per_addr
============================================================

property per_we_to_per_addr;
  @(posedge clk) disable iff (reset)
  per_we |-> (per_addr != $past(per_addr));
endproperty
assert property (per_we_to_per_addr);

property per_en_to_per_addr;
  @(posedge clk) disable iff (reset)
  per_en |-> (per_addr != $past(per_addr));
endproperty
assert property (per_en_to_per_addr);

property stable_per_addr;
  @(posedge clk) disable iff (reset)
  !per_en |-> (per_addr == $past(per_addr));
endproperty
assert property (stable_per_addr);

property multi_signal_dependency;
  @(posedge clk) disable iff (reset)
  (per_we && per_en) |-> (per_addr != $past(per_addr));
endproperty
assert property (multi_signal_dependency);


============================================================
// TARGET: dma_en
============================================================

property dma_wkup_to_dma_en;
  @(posedge clk) disable iff (reset)
  dma_wkup |-> (dma_en != $past(dma_en));
endproperty
assert property (dma_wkup_to_dma_en);

property per_en_to_dma_en;
  @(posedge clk) disable iff (reset)
  per_en |-> (dma_en != $past(dma_en));
endproperty
assert property (per_en_to_dma_en);

property stability_dma_en;
  @(posedge clk) disable iff (reset)
  !dma_en |-> (dma_en == $past(dma_en));
endproperty
assert property (stability_dma_en);

property multi_dependency_dma_en;
  @(posedge clk) disable iff (reset)
  (dma_wkup && per_en) |-> (dma_en != $past(dma_en));
endproperty
assert property (multi_dependency_dma_en);


============================================================
// TARGET: dmem_addr
============================================================

property p_dmem_cen_to_dmem_addr;
  @(posedge clk) disable iff (reset)
  dmem_cen |-> (dmem_addr != $past(dmem_addr));
endproperty
assert property (p_dmem_cen_to_dmem_addr);

property p_not_dmem_cen_stability;
  @(posedge clk) disable iff (reset)
  !dmem_cen |-> (dmem_addr == $past(dmem_addr));
endproperty
assert property (p_not_dmem_cen_stability);


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
// TARGET: aclk_en
============================================================

property cpu_en_to_aclk_en;
  @(posedge clk) disable iff (reset)
  cpu_en |-> (aclk_en != $past(aclk_en));
endproperty
assert property (cpu_en_to_aclk_en);

property stable_aclk_en;
  @(posedge clk) disable iff (reset)
  !cpu_en |-> (aclk_en == $past(aclk_en));
endproperty
assert property (stable_aclk_en);

property multi_dependency_aclk_en;
  @(posedge clk) disable iff (reset)
  (cpu_en && aclk_en) |-> (aclk_en != $past(aclk_en));
endproperty
assert property (multi_dependency_aclk_en);


============================================================
// TARGET: cpu_en
============================================================

property p_wkup_to_cpu_en;
  @(posedge clk) disable iff (reset)
  wkup |-> (cpu_en != $past(cpu_en));
endproperty
assert property (p_wkup_to_cpu_en);

property p_stability_cpu_en;
  @(posedge clk) disable iff (reset)
  !wkup |-> (cpu_en == $past(cpu_en));
endproperty
assert property (p_stability_cpu_en);


============================================================
// TARGET: dco_enable
============================================================

property cpu_en_to_dco_enable;
  @(posedge clk) disable iff (reset)
  cpu_en |-> (dco_enable != $past(dco_enable));
endproperty
assert property (cpu_en_to_dco_enable);

property no_cpu_en_stability;
  @(posedge clk) disable iff (reset)
  !cpu_en |-> (dco_enable == $past(dco_enable));
endproperty
assert property (no_cpu_en_stability);

property multi_signal_dependency;
  @(posedge clk) disable iff (reset)
  (dco_enable && cpu_en) |-> (cpu_en != $past(cpu_en));
endproperty
assert property (multi_signal_dependency);

