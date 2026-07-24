#!/usr/bin/env python3
"""equity-research skill · 估值计算器 v2（禁止心算的替代物）

用法：
    python dcf.py --config assumptions.json        # 完整运行
    python dcf.py --demo                           # 内置示例自检

模块：三阶段情景 DCF、概率加权、WACC×g 敏感性、反向 DCF、EPV/三要素、
EVA/剩余收益、PVGO 分解、蒙特卡洛、仓位思维（EV/不对称比/Kelly-lite）、
预注册标定标签。所有输入校验用显式异常（python -O 下依然生效）。

config JSON 顶层字段：price, shares, net_debt, wacc, terminal_g,
scenarios[], sensitivity{}, reverse{}, epv{}, eva{}, pvgo{}, montecarlo{},
range_low, range_high
"""
import argparse, json, math, random, sys

LABELS = ["显著低估", "低估", "合理", "高估", "显著高估"]

def die(msg):
    raise ValueError(f"[配置错误] {msg}")

def need(d, key, ctx):
    if key not in d:
        die(f"{ctx} 缺少必需字段 `{key}`")
    return d[key]

# ---------- 核心计算 ----------

def scenario_fcfs(sc, terminal_g):
    """显式期+衰减期完整 FCF 序列与末年营收。"""
    name = sc.get("name", "?")
    if "fcf" in sc:
        if not isinstance(sc["fcf"], list) or not sc["fcf"]:
            die(f"情景 {name}: fcf 必须是非空数组")
        fcfs = list(sc["fcf"]); rev = None
    else:
        rev_path, m = need(sc, "revenue", f"情景 {name}"), need(sc, "fcf_margin", f"情景 {name}")
        if len(rev_path) != len(m):
            die(f"情景 {name}: revenue({len(rev_path)}) 与 fcf_margin({len(m)}) 长度不等")
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
    if wacc <= g:
        die(f"WACC({wacc}) 必须大于永续增长 g({g})")
    if shares <= 0:
        die(f"股本必须为正（shares={shares}）")
    fcfs, _ = scenario_fcfs(sc, g)
    n = len(fcfs)
    pv = sum(f / (1 + wacc) ** (i + 1) for i, f in enumerate(fcfs))
    tv = fcfs[-1] * (1 + g) / (wacc - g)
    ev = pv + tv / (1 + wacc) ** n
    explicit_years = len(sc.get("fcf", sc.get("revenue", [])))
    sh = shares * (1 + sc.get("annual_dilution", 0.0)) ** explicit_years
    tv_share = (tv / (1 + wacc) ** n) / ev if ev else float("nan")
    return {"ev": ev, "equity": ev - net_debt, "per_share": (ev - net_debt) / sh,
            "shares_end": sh, "terminal_fcf": fcfs[-1],
            "exit_pfcf": tv / fcfs[-1] if fcfs[-1] else float("nan"),
            "tv_share": tv_share}

def reverse_dcf(price, shares, net_debt, wacc, g, interim_fcf, steady_margins, base_revenue):
    if wacc <= g:
        die(f"反向 DCF: WACC({wacc}) 必须大于 g({g})")
    ev = price * shares + net_debt
    n = len(interim_fcf)
    pv_interim = sum(f / (1 + wacc) ** (i + 1) for i, f in enumerate(interim_fcf))
    tv_needed = (ev - pv_interim) * (1 + wacc) ** n
    fcf_req = tv_needed * (wacc - g)
    rows = []
    for m in steady_margins:
        if m <= 0:
            die(f"反向 DCF: steady_margin 必须为正（{m}）")
        rev_req = fcf_req / m
        cagr = (rev_req / base_revenue) ** (1 / n) - 1 if base_revenue else None
        rows.append({"margin": m, "revenue_required": rev_req, "implied_cagr": cagr})
    return {"ev": ev, "pv_interim": pv_interim, "fcf_required": fcf_req, "rows": rows}

def calibrate(price, lo, hi):
    """预注册标定（与 check_research_output.py 及 valuation-methods.md §9 完全一致）。"""
    if lo > hi:
        die(f"标定: range_low({lo}) > range_high({hi})")
    if price < lo * 0.50: return "显著低估"
    if price < lo * 0.85: return "低估"
    if price <= hi * 1.15: return "合理"
    if price <= hi * 1.50: return "高估"
    return "显著高估"

