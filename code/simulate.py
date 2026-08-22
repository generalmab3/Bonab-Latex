#!/usr/bin/env python3
"""Synthetic microgrid experiment: data-driven MLP vs physics-informed MLP."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
RESULTS = ROOT / "code" / "results"
ASSETS.mkdir(exist_ok=True)
RESULTS.mkdir(parents=True, exist_ok=True)

DT = 1.0
E_MAX = 20.0
ETA_CH = 0.95
ETA_DIS = 0.95
SOC_MIN = 0.20
SOC_MAX = 0.90
KAPPA = 0.02
SEED = 7
EPOCHS = 350
BATCH = 64
HIDDEN = 48
LR = 8e-4


@dataclass
class Series:
    t: np.ndarray
    p_load: np.ndarray
    p_pv: np.ndarray
    c_buy: np.ndarray
    c_sell: np.ndarray
    soc: np.ndarray
    p_grid: np.ndarray
    p_ch: np.ndarray
    p_dis: np.ndarray
    soc_next: np.ndarray


def make_profiles(hours: int, rng: np.random.Generator) -> Series:
    t = np.arange(hours, dtype=np.float64)
    hod = t % 24
    p_load = (
        2.4
        + 0.9 * np.sin((hod - 8) * np.pi / 12)
        + 0.35 * (hod >= 18) * (hod <= 22)
        + 0.12 * rng.normal(size=hours)
    )
    p_load = np.clip(p_load, 0.6, None)
    daylight = np.clip(np.sin((hod - 6) * np.pi / 12), 0.0, None)
    p_pv = 4.2 * daylight**1.4 + 0.08 * rng.normal(size=hours)
    p_pv = np.clip(p_pv, 0.0, None)
    c_buy = 0.18 + 0.10 * (hod >= 17) * (hod <= 21) + 0.01 * rng.normal(size=hours)
    c_buy = np.clip(c_buy, 0.10, None)
    c_sell = 0.55 * c_buy

    soc = np.zeros(hours)
    p_grid = np.zeros(hours)
    p_ch = np.zeros(hours)
    p_dis = np.zeros(hours)
    soc_next = np.zeros(hours)
    soc[0] = 0.55
    for i in range(hours):
        s = soc[i]
        surplus = p_pv[i] - p_load[i]
        ch = dis = 0.0
        if surplus > 0.05 and s < SOC_MAX - 1e-3:
            room = (SOC_MAX - s) * E_MAX / (ETA_CH * DT)
            ch = float(min(surplus, room, 2.5))
        elif surplus < -0.05 and s > SOC_MIN + 1e-3:
            avail = (s - SOC_MIN) * E_MAX * ETA_DIS / DT
            dis = float(min(-surplus, avail, 2.5))
        grid = p_load[i] + ch - p_pv[i] - dis
        nxt = s + ETA_CH * ch * DT / E_MAX - dis * DT / (ETA_DIS * E_MAX)
        nxt = float(np.clip(nxt, SOC_MIN, SOC_MAX))
        p_ch[i], p_dis[i], p_grid[i], soc_next[i] = ch, dis, grid, nxt
        if i + 1 < hours:
            soc[i + 1] = nxt
    return Series(t, p_load, p_pv, c_buy, c_sell, soc, p_grid, p_ch, p_dis, soc_next)


def stack_x(s: Series) -> np.ndarray:
    tnorm = (s.t % 24) / 24.0
    return np.column_stack([tnorm, s.p_load, s.p_pv, s.c_buy, s.c_sell, s.soc])


def stack_y(s: Series) -> np.ndarray:
    return np.column_stack([s.p_grid, s.p_ch, s.p_dis, s.soc_next])


class MLP:
    def __init__(self, rng: np.random.Generator, n_in=6, n_out=4, width=HIDDEN):
        scale = lambda a, b: rng.normal(0.0, np.sqrt(2.0 / a), size=(a, b))
        self.w1 = scale(n_in, width)
        self.b1 = np.zeros(width)
        self.w2 = scale(width, width)
        self.b2 = np.zeros(width)
        self.w3 = scale(width, n_out)
        self.b3 = np.zeros(n_out)
        self.mw = [np.zeros_like(self.w1), np.zeros_like(self.w2), np.zeros_like(self.w3)]
        self.mb = [np.zeros_like(self.b1), np.zeros_like(self.b2), np.zeros_like(self.b3)]
        self.vw = [np.zeros_like(self.w1), np.zeros_like(self.w2), np.zeros_like(self.w3)]
        self.vb = [np.zeros_like(self.b1), np.zeros_like(self.b2), np.zeros_like(self.b3)]
        self.t = 0

    def forward(self, x):
        h1 = np.tanh(x @ self.w1 + self.b1)
        h2 = np.tanh(h1 @ self.w2 + self.b2)
        y = h2 @ self.w3 + self.b3
        return y, (x, h1, h2)

    def adam(self, gw, gb, lr=LR, b1=0.9, b2=0.999, eps=1e-8):
        self.t += 1
        for i in range(3):
            self.mw[i] = b1 * self.mw[i] + (1 - b1) * gw[i]
            self.mb[i] = b1 * self.mb[i] + (1 - b1) * gb[i]
            self.vw[i] = b2 * self.vw[i] + (1 - b2) * (gw[i] ** 2)
            self.vb[i] = b2 * self.vb[i] + (1 - b2) * (gb[i] ** 2)
        self.w1 -= lr * (self.mw[0] / (1 - b1**self.t)) / (np.sqrt(self.vw[0] / (1 - b2**self.t)) + eps)
        self.w2 -= lr * (self.mw[1] / (1 - b1**self.t)) / (np.sqrt(self.vw[1] / (1 - b2**self.t)) + eps)
        self.w3 -= lr * (self.mw[2] / (1 - b1**self.t)) / (np.sqrt(self.vw[2] / (1 - b2**self.t)) + eps)
        self.b1 -= lr * (self.mb[0] / (1 - b1**self.t)) / (np.sqrt(self.vb[0] / (1 - b2**self.t)) + eps)
        self.b2 -= lr * (self.mb[1] / (1 - b1**self.t)) / (np.sqrt(self.vb[1] / (1 - b2**self.t)) + eps)
        self.b3 -= lr * (self.mb[2] / (1 - b1**self.t)) / (np.sqrt(self.vb[2] / (1 - b2**self.t)) + eps)

    def backward(self, cache, gy):
        x, h1, h2 = cache
        gw3 = h2.T @ gy
        gb3 = gy.sum(axis=0)
        gh2 = gy @ self.w3.T * (1 - h2**2)
        gw2 = h1.T @ gh2
        gb2 = gh2.sum(axis=0)
        gh1 = gh2 @ self.w2.T * (1 - h1**2)
        gw1 = x.T @ gh1
        gb1 = gh1.sum(axis=0)
        return [gw1, gw2, gw3], [gb1, gb2, gb3]


def predict(model: MLP, x: np.ndarray) -> np.ndarray:
    y, _ = model.forward(x)
    return y


def physics_terms(x, yhat):
    p_load = x[:, 1]
    p_pv = x[:, 2]
    soc = x[:, 5]
    p_grid, p_ch, p_dis, soc_next = yhat.T
    r_p = p_grid + p_pv + p_dis - p_ch - p_load
    expected = soc + ETA_CH * p_ch * DT / E_MAX - p_dis * DT / (ETA_DIS * E_MAX)
    r_s = soc_next - expected
    over = np.maximum(0.0, soc_next - SOC_MAX)
    under = np.maximum(0.0, SOC_MIN - soc_next)
    return r_p, r_s, over + under


def operating_cost(x, yhat):
    c_buy = x[:, 3]
    c_sell = x[:, 4]
    p_grid, p_ch, p_dis, _ = yhat.T
    buy = np.maximum(p_grid, 0.0)
    sell = np.maximum(-p_grid, 0.0)
    return c_buy * buy - c_sell * sell + KAPPA * (np.maximum(p_ch, 0) + np.maximum(p_dis, 0))


def train(model: MLP, x, y, physics: bool, rng: np.random.Generator):
    n = len(x)
    for _ in range(EPOCHS):
        idx = rng.permutation(n)
        for start in range(0, n, BATCH):
            sl = idx[start : start + BATCH]
            xb, yb = x[sl], y[sl]
            yhat, cache = model.forward(xb)
            diff = yhat - yb
            gy = (2.0 / len(xb)) * diff
            if physics:
                r_p, r_s, r_b = physics_terms(xb, yhat)
                # d L_p / d y : r_p depends on p_grid(+), p_ch(-), p_dis(+)
                gp = np.zeros_like(yhat)
                coef = 2.0 / len(xb)
                gp[:, 0] += coef * r_p
                gp[:, 1] += -coef * r_p
                gp[:, 2] += coef * r_p
                gp[:, 1] += coef * r_s * (ETA_CH * DT / E_MAX) * (-1.0) * (-1.0)
                # r_s = soc_next - (soc + eta_ch p_ch dt/E - p_dis dt/(eta E))
                gp[:, 3] += coef * r_s
                gp[:, 1] += coef * r_s * (-ETA_CH * DT / E_MAX)
                gp[:, 2] += coef * r_s * (DT / (ETA_DIS * E_MAX))
                # bounds on soc_next
                over = np.maximum(0.0, yhat[:, 3] - SOC_MAX)
                under = np.maximum(0.0, SOC_MIN - yhat[:, 3])
                gp[:, 3] += 6.0 * coef * (over - under)
                gy = 0.8 * gy + 4.0 * gp
            gw, gb = model.backward(cache, gy)
            model.adam(gw, gb)


def metrics(x, y_true, yhat):
    mse = float(np.mean((yhat - y_true) ** 2))
    r_p, r_s, r_b = physics_terms(x, yhat)
    e_p = float(np.mean(np.abs(r_p)))
    viol = float(np.mean((yhat[:, 3] < SOC_MIN - 1e-3) | (yhat[:, 3] > SOC_MAX + 1e-3)) * 100.0)
    cost = float(np.mean(operating_cost(x, yhat)))
    return {"mse": mse, "power_residual": e_p, "violation_pct": viol, "cost": cost}


def plot_day(s: Series, y_dd, y_pi, path: Path):
    hours = np.arange(24)
    sl = slice(24, 48)
    fig, axes = plt.subplots(2, 1, figsize=(7.2, 5.2), sharex=True)
    axes[0].plot(hours, s.p_load[sl], label="Load", color="#1f4e79")
    axes[0].plot(hours, s.p_pv[sl], label="PV", color="#e09f3e")
    axes[0].set_ylabel("Power (kW)")
    axes[0].legend(frameon=False, ncol=2)
    axes[0].set_title("One validation day of the synthetic microgrid")
    axes[1].plot(hours, s.soc_next[sl], label="Reference SOC", color="#2a9d8f")
    axes[1].plot(hours, y_dd[sl, 3], "--", label="Data-driven", color="#c1121f")
    axes[1].plot(hours, y_pi[sl, 3], label="Physics-informed", color="#3a0ca3")
    axes[1].axhline(SOC_MIN, color="gray", lw=0.8, ls=":")
    axes[1].axhline(SOC_MAX, color="gray", lw=0.8, ls=":")
    axes[1].set_xlabel("Hour")
    axes[1].set_ylabel("SOC")
    axes[1].legend(frameon=False, ncol=3, fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def plot_residual(x, y_dd, y_pi, path: Path):
    r_dd, _, _ = physics_terms(x, y_dd)
    r_pi, _, _ = physics_terms(x, y_pi)
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.plot(np.abs(r_dd[:120]), label="Data-driven |r_P|", color="#c1121f", lw=1.0)
    ax.plot(np.abs(r_pi[:120]), label="Physics-informed |r_P|", color="#3a0ca3", lw=1.0)
    ax.set_xlabel("Test hour")
    ax.set_ylabel("Power-balance residual (kW)")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def main():
    rng = np.random.default_rng(SEED)
    series = make_profiles(24 * 21, rng)
    x = stack_x(series)
    y = stack_y(series)
    # Corrupt a subset of training labels so the physics term has work to do.
    n = len(x)
    n_train, n_val = int(0.60 * n), int(0.20 * n)
    y_obs = y.copy()
    noise = rng.normal(0.0, 0.35, size=y_obs[:n_train].shape)
    y_obs[:n_train] += noise

    x_tr, y_tr = x[:n_train], y_obs[:n_train]
    x_te, y_te = x[n_train + n_val :], y[n_train + n_val :]

    dd = MLP(np.random.default_rng(SEED + 1))
    pi = MLP(np.random.default_rng(SEED + 2))
    train(dd, x_tr, y_tr, physics=False, rng=np.random.default_rng(11))
    train(pi, x_tr, y_tr, physics=True, rng=np.random.default_rng(12))

    y_dd = predict(dd, x_te)
    y_pi = predict(pi, x_te)
    m_dd = metrics(x_te, y_te, y_dd)
    m_pi = metrics(x_te, y_te, y_pi)

    payload = {
        "seed": SEED,
        "hours_total": int(n),
        "hours_test": int(len(x_te)),
        "dt_h": DT,
        "e_max_kwh": E_MAX,
        "data_driven": m_dd,
        "physics_informed": m_pi,
    }
    (RESULTS / "metrics.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    with (RESULTS / "metrics.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["model", "mse", "power_residual", "violation_pct", "cost"])
        w.writerow(["data_driven", m_dd["mse"], m_dd["power_residual"], m_dd["violation_pct"], m_dd["cost"]])
        w.writerow(["physics_informed", m_pi["mse"], m_pi["power_residual"], m_pi["violation_pct"], m_pi["cost"]])

    plot_day(series, predict(dd, x), predict(pi, x), ASSETS / "fig-soc-day.png")
    plot_residual(x_te, y_dd, y_pi, ASSETS / "fig-power-residual.png")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
