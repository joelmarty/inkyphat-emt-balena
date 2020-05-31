FROM balenalib/raspberry-pi-debian-python:3.7-buster-build

WORKDIR /usr/app
COPY pip.conf /etc/

RUN install_packages \
  libatlas3-base \
  libgfortran3 \
  libzstd1 \
  libjbig0 \
  libwebpdemux2 \
  libwebpmux3 \
  libtiff5 \
  libopenjp2-7 \
  libwebp6 \
  liblcms2-2

COPY . .

RUN pip install -r requirements.txt

CMD python emt_bus_arrivals.py