# ---------- EPV / 三要素（Greenwald）----------

def epv_value(e, coc, basis='NOPAT', net_debt=0.0, excess_cash=0.0):
    if coc <= 0:
        die("EPV: coc 必须为正")
    ev = e / coc
    if basis.upper() == 'NOPAT':
        return {'ev': ev, 'equity': ev - net_debt + excess_cash}
    return {'ev': None, 'equity': ev}

def franchise_growth_value(e, coc, g, roiic, basis='NOPAT', net_debt=0.0, excess_cash=0.0):
    if roiic is None or roiic <= 0 or not (coc > g):
        return None
    v = e * (1 - g / roiic) / (coc - g)
    if basis.upper() == 'NOPAT':
        return {'ev': v, 'equity': v - net_debt + excess_cash}
    return {'ev': None, 'equity': v}

def moat_verdict(ratio):
    if ratio < 1.0:  return 'EPV<净资产 → 毁灭价值（ROIC<资本成本），规避'
    if ratio <= 1.3: return 'EPV≈净资产 → 无/弱护城河的辛苦生意'
    return 'EPV≫净资产 → 护城河的财务度量（差额=特许经营价值）'

def run_epv(c):
    basis = c.get('earnings_basis', 'NOPAT')
    e, coc = need(c, 'normalized_earnings', 'epv'), need(c, 'coc', 'epv')
    nd, xc = c.get('net_debt', 0.0), c.get('excess_cash', 0.0)
    sh, av, price = need(c, 'shares', 'epv'), c.get('asset_value'), c.get('price')
    print(f"\n=== 盈利能力价值 EPV === 口径 {basis} | 常态化盈利 {e} | 资本成本(=WACC) {coc:.2%}")
    if basis.upper() != 'NOPAT':
        print("  [注] 退回净利润口径（coc 视作权益成本）")
    ep = epv_value(e, coc, basis, nd, xc)
    epv_ps = ep['equity'] / sh
    print(f"  EPV 权益价值 {ep['equity']:,.1f} | 每股 {epv_ps:,.2f}")
    if av:
        ratio = ep['equity'] / av
        print(f"  护城河验证：EPV/净资产 = {ratio:.2f}x → {moat_verdict(ratio)}")
    if c.get('asset_series'):
        print("  EPV/净资产 多年趋势：")
        for yr, ee, aa in c['asset_series']:
            print(f"    {yr}: {(ee/coc)/aa:.2f}x")
    growth_ps = None
    g = c.get('growth')
    if g:
        gg, roiic, mode = need(g, 'g', 'epv.growth'), g.get('roiic'), g.get('mode', 'franchise')
        fg = franchise_growth_value(e, coc, gg, roiic, basis, nd, xc) if mode == 'franchise' else None
        if fg is None:
            growth_ps = ep['equity'] * (1 + gg) / sh
            print(f"  成长价值（简化式兜底，g={gg:.1%}）：每股 {growth_ps:,.2f}")
        else:
            growth_ps = fg['equity'] / sh
            warn = ' ⚠ ROIIC<coc，增长毁灭价值' if roiic < coc else ''
            print(f"  成长价值（franchise 严格式，g={gg:.1%}，ROIIC={roiic:.1%}）：每股 {growth_ps:,.2f}{warn}")
    if av and price:
        asset_ps = av / sh
        print(f"  买点阶梯：底价 {asset_ps:,.2f}｜EPV {epv_ps:,.2f}" +
              (f"｜成长调整 {growth_ps:,.2f}" if growth_ps else ""))
    return {"epv_ps": epv_ps, "growth_ps": growth_ps}

# ---------- EVA / 剩余收益 ----------

