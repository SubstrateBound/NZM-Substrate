# nzm_ingest.py
#
# NZM DATA INGESTION LAYER
# Author: Barry R. Greer (@NZMTDU)
# Date: 2026-02-25
#
# PURPOSE:
# Classical datasets encode absence as zero and missing as NaN.
# In NZM neither exists. Zero is Omega (substrate floor, minimum
# state). NaN is an unmeasured state — the substrate was there,
# the instrument didn't reach it.
#
# This module translates once at load time.
# Everything downstream is NZM-native.
# No zero. No null. No classical contamination.
#
# TRANSLATION RULES:
#   Classical 0   → OMEGA (1e-10 — below measurement but above zero)
#   Classical NaN → OMEGA (same floor — unmeasured, not absent)
#   Classical -ve → abs() then floor at OMEGA (no negative substrate)
#
# OMEGA VALUE:
#   Not literally 1. Not literally 0.
#   The smallest measurable substrate state in the dataset.
#   Computed per-column as 1% of the minimum positive value.
#   This preserves the scale relationship between floor and signal.
#
# USAGE:
#   from nzm_ingest import load_nzm
#   df = load_nzm('chimefrbcat2.csv', omega_cols=['scat_time','dm_exc'])

import pandas as pd
import numpy as np
from typing import List, Optional


# Sentinel value — marks Omega states in the dataframe
# Not zero. The minimum expressing state.
OMEGA_SENTINEL = "OMEGA"
OMEGA_NUMERIC  = 1e-10  # used when column must stay numeric


def compute_omega(series: pd.Series) -> float:
    """
    Compute the Omega floor value for a column.
    Omega = 1% of the minimum positive observed value.
    Preserves scale. Not arbitrary. Not zero.
    """
    positive = series[series > 0].dropna()
    if len(positive) == 0:
        return OMEGA_NUMERIC
    return positive.min() * 0.01


def translate_column(series: pd.Series, omega_val: float) -> pd.Series:
    """
    Translate one column from classical to NZM encoding.
    0 → omega_val (floor state, not absent)
    NaN → omega_val (unmeasured, not absent)
    negative → abs, then floor at omega_val
    """
    s = pd.to_numeric(series, errors='coerce')
    s = s.abs()                          # no negative substrate
    s = s.fillna(omega_val)              # NaN → Omega
    s = s.where(s > 0, omega_val)        # 0 → Omega
    s = s.clip(lower=omega_val)          # nothing below floor
    return s


def load_nzm(
    filepath: str,
    omega_cols: Optional[List[str]] = None,
    flag_cols:  Optional[List[str]] = None,
    exclude_flagged: bool = True,
    **kwargs
) -> pd.DataFrame:
    """
    Load a classical dataset and translate to NZM encoding.

    Parameters
    ----------
    filepath     : path to CSV
    omega_cols   : columns to translate (0/NaN → Omega)
    flag_cols    : columns that are floor-state flags
                   (e.g. excluded_flag — floor state = valid)
    exclude_flagged : if True, keep only rows where flag_cols are at Omega
                      (floor state = no flag applied = clean event)
    **kwargs     : passed to pd.read_csv

    Returns
    -------
    NZM-encoded DataFrame. No zeros. No nulls.
    Each translated column gets a companion _omega_val column
    recording the floor value used.
    """
    df = pd.read_csv(filepath, low_memory=False, **kwargs)

    # ── APPLY EXCLUSION FLAGS BEFORE TRANSLATION ──────────────
    # Flag at floor state (classical 0) = valid event
    # Flag above floor (classical 1,2...) = excluded
    # We filter BEFORE translation so we're reading classical
    # encoding correctly at this one point of contact.
    if flag_cols and exclude_flagged:
        for col in flag_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                n_before = len(df)
                df = df[df[col] == 0].copy()  # floor state = valid
                n_after  = len(df)
                print(f"  [{col}] Kept {n_after} floor-state (valid) events "
                      f"of {n_before} total")

    # ── TRANSLATE OMEGA COLUMNS ───────────────────────────────
    if omega_cols:
        for col in omega_cols:
            if col not in df.columns:
                continue
            raw     = pd.to_numeric(df[col], errors='coerce')
            omega   = compute_omega(raw)
            translated = translate_column(raw, omega)
            df[col]               = translated
            df[f'{col}_omega_val'] = omega  # record floor for audit

            n_at_floor = (translated <= omega * 1.01).sum()
            print(f"  [{col}] Omega={omega:.2e}  "
                  f"Floor-locked: {n_at_floor} ({n_at_floor/len(df)*100:.2f}%)")

    df.attrs['nzm_encoded'] = True
    df.attrs['omega_cols']  = omega_cols or []
    return df


def load_chime(filepath: str) -> pd.DataFrame:
    """
    Load CHIME FRB catalog with standard NZM translation.
    """
    print(f"Loading CHIME: {filepath.split('/')[-1]}")
    return load_nzm(
        filepath,
        omega_cols  = ['scat_time', 'dm_exc_ne2001', 'dm_exc_ymw16',
                        'bonsai_dm', 'dm_fitb', 'flux', 'fluence'],
        flag_cols   = ['excluded_flag'],
        exclude_flagged = True,
    )


def load_sync(filepath: str) -> pd.DataFrame:
    """
    Load SYNC cluster catalog with standard NZM translation.
    """
    print(f"Loading SYNC: {filepath.split('/')[-1]}")
    return load_nzm(
        filepath,
        omega_cols = ['b/a', 'PA', 'PAcl', 'z', 'Re', 'n'],
    )


def load_sparc(filepath: str) -> pd.DataFrame:
    """
    Load SPARC galaxy rotation catalog with standard NZM translation.
    """
    print(f"Loading SPARC: {filepath.split('/')[-1]}")
    return load_nzm(
        filepath,
        omega_cols = ['Vobs', 'Vbar', 'errV', 'Rad'],
    )


# ── AUDIT HELPER ──────────────────────────────────────────────

def omega_audit(df: pd.DataFrame) -> pd.DataFrame:
    """
    Report floor-state population for all translated columns.
    Shows what was zero/null in the classical data and is now Omega.
    """
    omega_cols = df.attrs.get('omega_cols', [])
    rows = []
    for col in omega_cols:
        if col not in df.columns:
            continue
        omega_val_col = f'{col}_omega_val'
        if omega_val_col not in df.columns:
            continue
        omega_val = df[omega_val_col].iloc[0]
        at_floor  = (df[col] <= omega_val * 1.01).sum()
        rows.append({
            'column':      col,
            'omega_val':   omega_val,
            'n_total':     len(df),
            'n_at_floor':  at_floor,
            'floor_pct':   at_floor / len(df) * 100,
        })
    return pd.DataFrame(rows)


# ── DEMO ──────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("NZM INGESTION LAYER — Translation Demo")
    print("Classical 0 → Omega  |  NaN → Omega  |  No zero downstream")
    print("=" * 60)
    print()

    df = load_chime('/mnt/user-data/uploads/chimefrbcat2__1_.csv')

    print()
    print("OMEGA AUDIT:")
    audit = omega_audit(df)
    print(audit[['column','omega_val','n_total','n_at_floor','floor_pct']].to_string(index=False))

    print()
    print(f"Final dataset: N={len(df)} clean NZM-encoded events")
    print(f"Zero count in scat_time: {(df['scat_time'] == 0).sum()}  ← should be 0")
    print(f"NaN count in scat_time:  {df['scat_time'].isna().sum()}  ← should be 0")
    print()
    print("No zeros. No nulls. NZM-native from ingestion.")
