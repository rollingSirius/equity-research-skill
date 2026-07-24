#!/usr/bin/env python3
"""equity-research skill · 财务/估值一致性检查器

用法：
    python scripts/check_research_output.py --report report.md --assumptions valuation.json
    python scripts/check_research_output.py --financials financials.csv
    python scripts/check_research_output.py --demo

输入都是可选的；脚本会检查已提供文件中可复算的内容。仅使用 Python 标准库。
"""

import argparse
import csv
import json
import math
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


SEVERITY_RANK = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
LABELS = ["显著低估", "低估", "合理", "高估", "显著高估"]


@dataclass
class Issue:
    severity: str
    code: str
    message: str
    detail: str = ""
    file: str = ""

    def line(self) -> str:
        loc = f" [{self.file}]" if self.file else ""
        detail = f"\n    {self.detail}" if self.detail else ""
        return f"[{self.severity}] {self.code}{loc}: {self.message}{detail}"


def add(issues: List[Issue], severity: str, code: str, message: str, detail: str = "", file: str = "") -> None:
    issues.append(Issue(severity, code, message, detail, file))


def load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_json(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def norm_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.strip().lower())


def parse_number(value) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return None
        return float(value)
    s = str(value).strip()
    if not s or s in {"-", "—", "N/A", "NA", "n/a", "未获取到"}:
        return None
    mult = 1.0
    if s.endswith("%"):
        mult = 0.01
        s = s[:-1]
    s = s.replace(",", "").replace("$", "").replace("￥", "").replace("¥", "")
    s = s.replace("倍", "").replace("x", "").replace("X", "")
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    if not m:
        return None
    return float(m.group(0)) * mult


def pct(value: float) -> str:
    return f"{value:.1%}"


def close_enough(a: float, b: float, rel_tol: float = 0.015, abs_tol: float = 0.02) -> bool:
    return abs(a - b) <= max(abs_tol, rel_tol * max(abs(a), abs(b), 1.0))




def detect_labels(text: str) -> List[str]:
    """长标签优先匹配，避免“显著低估”被同时计为“低估”。"""
    found: List[str] = []
    masked = text
    for label in sorted(LABELS, key=len, reverse=True):
        if label in masked:
            found.append(label)
            masked = masked.replace(label, "■" * len(label))
    return found

def calibrate(price: float, lo: float, hi: float) -> str:
    if price < lo * 0.50:
        return "显著低估"
    if price < lo * 0.85:
        return "低估"
    if price <= hi * 1.15:
        return "合理"
    if price <= hi * 1.50:
        return "高估"
    return "显著高估"


def load_csv(path: str) -> Tuple[List[Dict[str, str]], Dict[str, str]]:
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    aliases = {norm_key(k): k for k in (reader.fieldnames or [])}
    return rows, aliases


def pick(aliases: Dict[str, str], names: Sequence[str]) -> Optional[str]:
    for name in names:
        key = norm_key(name)
        if key in aliases:
            return aliases[key]
    return None


def row_num(row: Dict[str, str], col: Optional[str]) -> Optional[float]:
    return parse_number(row.get(col)) if col else None


