
from fastapi import APIRouter, HTTPException, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Depends
from pydantic import BaseModel
import pandas as pd
from io import StringIO
from typing import Annotated
import json

router = APIRouter()

class ConvertRequest(BaseModel):
    data: str  # Input data for conversion
    format_from: str  # Original data format (csv, json, html)
    format_to: str  # Desired data format (csv, json, html)
    
    #Converts form data using classmethod
    @classmethod
    def as_form(
        cls,
        data: str = Form(),
        format_from: str = Form(), 
        format_to: str = Form()
    ):
        return cls(data=data, format_from=format_from, format_to=format_to)

@router.post('')
async def convert_data(request: ConvertRequest):
    data = request.data
    format_from = request.format_from.lower()
    format_to = request.format_to.lower()

    try:
        if format_from == "csv":
            df = pd.read_csv(StringIO(data))
        elif format_from == "json":
            df = pd.read_json(StringIO(data))
        elif format_from == "html":
            df = pd.read_html(data)[0]  # Assuming there's only one table in the HTML
        else:
            raise HTTPException(status_code=400, detail="Invalid format_from specified")

        if format_to == "csv":
            result_data = df.to_csv(index=False)
        elif format_to == "json":
            result_data = df.to_json(orient="records")
        elif format_to == "html":
            result_data = df.to_html(index=False, escape=False)
        else:
            raise HTTPException(status_code=400, detail="Invalid format_to specified")

        return {"converted_data": result_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during conversion: {str(e)}")
    
# Additional route for serving HTML content with HTMLResponse
@router.post('/html', response_class=HTMLResponse)
async def convert_data_html(request: ConvertRequest):
    response = await convert_data(request)
    return response["converted_data"]

# Additional route for handling form data using classmethod
@router.post('/form')
async def convert_data_form(request: ConvertRequest = Depends(ConvertRequest.as_form)):
    result = await convert_data(request)
    return result

# Old way... will probably delete
# @router.post('/form')
# async def convert_data_form(data: Annotated[str, Form()], format_from: Annotated[str, Form()], format_to: Annotated[str, Form()]):
#     print(data)
#     return convert_data_logic(data, format_from.lower(), format_to.lower())