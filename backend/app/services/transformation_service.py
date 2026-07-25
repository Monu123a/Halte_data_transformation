import os
import json
import shutil
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple
import pandas as pd

from app.models.context import ExecutionContext
from app.engines.transformation import TransformationEngine
from app.engines.validation import ValidationEngine
from app.repositories.config_repository import ConfigRepository

logger = logging.getLogger("amazon_logic_transformer")

class TransformationService:
    def __init__(
        self,
        transformation_engine: TransformationEngine,
        validation_engine: ValidationEngine,
        config_repo: ConfigRepository,
        output_dir: str,
        logs_dir: str,
    ):
        self.transformation_engine = transformation_engine
        self.validation_engine = validation_engine
        self.config_repo = config_repo
        self.output_dir = output_dir
        self.logs_dir = logs_dir

    def process(self, context: ExecutionContext, filenames: List[str]) -> Tuple[str, str, Dict[str, Any]]:
        """
        Executes the transformation pipeline on the provided context.
        Returns a tuple: (output_filename, audit_filename, result_dict)
        """
        # Run pipeline
        self.transformation_engine.execute_pipeline(context)

        # Run validation
        self.validation_engine.validate(context)

        # Generate output filename
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"logic_erp_output_{ts}.xlsx"
        output_path = os.path.join(self.output_dir, output_filename)

        if context.current_data is not None:
            context.current_data.to_excel(output_path, index=False, engine="openpyxl")
            logger.info("Output saved: %s (%d rows)", output_path, len(context.current_data))

        audit_filename = self._save_audit_report(context, ts)
        req_filename = self._generate_product_requirement_report(context)
        self._save_manifest(context, filenames, output_filename)

        result_dict = {
            "output_filename": output_filename,
            "audit_filename": audit_filename,
            "requirement_filename": req_filename,
            "stats": context.statistics.model_dump(),
            "warnings": [w.model_dump() for w in context.warnings],
            "message": "Transformation completed successfully.",
        }

        return output_filename, audit_filename, result_dict

    def _save_audit_report(self, context: ExecutionContext, ts: str) -> str:
        if not context.warnings:
            return ""
        
        data = []
        for w in context.warnings:
            data.append({
                "Level": w.level.value if hasattr(w.level, "value") else str(w.level),
                "Message": w.message,
                "Row Index": w.row_index if w.row_index is not None else "",
                "Column": w.column if w.column is not None else ""
            })
        
        df = pd.DataFrame(data)
        audit_filename = f"audit_report_{ts}.xlsx"
        audit_path = os.path.join(self.output_dir, audit_filename)
        df.to_excel(audit_path, index=False, engine="openpyxl")
        logger.info("Audit report saved: %s", audit_path)
        return audit_filename

    def _generate_product_requirement_report(self, context: ExecutionContext) -> str:
        if context.current_data is None or context.current_data.empty:
            return ""
            
        df = context.current_data.copy()
        
        # Identify columns
        sku_col = "Sku" if "Sku" in df.columns else "sku"
        qty_col = "Quantity" if "Quantity" in df.columns else "quantity"
        name_col = "Item Description" if "Item Description" in df.columns else "item-description"
        
        if sku_col not in df.columns or qty_col not in df.columns:
            logger.warning("Missing SKU or Quantity columns. Skipping product requirement report.")
            return ""
            
        if name_col not in df.columns:
            if "Product Name" in df.columns:
                name_col = "Product Name"
            else:
                df["Product Name"] = "Unknown"
                name_col = "Product Name"
                
        # Convert quantity to numeric
        df[qty_col] = pd.to_numeric(df[qty_col], errors='coerce').fillna(0)
        
        # Group by SKU
        report_df = df.groupby(sku_col, as_index=False).agg({
            name_col: 'first',
            qty_col: 'sum'
        })
        
        # Rename and reorder
        report_df.rename(columns={
            sku_col: 'SKU',
            name_col: 'Product Name',
            qty_col: 'Total Quantity Required'
        }, inplace=True)
        report_df = report_df[['SKU', 'Product Name', 'Total Quantity Required']]
        
        req_filename = "Product_Requirement_List.xlsx"
        req_path = os.path.join(self.output_dir, req_filename)
        report_df.to_excel(req_path, index=False, engine='openpyxl')
        logger.info("Product requirement report saved: %s", req_path)
        
        return req_filename

    def _save_manifest(self, context: ExecutionContext, filenames: List[str], output_filename: str):
        run_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        run_dir = os.path.join(self.logs_dir, run_id)
        os.makedirs(run_dir, exist_ok=True)

        manifest = {
            "run_id": run_id,
            "input_files": filenames,
            "output_file": output_filename,
            "mapping_version": "1.0",
            "rules_version": "1.0",
            "lookup_version": "1.0",
            "stats": context.statistics.model_dump(),
            "warnings": [w.model_dump() for w in context.warnings],
        }
        with open(os.path.join(run_dir, "manifest.json"), "w") as f:
            json.dump(manifest, f, indent=2, default=str)

        # Save config snapshot
        shutil.copy(os.path.join(self.config_repo.config_dir, "rules.json"), os.path.join(run_dir, "rules.json"))
        shutil.copy(os.path.join(self.config_repo.config_dir, "mapping.json"), os.path.join(run_dir, "mapping.json"))

        logger.info("Manifest saved to %s", run_dir)
