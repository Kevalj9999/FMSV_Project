
============================================================
// TARGET: dco_disable_by_cpu_en
============================================================

property cpu_en_wkup_to_dco_disable;
  @(posedge clk) disable iff (reset)
  cpu_en_wkup |-> (dco_disable_by_cpu_en != $past(dco_disable_by_cpu_en));
endproperty
assert property (cpu_en_wkup_to_dco_disable);

property cpu_enabled_with_dco_to_dco_disable;
  @(posedge clk) disable iff (reset)
  cpu_enabled_with_dco |-> (dco_disable_by_cpu_en != $past(dco_disable_by_cpu_en));
endproperty
assert property (cpu_enabled_with_dco_to_dco_disable);

property no_cpu_en_stability;
  @(posedge clk) disable iff (reset)
  !cpu_en_wkup |-> (dco_disable_by_cpu_en == $past(dco_disable_by_cpu_en));
endproperty
assert property (no_cpu_en_stability);

property multi_signal_dependency;
  @(posedge clk) disable iff (reset)
  (cpu_en_wkup && cpu_enabled_with_dco) |-> (dco_disable_by_cpu_en != $past(dco_disable_by_cpu_en));
endproperty
assert property (multi_signal_dependency);


============================================================
// TARGET: wkup_event
============================================================

property wkup_event_change;
  @(posedge clk) disable iff (reset)
  wkup_clear |-> (wkup_event != $past(wkup_event));
endproperty
assert property (wkup_event_change);

property wkup_event_stability;
  @(posedge clk) disable iff (reset)
  !wkup_clear |-> (wkup_event == $past(wkup_event));
endproperty
assert property (wkup_event_stability);

property wkup_event_multi_dependency;
  @(posedge clk) disable iff (reset)
  (wkup_event && wkup_clear) |-> (wkup_event != $past(wkup_event));
endproperty
assert property (wkup_event_multi_dependency);


============================================================
// TARGET: cpuoff_and_mclk_enable
============================================================

property cpuoff_to_cpuoff_and_mclk_enable;
  @(posedge clk) disable iff (reset)
  cpuoff |-> (cpuoff_and_mclk_enable != $past(cpuoff_and_mclk_enable));
endproperty
assert property (cpuoff_to_cpuoff_and_mclk_enable);

property scg1_to_cpuoff_and_mclk_enable;
  @(posedge clk) disable iff (reset)
  scg1 |-> (cpuoff_and_mclk_enable != $past(cpuoff_and_mclk_enable));
endproperty
assert property (scg1_to_cpuoff_and_mclk_enable);

property stability_cpuoff_and_mclk_enable;
  @(posedge clk) disable iff (reset)
  !cpuoff_and_mclk_enable |-> (cpuoff_and_mclk_enable == $past(cpuoff_and_mclk_enable));
endproperty
assert property (stability_cpuoff_and_mclk_enable);

property multi_dependency_cpuoff_scg1_to_cpuoff_and_mclk_enable;
  @(posedge clk) disable iff (reset)
  (cpuoff && scg1) |-> (cpuoff_and_mclk_enable != $past(cpuoff_and_mclk_enable));
endproperty
assert property (multi_dependency_cpuoff_scg1_to_cpuoff_and_mclk_enable);


============================================================
// TARGET: dmem_addr
============================================================

property p_dma_mclk_to_dmem_addr;
  @(posedge dma_mclk) disable iff (reset)
  (dma_mclk) |-> (dmem_addr != $past(dmem_addr));
endproperty
assert property (p_dma_mclk_to_dmem_addr);

property p_not_dma_mclk_stability_dmem_addr;
  @(posedge dma_mclk) disable iff (reset)
  (!dma_mclk) |-> (dmem_addr == $past(dmem_addr));
endproperty
assert property (p_not_dma_mclk_stability_dmem_addr);


============================================================
// TARGET: pmem_addr
============================================================

property p_mclk_irq_num_to_pmem_addr;
  @(posedge clk) disable iff (reset)
  (mclk_irq_num) |-> (pmem_addr != $past(pmem_addr));
endproperty
assert property (p_mclk_irq_num_to_pmem_addr);

property p_not_mclk_irq_num_stable_pmem_addr;
  @(posedge clk) disable iff (reset)
  (!mclk_irq_num) |-> (pmem_addr == $past(pmem_addr));