def check_report(path: str, assumptions: Optional[Dict], issues: List[Issue]) -> None:
    text = load_text(path)
    lower = text.lower()

    if "数据来源" not in text and "来源" not in text:
        add(issues, "P1", "REPORT_NO_SOURCE_SECTION", "报告未发现来源清单或来源说明。", file=path)
    if not re.search(r"20\d{2}[-年/.]\d{1,2}", text):
        add(issues, "P2", "REPORT_NO_TIMESTAMP", "报告未发现明确日期或时间戳。", file=path)
    if "未获取到" not in text:
        add(issues, "P3", "REPORT_NO_MISSING_DATA_MARKER", "报告未出现“未获取到”；若确无缺失数据可忽略。", file=path)
    if "我的判断" not in text:
        add(issues, "P2", "REPORT_NO_JUDGMENT_MARKER", "报告未显式标注“我的判断”，事实与判断可能混在一起。", file=path)
    if "scripts/dcf.py" not in text and "dcf.py" not in lower:
        add(issues, "P2", "REPORT_NO_DCF_SCRIPT_EVIDENCE", "报告未说明 DCF/EPV 由脚本执行。", file=path)
    if "反向 dcf" not in lower and "反向DCF" not in text:
        add(issues, "P2", "REPORT_NO_REVERSE_DCF", "报告未发现反向 DCF 框架。", file=path)
    if "情景" not in text and "scenario" not in lower:
        add(issues, "P2", "REPORT_NO_SCENARIO_VALUATION", "报告未发现情景估值或概率加权讨论。", file=path)
    if "epv" not in lower and "盈利能力价值" not in text and "三要素" not in text:
        add(issues, "P2", "REPORT_NO_EPV", "报告未发现 EPV/三要素估值交叉验证。", file=path)

    if assumptions:
        price = parse_number(assumptions.get("price"))
        lo = parse_number(assumptions.get("range_low"))
        hi = parse_number(assumptions.get("range_high"))
        if price is not None and lo is not None and hi is not None and hi >= lo:
            expected = calibrate(price, lo, hi)
            found_labels = detect_labels(text)
            if expected not in found_labels:
                add(
                    issues,
                    "P1",
                    "REPORT_VALUATION_LABEL_MISMATCH",
                    f"报告结论未发现按规则应出现的估值标签：{expected}。",
                    f"price={price}, range=[{lo}, {hi}], report_labels={found_labels or 'none'}",
                    path,
                )


def check_assumptions(path: str, issues: List[Issue]) -> Dict:
    cfg = load_json(path)
    price = parse_number(cfg.get("price"))
    shares = parse_number(cfg.get("shares"))
    wacc = parse_number(cfg.get("wacc"))
    g = parse_number(cfg.get("terminal_g"))
    lo = parse_number(cfg.get("range_low"))
    hi = parse_number(cfg.get("range_high"))

    for key, value in [("price", price), ("shares", shares), ("wacc", wacc), ("terminal_g", g)]:
        if value is None:
            add(issues, "P2", "ASSUMPTION_MISSING_CORE_FIELD", f"估值假设缺少核心字段 `{key}`。", file=path)

    if wacc is not None and g is not None:
        if wacc <= g:
            add(issues, "P0", "DCF_WACC_NOT_ABOVE_G", "WACC 必须大于永续增长率 g。", f"wacc={wacc}, terminal_g={g}", path)
        if not 0.03 <= wacc <= 0.20:
            add(issues, "P2", "DCF_WACC_UNUSUAL", "WACC 超出常见区间，请确认口径。", f"wacc={pct(wacc)}", path)
        if not -0.02 <= g <= 0.05:
            add(issues, "P2", "DCF_TERMINAL_G_UNUSUAL", "永续增长率 g 超出常见区间，请确认长期名义增长锚。", f"g={pct(g)}", path)

    if shares is not None and shares <= 0:
        add(issues, "P0", "SHARES_NON_POSITIVE", "股本必须为正数。", f"shares={shares}", path)
    if lo is not None and hi is not None:
        if lo > hi:
            add(issues, "P0", "VALUATION_RANGE_INVERTED", "综合估值区间下限高于上限。", f"range_low={lo}, range_high={hi}", path)

    scenarios = cfg.get("scenarios") or []
    if not scenarios:
        add(issues, "P1", "DCF_NO_SCENARIOS", "估值假设未包含 scenarios，无法检查三情景概率加权 DCF。", file=path)
    else:
        prob_sum = 0.0
        seen = set()
        for idx, sc in enumerate(scenarios):
            name = str(sc.get("name") or f"scenario_{idx}")
            if name in seen:
                add(issues, "P2", "DCF_DUPLICATE_SCENARIO", "情景名称重复。", name, path)
            seen.add(name)
            prob = parse_number(sc.get("prob"))
            if prob is None:
                add(issues, "P1", "DCF_SCENARIO_MISSING_PROB", "情景缺少概率。", name, path)
            else:
                prob_sum += prob
                if prob < 0 or prob > 1:
                    add(issues, "P0", "DCF_SCENARIO_PROB_OUT_OF_RANGE", "情景概率必须在 0 到 1 之间。", f"{name}: prob={prob}", path)
            if "fcf" not in sc:
                revenue = sc.get("revenue")
                margin = sc.get("fcf_margin")
                if not isinstance(revenue, list) or not isinstance(margin, list):
                    add(issues, "P1", "DCF_SCENARIO_NO_FCF_OR_DRIVERS", "情景必须提供 fcf，或 revenue + fcf_margin。", name, path)
                elif len(revenue) != len(margin):
                    add(issues, "P0", "DCF_DRIVER_LENGTH_MISMATCH", "revenue 与 fcf_margin 长度不一致。", f"{name}: revenue={len(revenue)}, fcf_margin={len(margin)}", path)
            dilution = parse_number(sc.get("annual_dilution", 0))
            if dilution is not None and (dilution < -0.20 or dilution > 0.20):
                add(issues, "P2", "DCF_DILUTION_UNUSUAL", "年化股本变化超出常见区间，请确认。", f"{name}: annual_dilution={pct(dilution)}", path)
        if abs(prob_sum - 1.0) > 0.005:
            add(issues, "P1", "DCF_PROBABILITY_SUM_NOT_ONE", "情景概率之和不等于 1。", f"prob_sum={prob_sum:.4f}", path)

    epv = cfg.get("epv")
    if epv:
        e = parse_number(epv.get("normalized_earnings"))
        coc = parse_number(epv.get("coc"))
        epv_shares = parse_number(epv.get("shares"))
        if e is None or coc is None or epv_shares is None:
            add(issues, "P1", "EPV_MISSING_CORE_FIELD", "EPV 块缺少 normalized_earnings / coc / shares。", file=path)
        if coc is not None and coc <= 0:
            add(issues, "P0", "EPV_COC_NON_POSITIVE", "EPV 资本成本必须为正。", f"coc={coc}", path)
        growth = epv.get("growth") or {}
        gg = parse_number(growth.get("g"))
        roiic = parse_number(growth.get("roiic"))
        if gg is not None and coc is not None and gg >= coc:
            add(issues, "P1", "EPV_G_NOT_BELOW_COC", "franchise 成长公式要求 g < 资本成本；否则需说明使用兜底简化式。", f"g={gg}, coc={coc}", path)
        if roiic is not None and coc is not None and roiic < coc:
            add(issues, "P2", "EPV_ROIIC_BELOW_COC", "ROIIC 低于资本成本，增长可能毁灭价值。", f"roiic={pct(roiic)}, coc={pct(coc)}", path)
    else:
        add(issues, "P2", "EPV_BLOCK_MISSING", "估值假设未包含 epv 块，难以复核三要素/EPV 估值。", file=path)

    return cfg


