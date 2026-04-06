FROM node:16-alpine

RUN npm install -g @stoplight/spectral-cli

WORKDIR /app

COPY . .

RUN npm install
RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
