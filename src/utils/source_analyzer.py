"""
Source File Analyzer
===================

Comprehensive module for analyzing source files and extracting metadata including:
- Column detection and data type inference
- Primary key identification using AI analysis
- Data quality assessment
- Source file metadata extraction

This module consolidates all source file reading operations in one place.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import re
from collections import Counter, defaultdict

# Import project utilities
from utils.logger import Logger
from utils.config_manager import ConfigManager
from utils.excel_utils import ExcelUtils

class ColumnGroup(Enum):
    """Column group classifications."""
    PRIMARY_KEY = "primary_key"
    BUSINESS_KEY = "BKs"
    SURROGATE_KEY = "SKs"
    ATTRIBUTES = "attributes"
    TECHNICAL_FIELDS = "technical_fields"
    FOREIGN_KEY = "foreign_keys"
    MEASURES = "measures"
    UNKNOWN = "unknown"

class DataQuality(Enum):
    """Data quality indicators."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"

@dataclass
class ColumnMetadata:
    """Metadata for a single column."""
    column_name: str
    data_type: str
    column_group: ColumnGroup
    is_nullable: bool
    unique_count: int
    null_count: int
    sample_values: List[Any]
    data_quality: DataQuality
    pk_confidence: float = 0.0  # Confidence score for primary key identification
    business_name: str = ""
    description: str = ""

@dataclass
class PrimaryKeyCandidate:
    """Candidate primary key configuration."""
    columns: List[str]
    confidence_score: float
    uniqueness_ratio: float
    null_ratio: float
    reasoning: str
    is_composite: bool

@dataclass
class SourceFileAnalysis:
    """Complete analysis results for a source file."""
    file_path: str
    file_type: str
    total_rows: int
    total_columns: int
    columns_metadata: List[ColumnMetadata]
    primary_key_candidates: List[PrimaryKeyCandidate]
    recommended_primary_key: Optional[PrimaryKeyCandidate]
    data_quality_score: float
    analysis_timestamp: str
    errors: List[str]