def run_eva(c, top):
    ic = need(c, 'invested_capital', 'eva')
    nopat = need(c, 'nopat', 'eva')
    wacc = c.get('wacc', top.get('wacc'))
    sh = c.get('shares', top.get('shares'))
    nd = c.get('net_debt', top.get('net_debt', 0.0))
    fade = c.get('fade_years', 10)
    growth = c.get('nopat_growth', 0.0)
    rr, roiic = c.get('reinvestment_rate'), c.get('roiic')
    if wacc is None or wacc <= 0: die("eva: 缺少有效 wacc")
    if ic <= 0: die("eva: invested_capital 必须为正")
    roic = nopat / ic
    spread0 = roic - wacc
    print(f"\n=== EVA / 剩余收益 === NOPAT {nopat} | 投入资本 {ic} | ROIC {roic:.1%} | WACC {wacc:.2%} | 超额利差 {spread0:+.1%}")
    if rr is not None and roiic is not None:
        g_implied = rr * roiic
        print(f"  自洽检验：g = 再投资率 {rr:.0%} × ROIIC {roiic:.1%} = {g_implied:.1%}"
              f"（DCF 中假设的增速若高于此值，意味着需要外部资本或假设不自洽）")
    pv_eva, ic_t, nopat_t = 0.0, ic, nopat
    for t in range(1, fade + 1):
        spread_t = spread0 * (1 - t / fade)          # 超额回报线性衰减至 0
        nopat_t = nopat_t * (1 + growth)
        ic_t = nopat_t / (wacc + spread_t) if (wacc + spread_t) > 0 else ic_t
        eva_t = spread_t * ic_t
        pv_eva += eva_t / (1 + wacc) ** t
    value = ic + pv_eva
    equity = value - nd
    print(f"  剩余收益价值：投入资本 {ic:,.1f} + PV(EVA, {fade}年衰减) {pv_eva:,.1f} = EV {value:,.1f}")
    if sh:
        print(f"  权益 {equity:,.1f} | 每股 {equity/sh:,.2f}")
    if spread0 < 0:
        print("  ⚠ 当前 EVA 为负：公司未赚回资本成本，任何增长假设都在放大毁灭")
    return {"per_share": equity / sh if sh else None}

# ---------- PVGO 分解 ----------

def run_pvgo(c, top):
    e = need(c, 'earnings_ps', 'pvgo')          # 每股常态化盈利（或 FCF/股）
    r = c.get('r', top.get('wacc'))
    price = c.get('price', top.get('price'))
    if r is None or r <= 0: die("pvgo: 缺少有效折现率 r")
    if not price: die("pvgo: 缺少 price")
    zg = e / r
    pvgo = price - zg
    pct = pvgo / price
    print(f"\n=== PVGO 分解 === 每股盈利 {e} ÷ r {r:.2%} = 零增长价值 {zg:,.2f}/股")
    print(f"  现价 {price} = 零增长 {zg:,.2f} + 增长期权 PVGO {pvgo:,.2f} → **现价的 {pct:.0%} 在为未来增长付费**")
    if pct > 0.5:
        print("  ⚠ PVGO>50%：报告必须回答“这些增长从哪来、谁买单”（对照 base-rates）")
    return {"pvgo_pct": pct}

# ---------- 蒙特卡洛 ----------

def run_montecarlo(c, top):
    n = c.get('n', 2000)
    rng = random.Random(c.get('seed', 42))
    years = c.get('years', 5)
    rev0 = need(c, 'base_revenue', 'montecarlo')
    gm, gs = need(c, 'growth_mean', 'montecarlo'), need(c, 'growth_std', 'montecarlo')
    ml, mm, mh = need(c, 'margin_low', 'montecarlo'), need(c, 'margin_mode', 'montecarlo'), need(c, 'margin_high', 'montecarlo')
    wl, wh = c.get('wacc_low', top['wacc'] - 0.01), c.get('wacc_high', top['wacc'] + 0.01)
    g = c.get('terminal_g', top.get('terminal_g', 0.03))
    fade = c.get('fade_years', 5)
    shares, nd, price = top.get('shares'), top.get('net_debt', 0.0), top.get('price')
    if not shares: die("montecarlo: 顶层缺少 shares")
    vals = []
    for _ in range(n):
        gr = max(min(rng.gauss(gm, gs), gm + 3 * gs), gm - 3 * gs)   # 截断正态
        mg = rng.triangular(ml, mh, mm)
        wc = rng.uniform(wl, wh)
        if wc <= g: wc = g + 0.005
        rev, fcfs = rev0, []
        for _t in range(years):
            rev *= (1 + gr); fcfs.append(rev * mg)
        for k in range(fade):
            gr_f = gr + (g - gr) * (k + 1) / fade
            rev *= (1 + gr_f); fcfs.append(rev * mg)
        pv = sum(f / (1 + wc) ** (i + 1) for i, f in enumerate(fcfs))
        tv = fcfs[-1] * (1 + g) / (wc - g)
        ev = pv + tv / (1 + wc) ** len(fcfs)
        vals.append((ev - nd) / shares)
    vals.sort()
    q = lambda p: vals[min(int(p * n), n - 1)]
    mean = sum(vals) / n
    print(f"\n=== 蒙特卡洛（n={n}） === 公允价值分布（每股）")
    print(f"  P10 {q(.10):,.1f} | P25 {q(.25):,.1f} | P50 {q(.50):,.1f} | P75 {q(.75):,.1f} | P90 {q(.90):,.1f} | 均值 {mean:,.1f}")
    out = {"p50": q(.50), "mean": mean}
    if price:
        p_loss = sum(1 for v in vals if v < price) / n
        out["p_loss"] = p_loss
        print(f"  P(内在价值 < 现价 {price}) = {p_loss:.0%}  ← “现价买入是错误”的模型概率")
    return out

