import logging
import numpy as np
import pandas as pd
from app.plugins.base import BasePlugin
from app.models.context import ExecutionContext, LogLevel

logger = logging.getLogger(__name__)


class ColumnMapperPlugin(BasePlugin):
    NAME = "ColumnMapper"
    VERSION = "1.3"
    DESCRIPTION = "Reorders columns to match expected output and applies final business rules."

    def execute(self, context: ExecutionContext) -> None:
        df = context.current_data
        if df is None or df.empty:
            return

        # 0. Rename Promo columns exactly as Logic ERP expects
        promo_renames = {
            "Shipping Cess Tax": "Shipping Cess Tax Amount",
            "Item Promo Tax": "Item Promo Discount Tax",
            "Shipping Promo Tax": "Shipping Promo Discount Tax",
            "Gift Wrap Promo Tax": "Gift Wrap Promo Discount Tax"
        }
        df = df.rename(columns=promo_renames)

        # 1. Zero out Shipping Amount if canceled by Promo
        ship_amt = "Shipping Amount"
        ship_basis = "Shipping Amount Basis"
        promo = "Shipping Promo Discount"
        
        if ship_amt in df.columns and promo in df.columns:
            # If Shipping Amount + Shipping Promo Discount == 0, it means shipping was free
            mask = (pd.to_numeric(df[ship_amt], errors='coerce').fillna(0) + 
                    pd.to_numeric(df[promo], errors='coerce').fillna(0)) == 0
            df.loc[mask, ship_amt] = 0.0
            if ship_basis in df.columns:
                df.loc[mask, ship_basis] = 0.0
                
        # 2. Swap Igst and Utgst manually
        igst_col = "Igst Tax"
        utgst_col = "Utgst Tax"
        if igst_col in df.columns and utgst_col in df.columns:
            temp = df[igst_col].copy()
            df[igst_col] = df[utgst_col]
            df[utgst_col] = temp

        # 3. Clean up specific columns
        if "Item Serial No." in df.columns:
            df["Item Serial No."] = np.nan
            
        if "Invoice Number" in df.columns:
            try:
                # Try to convert to int where possible to match expected format
                df["Invoice Number"] = pd.to_numeric(df["Invoice Number"])
            except:
                pass
            
        if "TAX REGION" in df.columns:
            try:
                df["TAX REGION"] = pd.to_numeric(df["TAX REGION"])
            except:
                pass

        # 4. Reorder columns
        output_cols = context.mapping.get("logic_erp_output_columns", [])
        if not output_cols:
            context.add_warning(LogLevel.WARNING, "No logic ERP output columns defined in mapping.")
            return

        final_cols = []
        for col in output_cols:
            if col not in df.columns:
                df[col] = np.nan
            final_cols.append(col)

        df = df[final_cols]
        context.current_data = df
        context.add_warning(LogLevel.INFO, f"ColumnMapper ordered {len(final_cols)} columns.")