def check_ratio(
    issues: List[Issue],
    path: str,
    row_label: str,
    row: Dict[str, str],
    numerator_col: Optional[str],
    denominator_col: Optional[str],
    provided_col: Optional[str],
    code: str,
    name: str,
    tolerance: float = 0.006,
) -> None:
    if not numerator_col or not denominator_col or not provided_col:
        return
    num = row_num(row, numerator_col)
    den = row_num(row, denominator_col)
    provided = row_num(row, provided_col)
    if num is None or den in (None, 0) or provided is None:
        return
    expected = num / den
    if abs(expected - provided) > tolerance:
        add(
            issues,
            "P1",
            code,
            f"{row_label} 的{name}与原始数值不一致。",
            f"expected={pct(expected)}, provided={pct(provided)}, numerator={num}, denominator={den}",
            path,
        )


def check_growth(
    issues: List[Issue],
    path: str,
    rows: List[Dict[str, str]],
    period_col: Optional[str],
    value_col: Optional[str],
    provided_col: Optional[str],
    lag: int,
    code: str,
    name: str,
) -> None:
    if not value_col or not provided_col or len(rows) <= lag:
        return
    for idx in range(lag, len(rows)):
        cur = row_num(rows[idx], value_col)
        prev = row_num(rows[idx - lag], value_col)
        provided = row_num(rows[idx], provided_col)
        label = rows[idx].get(period_col, f"row {idx + 2}") if period_col else f"row {idx + 2}"
        if cur is None or prev in (None, 0) or provided is None:
            continue
        expected = cur / prev - 1
        if abs(expected - provided) > 0.015:
            add(
                issues,
                "P1",
                code,
                f"{label} 的{name}与序列计算不一致。",
                f"expected={pct(expected)}, provided={pct(provided)}, current={cur}, prior={prev}",
                path,
            )