# ---------- 仓位思维 ----------

def run_position(results, cfg):
    price = cfg.get('price')
    scs = cfg.get('scenarios') or []
    if not price or not results or not scs:
        return
    pairs = [(sc.get('prob', 0.0), results[sc['name']]['per_share']) for sc in scs if sc['name'] in results]
    if not pairs: return
    ev_ret = sum(p * (v / price - 1) for p, v in pairs)
    ups = [(p, v / price - 1) for p, v in pairs if v > price]
    downs = [(p, 1 - v / price) for p, v in pairs if v <= price]
    up_mag = max((v for _, v in ups), default=0.0)
    down_mag = max((v for _, v in downs), default=0.0)
    asym = up_mag / down_mag if down_mag > 0 else float('inf')
    print(f"\n=== 仓位思维 === 概率加权期望收益 EV = {ev_ret:+.0%}")
    print(f"  上行幅度（牛） {up_mag:+.0%} | 下行幅度（熊） {-down_mag:.0%} | 不对称比 {asym:.1f}"
          + ("（<1.5：赔率结构不支持重仓）" if asym < 1.5 else ""))
    p_up = sum(p for p, _ in ups); p_dn = sum(p for p, _ in downs)
    b = sum(p * v for p, v in ups) / p_up if p_up else 0.0
    a = sum(p * v for p, v in downs) / p_dn if p_dn else 0.0
    if a > 0 and b > 0:
        kelly = (p_up * b - p_dn * a) / (a * b)
        lite = max(0.0, min(kelly / 4, 0.15))
        size = "标准" if lite >= 0.08 else ("中" if lite >= 0.04 else ("小" if lite > 0 else "零"))
        print(f"  Kelly-lite（¼Kelly，上限15%）≈ {lite:.0%} → 该赔率结构支持 **{size}仓位**（量级参考，非配置建议）")

# ---------- 主流程 ----------

