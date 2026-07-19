#!/usr/bin/env python3
"""equity-research skill · DCF 计算器（禁止心算的替代物）

用法：
    python dcf.py --config assumptions.json        # 完整运行
    python dcf.py --demo                           # 内置示例自检

功能：三阶段情景 DCF（显式期 + 增速衰减期 + 永续）、概率加权公允价值、
WACC×g 敏感性矩阵、反向 DCF（由现价倒推隐含稳态 FCF 与营收）、
盈利能力价值 EPV / 三要素（资产·EPV·franchise 成长）与护城河验证、
以及按预注册规则输出估值标签建议（低估/合理/高估）。

config JSON 结构（金额单位统一，通常 $B 或 亿元；每股价值单位 = 金额单位/股本单位）：
{
  "price": 131.50,            // 现价（可选；缺省则跳过标定与反向 DCF）
  "shares": 13.17,            // 当前股本
  "net_debt": 13.3,           // 净有息负债（现金多于债务则为负）
  "wacc": 0.095,
  "terminal_g": 0.03,
  "scenarios": [
    {"name": "bear", "prob": 0.40,
     "revenue": [...], "fcf_margin": [...],   // 等长；或直接给 "fcf": [...]
     "fade_years": 5, "fade_g_start": 0.04,   // 衰减期：末年营收增速由此线性降至 terminal_g
     "annual_dilution": 0.015}                // 显式期内年均股本稀释
  ],
  "sensitivity": {"scenario": "base", "wacc": [0.085,0.095,0.105], "g": [0.02,0.03,0.04]},
  "reverse": {"interim_fcf": [-28,-18,-8,5,25],  // 建设期 FCF 路径
              "steady_margins": [0.25,0.30,0.35],
              "base_revenue": 38},                // 当年营收基数，用于隐含 CAGR
  "range_low": 25, "range_high": 65             // 综合区间（可选，供标定）
}
"""
import argparse, json, sys

# ---------- 核心计算 ----------

def scenario_fcfs(sc, terminal_g):
    """返回显式期+衰减期的完整 FCF 序列与末年营收。"""
    if "fcf" in sc:
        fcfs = list(sc["fcf"]); rev = None
    else:
        rev_path, m = sc["revenue"], sc["fcf_margin"]
        assert len(rev_path) == len(m), f"{sc['name']}: revenue 与 fcf_margin 长度不等"
        fcfs = [r * mm for r, mm in zip(rev_path, m)]
        rev = rev_path[-1]
    fade, g0 = sc.get("fade_years", 0), sc.get("fade_g_start", terminal_g)
    mm_last = sc["fcf_margin"][-1] if "fcf_margin" in sc else None
    for k in range(fade):
        gr = g0 + (terminal_g - g0) * (k + 1) / fade
        if rev is not None:
            rev *= (1 + gr); fcfs.append(rev * mm_last)
        else:
            fcfs.append(fcfs[-1] * (1 + gr))
    return fcfs, rev

def dcf_value(sc, wacc, g, shares, net_debt):
    assert wacc > g, f"WACC({wacc}) 必须大于永续增长 g({g})"
    fcfs, _ = scenario_fcfs(sc, g)
    n = len(fcfs)
    pv = sum(f / (1 + wacc) ** (i + 1) for i, f in enumerate(fcfs))
    tv = fcfs[-1] * (1 + g) / (wacc - g)
    ev = pv + tv / (1 + wacc) ** n
    explicit_years = len(sc.get("fcf", sc.get("revenue", [])))
    sh = shares * (1 + sc.get("annual_dilution", 0.0)) ** explicit_years
    ps = (ev - net_debt) / sh
    return {"ev": ev, "equity": ev - net_debt, "per_share": ps, "shares_end": sh,
            "terminal_fcf": fcfs[-1], "exit_pfcf": tv / fcfs[-1]}

