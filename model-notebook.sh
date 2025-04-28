trap kill_all_children SIGINT

kill_all_children(){
  echo "Ending all servers..."
  kill 0
}

uv sync --all-packages --dev
uv run --package model jupyter notebook ./packages/model/notebooks &

wait