def run(cfg):
    shares = need(cfg, "shares", "顶层")
    nd = cfg.get("net_debt", 0.0)
    wacc, g = need(cfg, "wacc", "顶层"), need(cfg, "terminal_g", "顶层")
    price = cfg.get("price")
    if shares <= 0: die("shares 必须为正")
    if not (0 < wacc < 0.5): die(f"wacc={wacc} 不在合理范围 (0, 0.5)")

    print(f"=== 输入 === 股本 {shares} | 净债 {nd} | WACC {wacc:.2%} | g {g:.2%}"
          + (f" | 现价 {price}" if price else ""))

    weighted, probs, results = 0.0, 0.0, {}
    if cfg.get("scenarios"):
        print("\n=== 情景 DCF ===")
        for sc in cfg["scenarios"]:
            r = dcf_value(sc, wacc, g, shares, nd)
            results[sc["name"]] = r
            p = sc.get("prob", 0.0); probs += p; weighted += p * r["per_share"]
            tv_warn = " ⚠TV>80%" if r["tv_share"] > 0.80 else ""
            print(f"  {sc['name']:<8} p={p:.0%}  EV {r['ev']:>9,.0f} | 每股 {r['per_share']:>7,.1f} "
                  f"| 退出P/FCF {r['exit_pfcf']:.1f}x | TV占比 {r['tv_share']:.0%}{tv_warn} "
                  f"| 期末股本 {r['shares_end']:.2f}")
        if abs(probs - 1.0) > 1e-6:
            print(f"  [警告] 概率和 = {probs:.2f} ≠ 1，加权值不可用")
        else:
            print(f"  ── 概率加权公允价值: {weighted:,.1f}/股"
                  + (f"（较现价 {(weighted/price-1):+.0%}）" if price else ""))

    sens = cfg.get("sensitivity")
    if sens and cfg.get("scenarios"):
        sc = next((s for s in cfg["scenarios"] if s["name"] == sens["scenario"]), None)
        if sc is None: die(f"sensitivity.scenario `{sens['scenario']}` 不在 scenarios 中")
        print(f"\n=== 敏感性（{sens['scenario']}，每股） ===")
        print("            " + "".join(f"g={gg:.1%}  " for gg in sens["g"]))
        for w in sens["wacc"]:
            cells = "".join(f"{dcf_value(sc, w, gg, shares, nd)['per_share']:>7,.1f} " for gg in sens["g"])
            print(f"  WACC {w:.1%} {cells}")

    rev = cfg.get("reverse")
    if rev and price:
        r = reverse_dcf(price, shares, nd, wacc, g, need(rev, "interim_fcf", "reverse"),
                        need(rev, "steady_margins", "reverse"), rev.get("base_revenue"))
        print(f"\n=== 反向 DCF ===  EV {r['ev']:,.0f} | 建设期FCF现值 {r['pv_interim']:,.0f}")
        print(f"  现价隐含稳态首年 FCF: {r['fcf_required']:,.0f}/年")
        for row in r["rows"]:
            cagr = f"，隐含营收 CAGR {row['implied_cagr']:.0%}" if row["implied_cagr"] is not None else ""
            print(f"    @FCF率 {row['margin']:.0%} → 需营收 {row['revenue_required']:,.0f}{cagr}")

    if cfg.get("pvgo"):        run_pvgo(cfg["pvgo"], cfg)
    if cfg.get("epv"):         run_epv(cfg["epv"])
    if cfg.get("eva"):         run_eva(cfg["eva"], cfg)
    if cfg.get("montecarlo"):  run_montecarlo(cfg["montecarlo"], cfg)
    run_position(results, cfg)

    if price and cfg.get("range_low") and cfg.get("range_high"):
        lo, hi = cfg["range_low"], cfg["range_high"]
        print(f"\n=== 标定 === 综合区间 [{lo}, {hi}] × 现价 {price} → **{calibrate(price, lo, hi)}**")
        print("  （动作映射与否决项见 valuation-methods.md §9，由分析师结合不确定性与财报可信度执行）")
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
    "pvgo": {"earnings_ps": 5.5},
    "epv": {"earnings_basis": "NOPAT", "normalized_earnings": 6.0, "coc": 0.09,
            "net_debt": 5.0, "shares": 1.0, "asset_value": 30.0, "price": 100.0,
            "growth": {"g": 0.04, "roiic": 0.20, "mode": "franchise"},
            "asset_series": [["FY-2", 4.5, 26], ["FY-1", 5.2, 28], ["最新", 6.0, 30]]},
    "eva": {"invested_capital": 40.0, "nopat": 6.0, "fade_years": 10,
            "reinvestment_rate": 0.4, "roiic": 0.20},
    "montecarlo": {"n": 2000, "base_revenue": 10, "years": 5,
                   "growth_mean": 0.14, "growth_std": 0.06,
                   "margin_low": 0.10, "margin_mode": 0.18, "margin_high": 0.26},
}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", help="JSON 假设文件路径")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    try:
        if a.demo:
            run(DEMO)
        elif a.config:
            with open(a.config) as f:
                run(json.load(f))
        else:
            ap.print_help(); sys.exit(1)
    except ValueError as e:
        print(str(e), file=sys.stderr); sys.exit(2)
