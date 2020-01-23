# build environment
FROM python:3.6
LABEL maintainer="build@lecturegoggles.io"
COPY . /app
WORKDIR /app
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn

ENV db_username=${db_username}
ENV db_passwd=${db_passwd}
ENV db_name=${db_name}
ENV db_host=${db_host}
ENV db_port=${db_port}

EXPOSE 80

CMD ["gunicorn", "--bind", "0.0.0.0:80", "--timeout", "600", "autoapp:app"]
