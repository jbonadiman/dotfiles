echo "installing 'scoop'..."
iwr -useb get.scoop.sh | iex

echo "installing 'aria2'..."
scoop install aria2

echo "adding 'java' bucket to scoop..."
scoop bucket add java

echo "adding 'jetbrains' bucket to scoop..."
scoop bucket add jetbrains

echo "adding 'nerd-fonts' bucket to scoop..."
scoop bucket add nerd-fonts

echo "installing 'openjdk'..."
scoop install openjdk

