FROM willtack/asltlbx-py:0.4.0

MAINTAINER Will Tackett <William.Tackett@pennmedicine.upenn.edu>

# Install basic dependencies
RUN apt-get update && apt-get -y install \
    jq \
    tar \
    zip \
    curl \
    nano \
    build-essential


# Install python packages
RUN pip3 install flywheel-sdk==12.4.0 \
 && pip3 install pathlib

# Make directory for flywheel spec (v0)
ENV FLYWHEEL /flywheel/v0
RUN mkdir -p ${FLYWHEEL}
COPY run.py ${FLYWHEEL}/run.py
COPY manifest.json ${FLYWHEEL}/manifest.json
RUN chmod a+rx ${FLYWHEEL}/*

# Set the entrypoint
ENTRYPOINT ["/flywheel/v0/run.py"]

# ENV preservation for Flywheel Engine
RUN env -u HOSTNAME -u PWD | \
  awk -F = '{ print "export " $1 "=\"" $2 "\"" }' > ${FLYWHEEL}/docker-env.sh

WORKDIR /flywheel/v0
