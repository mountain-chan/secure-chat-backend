FROM python:3.7
WORKDIR /secure-chat-backend
ADD . /secure-chat-backend
RUN pip install -r requirements.txt
EXPOSE 5012
# CMD python main.py