def growth_rate(cur, prev):
    if cur is None or prev in (None, 0):
        return None
    return cur / prev - 1


def check_forensics(rows, aliases, path, issues) -> None:
    """财报质量核查检查：应计质量 / 现金转化 / DSO与递延背离 / Beneish M-Score。
    列名要求见 references/forensic-accounting.md 第 7 节；缺列自动跳过对应项。"""
    ni = pick(aliases, ["net_income", "netincome", "净利润"])
    cfo = pick(aliases, ["cfo", "operating_cash_flow", "cash_from_operations", "经营现金流"])
    ta = pick(aliases, ["total_assets", "totalassets", "总资产"])
    rev = pick(aliases, ["revenue", "sales", "收入", "营收"])
    rec = pick(aliases, ["receivables", "accounts_receivable", "应收账款", "应收"])
    dfr = pick(aliases, ["deferred_revenue", "contract_liabilities", "递延收入", "合同负债"])
    gp = pick(aliases, ["gross_profit", "grossprofit", "毛利"])
    ppe = pick(aliases, ["ppe", "net_ppe", "固定资产"])
    ca = pick(aliases, ["current_assets", "流动资产"])
    dep = pick(aliases, ["depreciation", "折旧"])
    sga = pick(aliases, ["sga", "sg_a", "销售管理费用"])
    tl = pick(aliases, ["total_liabilities", "totalliabilities", "总负债"])

    # -- 应计比率与现金转化（逐行 + 趋势） --
    conv_series = []
    for idx, row in enumerate(rows):
        label = row.get(pick(aliases, ["period", "fiscal_period", "date", "财期", "期间"]) or "", f"row {idx + 2}")
        ni_v, cfo_v, ta_v = row_num(row, ni), row_num(row, cfo), row_num(row, ta)
        if ni_v is not None and cfo_v is not None and ta_v not in (None, 0):
            accr = (ni_v - cfo_v) / ta_v
            if accr > 0.10:
                add(issues, "P1", "FORENSIC_HIGH_ACCRUALS", f"{label} 总应计比率 {accr:.1%} > 10%，盈利质量红旗。",
                    f"net_income={ni_v}, cfo={cfo_v}, total_assets={ta_v}", path)
            elif accr > 0.05:
                add(issues, "P2", "FORENSIC_ELEVATED_ACCRUALS", f"{label} 总应计比率 {accr:.1%} 偏高（5–10%）。", "", path)
        if ni_v not in (None, 0) and cfo_v is not None and ni_v > 0:
            conv_series.append((label, cfo_v / ni_v))
    if len(conv_series) >= 3:
        last = conv_series[-1][1]
        declining = all(conv_series[i][1] >= conv_series[i + 1][1] for i in range(len(conv_series) - 3, len(conv_series) - 1))
        if last < 0.8 and declining:
            add(issues, "P2", "FORENSIC_CASH_CONVERSION_DECLINING",
                f"现金转化率降至 {last:.0%}（<80% 且连续下滑），利润与现金背离。",
                ", ".join(f"{l}={v:.0%}" for l, v in conv_series[-3:]), path)

    # -- DSO / 递延收入 与收入增速背离（末两行） --
    if len(rows) >= 2 and rev:
        r_g = growth_rate(row_num(rows[-1], rev), row_num(rows[-2], rev))
        if rec:
            rec_g = growth_rate(row_num(rows[-1], rec), row_num(rows[-2], rec))
            if r_g is not None and rec_g is not None and rec_g - r_g > 0.15:
                add(issues, "P2", "FORENSIC_DSO_DIVERGENCE",
                    f"应收增速 {rec_g:.0%} 超收入增速 {r_g:.0%} 逾 15pp，警惕塞货/放宽信用/提前确认。", "", path)
        if dfr:
            d_g = growth_rate(row_num(rows[-1], dfr), row_num(rows[-2], dfr))
            if r_g is not None and d_g is not None and r_g > 0 and d_g < 0:
                add(issues, "P2", "FORENSIC_DEFERRED_DIVERGENCE",
                    f"收入增长 {r_g:.0%} 而递延收入下降 {d_g:.0%}，订阅型公司此为透支未来信号。", "", path)

    # -- Beneish M-Score（末两行，需全列） --
    needed = [rev, rec, gp, ppe, ca, dep, sga, tl, ta, ni, cfo]
    if len(rows) >= 2 and all(needed):
        t, p = rows[-1], rows[-2]
        try:
            def v(row, col):
                x = row_num(row, col)
                if x is None:
                    raise ValueError(col)
                return x
            dsri = (v(t, rec) / v(t, rev)) / (v(p, rec) / v(p, rev))
            gmi = (v(p, gp) / v(p, rev)) / (v(t, gp) / v(t, rev))
            aqi_t = 1 - (v(t, ca) + v(t, ppe)) / v(t, ta)
            aqi_p = 1 - (v(p, ca) + v(p, ppe)) / v(p, ta)
            aqi = aqi_t / aqi_p if aqi_p else 1.0
            sgi = v(t, rev) / v(p, rev)
            depi = (v(p, dep) / (v(p, dep) + v(p, ppe))) / (v(t, dep) / (v(t, dep) + v(t, ppe)))
            sgai = (v(t, sga) / v(t, rev)) / (v(p, sga) / v(p, rev))
            tata = (v(t, ni) - v(t, cfo)) / v(t, ta)
            lvgi = (v(t, tl) / v(t, ta)) / (v(p, tl) / v(p, ta))
            m = (-4.84 + 0.92 * dsri + 0.528 * gmi + 0.404 * aqi + 0.892 * sgi
                 + 0.115 * depi - 0.172 * sgai + 4.679 * tata - 0.327 * lvgi)
            detail = (f"M={m:.2f} | DSRI={dsri:.2f} GMI={gmi:.2f} AQI={aqi:.2f} SGI={sgi:.2f} "
                      f"DEPI={depi:.2f} SGAI={sgai:.2f} TATA={tata:.3f} LVGI={lvgi:.2f}")
            if m > -1.78:
                add(issues, "P1", "FORENSIC_MSCORE_FLAG",
                    f"Beneish M-Score = {m:.2f} > -1.78，落入盈余操纵可疑区，逐项手工核查。", detail, path)
            else:
                add(issues, "P3", "FORENSIC_MSCORE_INFO", f"Beneish M-Score = {m:.2f}（阈值 -1.78，未越限）。", detail, path)
        except (ValueError, ZeroDivisionError):
            add(issues, "P3", "FORENSIC_MSCORE_SKIPPED", "M-Score 所需列存在但含缺失/零值，跳过计算。", "", path)


