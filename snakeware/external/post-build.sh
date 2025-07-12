# This script is run by buildroot after it has finished building the rootfs, but before
# packing the final image.

# set this to the current Python 3.x version
PYLIBVER=python3.9

SNAKEWARE=$PWD/..

# copy snakewm
rm -rf output/target/usr/lib/$PYLIBVER/snakewm
cp -r $SNAKEWARE/../snakewm output/target/usr/lib/$PYLIBVER/

# copy snake-games
rm -rf output/target/usr/lib/$PYLIBVER/snake_games
cp -r $SNAKEWARE/../snake_games output/target/usr/lib/$PYLIBVER/