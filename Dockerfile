FROM python:3.11

RUN apt-get update

# Clone repository
COPY . /minimal-cors-server
WORKDIR /minimal-cors-server

# Install dependencies
RUN python -m pip install -r requirements.txt

CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0" , "--port", "8000"]