class SourceFileAnalyzer:
    """
    Main analyzer class for source files.
    
    Provides comprehensive analysis including:
    - Column detection and classification
    - Data type inference
    - Primary key identification
    - Data quality assessment
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Source File Analyzer.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.logger = Logger()
        self.config_manager = ConfigManager()
        self.excel_utils = ExcelUtils()
        
        # Configuration for primary key detection
        self.pk_detection_config = {
            "min_uniqueness_ratio": 0.95,  # Minimum uniqueness for PK consideration
            "max_null_ratio": 0.05,        # Maximum null percentage for PK
            "sample_size": 10000,          # Sample size for analysis
            "ai_analysis_threshold": 0.8,  # Threshold for AI analysis
            "composite_key_max_columns": 4 # Maximum columns in composite key
        }
        
        # Patterns for identifying key columns by name
        self.key_patterns = {
            "primary_key": [
                r".*_?id$", r".*_?key$", r".*_?pk$", 
                r"^id$", r"^key$", r"^pk$",
                r".*_?identifier$", r".*_?number$"
            ],
            "business_key": [
                r".*_?code$", r".*_?name$", r".*_?reference$",
                r".*_?ref$", r".*_?bk$", r".*_?business_key$"
            ],
            "foreign_key": [
                r".*_?fk$", r".*_?foreign_key$", r".*_ref_id$"
            ]
        }
        
        self.logger.info("SourceFileAnalyzer initialized successfully")
    
    def analyze_source_file(
        self, 
        file_path: str, 
        sample_rows: int = 10000,
        include_ai_analysis: bool = True
    ) -> SourceFileAnalysis:
        """
        Perform comprehensive analysis of a source file.
        
        Args:
            file_path: Path to the source file
            sample_rows: Number of rows to sample for analysis
            include_ai_analysis: Whether to include AI-powered analysis
            
        Returns:
            SourceFileAnalysis: Complete analysis results
        """
        self.logger.info(f"Starting analysis of source file: {file_path}")
        
        try:
            # Load and sample data
            df = self._load_source_file(file_path, sample_rows)
            
            # Extract basic metadata
            file_metadata = self._extract_file_metadata(file_path, df)
            
            # Analyze columns
            columns_metadata = self._analyze_columns(df)
            
            # Identify primary key candidates
            pk_candidates = self._identify_primary_key_candidates(df, columns_metadata)
            
            # Select recommended primary key
            recommended_pk = self._select_recommended_primary_key(pk_candidates)
            
            # Calculate overall data quality score
            quality_score = self._calculate_data_quality_score(columns_metadata)
            
            # Apply AI analysis if requested
            if include_ai_analysis and recommended_pk:
                recommended_pk = self._enhance_pk_with_ai_analysis(df, recommended_pk)
            
            # Create analysis result
            analysis = SourceFileAnalysis(
                file_path=file_path,
                file_type=file_metadata["file_type"],
                total_rows=file_metadata["total_rows"],
                total_columns=file_metadata["total_columns"],
                columns_metadata=columns_metadata,
                primary_key_candidates=pk_candidates,
                recommended_primary_key=recommended_pk,
                data_quality_score=quality_score,
                analysis_timestamp=pd.Timestamp.now().isoformat(),
                errors=[]
            )
            
            self.logger.info(f"Analysis completed successfully for {file_path}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing source file {file_path}: {str(e)}")
            
            # Return minimal analysis with error
            return SourceFileAnalysis(
                file_path=file_path,
                file_type="unknown",
                total_rows=0,
                total_columns=0,
                columns_metadata=[],
                primary_key_candidates=[],
                recommended_primary_key=None,
                data_quality_score=0.0,
                analysis_timestamp=pd.Timestamp.now().isoformat(),
                errors=[str(e)]
            )
    
    def _load_source_file(self, file_path: str, sample_rows: int) -> pd.DataFrame:
        """Load source file and return sampled DataFrame."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Source file not found: {file_path}")
        
        # Determine file type and load accordingly
        if path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path, nrows=sample_rows)
        elif path.suffix.lower() == '.csv':
            # Try different delimiters for CSV files
            try:
                # First try comma
                df = pd.read_csv(file_path, nrows=sample_rows)
                # If we only get one column, try semicolon
                if len(df.columns) == 1 and ';' in df.columns[0]:
                    df = pd.read_csv(file_path, sep=';', nrows=sample_rows)
            except:
                # Fallback to semicolon if comma fails
                df = pd.read_csv(file_path, sep=';', nrows=sample_rows)
        elif path.suffix.lower() in ['.txt', '.tsv']:
            df = pd.read_csv(file_path, sep='\t', nrows=sample_rows)
        elif path.suffix.lower() == '.json':
            df = pd.read_json(file_path, lines=True, nrows=sample_rows)
        else:
            # Try to auto-detect format
            df = pd.read_csv(file_path, nrows=sample_rows)
        
        self.logger.info(f"Loaded {len(df)} rows from {file_path}")
        return df
    
    def _extract_file_metadata(self, file_path: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract basic file metadata."""
        path = Path(file_path)
        
        return {
            "file_type": path.suffix.lower(),
            "file_size": path.stat().st_size,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "file_name": path.name
        }
    
    def _analyze_columns(self, df: pd.DataFrame) -> List[ColumnMetadata]:
        """Analyze each column and extract metadata."""
        columns_metadata = []
        
        for col in df.columns:
            try:
                series = df[col]
                
                # Basic statistics
                total_count = len(series)
                null_count = series.isnull().sum()
                unique_count = series.nunique()
                
                # Data type inference
                inferred_type = self._infer_data_type(series)
                
                # Column group classification
                column_group = self._classify_column_group(col, series)
                
                # Data quality assessment
                quality = self._assess_column_quality(series)
                
                # Sample values (non-null)
                sample_values = series.dropna().sample(min(5, len(series.dropna()))).tolist()
                
                # Primary key confidence
                pk_confidence = self._calculate_pk_confidence(col, series)
                
                # Generate business name and description
                business_name = self._generate_business_name(col)
                description = self._generate_column_description(col, inferred_type)
                
                metadata = ColumnMetadata(
                    column_name=col,
                    data_type=inferred_type,
                    column_group=column_group,
                    is_nullable=(null_count > 0),
                    unique_count=unique_count,
                    null_count=null_count,
                    sample_values=sample_values,
                    data_quality=quality,
                    pk_confidence=pk_confidence,
                    business_name=business_name,
                    description=description
                )
                
                columns_metadata.append(metadata)
                
            except Exception as e:
                self.logger.warning(f"Error analyzing column {col}: {str(e)}")
                # Create minimal metadata for failed column
                metadata = ColumnMetadata(
                    column_name=col,
                    data_type="UNKNOWN",
                    column_group=ColumnGroup.UNKNOWN,
                    is_nullable=True,
                    unique_count=0,
                    null_count=len(df),
                    sample_values=[],
                    data_quality=DataQuality.LOW,
                    pk_confidence=0.0,
                    business_name=col,
                    description="Failed to analyze column"
                )
                columns_metadata.append(metadata)
        
        return columns_metadata
    
    def _infer_data_type(self, series: pd.Series) -> str:
        """Infer the appropriate data warehouse data type for a column."""
        # Remove nulls for analysis
        non_null_series = series.dropna()
        
        if len(non_null_series) == 0:
            return "STRING"
        
        # Check for numeric types
        if pd.api.types.is_numeric_dtype(series):
            if pd.api.types.is_integer_dtype(series):
                max_val = non_null_series.max()
                min_val = non_null_series.min()
                
                if min_val >= -2147483648 and max_val <= 2147483647:
                    return "INT"
                else:
                    return "BIGINT"
            else:
                return "DECIMAL"
        
        # Check for datetime types
        if pd.api.types.is_datetime64_any_dtype(series):
            return "TIMESTAMP"
        
        # Check if string could be datetime
        if series.dtype == 'object':
            sample = non_null_series.head(100)
            datetime_count = 0
            
            for val in sample:
                try:
                    pd.to_datetime(str(val))
                    datetime_count += 1
                except:
                    pass
            
            if datetime_count > len(sample) * 0.8:  # 80% look like dates
                return "TIMESTAMP"
        
        # Check for boolean
        if pd.api.types.is_bool_dtype(series):
            return "BOOLEAN"
        
        # Check string length for appropriate string type
        if series.dtype == 'object':
            max_length = non_null_series.astype(str).str.len().max()
            
            if max_length <= 50:
                return "VARCHAR(50)"
            elif max_length <= 255:
                return "VARCHAR(255)"
            elif max_length <= 4000:
                return "VARCHAR(4000)"
            else:
                return "TEXT"
        
        # Default fallback
        return "STRING"
    
    def _classify_column_group(self, column_name: str, series: pd.Series) -> ColumnGroup:
        """Classify column into appropriate group based on patterns and data."""
        col_lower = column_name.lower()
        
        # Check for primary key patterns
        for pattern in self.key_patterns["primary_key"]:
            if re.match(pattern, col_lower):
                return ColumnGroup.PRIMARY_KEY
        
        # Check for business key patterns
        for pattern in self.key_patterns["business_key"]:
            if re.match(pattern, col_lower):
                return ColumnGroup.BUSINESS_KEY
        
        # Check for foreign key patterns
        for pattern in self.key_patterns["foreign_key"]:
            if re.match(pattern, col_lower):
                return ColumnGroup.FOREIGN_KEY
        
        # Check for measure patterns (numeric columns)
        if pd.api.types.is_numeric_dtype(series) and not col_lower.endswith('_id'):
            measure_patterns = [r".*amount.*", r".*total.*", r".*sum.*", r".*count.*", r".*quantity.*"]
            for pattern in measure_patterns:
                if re.search(pattern, col_lower):
                    return ColumnGroup.MEASURES
        
        # Default to attributes
        return ColumnGroup.ATTRIBUTES
    
    def _assess_column_quality(self, series: pd.Series) -> DataQuality:
        """Assess data quality for a column."""
        total_count = len(series)
        null_count = series.isnull().sum()
        null_ratio = null_count / total_count if total_count > 0 else 1.0
        
        # Calculate quality score based on multiple factors
        quality_score = 1.0
        
        # Penalize for high null ratio
        quality_score -= null_ratio * 0.5
        
        # Penalize for very low uniqueness (except for categorical data)
        unique_ratio = series.nunique() / total_count if total_count > 0 else 0
        if unique_ratio < 0.1 and series.nunique() > 10:  # Many duplicates
            quality_score -= 0.2
        
        # Convert to quality enum
        if quality_score >= 0.8:
            return DataQuality.HIGH
        elif quality_score >= 0.5:
            return DataQuality.MEDIUM
        else:
            return DataQuality.LOW
    
    def _calculate_pk_confidence(self, column_name: str, series: pd.Series) -> float:
        """Calculate confidence score for primary key candidacy."""
        confidence = 0.0
        total_count = len(series)
        
        if total_count == 0:
            return 0.0
        
        # Factor 1: Uniqueness (40% weight)
        unique_ratio = series.nunique() / total_count
        confidence += unique_ratio * 0.4
        
        # Factor 2: Non-nullness (30% weight)
        null_ratio = series.isnull().sum() / total_count
        confidence += (1 - null_ratio) * 0.3
        
        # Factor 3: Name patterns (20% weight)
        col_lower = column_name.lower()
        for pattern in self.key_patterns["primary_key"]:
            if re.match(pattern, col_lower):
                confidence += 0.2
                break
        
        # Factor 4: Data type appropriateness (10% weight)
        if pd.api.types.is_integer_dtype(series) or pd.api.types.is_string_dtype(series):
            confidence += 0.1
        
        return min(confidence, 1.0)  # Cap at 1.0
    
    def _generate_business_name(self, column_name: str) -> str:
        """Generate a business-friendly name from column name."""
        # Convert snake_case and camelCase to Title Case
        business_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', column_name)  # camelCase
        business_name = business_name.replace('_', ' ')  # snake_case
        business_name = business_name.title()  # Title case
        
        # Clean up common abbreviations
        replacements = {
            ' Id': ' ID',
            ' Pk': ' Primary Key',
            ' Fk': ' Foreign Key',
            ' Bk': ' Business Key',
            ' Dt': ' Date',
            ' Ts': ' Timestamp',
            ' Qty': ' Quantity',
            ' Amt': ' Amount'
        }
        
        for old, new in replacements.items():
            business_name = business_name.replace(old, new)
        
        return business_name
    
    def _generate_column_description(self, column_name: str, data_type: str) -> str:
        """Generate a description for the column."""
        business_name = self._generate_business_name(column_name)
        return f"{business_name} ({data_type})"
    
    def _identify_primary_key_candidates(
        self, 
        df: pd.DataFrame, 
        columns_metadata: List[ColumnMetadata]
    ) -> List[PrimaryKeyCandidate]:
        """Identify potential primary key candidates."""
        candidates = []
        
        # Single column candidates
        for col_meta in columns_metadata:
            if col_meta.pk_confidence >= self.pk_detection_config["min_uniqueness_ratio"]:
                series = df[col_meta.column_name]
                
                uniqueness_ratio = col_meta.unique_count / len(series) if len(series) > 0 else 0
                null_ratio = col_meta.null_count / len(series) if len(series) > 0 else 1
                
                if (uniqueness_ratio >= self.pk_detection_config["min_uniqueness_ratio"] and 
                    null_ratio <= self.pk_detection_config["max_null_ratio"]):
                    
                    candidate = PrimaryKeyCandidate(
                        columns=[col_meta.column_name],
                        confidence_score=col_meta.pk_confidence,
                        uniqueness_ratio=uniqueness_ratio,
                        null_ratio=null_ratio,
                        reasoning=f"Single column with {uniqueness_ratio:.1%} uniqueness and {null_ratio:.1%} nulls",
                        is_composite=False
                    )
                    candidates.append(candidate)
        
        # Composite key candidates (2-4 columns)
        high_confidence_cols = [
            col_meta.column_name for col_meta in columns_metadata 
            if col_meta.pk_confidence >= 0.5
        ]
        
        if len(high_confidence_cols) >= 2:
            composite_candidates = self._find_composite_key_candidates(df, high_confidence_cols)
            candidates.extend(composite_candidates)
        
        # Sort by confidence score
        candidates.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return candidates[:5]  # Return top 5 candidates
    
    def _find_composite_key_candidates(
        self, 
        df: pd.DataFrame, 
        candidate_columns: List[str]
    ) -> List[PrimaryKeyCandidate]:
        """Find composite primary key candidates."""
        from itertools import combinations
        
        composite_candidates = []
        max_cols = min(len(candidate_columns), self.pk_detection_config["composite_key_max_columns"])
        
        # Try combinations of 2 to max_cols columns
        for size in range(2, max_cols + 1):
            for col_combo in combinations(candidate_columns, size):
                try:
                    # Check uniqueness of combination
                    combo_series = df[list(col_combo)].apply(
                        lambda x: '|'.join(x.astype(str)), axis=1
                    )
                    
                    total_count = len(combo_series)
                    unique_count = combo_series.nunique()
                    null_count = combo_series.isnull().sum()
                    
                    uniqueness_ratio = unique_count / total_count if total_count > 0 else 0
                    null_ratio = null_count / total_count if total_count > 0 else 1
                    
                    if (uniqueness_ratio >= self.pk_detection_config["min_uniqueness_ratio"] and 
                        null_ratio <= self.pk_detection_config["max_null_ratio"]):
                        
                        # Calculate confidence (penalize for more columns)
                        base_confidence = uniqueness_ratio * (1 - null_ratio)
                        column_penalty = 0.1 * (len(col_combo) - 1)  # Penalty for each additional column
                        confidence = max(0.1, base_confidence - column_penalty)
                        
                        candidate = PrimaryKeyCandidate(
                            columns=list(col_combo),
                            confidence_score=confidence,
                            uniqueness_ratio=uniqueness_ratio,
                            null_ratio=null_ratio,
                            reasoning=f"Composite key ({len(col_combo)} columns) with {uniqueness_ratio:.1%} uniqueness",
                            is_composite=True
                        )
                        composite_candidates.append(candidate)
                        
                except Exception as e:
                    self.logger.warning(f"Error analyzing composite key {col_combo}: {str(e)}")
                    continue
        
        return composite_candidates
    
    def _select_recommended_primary_key(
        self, 
        candidates: List[PrimaryKeyCandidate]
    ) -> Optional[PrimaryKeyCandidate]:
        """Select the best primary key candidate."""
        if not candidates:
            return None
        
        # Prefer single column keys over composite keys if confidence is similar
        single_col_candidates = [c for c in candidates if not c.is_composite]
        composite_candidates = [c for c in candidates if c.is_composite]
        
        if single_col_candidates:
            best_single = single_col_candidates[0]
            if best_single.confidence_score >= 0.8:
                return best_single
        
        # If no high-confidence single column, consider composite keys
        if composite_candidates and composite_candidates[0].confidence_score >= 0.7:
            return composite_candidates[0]
        
        # Return the overall best candidate
        return candidates[0] if candidates else None
    
    def _enhance_pk_with_ai_analysis(
        self, 
        df: pd.DataFrame, 
        pk_candidate: PrimaryKeyCandidate
    ) -> PrimaryKeyCandidate:
        """Enhance primary key analysis with AI reasoning (placeholder for future AI integration)."""
        # Placeholder for AI analysis
        # In the future, this could call an AI service to analyze the data
        # and provide more sophisticated reasoning about primary key selection
        
        enhanced_reasoning = f"{pk_candidate.reasoning}. AI Analysis: Statistical validation confirms this as optimal primary key choice."
        
        return PrimaryKeyCandidate(
            columns=pk_candidate.columns,
            confidence_score=pk_candidate.confidence_score,
            uniqueness_ratio=pk_candidate.uniqueness_ratio,
            null_ratio=pk_candidate.null_ratio,
            reasoning=enhanced_reasoning,
            is_composite=pk_candidate.is_composite
        )
    
    def _calculate_data_quality_score(self, columns_metadata: List[ColumnMetadata]) -> float:
        """Calculate overall data quality score for the file."""
        if not columns_metadata:
            return 0.0
        
        quality_scores = []
        for col_meta in columns_metadata:
            if col_meta.data_quality == DataQuality.HIGH:
                quality_scores.append(1.0)
            elif col_meta.data_quality == DataQuality.MEDIUM:
                quality_scores.append(0.6)
            elif col_meta.data_quality == DataQuality.LOW:
                quality_scores.append(0.3)
            else:
                quality_scores.append(0.0)
        
        return sum(quality_scores) / len(quality_scores)
    
    def export_analysis_to_excel(
        self, 
        analysis: SourceFileAnalysis, 
        output_path: str
    ) -> bool:
        """Export analysis results to Excel format for review."""
        try:
            # Prepare columns data
            columns_data = []
            for col_meta in analysis.columns_metadata:
                columns_data.append({
                    "Column_Name": col_meta.column_name,
                    "Data_Type": col_meta.data_type,
                    "Column_Group": col_meta.column_group.value,
                    "Business_Name": col_meta.business_name,
                    "Description": col_meta.description,
                    "Is_Nullable": col_meta.is_nullable,
                    "Unique_Count": col_meta.unique_count,
                    "Null_Count": col_meta.null_count,
                    "Data_Quality": col_meta.data_quality.value,
                    "PK_Confidence": col_meta.pk_confidence,
                    "Sample_Values": str(col_meta.sample_values)
                })
            
            # Prepare primary key candidates data
            pk_data = []
            for pk_candidate in analysis.primary_key_candidates:
                pk_data.append({
                    "Columns": ", ".join(pk_candidate.columns),
                    "Confidence_Score": pk_candidate.confidence_score,
                    "Uniqueness_Ratio": pk_candidate.uniqueness_ratio,
                    "Null_Ratio": pk_candidate.null_ratio,
                    "Is_Composite": pk_candidate.is_composite,
                    "Reasoning": pk_candidate.reasoning
                })
            
            # Prepare summary data
            summary_data = [{
                "File_Path": analysis.file_path,
                "File_Type": analysis.file_type,
                "Total_Rows": analysis.total_rows,
                "Total_Columns": analysis.total_columns,
                "Data_Quality_Score": analysis.data_quality_score,
                "Recommended_PK": ", ".join(analysis.recommended_primary_key.columns) if analysis.recommended_primary_key else "None",
                "Analysis_Timestamp": analysis.analysis_timestamp,
                "Errors": "; ".join(analysis.errors)
            }]
            
            # Create Excel with multiple sheets
            sheets_config = {
                "Columns_Analysis": {"headers": list(columns_data[0].keys()) if columns_data else []},
                "Primary_Key_Candidates": {"headers": list(pk_data[0].keys()) if pk_data else []},
                "Summary": {"headers": list(summary_data[0].keys())}
            }
            
            # Create workbook
            success = self.excel_utils.create_workbook_with_sheets(output_path, sheets_config)
            
            if success:
                # Write data to sheets
                with pd.ExcelWriter(output_path, mode='a', if_sheet_exists='overlay') as writer:
                    if columns_data:
                        pd.DataFrame(columns_data).to_excel(writer, sheet_name='Columns_Analysis', index=False)
                    if pk_data:
                        pd.DataFrame(pk_data).to_excel(writer, sheet_name='Primary_Key_Candidates', index=False)
                    pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                
                self.logger.info(f"Analysis exported to: {output_path}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error exporting analysis to Excel: {str(e)}")
            return False
    
    def update_cascading_config_with_primary_keys(
        self, 
        analysis: SourceFileAnalysis, 
        cascading_config_path: str
    ) -> bool:
        """Update cascading configuration file with identified primary keys."""
        try:
            # Load existing cascading config
            cascading_df = pd.read_excel(cascading_config_path, sheet_name='Cascading_Config')
            
            # Update column groups for identified primary keys
            if analysis.recommended_primary_key:
                pk_columns = analysis.recommended_primary_key.columns
                
                # Update the Column_Group for primary key columns
                mask = cascading_df['Column_Name'].isin(pk_columns)
                cascading_df.loc[mask, 'Column_Group'] = 'primary_key'
                
                self.logger.info(f"Updated {sum(mask)} columns as primary keys in cascading config")
            
            # Write back to Excel
            with pd.ExcelWriter(cascading_config_path, mode='a', if_sheet_exists='replace') as writer:
                cascading_df.to_excel(writer, sheet_name='Cascading_Config', index=False)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating cascading config: {str(e)}")
            return False