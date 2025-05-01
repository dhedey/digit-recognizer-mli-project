trap kill_all_children SIGINT

kill_all_children(){
  echo "Ending all servers..."
  kill 0
}

uv sync --all-packages --dev
uv run --package model-api fastapi dev packages/model-api/src/model_api/main.py &
echo "Waiting 5s to start streamlit..."
sleep 5
MODEL_API_BASE_URL=http://localhost:8000 uv run --package app streamlit run packages/app/src/app/streamlit_app.py &

wait