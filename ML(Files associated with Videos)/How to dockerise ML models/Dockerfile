FROM python:slim
WORKDIR /ml-docker
ADD . /ml-docker
RUN pip install --upgrade pip
RUN pip install numpy scipy sklearn
CMD ["python", "main.py"]