def reverse_dcf(price, shares, net_debt, wacc, g, interim_fcf, steady_margins, base_revenue):
    ev = price * shares + net_debt
    n = len(interim_fcf)
    pv_interim = sum(f / (1 + wacc) ** (i + 1) for i, f in enumerate(interim_fcf))
    tv_needed = (ev - pv_interim) * (1 + wacc) ** n
    fcf_req = tv_needed * (wacc - g)          # 稳态首年 FCF
    rows = []
    for m in steady_margins:
        rev_req = fcf_req / m
        cagr = (rev_req / base_revenue) ** (1 / n) - 1 if base_revenue else None
        rows.append({"margin": m, "revenue_required": rev_req, "implied_cagr": cagr})
    return {"ev": ev, "pv_interim": pv_interim, "fcf_required": fcf_req, "rows": rows}

def calibrate(price, lo, hi):
    """预注册标定规则：区间外 ±15% 为缓冲带；越界 >50% 记'显著'。"""
    if price < lo * 0.85:
        return "显著低估" if price < lo * 0.50 else "低估"
    if price > hi * 1.15:
        return "显著高估" if price > hi * 1.50 else "高估"
    return "合理（区间内或贴近）"

# ---------- 盈利能力价值 EPV / 三要素（Greenwald）----------

def epv_value(e, coc, basis='NOPAT', net_debt=0.0, excess_cash=0.0):
    """盈利能力价值（零增长永续年金）。
    NOPAT 口径：企业价值 EV = E/coc（coc 即 WACC，与 skill 口径一致），权益 = EV − 净债 + 过剩现金。
    净利润口径：coc 视作权益成本，E/coc 直接得权益价值（不再减净债）。"""
    assert coc > 0, 'coc 必须为正'
    if basis.upper() == 'NOPAT':
        ev = e / coc
        return {'ev': ev, 'equity': ev - net_debt + excess_cash}
    ev = e / coc
    return {'ev': None, 'equity': ev}

def franchise_growth_value(e, coc, g, roiic, basis='NOPAT', net_debt=0.0, excess_cash=0.0):
    """严格 franchise-growth（Greenwald）：只有 ROIIC>coc 的增长才创造价值。
    价值 = E×(1 − g/ROIIC)/(coc − g)。要求 g<coc 才收敛；否则返回 None 交上层兜底。
    ROIIC=coc → 结果=EPV（增长不增值）；ROIIC<coc → 结果<EPV（增长毁灭价值）。"""
    if roiic is None or roiic <= 0 or not (coc > g):
        return None
    v = e * (1 - g / roiic) / (coc - g)
    if basis.upper() == 'NOPAT':
        return {'ev': v, 'equity': v - net_debt + excess_cash}
    return {'ev': None, 'equity': v}

def moat_verdict(ratio):
    if ratio < 1.0:  return 'EPV<净资产 → 管理层毁灭价值（ROIC<资本成本），规避'
    if ratio <= 1.3: return 'EPV≈净资产 → 无/弱护城河的辛苦生意（对手可复制）'
    return 'EPV≫净资产 → 护城河的财务度量（差额=特许经营价值）'

