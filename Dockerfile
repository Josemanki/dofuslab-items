FROM python:3-slim

# set up non-root user:
RUN useradd -m -d /home/python python
USER python
WORKDIR /home/python

# set up our folder structure and install requirements:
RUN mkdir -p input output
COPY requirements.txt .
RUN python3 -m pip install --user -r requirements.txt
ENV PYTHONPATH="/home/python/.local/bin"

# copy our files:
COPY --chown=python:python run_latest_update.sh .
COPY *.py ./

# run the latest update when we run the container
CMD /home/python/run_latest_update.sh
# note that you may want to run the container with:
#  -v output:/home/python/output
