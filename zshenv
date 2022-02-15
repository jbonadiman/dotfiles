function exists() {
  command -v $1 >/dev/null 2>&1
}

function capitalize()
{
  printf '%s' "$1" | head -c 1 | tr [:lower:] [:upper:]
  printf '%s' "$1" | tail -c '+2'
}