def check_financials(path: str, issues: List[Issue]) -> None:
    rows, aliases = load_csv(path)
    if not rows:
        add(issues, "P1", "FINANCIALS_EMPTY", "财务 CSV 没有数据行。", file=path)
        return

    period = pick(aliases, ["period", "fiscal_period", "date", "财期", "期间"])
    revenue = pick(aliases, ["revenue", "sales", "收入", "营收"])
    gross_profit = pick(aliases, ["gross_profit", "grossprofit", "毛利"])
    operating_income = pick(aliases, ["operating_income", "operatingincome", "ebit", "营业利润", "经营利润"])
    net_income = pick(aliases, ["net_income", "netincome", "净利润"])
    cfo = pick(aliases, ["cfo", "operating_cash_flow", "cash_from_operations", "经营现金流"])
    capex = pick(aliases, ["capex", "capital_expenditure", "capitalexpenditure", "资本开支"])
    fcf = pick(aliases, ["fcf", "free_cash_flow", "freecashflow", "自由现金流"])
    shares = pick(aliases, ["shares", "diluted_shares", "share_count", "股本", "稀释股数"])
    eps = pick(aliases, ["eps", "diluted_eps", "每股收益"])
    cash_begin = pick(aliases, ["cash_begin", "beginning_cash", "期初现金"])
    cash_end = pick(aliases, ["cash_end", "ending_cash", "期末现金"])
    cfi = pick(aliases, ["cfi", "investing_cash_flow", "投资现金流"])
    cff = pick(aliases, ["cff", "financing_cash_flow", "融资现金流"])
    gross_margin = pick(aliases, ["gross_margin", "grossmargin", "毛利率"])
    operating_margin = pick(aliases, ["operating_margin", "operatingmargin", "营业利润率", "经营利润率"])
    net_margin = pick(aliases, ["net_margin", "netmargin", "净利率"])
    fcf_margin = pick(aliases, ["fcf_margin", "fcfmargin", "自由现金流率"])
    yoy_revenue = pick(aliases, ["revenue_yoy", "yoy_revenue", "营收同比"])
    qoq_revenue = pick(aliases, ["revenue_qoq", "qoq_revenue", "营收环比"])

    if not period:
        add(issues, "P2", "FINANCIALS_NO_PERIOD_COLUMN", "财务 CSV 未发现期间列。", file=path)
    if not revenue:
        add(issues, "P1", "FINANCIALS_NO_REVENUE_COLUMN", "财务 CSV 未发现收入列，很多比率无法复核。", file=path)

    for idx, row in enumerate(rows):
        label = row.get(period, f"row {idx + 2}") if period else f"row {idx + 2}"
        check_ratio(issues, path, label, row, gross_profit, revenue, gross_margin, "GROSS_MARGIN_MISMATCH", "毛利率")
        check_ratio(issues, path, label, row, operating_income, revenue, operating_margin, "OPERATING_MARGIN_MISMATCH", "经营利润率")
        check_ratio(issues, path, label, row, net_income, revenue, net_margin, "NET_MARGIN_MISMATCH", "净利率")
        check_ratio(issues, path, label, row, fcf, revenue, fcf_margin, "FCF_MARGIN_MISMATCH", "自由现金流率")

        cfo_v = row_num(row, cfo)
        capex_v = row_num(row, capex)
        fcf_v = row_num(row, fcf)
        if cfo_v is not None and capex_v is not None and fcf_v is not None:
            expected = cfo_v - abs(capex_v) if capex_v >= 0 else cfo_v + capex_v
            if not close_enough(expected, fcf_v):
                add(issues, "P1", "FCF_RECONCILIATION_MISMATCH", f"{label} 的 FCF 与 CFO/Capex 不一致。", f"expected={expected}, provided={fcf_v}, cfo={cfo_v}, capex={capex_v}", path)

        net_income_v = row_num(row, net_income)
        shares_v = row_num(row, shares)
        eps_v = row_num(row, eps)
        if net_income_v is not None and shares_v not in (None, 0) and eps_v is not None:
            expected = net_income_v / shares_v
            if not close_enough(expected, eps_v, rel_tol=0.025, abs_tol=0.03):
                add(issues, "P2", "EPS_RECONCILIATION_MISMATCH", f"{label} 的 EPS 与净利润/股本不一致，请确认单位。", f"expected={expected}, provided={eps_v}, net_income={net_income_v}, shares={shares_v}", path)

        if cash_begin and cash_end and cfo and cfi and cff:
            cb = row_num(row, cash_begin)
            ce = row_num(row, cash_end)
            cfo_v = row_num(row, cfo)
            cfi_v = row_num(row, cfi)
            cff_v = row_num(row, cff)
            if None not in (cb, ce, cfo_v, cfi_v, cff_v):
                expected = cb + cfo_v + cfi_v + cff_v
                if not close_enough(expected, ce):
                    add(issues, "P1", "CASH_FLOW_ROLL_FORWARD_MISMATCH", f"{label} 的现金流量表勾稽不一致。", f"expected_ending_cash={expected}, provided={ce}", path)

    check_growth(issues, path, rows, period, revenue, yoy_revenue, 4, "REVENUE_YOY_MISMATCH", "营收同比")
    check_growth(issues, path, rows, period, revenue, qoq_revenue, 1, "REVENUE_QOQ_MISMATCH", "营收环比")

    check_forensics(rows, aliases, path, issues)


