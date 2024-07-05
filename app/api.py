import sys
from pathlib import Path
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

import json
from typing import Any

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from bike_sharing_model import __version__ as model_version
from bike_sharing_model.predict import make_prediction

from app import __version__, schemas
from app.config import settings

api_router = APIRouter()


@api_router.get("/health", response_model=schemas.Health, status_code=200)
def health() -> dict:
    """
    Root Get
    """
    health = schemas.Health(
        name=settings.PROJECT_NAME, api_version=__version__, model_version=model_version
    )

    return health.dict()


@api_router.post("/predict", response_model=schemas.PredictionResults, status_code=200)
async def predict(input_data: schemas.MultipleDataInputs) -> Any:
    try:
        
        input_df = pd.DataFrame(jsonable_encoder(input_data.inputs))
        results = make_prediction(input_data=input_df.replace({np.nan: None}))

        if results["errors"] is not None:
            raise HTTPException(status_code=400, detail=json.loads(results["errors"]))
        
        predictions = results["predictions"].item() if isinstance(results["predictions"], np.ndarray) else results["predictions"]
        return {
            "predictions": predictions,
            "version": results['version'],
            "errors": results["errors"]
        }
    
    except HTTPException as http_exc:
        # Custom error handling for HTTPException
        return {
            "errors": str(http_exc.detail),
            "version": "unknown",
            "predictions": None,
        }
    
    except KeyError as key_error:
        # Handle missing keys in the results or input data
        error_message = f"Missing required key: {str(key_error)} in the input data. Please ensure all fields are provided."
        return {
            "errors": error_message,
            "version": "unknown",
            "predictions": None,
        }
    