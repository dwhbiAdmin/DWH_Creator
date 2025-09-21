"""
Source File Integration Module
=============================

Orchestrates the complete source file analysis and integration workflow:
1. Source file analysis (columns, data types, primary keys)
2. Cascading configuration update
3. Primary key propagation through cascading logic

This module serves as the main entry point for source file processing.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import json
from datetime import datetime

# Import project utilities
from utils.source_analyzer import SourceFileAnalyzer, SourceFileAnalysis, ColumnGroup
from utils.column_cascading import ColumnCascadingEngine
from utils.excel_utils import ExcelUtils
from utils.logger import Logger
from utils.config_manager import ConfigManager

class SourceFileIntegrator:
    """
    Main orchestrator for source file analysis and integration.
    
    Handles the complete workflow from source file analysis to 
    cascading configuration updates and primary key propagation.
    """
    
    def __init__(self, workbook_path: str, config_path: Optional[str] = None):
        """
        Initialize the Source File Integrator.
        
        Args:
            workbook_path: Path to the main workbook
            config_path: Optional path to configuration file
        """
        self.workbook_path = workbook_path
        self.config_path = config_path
        
        # Initialize components
        self.logger = Logger()
        self.config_manager = ConfigManager()
        self.excel_utils = ExcelUtils()
        self.source_analyzer = SourceFileAnalyzer(config_path)
        self.cascading_engine = ColumnCascadingEngine(workbook_path, config_path)
        
        self.logger.info("SourceFileIntegrator initialized successfully")
    
    def process_source_file(
        self, 
        source_file_path: str,
        table_name: str,
        stage_name: str = "1_bronze",
        artifact_type: str = "dimension",
        include_ai_analysis: bool = True,
        update_cascading_config: bool = True,
        apply_cascading: bool = True
    ) -> Dict[str, Any]:
        """
        Complete source file processing workflow.
        
        Args:
            source_file_path: Path to the source file to analyze
            table_name: Name for the target table/artifact
            stage_name: Target stage name (default: "1_bronze")
            artifact_type: Type of artifact (dimension, fact, etc.)
            include_ai_analysis: Whether to include AI-powered analysis
            update_cascading_config: Whether to update cascading configuration
            apply_cascading: Whether to apply cascading logic
            
        Returns:
            Dict[str, Any]: Processing results and metadata
        """
        self.logger.info(f"Starting source file processing: {source_file_path}")
        
        try:
            # Step 1: Analyze source file
            self.logger.info("Step 1: Analyzing source file structure and content...")
            analysis = self.source_analyzer.analyze_source_file(
                source_file_path, 
                include_ai_analysis=include_ai_analysis
            )
            
            if analysis.errors:
                self.logger.warning(f"Analysis completed with errors: {analysis.errors}")
            
            # Step 2: Generate column configuration
            self.logger.info("Step 2: Generating column configuration...")
            column_config = self._generate_column_configuration(
                analysis, table_name, stage_name, artifact_type
            )
            
            # Step 3: Update cascading configuration (if requested)
            cascading_update_success = False
            if update_cascading_config:
                self.logger.info("Step 3: Updating cascading configuration...")
                cascading_update_success = self._update_cascading_configuration(
                    column_config, analysis
                )
            
            # Step 4: Apply cascading logic (if requested)
            cascading_results = None
            if apply_cascading and cascading_update_success:
                self.logger.info("Step 4: Applying cascading logic...")
                cascading_results = self._apply_cascading_logic(table_name, stage_name)
            
            # Step 5: Generate comprehensive report
            self.logger.info("Step 5: Generating processing report...")
            report = self._generate_processing_report(
                analysis, column_config, cascading_update_success, cascading_results
            )
            
            # Step 6: Export results to Excel
            output_path = self._generate_output_path(source_file_path, table_name)
            export_success = self._export_results_to_excel(
                analysis, column_config, report, output_path
            )
            
            # Compile final results
            results = {
                "source_file": source_file_path,
                "table_name": table_name,
                "stage_name": stage_name,
                "artifact_type": artifact_type,
                "analysis": analysis,
                "column_config": column_config,
                "cascading_updated": cascading_update_success,
                "cascading_results": cascading_results,
                "report": report,
                "output_path": output_path if export_success else None,
                "export_success": export_success,
                "processing_timestamp": datetime.now().isoformat(),
                "success": True
            }
            
            self.logger.info(f"Source file processing completed successfully: {source_file_path}")
            return results
            
        except Exception as e:
            error_msg = f"Error processing source file {source_file_path}: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                "source_file": source_file_path,
                "table_name": table_name,
                "error": error_msg,
                "processing_timestamp": datetime.now().isoformat(),
                "success": False
            }
    
    def _generate_column_configuration(
        self, 
        analysis: SourceFileAnalysis, 
        table_name: str,
        stage_name: str,
        artifact_type: str
    ) -> List[Dict[str, Any]]:
        """Generate column configuration from analysis results."""
        column_config = []
        order = 1
        
        # Process analyzed columns
        for col_meta in analysis.columns_metadata:
            # Map column group from analysis to cascading format
            column_group = self._map_column_group_to_cascading(col_meta.column_group)
            
            # Special handling for primary key columns
            if analysis.recommended_primary_key and col_meta.column_name in analysis.recommended_primary_key.columns:
                column_group = "primary_key"
            
            column_def = {
                "Stage Name": stage_name,
                "Artifact Name": table_name,
                "Artifact Type": artifact_type,
                "Column Name": col_meta.column_name,
                "Data Type": col_meta.data_type,
                "Column Group": column_group,
                "Column Business Name": col_meta.business_name,
                "Column Comment": col_meta.description,
                "Order": order,
                "Is_Nullable": col_meta.is_nullable,
                "Unique_Count": col_meta.unique_count,
                "Null_Count": col_meta.null_count,
                "Data_Quality": col_meta.data_quality.value,
                "PK_Confidence": col_meta.pk_confidence,
                "Sample_Values": str(col_meta.sample_values)
            }
            
            column_config.append(column_def)
            order += 1
        
        return column_config
    
    def _map_column_group_to_cascading(self, column_group: ColumnGroup) -> str:
        """Map analysis column group to cascading engine format."""
        mapping = {
            ColumnGroup.PRIMARY_KEY: "primary_key",
            ColumnGroup.BUSINESS_KEY: "BKs",
            ColumnGroup.SURROGATE_KEY: "SKs",
            ColumnGroup.ATTRIBUTES: "attributes",
            ColumnGroup.TECHNICAL_FIELDS: "technical_fields",
            ColumnGroup.FOREIGN_KEY: "foreign_keys",
            ColumnGroup.MEASURES: "measures",
            ColumnGroup.UNKNOWN: "attributes"
        }
        return mapping.get(column_group, "attributes")
    
    def _update_cascading_configuration(
        self, 
        column_config: List[Dict[str, Any]], 
        analysis: SourceFileAnalysis
    ) -> bool:
        """Update the cascading configuration with new columns."""
        try:
            # Load existing cascading config
            cascading_config_path = self.cascading_engine.config_path
            
            # Read current configuration
            existing_df = pd.read_excel(cascading_config_path, sheet_name='Cascading_Config')
            
            # Convert new columns to DataFrame
            new_columns_df = pd.DataFrame(column_config)
            
            # Remove any existing columns for the same artifact to avoid duplicates
            artifact_name = column_config[0]["Artifact Name"] if column_config else ""
            if artifact_name:
                existing_df = existing_df[existing_df['Artifact Name'] != artifact_name]
            
            # Combine existing and new columns
            updated_df = pd.concat([existing_df, new_columns_df], ignore_index=True)
            
            # Sort by Stage Name, Artifact Name, and Order
            updated_df = updated_df.sort_values(['Stage Name', 'Artifact Name', 'Order'])
            
            # Write back to Excel
            with pd.ExcelWriter(cascading_config_path, mode='a', if_sheet_exists='replace') as writer:
                updated_df.to_excel(writer, sheet_name='Cascading_Config', index=False)
            
            self.logger.info(f"Successfully updated cascading configuration with {len(column_config)} columns")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating cascading configuration: {str(e)}")
            return False
    
    def _apply_cascading_logic(self, table_name: str, stage_name: str) -> Optional[Dict]:
        """Apply cascading logic for the new artifact."""
        try:
            # Find the artifact ID for the new table
            # This would need to be implemented based on how artifacts are tracked
            # For now, we'll use a placeholder approach
            
            success = self.cascading_engine.cascade_all_missing_artifacts(include_technical_fields=True)
            
            if success:
                return {
                    "success": True,
                    "message": f"Cascading applied successfully for {table_name}",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "message": f"Cascading failed for {table_name}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error applying cascading logic: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_processing_report(
        self,
        analysis: SourceFileAnalysis,
        column_config: List[Dict[str, Any]],
        cascading_success: bool,
        cascading_results: Optional[Dict]
    ) -> Dict[str, Any]:
        """Generate comprehensive processing report."""
        # Primary key analysis
        pk_info = {
            "recommended_primary_key": None,
            "pk_confidence": 0.0,
            "is_composite": False,
            "total_candidates": len(analysis.primary_key_candidates)
        }
        
        if analysis.recommended_primary_key:
            pk_info.update({
                "recommended_primary_key": analysis.recommended_primary_key.columns,
                "pk_confidence": analysis.recommended_primary_key.confidence_score,
                "is_composite": analysis.recommended_primary_key.is_composite,
                "reasoning": analysis.recommended_primary_key.reasoning
            })
        
        # Column statistics
        column_stats = {
            "total_columns": len(column_config),
            "primary_key_columns": len([c for c in column_config if c["Column Group"] == "primary_key"]),
            "business_key_columns": len([c for c in column_config if c["Column Group"] == "BKs"]),
            "attribute_columns": len([c for c in column_config if c["Column Group"] == "attributes"]),
            "technical_columns": len([c for c in column_config if c["Column Group"] == "technical_fields"]),
            "data_quality_high": len([c for c in column_config if c.get("Data_Quality") == "high"]),
            "data_quality_medium": len([c for c in column_config if c.get("Data_Quality") == "medium"]),
            "data_quality_low": len([c for c in column_config if c.get("Data_Quality") == "low"])
        }
        
        # Overall assessment
        overall_quality = "high" if analysis.data_quality_score >= 0.8 else "medium" if analysis.data_quality_score >= 0.5 else "low"
        
        report = {
            "file_analysis": {
                "file_path": analysis.file_path,
                "file_type": analysis.file_type,
                "total_rows": analysis.total_rows,
                "total_columns": analysis.total_columns,
                "data_quality_score": analysis.data_quality_score,
                "overall_quality": overall_quality,
                "analysis_timestamp": analysis.analysis_timestamp,
                "errors": analysis.errors
            },
            "primary_key_analysis": pk_info,
            "column_statistics": column_stats,
            "cascading_results": {
                "configuration_updated": cascading_success,
                "cascading_applied": cascading_results is not None,
                "cascading_success": cascading_results.get("success", False) if cascading_results else False,
                "cascading_details": cascading_results
            },
            "recommendations": self._generate_recommendations(analysis, column_config),
            "report_timestamp": datetime.now().isoformat()
        }
        
        return report
    
    def _generate_recommendations(
        self, 
        analysis: SourceFileAnalysis, 
        column_config: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on analysis results."""
        recommendations = []
        
        # Primary key recommendations
        if not analysis.recommended_primary_key:
            recommendations.append("No clear primary key identified. Consider creating a surrogate key.")
        elif analysis.recommended_primary_key.confidence_score < 0.8:
            recommendations.append(f"Primary key confidence is {analysis.recommended_primary_key.confidence_score:.1%}. Review the recommended primary key.")
        
        # Data quality recommendations
        if analysis.data_quality_score < 0.6:
            recommendations.append("Data quality is below acceptable threshold. Consider data cleansing.")
        
        # Column-specific recommendations
        low_quality_columns = [c for c in analysis.columns_metadata if c.data_quality.value == "low"]
        if low_quality_columns:
            recommendations.append(f"{len(low_quality_columns)} columns have low data quality. Review: {[c.column_name for c in low_quality_columns[:3]]}")
        
        # Null value recommendations
        high_null_columns = [c for c in analysis.columns_metadata if c.null_count > analysis.total_rows * 0.5]
        if high_null_columns:
            recommendations.append(f"Columns with >50% null values: {[c.column_name for c in high_null_columns]}")
        
        return recommendations
    
    def _generate_output_path(self, source_file_path: str, table_name: str) -> str:
        """Generate output path for results export."""
        source_path = Path(source_file_path)
        output_dir = source_path.parent / "analysis_results"
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{table_name}_analysis_{timestamp}.xlsx"
        
        return str(output_dir / output_filename)
    
    def _export_results_to_excel(
        self,
        analysis: SourceFileAnalysis,
        column_config: List[Dict[str, Any]],
        report: Dict[str, Any],
        output_path: str
    ) -> bool:
        """Export all results to comprehensive Excel file."""
        try:
            # Export analysis using the source analyzer
            analysis_export_success = self.source_analyzer.export_analysis_to_excel(analysis, output_path)
            
            if analysis_export_success:
                # Add additional sheets for column configuration and report
                with pd.ExcelWriter(output_path, mode='a', if_sheet_exists='replace') as writer:
                    # Column configuration sheet
                    pd.DataFrame(column_config).to_excel(writer, sheet_name='Column_Configuration', index=False)
                    
                    # Processing report sheet
                    report_data = []
                    for section, content in report.items():
                        if isinstance(content, dict):
                            for key, value in content.items():
                                report_data.append({
                                    "Section": section,
                                    "Key": key,
                                    "Value": str(value)
                                })
                        else:
                            report_data.append({
                                "Section": section,
                                "Key": "",
                                "Value": str(content)
                            })
                    
                    pd.DataFrame(report_data).to_excel(writer, sheet_name='Processing_Report', index=False)
                    
                    # Recommendations sheet
                    recommendations_data = [{"Recommendation": rec} for rec in report.get("recommendations", [])]
                    pd.DataFrame(recommendations_data).to_excel(writer, sheet_name='Recommendations', index=False)
                
                self.logger.info(f"Results exported successfully to: {output_path}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error exporting results to Excel: {str(e)}")
            return False
    
    def batch_process_source_files(
        self, 
        source_files: List[Dict[str, str]],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Process multiple source files in batch.
        
        Args:
            source_files: List of dicts with keys: 'path', 'table_name', 'stage_name', 'artifact_type'
            **kwargs: Additional arguments passed to process_source_file
            
        Returns:
            List[Dict[str, Any]]: Results for each processed file
        """
        self.logger.info(f"Starting batch processing of {len(source_files)} source files")
        
        results = []
        for i, file_info in enumerate(source_files, 1):
            self.logger.info(f"Processing file {i}/{len(source_files)}: {file_info['path']}")
            
            try:
                result = self.process_source_file(
                    source_file_path=file_info['path'],
                    table_name=file_info['table_name'],
                    stage_name=file_info.get('stage_name', '1_bronze'),
                    artifact_type=file_info.get('artifact_type', 'dimension'),
                    **kwargs
                )
                results.append(result)
                
            except Exception as e:
                error_result = {
                    "source_file": file_info['path'],
                    "table_name": file_info['table_name'],
                    "error": str(e),
                    "success": False
                }
                results.append(error_result)
                self.logger.error(f"Error processing {file_info['path']}: {str(e)}")
        
        self.logger.info(f"Batch processing completed: {sum(1 for r in results if r['success'])} successful, {sum(1 for r in results if not r['success'])} failed")
        return results