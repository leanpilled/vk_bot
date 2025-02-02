
FROM python:3.13-alpine

RUN mkdir vk_bot
WORKDIR /vk_bot
COPY ./pyproject.toml ./
COPY ./.python-version ./
COPY ./uv.lock ./
RUN pip3 install uv
RUN uv sync --frozen
ADD . /vk_bot

CMD ["uv", "run", "app/main.py"]