def run_epv(c):
    basis = c.get('earnings_basis', 'NOPAT')
    e, coc = c['normalized_earnings'], c['coc']
    nd, xc = c.get('net_debt', 0.0), c.get('excess_cash', 0.0)
    sh, av, price = c['shares'], c.get('asset_value'), c.get('price')
    print(f"\n=== 盈利能力价值 EPV === 口径 {basis} | 常态化盈利 {e} | 资本成本(=WACC) {coc:.2%}")
    if basis.upper() != 'NOPAT':
        print("  [注] 数据不足/复杂，退回净利润口径（coc 视作权益成本，未剔除资本结构影响）")
    ep = epv_value(e, coc, basis, nd, xc)
    epv_ps = ep['equity'] / sh
    print(f"  EPV 权益价值 {ep['equity']:,.1f} | 每股 {epv_ps:,.2f}" +
          (f" | EV {ep['ev']:,.1f} − 净债 {nd} + 过剩现金 {xc}" if ep['ev'] is not None else ""))
    if av:
        ratio = ep['equity'] / av
        print(f"  护城河验证：EPV/调整后净资产 = {ep['equity']:,.1f}/{av:,.1f} = {ratio:.2f}x → {moat_verdict(ratio)}")
    if c.get('asset_series'):
        print("  EPV/净资产 多年趋势（须长期稳定才算护城河，单年暴涨多是景气非壁垒）：")
        for yr, ee, aa in c['asset_series']:
            print(f"    {yr}: EPV {ee/coc:,.1f} / 净资产 {aa:,.1f} = {(ee/coc)/aa:.2f}x")
    growth_ps = None
    g = c.get('growth')
    if g:
        gg, roiic, mode = g['g'], g.get('roiic'), g.get('mode', 'franchise')
        fg = franchise_growth_value(e, coc, gg, roiic, basis, nd, xc) if mode == 'franchise' else None
        if fg is None:
            gv = ep['equity'] * (1 + gg)
            growth_ps = gv / sh
            why = ('franchise 式无法收敛(g≥WACC 或缺 ROIIC)，' if mode == 'franchise' else '') + '按简化式 EPV×(1+g) 兜底'
            print(f"  成长价值（{why}）：g={gg:.1%} → 每股 {growth_ps:,.2f}")
        else:
            growth_ps = fg['equity'] / sh
            prem = (fg['equity'] / ep['equity'] - 1) * 100
            warn = ' ⚠ ROIIC<WACC，增长毁灭价值' if roiic < coc else ''
            print(f"  成长价值（franchise 严格式，g={gg:.1%}，ROIIC={roiic:.1%}）：每股 {growth_ps:,.2f}（较 EPV {prem:+.0f}%）{warn}")
    if av and price:
        asset_ps = av / sh
        print(f"\n  买点阶梯（每股）：底价 {asset_ps:,.2f}｜EPV {epv_ps:,.2f}" +
              (f"｜成长调整 {growth_ps:,.2f}" if growth_ps else ""))
        if price <= asset_ps: zone = '≤底价：极端安全（烟蒂，须先排除价值毁灭陷阱）'
        elif price <= epv_ps: zone = '底价~EPV：黄金击球区（买到当前盈利，成长白送）'
        elif growth_ps and price <= max(epv_ps, growth_ps): zone = 'EPV~成长调整：合理，为部分成长付费，安全边际薄'
        else: zone = '＞成长调整价值：偏贵，盈利+成长已充分 price in'
        print(f"  现价 {price} → {zone}")
        if growth_ps and growth_ps > epv_ps:
            lo_r, hi_r, tag = epv_ps, growth_ps, "range_low=EPV、range_high=成长调整"
        else:
            lo_r, hi_r, tag = asset_ps, epv_ps, "range_low=底价、range_high=EPV（成长未增值，不计成长溢价）"
        print(f"  （可令 {tag}：[{lo_r:.2f}, {hi_r:.2f}] 并入综合区间；最终标签仍按 valuation-methods.md 第8节规则产出）")

# ---------- 输出 ----------

