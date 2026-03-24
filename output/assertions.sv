
// ===== TARGET: pmem_addr =====

```systemverilog
property pmem_addr_cen_dependency;
  @(posedge gclk) disable iff (dbg_rst)
  pmem_cen |-> (pmem_addr == $past(pmem_addr));
endproperty
assert property (pmem_addr_cen_dependency);

property pmem_addr_stability;
  @(posedge gclk) disable iff (dbg_rst)
  (pmem_cen == 1'b0) |-> (pmem_addr == $past(pmem_addr));
endproperty
assert property (pmem_addr_stability);

property pmem_addr_gclk_dependency;
  @(posedge gclk) disable iff (dbg_rst)
  (pmem_cen == 1'b1) |-> (pmem_addr != $past(pmem_addr));
endproperty
assert property (pmem_addr_gclk_dependency);

// ===== TARGET: per_addr =====

```systemverilog
property per_addr_enable_behavior;
  @(posedge dbg_clk) disable iff (dbg_rst)
  (per_en) |-> (per_addr != per_addr);
endproperty
assert property (per_addr_enable_behavior);

property per_addr_dependency;
  @(posedge dbg_clk) disable iff (dbg_rst)
  (per_addr) |-> (per_en && gclk);
endproperty
assert property (per_addr_dependency);

