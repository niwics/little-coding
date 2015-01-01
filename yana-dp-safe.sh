# /bin/bash

# Autosave of latex source file of master thesis.
# Should be called from Cron.
# author: niwi.cz, 2012

SRC='/home/niwi/Ubuntu One/Yana/DP/text/obsah.tex'
DST_DIR=/media/terka2/zalohy/Yana-DP/
LAST_FILE=$DST_DIR$(ls -t $DST_DIR | head -1)
stat -c%s "$SRC"
stat -c%s "$LAST_FILE"
if [ $(stat -c%s "$SRC") != $(stat -c%s "$LAST_FILE") ]; then
  cp "$SRC" $DST_DIR"obsah-`date +%F-%X`.tex"
fi
