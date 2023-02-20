FROM python:3.8
ENV PYTHONBUFFERED=1
RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app/
RUN pip3 install -r requirements.txt
RUN pip3 install psycopg2-binary

COPY . /app/
COPY entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
