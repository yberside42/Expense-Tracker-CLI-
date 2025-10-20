# exporters.py

from __future__ import annotations
from typing import Any, Dict, List
from pathlib import Path
import csv 
import json

def export_to_csv(rows: List[Dict[str, Any]], *, 
                  dest: str, 
                  columns: List[str], 
                  overwrite: bool = False
) -> None:
    """Export the selected data to a CSV file.

    Args:
        rows (List[Dict[str, Any]]): List to export.
        dest (str): Destination path for the file.
        columns (List[str]): Columns to export
        overwrite (bool, optional): In case the file already exists (situational). Defaults to False.

    Raises:
        FileExistsError: If the file already exists.
    """
    path = Path(dest)
    
    # Checking if the path exists and if the file already exists
    if path.exists() and not overwrite:
        raise FileExistsError(str(path))
    
    # Creating the CSV file
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with path.open(mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        writer.writerow(columns)
        
        for row in rows:
            writer.writerow([row.get(column) for column in columns])
    

def export_to_json(rows: List[Dict[str, Any]], *, 
                   dest: str, 
                   overwrite: bool = False, 
                   pretty: bool = False
) -> None:
    """Export the selected data to a JSON file.

    Args:
        rows (List[Dict[str, Any]]): List to export.
        dest (str): Destination path for the file.
        overwrite (bool): In case the file already exists (situational). Defaults to False.
        pretty (bool): Format (optional).

    Raises:
        FileExistsError: If the file already exists.
    """
    path = Path(dest)
    
    # Checking if the path exists and if the file already exists
    if path.exists() and not overwrite:
        raise FileExistsError(str(path))
    
    # Creating the JSON file
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open(mode="w", encoding="utf-8") as file:
        json.dump(rows, file, ensure_ascii=False, indent=(2 if pretty else None))
                  
    
