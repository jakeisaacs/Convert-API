from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import pandas as pd
from io import StringIO

app = FastAPI()

class ConvertRequest(BaseModel):
    data: str  # Input data for conversion
    format_from: str  # Original data format (csv, json, html)
    format_to: str  # Desired data format (csv, json, html)

@app.post("/convert")
async def convert_data(request: ConvertRequest):
    data = request.data
    format_from = request.format_from.lower()
    format_to = request.format_to.lower()

    try:
        if format_from == "csv":
            df = pd.read_csv(StringIO(data))
        elif format_from == "json":
            df = pd.read_json(data)
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
@app.post("/convert/html", response_class=HTMLResponse)
def convert_data_html(request: ConvertRequest):
    response = convert_data(request)
    return {"converted_data": response["converted_data"]}

# Additional route for serving a simple HTML form for testing
@app.get("/")
def read_root():
    return HTMLResponse(
        """
        <html>
            <head>
                <title>Data Conversion Form</title>
            </head>
            <body>
                <h1>Data Conversion</h1>
                <form action="/convert" method="post">
                    <label for="data">Data:</label>
                    <textarea name="data" rows="5" cols="50"></textarea><br>
                    <label for="format_from">Format From:</label>
                    <input type="text" name="format_from" required><br>
                    <label for="format_to">Format To:</label>
                    <input type="text" name="format_to" required><br>
                    <button type="submit">Convert</button>
                </form>
            </body>
        </html>
        """
    )
