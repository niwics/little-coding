#!/bin/bash

# author: Miroslav Kvasnica
# niwi.cz
# May 2011

STARTING_NUMBER=0
DIR='/media/terka2/Fotky/2007/Červen 2007/Jugyna vyber II'
OUTPUT_DIR='converted'

# move to dir
cd "$DIR"

# prepare subdir
if [ ! -d $OUTPUT_DIR ]; then
  mkdir "$OUTPUT_DIR"
fi

y=$STARTING_NUMBER

# alfabeticky
#files=$(ls -1 "$DIR" | sort -g | grep "\.jpg$")
#for src in $files

# s maskou
for n in `seq 170`;
do
  num=`expr $n - 1`
  src="jugyna ($num).jpg"
  if [ "$num" -lt "10" ]; then
    y="00$num"
  elif [ "$num" -lt "100" ]; then
    y="0$num"
  fi
  target="$OUTPUT_DIR/jug2007-$y.jpg"
  #echo "cp \"$src\" \"$target\""
  cp "$src" "$target"
  y=`expr $y + 1`
done
