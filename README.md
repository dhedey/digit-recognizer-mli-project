# Digit Recognizer - Machine Learning Institute Project

The full stack application is deployed at https://digit-recognizer.david-edey.com

I plan to add new/revised/better models over the coming days, to compare their performance.

![A screenshot of the digit recognizer application](./screenshot.png)

## Development

To get started:

* Install the [uv package manager](https://docs.astral.sh/uv/getting-started/installation/)
* You can use `./dev-server.sh` to run locally, which spins up:
  * The streamlit front-end on `:6080`
  * The model api on `:8000`, using an in-memory data store
* If you have docker you can also test the docker file with `docker compose up --build`, which spins up:
  * The streamlit front-end on `:6080`
  * The model api on `:8000`, using a PostgreSQL data store
  * A PostgreSQL container, with an init script to create a database and user 

## Deployment

See the scripts in the deployment folder. It uses the caddy reverse proxy for SSL termination.
