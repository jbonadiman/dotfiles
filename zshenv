function exists() {
  command -v $1 >/dev/null 2>&1
}

function push() {
  git commit -m $1; git push
}

function capitalize()
{
  printf '%s' "$1" | head -c 1 | tr [:lower:] [:upper:]
  printf '%s' "$1" | tail -c '+2'
}
