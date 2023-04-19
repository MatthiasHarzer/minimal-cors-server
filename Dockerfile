FROM python:3.11

RUN apt-get update

# Install git
RUN apt-get install -y git

# Clone repository
RUN git clone "https://github.com/MatthiasHarzer/minimal-cors-server.git"
WORKDIR /minimal-cors-server

# Install dependencies
RUN python -m pip install -r requirements.txt

CMD ["uvicorn", "server:app", "--host", "0.0.0.0" , "--port", "8000"]
