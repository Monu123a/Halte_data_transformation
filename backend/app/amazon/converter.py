import os
import requests
import gzip
import logging
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger("amazon.converter")

class AmazonReportConverter:
    def __init__(self, base_reports_dir: str = "reports"):
        self.base_reports_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
            base_reports_dir
        )

    def _get_daily_dir(self) -> str:
        today = datetime.now()
        dir_path = os.path.join(
            self.base_reports_dir,
            str(today.year),
            f"{today.month:02d}",
            f"{today.day:02d}"
        )
        os.makedirs(dir_path, exist_ok=True)
        return dir_path

    def process_document(self, doc_details: Dict[str, Any]) -> Optional[str]:
        """
        Downloads, decompresses, and converts the SP-API document to an Excel file.
        Returns the absolute path to the generated Excel file.
        """
        try:
            url = doc_details["url"]
            compression = doc_details.get("compressionAlgorithm")
            
            logger.info("Downloading report document...")
            response = requests.get(url)
            response.raise_for_status()
            
            daily_dir = self._get_daily_dir()
            ts = datetime.now().strftime("%H%M%S")
            
            # Save raw file
            raw_ext = ".gz" if compression == "GZIP" else ".tsv"
            raw_filename = f"amazon_report_{ts}{raw_ext}"
            raw_path = os.path.join(daily_dir, raw_filename)
            
            with open(raw_path, "wb") as f:
                f.write(response.content)
            logger.info(f"Raw report saved to {raw_path}")
            
            # Decompress and read data
            if compression == "GZIP":
                logger.info("Decompressing GZIP report...")
                with gzip.open(raw_path, 'rt', encoding='utf-8') as f:
                    # Amazon reports are typically tab-separated
                    df = pd.read_csv(f, sep='\t', dtype=str)
            else:
                df = pd.read_csv(raw_path, sep='\t', dtype=str)
                
            logger.info(f"Loaded {len(df)} rows from report.")
            
            # Convert to Excel
            excel_filename = f"amazon_report_{ts}.xlsx"
            excel_path = os.path.join(daily_dir, excel_filename)
            
            logger.info("Converting report to Excel format...")
            df.to_excel(excel_path, index=False, engine="openpyxl")
            logger.info(f"Excel report saved to {excel_path}")
            
            return excel_path
            
        except Exception as e:
            logger.error(f"Failed to process document: {e}")
            return None
