FROM modelw-base-test

COPY --chown=user poetry.lock pyproject.toml ./

RUN modelw-docker install

COPY --chown=user . .

RUN modelw-docker build

CMD ["modelw-docker", "serve"]
