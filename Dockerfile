FROM 3.11.1-bullseye-slim

RUN apt-get update

# Install dependencies
RUN python -m pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0" , "--port", "8000"]
