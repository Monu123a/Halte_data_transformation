import logging
from app.plugins.base import BasePlugin
from app.models.context import ExecutionContext, LogLevel

logger = logging.getLogger(__name__)


class AccountCodeMapperPlugin(BasePlugin):
    NAME = "AccountCodeMapper"
    VERSION = "1.2"
    DESCRIPTION = "Looks up ACCOUNT CODE from GSTIN (B2B) or Ship To State (B2C) using the lookup table."

    def execute(self, context: ExecutionContext) -> None:
        df = context.current_data
        if df is None or df.empty:
            return

        gst_col = "Customer Bill To Gstid"
        state_col = "Ship To State"
        
        # Load the lookup table
        lookup_df = context.lookups.get("account_lookup")
        if lookup_df is None or lookup_df.empty:
            context.add_warning(LogLevel.ERROR, "Account lookup table not loaded – cannot map account codes.")
            df["ACCOUT CODE"] = ""
            context.current_data = df
            return

        # Build B2B Map: GST STATE CODE -> ACCOUNT CODE
        # Use only rows for "AMAZON SELLER PORTAL CUSTOMER" to avoid duplicates
        portal_lookup = lookup_df[
            lookup_df["ACCOUNT NAME"].astype(str).str.contains("AMAZON SELLER PORTAL CUSTOMER", case=False, na=False)
        ].copy()

        portal_lookup["GST STATE CODE"] = portal_lookup["GST STATE CODE"].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        portal_lookup["ACCOUNT CODE"] = portal_lookup["ACCOUNT CODE"].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        b2b_code_map = dict(zip(portal_lookup["GST STATE CODE"], portal_lookup["ACCOUNT CODE"]))

        # Build B2C Map: GST STATE NAME -> ACCOUNT CODE
        portal_lookup["GST STATE NAME"] = portal_lookup["GST STATE NAME"].astype(str).str.strip().str.upper()
        
        # Clean non-breaking spaces
        portal_lookup["GST STATE NAME"] = portal_lookup["GST STATE NAME"].str.replace('\xa0', ' ')

        b2c_code_map = dict(zip(portal_lookup["GST STATE NAME"], portal_lookup["ACCOUNT CODE"]))
        
        # Hardcode some known variations
        b2c_code_map["ANDAMAN AND NICOBAR ISLANDS"] = b2c_code_map.get("ANDAMAN AND NICOBAR ISLAND", "")
        b2c_code_map["DELHI"] = b2c_code_map.get("DELHI", "4020")
        b2c_code_map["UTTAR PRADESH"] = "4052" # Force UTTAR PRADESH just in case
        b2c_code_map["JAMMU & KASHMIR"] = b2c_code_map.get("JAMMU AND KASHMIR", "")
        b2c_code_map["ODISHA"] = b2c_code_map.get("ORISSA", "")
        
        account_codes = []
        missing_count = 0

        for idx, row in df.iterrows():
            gstin = str(row.get(gst_col, "")).strip()
            state = str(row.get(state_col, "")).strip().upper()
            
            ac = ""
            if gstin and len(gstin) >= 2 and gstin.lower() != "nan":
                # B2B Mapping
                try:
                    state_code = str(int(gstin[:2]))
                except ValueError:
                    state_code = gstin[:2]
                ac = b2b_code_map.get(state_code, "")
                if not ac:
                    missing_count += 1
                    context.add_warning(
                        LogLevel.WARNING,
                        f"No account code for GST state code '{state_code}'.",
                        row_index=int(idx),
                        column="ACCOUT CODE",
                    )
            else:
                # B2C Mapping
                ac = b2c_code_map.get(state, "")
                
                # Try partial match if exact fails
                if not ac:
                    for k, v in b2c_code_map.items():
                        if state in k or k in state:
                            ac = v
                            break

                if not ac:
                    missing_count += 1
                    context.add_warning(
                        LogLevel.WARNING,
                        f"No account code for state name '{state}'.",
                        row_index=int(idx),
                        column="ACCOUT CODE",
                    )

            account_codes.append(ac)

        df["ACCOUT CODE"] = account_codes
        context.current_data = df
        context.statistics.missing_account_code = missing_count
        
        if missing_count == 0:
            context.add_warning(LogLevel.INFO, f"AccountCodeMapper: Mapped all {len(df)} codes successfully.")
        else:
            context.add_warning(LogLevel.INFO, f"AccountCodeMapper: Mapped {len(df) - missing_count} codes, {missing_count} missing.")
