# Stage 1 - Backend build environment
# includes compilers and build tooling to create the environment
FROM python:3.12-slim-bullseye AS backend-build

RUN apt-get update && apt-get install -y --no-install-recommends \
        pkg-config \
        build-essential \
        git \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN mkdir /app/src

ARG ENVIRONMENT=production

RUN pip install uv -U
COPY ./backend/requirements /app/requirements
RUN uv pip install --system -r requirements/${ENVIRONMENT}.txt

# Stage 2 - Build the Front end
FROM node:20-bullseye-slim AS frontend-build

RUN mkdir /frontend
WORKDIR /frontend

RUN apt-get update && apt-get install -y --no-install-recommends \
  git \
  ca-certificates \
  && rm -rf /var/lib/apt/lists/*

COPY ./frontend/package-lock.json ./frontend/package.json ./

RUN npm ci

COPY ./frontend .

RUN npm run build

# Stage 3 - Build docker image suitable for production
FROM python:3.12-slim-bullseye

# Stage 3.1 - Set up the needed production dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        procps \
        vim \
        mime-support \
        postgresql-client \
        gettext \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./backend/bin/docker_start.sh /start.sh

RUN mkdir -p /app/log /app/media /app/src/openbeheer/static/

# copy backend build deps
COPY --from=backend-build /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=backend-build /usr/local/bin/uwsgi /usr/local/bin/uwsgi

COPY ./backend/src /app/src

COPY --from=frontend-build /frontend/dist /app/src/openbeheer/static/frontend
COPY --from=frontend-build /frontend/dist/static/assets /app/src/openbeheer/static/assets

RUN useradd -M -u 1000 maykin && chown -R maykin:maykin /app

VOLUME ["/app/log", "/app/media"]

# drop privileges
USER maykin

ARG COMMIT_HASH
ARG RELEASE=latest
ARG DJANGO_SETTINGS=docker

ENV RELEASE=${RELEASE} \
    GIT_SHA=${COMMIT_HASH} \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=openbeheer.conf.${DJANGO_SETTINGS} 
    
# Needed otherwise the call to collectstatic fails
ARG SECRET_KEY=dummy

LABEL org.label-schema.vcs-ref=$COMMIT_HASH \
      org.label-schema.vcs-url="https://github.com/maykinmedia/open-beheer" \
      org.label-schema.version=$RELEASE \
      org.label-schema.name="openbeheer"

RUN python src/manage.py collectstatic --noinput \
    && python src/manage.py compilemessages

EXPOSE 8000
CMD ["/start.sh"]