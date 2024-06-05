from fastapi import FastAPI, Body, Response
from pydantic import BaseModel
from ai_model import generate_response
import pandas as pd
import io


class Item(BaseModel):
    user_question: str


app = FastAPI()


@app.post("/generate-response")
def generate_response_api(item: Item = Body(...)):
    response = generate_response(item.user_question)
    # if isinstance(response, pd.DataFrame):
    #     response.to_csv("Report.csv", index=False)
    #     return send_report()
    # else:
    return response


# TODO: ver como retornar no chat
@app.get("/send-report")
def send_report():

    with open("Report.csv", "rb") as file:
        data = file.read()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerows(data)

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=data.csv"},
    )