property per_addr_stability;
  @(posedge dbg_clk) disable iff (dbg_rst)
  (per_en == 1'b0) |-> (per_addr == $past(per_addr));
endproperty
assert property (per_addr_stability);

property per_addr_gclk_dependency;
  @(posedge dbg_clk) disable iff (dbg_rst)
  (per_addr && per_en) |-> (gclk);
endproperty
assert property (per_addr_gclk_dependency);

property per_addr_cpuoff_en_dependency;
  @(posedge dbg_clk) disable iff (dbg_rst)
  (per_addr && per_en && gclk) |-> (cpuoff_en);
endproperty
assert property (per_addr_cpuoff_en_dependency);
```

// ===== TARGET: dma_addr =====

```systemverilog
property dma_addr_stable_on_cpuoff;
  @(posedge gclk) disable iff (cpuoff_en) (dma_addr == $past(dma_addr));
endproperty
assert property (dma_addr_stable_on_cpuoff);

property dma_addr_valid_when_ready;
  @(posedge gclk) disable iff (puc_rst) (dma_ready -> (dma_addr !== 'x));
endproperty
assert property (dma_addr_valid_when_ready);

property dma_addr_changes_on_mclk;
  @(posedge mclk) disable iff (puc_rst) (dma_addr != $past(dma_addr) -> (dma_ready));
endproperty
assert property (dma_addr_changes_on_mclk);

property dma_addr_no_change_when_not_ready;
  @(posedge gclk) disable iff (puc_rst) (!dma_ready -> (dma_addr == $past(dma_addr)));
endproperty
assert property (dma_addr_no_change_when_not_ready);
```

// ===== TARGET: dbg_i2c_addr =====

```systemverilog
property p_dbg_i2c_addr_stable;
  @(posedge dbg_clk) disable iff (dbg_rst)
  (gclk) |-> (dbg_i2c_addr == $past(dbg_i2c_addr));
endproperty
assert property (p_dbg_i2c_addr_stable);

property p_dbg_i2c_addr_when_gclk;
  @(posedge dbg_clk) disable iff (dbg_rst)
  (gclk) |-> (dbg_i2c_addr != 2'b00);
endproperty
assert property (p_dbg_i2c_addr_when_gclk);

property p_dbg_i2c_addr_transition;
  @(posedge dbg_clk) disable iff (dbg_rst)
  (dbg_i2c_addr != $past(dbg_i2c_addr)) |-> (gclk);
endproperty
assert property (p_dbg_i2c_addr_transition);

// ===== TARGET: dmem_addr =====

```systemverilog
property p_dmem_addr_stable;
  @(posedge dbg_clk) disable iff (dbg_rst)
  (dmem_cen) |-> (dmem_addr == $past(dmem_addr));
endproperty
assert property (p_dmem_addr_stable);

property p_dmem_addr_when_cen;
  @(posedge dbg_clk) disable iff (dbg_rst)
  (dmem_cen) |-> (dmem_addr != 0);
endproperty
assert property (p_dmem_addr_when_cen);

property p_dmem_addr_no_change;
  @(posedge dbg_clk) disable iff (dbg_rst)
  (dmem_cen && !gclk) |-> (dmem_addr == $past(dmem_addr));
endproperty
assert property (p_dmem_addr_no_change);

property p_dmem_addr_valid;
  @(posedge dbg_clk) disable iff (dbg_rst)
  (dmem_cen) |-> (dmem_addr != 'x);
endproperty
assert property (p_dmem_addr_valid);
```

// ===== TARGET: smclk_en =====

```systemverilog
property smclk_en_behavior;
  @(posedge nodiv_mclk) disable iff (puc_rst)
  smclk_en |-> (smclk_en_nxt & cpu_en_s);
endproperty
assert property (smclk_en_behavior);

property smclk_en_dependency;
  @(posedge nodiv_mclk) disable iff (puc_rst)
  smclk_en |-> (aclk_en == 1'b1);
endproperty
assert property (smclk_en_dependency);

property smclk_en_stability;
  @(posedge nodiv_mclk) disable iff (puc_rst)
  !smclk_en |-> (smclk_en == $past(smclk_en));
endproperty
assert property (smclk_en_stability);

property smclk_en_gclk_dependency;
  @(posedge nodiv_mclk) disable iff (puc_rst)
  smclk_en |-> (gclk == 1'b1);
endproperty
assert property (smclk_en_gclk_dependency);

property smclk_en_cpuoff_dependency;
  @(posedge nodiv_mclk) disable iff (puc_rst)
  smclk_en |-> (cpuoff_en == 1'b0);
endproperty
assert property (smclk_en_cpuoff_dependency);
```

// ===== TARGET: lfxt_enable =====

```systemverilog
property lfxt_enable_stable;
  @(posedge nodiv_mclk) disable iff (por) lfxt_enable |-> (lfxt_enable == 1'b1);
endproperty
assert property (lfxt_enable_stable);

property lfxt_disable_condition;
  @(posedge nodiv_mclk) disable iff (por) (lfxt_enable == 1'b1) |-> (lfxt_disable == 1'b0);
endproperty
assert property (lfxt_disable_condition);

property lfxt_clk_en_dependency;
  @(posedge nodiv_mclk) disable iff (por) (lfxt_clk_en) |-> (lfxt_clk_s && ~lfxt_clk_dly);
endproperty
assert property (lfxt_clk_en_dependency);

property lfxt_enable_no_change;
  @(posedge nodiv_mclk) disable iff (por) (lfxt_enable == 1'b1) |-> (lfxt_enable == $past(lfxt_enable));
endproperty
assert property (lfxt_enable_no_change);
```

// ===== TARGET: per_en =====

```systemverilog
property per_en_stable;
  @(posedge gclk) disable iff (puc_rst) per_en |-> (per_en == $past(per_en));
endproperty
assert property (per_en_stable);

property per_en_implication;
  @(posedge gclk) disable iff (puc_rst) per_en |-> (cpuoff_en == 1'b0);
endproperty
assert property (per_en_implication);

property per_en_mux_selection;
  @(posedge gclk) disable iff (puc_rst) per_en |-> (ext_mem_din_sel[0] == 1'b1);
endproperty
assert property (per_en_mux_selection);

property per_en_dma_ready;
  @(posedge gclk) disable iff (puc_rst) per_en |-> (dma_ready == 1'b1);
endproperty
assert property (per_en_dma_ready);

property per_en_no_change;
  @(posedge gclk) disable iff (puc_rst) (per_en == 1'b1) |-> (per_en == $past(per_en));
endproperty
assert property (per_en_no_change);
```

// ===== TARGET: dmem_cen =====

```systemverilog
property p_dmem_cen_pmem_cen;
  @(posedge dbg_clk) disable iff (dbg_rst)
  pmem_cen |-> dmem_cen;
endproperty
assert property (p_dmem_cen_pmem_cen);

property p_dmem_cen_gclk;
  @(posedge dbg_clk) disable iff (dbg_rst)
  gclk |-> dmem_cen;
endproperty
assert property (p_dmem_cen_gclk);

property p_dmem_cen_stability;
  @(posedge dbg_clk) disable iff (dbg_rst)
  (dmem_cen == 1'b1) |-> (dmem_cen == 1'b1) throughout (gclk);
endproperty
assert property (p_dmem_cen_stability);

property p_pmem_cen_dmem_cen;
  @(posedge dbg_clk) disable iff (dbg_rst)
  (pmem_cen == 1'b1) |-> (dmem_cen == 1'b1);
endproperty
assert property (p_pmem_cen_dmem_cen);

property p_dmem_cen_dependency;
  @(posedge dbg_clk) disable iff (dbg_rst)
  (pmem_cen && gclk) |-> dmem_cen;
endproperty
assert property (p_dmem_cen_dependency);
```

// ===== TARGET: dbg_en =====

```systemverilog
property dbg_en_behavior;
  @(posedge dbg_clk) disable iff (dbg_rst)
  dbg_en_s |-> (dbg_rd_rdy == 1'b1);
endproperty
assert property (dbg_en_behavior);

property dbg_en_stability;
  @(posedge dbg_clk) disable iff (dbg_rst)
  !dbg_en_s |-> (dbg_en_s == $past(dbg_en_s));
endproperty
assert property (dbg_en_stability);

property dbg_halt_dependency;
  @(posedge dbg_clk) disable iff (dbg_rst)
  dbg_en_s |-> (dbg_halt_cmd == 1'b1);
endproperty
assert property (dbg_halt_dependency);

property dbg_freeze_condition;
  @(posedge dbg_clk) disable iff (dbg_rst)
  dbg_en_s |-> (dbg_freeze == 1'b1) iff (dbg_halt_st);
endproperty
assert property (dbg_freeze_condition);

property dbg_swbrk_dependency;
  @(posedge dbg_clk) disable iff (dbg_rst)
  dbg_en_s |-> (dbg_swbrk == 1'b1) iff (cpu_ctl[`SW_BRK_EN]);
endproperty
assert property (dbg_swbrk_dependency);
```

// ===== TARGET: dco_enable =====

```systemverilog
property p_dco_enable_behavior;
  @(posedge nodiv_mclk) disable iff (por)
  dco_enable |-> (dco_disable == 1'b0);
endproperty
assert property (p_dco_enable_behavior);

property p_dco_enable_dependency;
  @(posedge nodiv_mclk) disable iff (por)
  dco_enable |-> (dco_wkup_set_scan_observe == 1'b0);
endproperty
assert property (p_dco_enable_dependency);

property p_dco_enable_no_change;
  @(posedge nodiv_mclk) disable iff (por)
  !dco_enable |-> (dco_enable == $past(dco_enable));
endproperty
assert property (p_dco_enable_no_change);

property p_dco_enable_stability;
  @(posedge nodiv_mclk) disable iff (por)
  (dco_enable == 1'b1) |-> (dco_enable == $past(dco_enable));
endproperty
assert property (p_dco_enable_stability);
```

// ===== TARGET: scan_enable =====

```systemverilog
property p_scan_enable_r11_en;
  @(posedge mclk) disable iff (puc_rst)
  scan_enable |-> r11_en;
endproperty
assert property (p_scan_enable_r11_en);

property p_scan_enable_r5_en;
  @(posedge mclk) disable iff (puc_rst)
  scan_enable |-> r5_en;
endproperty
assert property (p_scan_enable_r5_en);

property p_no_change_scan_enable;
  @(posedge mclk) disable iff (puc_rst)
  !scan_enable |-> (scan_enable == $past(scan_enable));
endproperty
assert property (p_no_change_scan_enable);
```

// ===== TARGET: pmem_cen =====

```systemverilog
property pmem_cen_stable;
  @(posedge gclk) disable iff (dbg_rst) (pmem_cen == $past(pmem_cen)) |-> (pmem_cen == $past(pmem_cen));
endproperty
assert property (pmem_cen_stable);

property pmem_cen_when_gclk;
  @(posedge gclk) disable iff (dbg_rst) (pmem_cen == 1'b1) |-> (gclk == 1'b1);
endproperty
assert property (pmem_cen_when_gclk);

property pmem_cen_dependency;
  @(posedge gclk) disable iff (dbg_rst) (pmem_cen == 1'b1) |-> (cpuoff_en == 1'b0);
endproperty
assert property (pmem_cen_dependency);

property pmem_cen_no_change;
  @(posedge gclk) disable iff (dbg_rst) (pmem_cen == 1'b1) |-> (pmem_cen == $past(pmem_cen));
endproperty
assert property (pmem_cen_no_change);

property pmem_cen_mclk_mux_dependency;
  @(posedge gclk) disable iff (dbg_rst) (pmem_cen == 1'b1) |-> (mclk_mux == 1'b1);
endproperty
assert property (pmem_cen_mclk_mux_dependency);
```

// ===== TARGET: aclk_en =====

```systemverilog
property aclk_en_behavior;
  @(posedge mclk) disable iff (puc_rst)
  aclk_en |-> (gclk == 1'b1);
endproperty
assert property (aclk_en_behavior);

property aclk_en_stability;
  @(posedge mclk) disable iff (puc_rst)
  !aclk_en |-> (aclk_en == $past(aclk_en));
endproperty
assert property (aclk_en_stability);

property aclk_en_wakeup;
  @(posedge mclk) disable iff (puc_rst)
  aclk_en |-> (wdt_wkup_en == 1'b1);
endproperty
assert property (aclk_en_wakeup);

property aclk_en_clear;
  @(posedge mclk) disable iff (puc_rst)
  (wdtifg_clr == 1'b1) |-> (aclk_en == 1'b0);
endproperty
assert property (aclk_en_clear);
```

// ===== TARGET: dma_en =====

```systemverilog
property dma_en_behavior;
  @(posedge mclk) disable iff (puc_rst)
  dma_en |-> (dma_ready == 1'b1);
endproperty
assert property (dma_en_behavior);

property dma_en_stability;
  @(posedge mclk) disable iff (puc_rst)
  !dma_en |-> (dma_en == $past(dma_en));
endproperty
assert property (dma_en_stability);

property dma_en_dependency;
  @(posedge mclk) disable iff (puc_rst)
  dma_en |-> (ext_mem_en == 1'b1);
endproperty
assert property (dma_en_dependency);

property dma_ready_dly_stability;
  @(posedge mclk) disable iff (puc_rst)
  dma_ready |-> (dma_ready_dly == $past(dma_ready_dly));
endproperty
assert property (dma_ready_dly_stability);
```