def sort_issues(issues: Iterable[Issue]) -> List[Issue]:
    return sorted(issues, key=lambda x: (SEVERITY_RANK.get(x.severity, 9), x.code, x.file))


def print_report(issues: List[Issue], as_json: bool = False) -> None:
    ordered = sort_issues(issues)
    if as_json:
        print(json.dumps([issue.__dict__ for issue in ordered], ensure_ascii=False, indent=2))
        return
    if not ordered:
        print("财务/估值一致性检查通过：未发现可复算异常。")
        return
    counts = {}
    for issue in ordered:
        counts[issue.severity] = counts.get(issue.severity, 0) + 1
    summary = " ".join(f"{sev}={counts.get(sev, 0)}" for sev in ["P0", "P1", "P2", "P3"])
    print(f"财务/估值一致性检查发现 {len(ordered)} 项：{summary}\n")
    for issue in ordered:
        print(issue.line())


def run(args) -> int:
    issues: List[Issue] = []
    assumptions = None
    if args.assumptions:
        assumptions = check_assumptions(args.assumptions, issues)
    if args.report:
        check_report(args.report, assumptions, issues)
    if args.financials:
        check_financials(args.financials, issues)
    if not any([args.report, args.assumptions, args.financials]):
        add(issues, "P1", "NO_INPUT", "请至少提供 --report、--assumptions 或 --financials 之一。")
    print_report(issues, args.json)
    fail_levels = {"P0", "P1"} if not args.strict else {"P0", "P1", "P2"}
    return 1 if any(issue.severity in fail_levels for issue in issues) else 0


