from pydantic import BaseModel
from typing import Dict, List

class FileDetectionConfig(BaseModel):
    b2b_identifier_column: str

class MappingEngineConfig(BaseModel):
    amazon_to_internal: Dict[str, str]
    internal_to_logic_erp: Dict[str, str]

class TransformationRulesConfig(BaseModel):
    allowed_transaction_types: List[str]
    invoice_prefixes: List[str]
    allowed_states: List[str]
    sku_trim_length: int
    defaults: Dict[str, str]

class AuditConfig(BaseModel):
    retention_days: int

class AppSettings(BaseModel):
    file_detection: FileDetectionConfig
    mapping_engine: MappingEngineConfig
    transformation_rules: TransformationRulesConfig
    audit: AuditConfig
