import logging
import pandas as pd
from typing import Optional

from app.amazon.auth import AmazonAuthenticator
from app.amazon.provider import ReportsAPIProvider
from app.amazon.converter import AmazonReportConverter
from app.main import _build_context, transformation_service

logger = logging.getLogger("amazon.pipeline")

class AmazonPipeline:
    def __init__(self):
        self.auth = AmazonAuthenticator()
        self.provider = ReportsAPIProvider(self.auth)
        self.converter = AmazonReportConverter()
        self.transformer = transformation_service

    def run(self) -> bool:
        """
        Executes the full Amazon integration pipeline:
        Download -> Convert -> Transform -> Export
        """
        logger.info("Starting Amazon SP-API Integration Pipeline...")
        
        # 1. Download Data
        logger.info("Step 1: Fetching report from Amazon SP-API...")
        doc_details = self.provider.download_data()
        if not doc_details:
            logger.error("Pipeline aborted: Failed to retrieve document details.")
            return False
            
        # 2. Convert Data
        logger.info("Step 2: Converting raw report to Excel...")
        excel_path = self.converter.process_document(doc_details)
        if not excel_path:
            logger.error("Pipeline aborted: Failed to convert report to Excel.")
            return False
            
        # 3. Transform Data
        logger.info(f"Step 3: Triggering Transformation Engine on {excel_path}...")
        try:
            context = _build_context()
            # Load the newly created excel file
            context.current_data = pd.read_excel(excel_path)
            
            # The filenames list is used just for metadata/manifest purposes
            filenames = [excel_path.split("/")[-1]]
            
            output_filename, audit_filename, result_dict = self.transformer.process(context, filenames)
            
            logger.info("Pipeline completed successfully!")
            logger.info(f"Final Logic ERP Output: {output_filename}")
            if audit_filename:
                logger.info(f"Audit Report: {audit_filename}")
            
            return True
            
        except Exception as e:
            logger.error(f"Pipeline aborted: Transformation Engine failed: {e}")
            return False