def write_demo_files(tmp: str) -> Tuple[str, str, str]:
    report = os.path.join(tmp, "demo_report.md")
    assumptions = os.path.join(tmp, "demo_assumptions.json")
    financials = os.path.join(tmp, "demo_financials.csv")
    with open(report, "w", encoding="utf-8") as f:
        f.write(
            "# Demo 投资结论\n\n"
            "截至 2026-07-21，来源 Demo。我的判断：公司合理。\n\n"
            "估值由 scripts/dcf.py 运行，包含反向 DCF、情景 DCF、EPV / 盈利能力价值。\n\n"
            "数据来源与时间戳：Demo 2026-07-21。未获取到：无。\n"
        )
    with open(assumptions, "w", encoding="utf-8") as f:
        json.dump(
            {
                "price": 100.0,
                "shares": 10.0,
                "net_debt": 5.0,
                "wacc": 0.09,
                "terminal_g": 0.03,
                "range_low": 80.0,
                "range_high": 110.0,
                "scenarios": [
                    {"name": "bear", "prob": 0.3, "revenue": [100, 105], "fcf_margin": [0.10, 0.11]},
                    {"name": "base", "prob": 0.5, "revenue": [100, 115], "fcf_margin": [0.12, 0.14]},
                    {"name": "bull", "prob": 0.2, "revenue": [100, 130], "fcf_margin": [0.15, 0.18]},
                ],
                "epv": {
                    "earnings_basis": "NOPAT",
                    "normalized_earnings": 12.0,
                    "coc": 0.09,
                    "shares": 10.0,
                    "net_debt": 5.0,
                    "growth": {"g": 0.03, "roiic": 0.18},
                },
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    with open(financials, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["period", "revenue", "gross_profit", "gross_margin", "cfo", "capex", "fcf", "fcf_margin"])
        writer.writerow(["Q1", "100", "60", "60%", "30", "10", "20", "20%"])
        writer.writerow(["Q2", "110", "66", "60%", "33", "11", "22", "20%"])
    return report, assumptions, financials


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", help="Markdown 报告路径")
    ap.add_argument("--assumptions", help="估值假设 JSON 路径，建议使用 dcf.py 的 config")
    ap.add_argument("--financials", help="历史/预测财务 CSV 路径")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出检查结果")
    ap.add_argument("--strict", action="store_true", help="P2 也返回非零退出码")
    ap.add_argument("--demo", action="store_true", help="运行内置示例")
    args = ap.parse_args()
    if args.demo:
        with tempfile.TemporaryDirectory() as tmp:
            report, assumptions, financials = write_demo_files(tmp)
            args.report, args.assumptions, args.financials = report, assumptions, financials
            sys.exit(run(args))
    sys.exit(run(args))


if __name__ == "__main__":
    main()