endproperty
assert property (p_not_mclk_irq_num_stable_pmem_addr);

property p_multi_dependency;
  @(posedge clk) disable iff (reset)
  (mclk_irq_num && pmem_addr) |-> (pmem_addr != $past(pmem_addr));
endproperty
assert property (p_multi_dependency);


============================================================
// TARGET: lfxt_enable
============================================================

property p1;
  @(posedge clk) disable iff (reset)
  lfxt_disable_by_cpu_en |-> (lfxt_enable != $past(lfxt_enable));
endproperty
assert property (p1);

property p2;
  @(posedge clk) disable iff (reset)
  !lfxt_disable_by_cpu_en |-> (lfxt_enable == $past(lfxt_enable));
endproperty
assert property (p2);

property p3;
  @(posedge clk) disable iff (reset)
  (lfxt_disable_by_cpu_en && cpu_en_wkup) |-> (lfxt_enable != $past(lfxt_enable));
endproperty
assert property (p3);


============================================================
// TARGET: cpu_en_wkup
============================================================

property p_wkup_clear_to_cpu_en_wkup;
  @(posedge clk) disable iff (reset)
  wkup_clear |-> (cpu_en_wkup != $past(cpu_en_wkup));
endproperty
assert property (p_wkup_clear_to_cpu_en_wkup);

property p_stability_cpu_en_wkup;
  @(posedge clk) disable iff (reset)
  !wkup_clear |-> (cpu_en_wkup == $past(cpu_en_wkup));
endproperty
assert property (p_stability_cpu_en_wkup);


============================================================
// TARGET: cpu_enabled_with_dco
============================================================

property cpu_en_wkup_to_cpu_enabled_with_dco;
  @(posedge clk) disable iff (reset)
  cpu_en_wkup |-> (cpu_enabled_with_dco != $past(cpu_enabled_with_dco));
endproperty
assert property (cpu_en_wkup_to_cpu_enabled_with_dco);

property not_cpu_en_wkup_stability;
  @(posedge clk) disable iff (reset)
  !cpu_en_wkup |-> (cpu_enabled_with_dco == $past(cpu_enabled_with_dco));
endproperty
assert property (not_cpu_en_wkup_stability);

property multi_signal_dependency;
  @(posedge clk) disable iff (reset)
  (cpu_enabled_with_dco && cpu_en_wkup) |-> (cpu_enabled_with_dco != $past(cpu_enabled_with_dco));
endproperty
assert property (multi_signal_dependency);


============================================================
// TARGET: cpu_en
============================================================

property cpu_en_wkup_to_cpu_en;
  @(posedge clk) disable iff (reset)
  cpu_en_wkup |-> (cpu_en != $past(cpu_en));
endproperty
assert property (cpu_en_wkup_to_cpu_en);

property not_cpu_en_stable_cpu_en;
  @(posedge clk) disable iff (reset)
  !cpu_en |-> (cpu_en == $past(cpu_en));
endproperty
assert property (not_cpu_en_stable_cpu_en);

property cpu_en_and_cpu_en_wkup_to_cpu_en;
  @(posedge clk) disable iff (reset)
  (cpu_en && cpu_en_wkup) |-> (cpu_en != $past(cpu_en));
endproperty
assert property (cpu_en_and_cpu_en_wkup_to_cpu_en);


============================================================
// TARGET: lfxt_disable_by_cpu_en
============================================================

property cpu_en_wkup_to_lfxt_disable_by_cpu_en;
  @(posedge clk) disable iff (reset)
  cpu_en_wkup |-> (lfxt_disable_by_cpu_en != $past(lfxt_disable_by_cpu_en));
endproperty
assert property (cpu_en_wkup_to_lfxt_disable_by_cpu_en);

property stability_lfxt_disable_by_cpu_en;
  @(posedge clk) disable iff (reset)
  !cpu_en_wkup |-> (lfxt_disable_by_cpu_en == $past(lfxt_disable_by_cpu_en));
endproperty
assert property (stability_lfxt_disable_by_cpu_en);

property multi_dependency_lfxt_disable_by_cpu_en;
  @(posedge clk) disable iff (reset)
  (cpu_en_wkup && wkup_clear) |-> (lfxt_disable_by_cpu_en != $past(lfxt_disable_by_cpu_en));
endproperty
assert property (multi_dependency_lfxt_disable_by_cpu_en);

