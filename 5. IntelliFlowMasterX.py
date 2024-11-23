# IntelliFlowMasterX.py
# Author: Paul, Tapajit
# Date: 19-09-2024

"""
Pipeline Execution: This script automatically runs the pipeline every time it is executed.

The List of scripts IntelliFlowMasterX.py triggers are:
1. DataSanitizerX: Cleans and sanitizes the Excel data based on predefined technical rules.
2. DataProcessorX: Processes the normalized Excel file for further rule-based transformations.
3. FromStatementGenerator: Generates SQL "FROM" statements from the normalized Excel data.
4. ExcelSanitizerSQLiteLoader: Loads sanitized data into SQLite for intermediate processing.
5. RuleExecutorX: Executes the business and technical rules defined in the Excel file.
6. GenerateTOC: Generates a Table of Contents (TOC) for the processed Excel output.
"""

import os
import subprocess
import logging
from datetime import datetime
import gc

# Global Configuration Parameters
OPCO_PARAM = "XYZ"  # Placeholder value
ENV_PARAM = "ENV"   # Placeholder value

# Define paths (Modify these paths as per your directory structure)
BASE_DIR = r"<BASE_DIRECTORY_PATH>"
EXCEL_FILE_PATH = os.path.join(BASE_DIR, 'Input_File.xlsx')
NORMALIZED_EXCEL_FILE_PATH = EXCEL_FILE_PATH.replace('.xlsx', '_Normalized.xlsx')
SCRIPT_DIR = r"<SCRIPT_DIRECTORY_PATH>"
DATA_DIRECTORY = r"<DATA_DIRECTORY_PATH>"
LOG_FILE_PATH = r"<LOG_FILE_PATH>"

# Define script paths dynamically (Adjusted to match your script names without spaces after numbers)
SCRIPT_PATHS = {
    'DataSanitizerX': os.path.join(SCRIPT_DIR, '1.DataSanitizerX.py'),
    'DataProcessorX': os.path.join(SCRIPT_DIR, '2.DataProcessorX.py'),
    'FromStatementGenerator': os.path.join(SCRIPT_DIR, 'from_statement_generator.py'),
    'ExcelSanitizerSQLiteLoader': os.path.join(SCRIPT_DIR, '3.ExcelSanitizerSQLiteLoader.py'),
    'RuleExecutorX': os.path.join(SCRIPT_DIR, '4.RuleExecutorX.py'),
    'GenerateTOC': os.path.join(SCRIPT_DIR, '7.Generate_Excel_ToC.py')
}

# Logging Setup
logging.basicConfig(filename=LOG_FILE_PATH, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def write_log(message):
    """Helper function to log a message to both the console and the log file."""
    print(message)
    logging.info(message)

def execute_script(script_name, params):
    """Execute a Python script and return its execution status."""
    try:
        script_path = SCRIPT_PATHS[script_name]
        if not os.path.isfile(script_path):
            write_log(f"Script {script_name} not found at path {script_path}")
            return "failure"
        write_log(f"Starting script: {script_name} with params {params}")
        cmd = ['python', script_path] + params
        write_log(f"Executing command: {cmd}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            write_log(f"Script {script_name} executed successfully.")
            return "success"
        else:
            write_log(f"Script {script_name} executed with warnings: {result.stderr}")
            return "success_with_warnings"
    except Exception as e:
        write_log(f"Script {script_name} failed with error: {str(e)}")
        return "failure"

def run_pipeline(opco, env):
    """Centralized function to manage and run the entire pipeline with dynamic parameters."""
    write_log("Pipeline execution started.")

    # Step 1: Execute DataSanitizerX
    params_dsx = [EXCEL_FILE_PATH, 'Tech Rules', 'Rule Desc,Remarks', NORMALIZED_EXCEL_FILE_PATH]
    result_1 = execute_script('DataSanitizerX', params_dsx)
    if result_1 == "failure":
        write_log("Pipeline terminated due to DataSanitizerX failure.")
        return

    # Step 2: Execute DataProcessorX
    params_dpx = [NORMALIZED_EXCEL_FILE_PATH, 'Normalized_TR']
    result_2 = execute_script('DataProcessorX', params_dpx)
    if result_2 == "failure":
        write_log("Pipeline terminated due to DataProcessorX failure.")
        return

    # Step 3: Execute FromStatementGenerator
    params_fsg = [NORMALIZED_EXCEL_FILE_PATH, 'Normalized_TR']
    result_fsg = execute_script('FromStatementGenerator', params_fsg)
    if result_fsg not in ("success", "success_with_warnings"):
        write_log("Pipeline terminated due to FromStatementGenerator failure.")
        return

    # Step 4: Execute ExcelSanitizerSQLiteLoader (Only if FromStatementGenerator succeeds or has warnings)
    params_esl = [DATA_DIRECTORY]
    result_3 = execute_script('ExcelSanitizerSQLiteLoader', params_esl)
    if result_3 == "failure":
        write_log("Pipeline terminated due to ExcelSanitizerSQLiteLoader failure.")
        return

    # Step 5: Execute RuleExecutorX
    params_rxe = [NORMALIZED_EXCEL_FILE_PATH, opco, env]
    result_4 = execute_script('RuleExecutorX', params_rxe)
    if result_4 == "failure":
        write_log("Pipeline terminated due to RuleExecutorX failure.")
        return

    # Step 6: Execute GenerateTOC
    params_toc = [NORMALIZED_EXCEL_FILE_PATH]
    result_5 = execute_script('GenerateTOC', params_toc)
    if result_5 == "failure":
        write_log("Pipeline terminated due to GenerateTOC failure.")
        return

    write_log("Pipeline execution completed successfully.")

def release_resources():
    """Release any resources or force garbage collection."""
    gc.collect()

if __name__ == "__main__":
    write_log(f"Running pipeline with OPCO_PARAM={OPCO_PARAM} and ENV_PARAM={ENV_PARAM}")
    run_pipeline(OPCO_PARAM, ENV_PARAM)
    release_resources()