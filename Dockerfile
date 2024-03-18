FROM tensorflow/tensorflow:2.13.0
RUN /usr/bin/python3 -m pip install --upgrade pip && \
    pip install ruamel.yaml
ENTRYPOINT bash