from fastapi import FastAPI, HTTPException, UploadFile, File, Body
from fastapi.responses import FileResponse, JSONResponse
import yaml
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from ShadowCalculator import ShadowCalculator
from DataModel.Shadow import Shadow
from .models import shadow_to_dict
from .help import get_help_data

app = FastAPI(
    title="Shadow Calculator API",
    description="API for calculating shadows cast by walls",
    version="1.0.0"
)

@app.post("/calculate/file")
async def calculate_shadows_from_file(
    file: UploadFile = File(...),
    save_animation: bool = True,
    save_plot: bool = True
) -> Dict[str, Any]:
    """Calculate shadows from an uploaded YAML/JSON file.
    
    Args:
        file: YAML or JSON file containing shadow calculation configuration
        save_animation: Whether to save animation (default: True)
        save_plot: Whether to save final plot (default: True)
        
    Returns:
        Dictionary containing:
        - shadows: List of shadow calculations
        - plot_path: Path to saved plot (if save_plot=True)
        - animation_path: Path to saved animation (if save_animation=True)
    """
    try:
        # Create temporary directory for outputs
        with tempfile.TemporaryDirectory() as temp_dir:
            # Read and parse input file
            content = await file.read()
            
            # Determine file type from extension
            if file.filename.endswith('.yml') or file.filename.endswith('.yaml'):
                data = yaml.safe_load(content)
            elif file.filename.endswith('.json'):
                data = json.loads(content)
            else:
                raise HTTPException(
                    status_code=400,
                    detail="File must be YAML (.yml/.yaml) or JSON (.json)"
                )
            
            # Configure output paths
            if save_plot:
                data.setdefault('plotConfig', {})
                data['plotConfig']['enabled'] = True
                data['plotConfig']['save_path'] = os.path.join(temp_dir, 'shadows_final.png')
                
            if save_animation:
                data.setdefault('animationConfig', {})
                data['animationConfig']['enabled'] = True
                data['animationConfig']['save_path'] = os.path.join(temp_dir, 'shadows.gif')
            
            # Calculate shadows
            calculator = ShadowCalculator.from_dict(data)
            all_shadows = calculator.calculate()
            
            # Convert shadows to dictionary format
            shadow_data = [
                [shadow_to_dict(shadow) for shadow in time_shadows]
                for time_shadows in all_shadows
            ]
            
            # Prepare response
            response = {'shadows': shadow_data}
            
            # Add file paths if files were saved
            if save_plot and calculator.plot_config.save_path:
                plot_path = calculator.plot_config.save_path
                if os.path.exists(plot_path):
                    response['plot'] = FileResponse(plot_path)
                    
            if save_animation and calculator.animation_config.save_path:
                animation_path = calculator.animation_config.save_path
                if os.path.exists(animation_path):
                    response['animation'] = FileResponse(animation_path)
            
            return response
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating shadows: {str(e)}"
        )

@app.post("/calculate/json")
async def calculate_shadows_from_json(
    data: Dict[str, Any] = Body(...),
    save_animation: bool = True,
    save_plot: bool = True
) -> Dict[str, Any]:
    """Calculate shadows from JSON data.
    
    Args:
        data: Shadow calculation configuration in the same format as YAML file
        save_animation: Whether to save animation (default: True)
        save_plot: Whether to save final plot (default: True)
        
    Returns:
        Dictionary containing:
        - shadows: List of shadow calculations
        - plot_path: Path to saved plot (if save_plot=True)
        - animation_path: Path to saved animation (if save_animation=True)
    """
    try:
        # Create temporary directory for outputs
        with tempfile.TemporaryDirectory() as temp_dir:
            # Configure output paths
            if save_plot:
                data.setdefault('plotConfig', {})
                data['plotConfig']['enabled'] = True
                data['plotConfig']['save_path'] = os.path.join(temp_dir, 'shadows_final.png')
                
            if save_animation:
                data.setdefault('animationConfig', {})
                data['animationConfig']['enabled'] = True
                data['animationConfig']['save_path'] = os.path.join(temp_dir, 'shadows.gif')
            
            # Calculate shadows
            calculator = ShadowCalculator.from_dict(data)
            all_shadows = calculator.calculate()
            
            # Convert shadows to dictionary format
            shadow_data = [
                [shadow_to_dict(shadow) for shadow in time_shadows]
                for time_shadows in all_shadows
            ]
            
            # Prepare response
            response = {'shadows': shadow_data}
            
            # Add file paths if files were saved
            if save_plot and calculator.plot_config.save_path:
                plot_path = calculator.plot_config.save_path
                if os.path.exists(plot_path):
                    response['plot'] = FileResponse(plot_path)
                    
            if save_animation and calculator.animation_config.save_path:
                animation_path = calculator.animation_config.save_path
                if os.path.exists(animation_path):
                    response['animation'] = FileResponse(animation_path)
            
            return response
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating shadows: {str(e)}"
        )

@app.get("/help")
async def get_help() -> Dict[str, Any]:
    """Get help information and example requests."""
    return get_help_data()

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
