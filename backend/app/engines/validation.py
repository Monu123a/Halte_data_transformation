import logging
import pandas as pd
from app.models.context import ExecutionContext, LogLevel

logger = logging.getLogger(__name__)


class ValidationEngine:
    """Validates the transformed data and populates warnings on the context."""

    def validate(self, context: ExecutionContext) -> None:
        df = context.current_data
        if df is None or df.empty:
            context.add_warning(LogLevel.ERROR, "No data to validate.")
            return

        self._check_missing_values(df, context, "Sku", "Missing SKU")
        self._check_missing_values(df, context, "Invoice Number", "Missing Invoice Number")
        self._check_duplicate_invoices(df, context)
        self._check_negative_amounts(df, context)
        self._check_invalid_gst_format(df, context)

        logger.info("Validation complete. Total warnings: %d", len(context.warnings))

    def _check_missing_values(
        self, df: pd.DataFrame, context: ExecutionContext, col: str, msg: str
    ) -> None:
        if col not in df.columns:
            return
        mask = df[col].isnull() | (df[col].astype(str).str.strip() == "") | (df[col].astype(str).str.lower() == "nan")
        count = mask.sum()
        if count:
            context.add_warning(LogLevel.ERROR, f"{msg}: {count} rows affected.")
            context.statistics.rows_failed += int(count)

    def _check_duplicate_invoices(self, df: pd.DataFrame, context: ExecutionContext) -> None:
        col = "Invoice Number"
        if col not in df.columns:
            return
        dup_mask = df.duplicated(subset=[col], keep=False)
        dup_count = dup_mask.sum()
        if dup_count:
            context.statistics.duplicate_invoices = int(dup_count)
            context.add_warning(
                LogLevel.WARNING,
                f"Duplicate invoices: {dup_count} rows share duplicated invoice numbers.",
            )

    def _check_negative_amounts(self, df: pd.DataFrame, context: ExecutionContext) -> None:
        for col in ["Principal Amount", "Shipping Amount", "Invoice Amount"]:
            if col not in df.columns:
                continue
            numeric = pd.to_numeric(df[col], errors="coerce")
            neg_count = int((numeric < 0).sum())
            if neg_count:
                context.add_warning(
                    LogLevel.WARNING, f"Negative values in '{col}': {neg_count} rows."
                )

    def _check_invalid_gst_format(self, df: pd.DataFrame, context: ExecutionContext) -> None:
        col = "Customer Bill To Gstid"
        if col not in df.columns:
            return
        for idx, val in df[col].items():
            val_str = str(val).strip()
            if val_str and val_str.lower() != "nan" and len(val_str) != 15:
                context.add_warning(
                    LogLevel.WARNING,
                    f"Invalid GSTIN format (length {len(val_str)}): '{val_str}'.",
                    row_index=int(idx),
                    column=col,
                )
