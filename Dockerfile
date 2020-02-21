# build environment
FROM python:3.7
LABEL maintainer="build@lecturegoggles.io"
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt update
RUN ACCEPT_EULA=Y apt install msodbcsql17 mssql-tools g++ -y
RUN apt install unixodbc-dev
COPY . /app
WORKDIR /app
RUN pip3 install --upgrade pip
RUN pip3 install pipenv
RUN pipenv lock -r >> requirements-from-pipenv.txt
RUN pip3 install -r requirements-from-pipenv.txt
RUN pip3 install gunicorn

EXPOSE 80

CMD ["gunicorn", "--bind", "0.0.0.0:80", "--timeout", "600", "autoapp:app"]