def run(cfg):
    shares, nd = cfg["shares"], cfg.get("net_debt", 0.0)
    wacc, g = cfg["wacc"], cfg["terminal_g"]
    price = cfg.get("price")

    print(f"=== 输入 === 股本 {shares} | 净债 {nd} | WACC {wacc:.2%} | g {g:.2%}"
          + (f" | 现价 {price}" if price else ""))

    weighted, probs = 0.0, 0.0
    results = {}
    if cfg.get("scenarios"):
        print("\n=== 情景 DCF ===")
        for sc in cfg["scenarios"]:
            r = dcf_value(sc, wacc, g, shares, nd)
            results[sc["name"]] = r
            p = sc.get("prob", 0.0); probs += p; weighted += p * r["per_share"]
            print(f"  {sc['name']:<8} p={p:.0%}  EV {r['ev']:>9,.0f} | 每股 {r['per_share']:>7,.1f} "
                  f"| 稳态首年FCF {r['terminal_fcf']:>7,.1f} | 退出P/FCF {r['exit_pfcf']:.1f}x "
                  f"| 期末股本 {r['shares_end']:.2f}")
        if abs(probs - 1.0) > 1e-6:
            print(f"  [警告] 概率和 = {probs:.2f} ≠ 1，加权值不可用")
        else:
            print(f"  ── 概率加权公允价值: {weighted:,.1f}/股"
                  + (f"（较现价 {(weighted/price-1):+.0%}）" if price else ""))

    sens = cfg.get("sensitivity")
    if sens and cfg.get("scenarios"):
        sc = next(s for s in cfg["scenarios"] if s["name"] == sens["scenario"])
        print(f"\n=== 敏感性（{sens['scenario']}，每股） ===")
        print("            " + "".join(f"g={gg:.1%}  " for gg in sens["g"]))
        for w in sens["wacc"]:
            cells = "".join(f"{dcf_value(sc, w, gg, shares, nd)['per_share']:>7,.1f} " for gg in sens["g"])
            print(f"  WACC {w:.1%} {cells}")

    rev = cfg.get("reverse")
    if rev and price:
        r = reverse_dcf(price, shares, nd, wacc, g, rev["interim_fcf"],
                        rev["steady_margins"], rev.get("base_revenue"))
        print(f"\n=== 反向 DCF ===  EV {r['ev']:,.0f} | 建设期FCF现值 {r['pv_interim']:,.0f}")
        print(f"  现价隐含稳态首年 FCF: {r['fcf_required']:,.0f}/年")
        for row in r["rows"]:
            cagr = f"，隐含营收 CAGR {row['implied_cagr']:.0%}" if row["implied_cagr"] is not None else ""
            print(f"    @FCF率 {row['margin']:.0%} → 需营收 {row['revenue_required']:,.0f}{cagr}")

    if price and cfg.get("range_low") and cfg.get("range_high"):
        lo, hi = cfg["range_low"], cfg["range_high"]
        print(f"\n=== 标定 === 综合区间 [{lo}, {hi}] × 现价 {price} → **{calibrate(price, lo, hi)}**")
        print("  （动作映射与否决项见 valuation-methods.md 末节，由分析师结合不确定性等级执行）")
    if cfg.get("epv"):
        run_epv(cfg["epv"])
    return results

DEMO = {
    "price": 100.0, "shares": 1.0, "net_debt": 5.0, "wacc": 0.09, "terminal_g": 0.03,
    "scenarios": [
        {"name": "bear", "prob": 0.3, "revenue": [10, 11, 12, 13, 14],
         "fcf_margin": [0.10, 0.12, 0.14, 0.15, 0.16], "fade_years": 3,
         "fade_g_start": 0.05, "annual_dilution": 0.01},
        {"name": "base", "prob": 0.5, "revenue": [10, 12, 14, 17, 20],
         "fcf_margin": [0.12, 0.15, 0.18, 0.20, 0.22], "fade_years": 5,
         "fade_g_start": 0.10, "annual_dilution": 0.01},
        {"name": "bull", "prob": 0.2, "revenue": [10, 13, 17, 22, 28],
         "fcf_margin": [0.14, 0.18, 0.22, 0.25, 0.28], "fade_years": 5,
         "fade_g_start": 0.14, "annual_dilution": 0.02}],
    "sensitivity": {"scenario": "base", "wacc": [0.08, 0.09, 0.10], "g": [0.02, 0.03, 0.04]},
    "reverse": {"interim_fcf": [1.2, 1.8, 2.5, 3.4, 4.4],
                "steady_margins": [0.20, 0.25], "base_revenue": 10},
    "range_low": 45, "range_high": 75,
    "epv": {
        "earnings_basis": "NOPAT", "normalized_earnings": 6.0, "coc": 0.09,
        "net_debt": 5.0, "excess_cash": 0.0, "shares": 1.0, "asset_value": 30.0, "price": 100.0,
        "growth": {"g": 0.04, "roiic": 0.20, "mode": "franchise"},
        "asset_series": [["FY-2", 4.5, 26], ["FY-1", 5.2, 28], ["最新", 6.0, 30]],
    },
}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", help="JSON 假设文件路径")
    ap.add_argument("--demo", action="store_true", help="运行内置示例")
    a = ap.parse_args()
    if a.demo:
        run(DEMO)
    elif a.config:
        with open(a.config) as f:
            run(json.load(f))
    else:
        ap.print_help(); sys.exit(1)
