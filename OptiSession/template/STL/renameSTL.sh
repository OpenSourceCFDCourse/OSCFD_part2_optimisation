#!/bin/bash
rm -rf joined.*

for filename in *.stl
do
  #echo $filename | tee log.sed  
  if [[ "$filename" != joined* ]]; 
  then
	echo $filename
	printf '1,$ s/solid.*$/solid '"${filename%\.*}"'/g\nw! '"./${filename%\.*}.stl"'\nq!' | ex - "./${filename%\.*}.stl"
    cat "./${filename%\.*}.stl" >> "./joined.stl"
    #rm "./${filename%\.*}.stl"  # comment line to keep the individual stl files.
  fi
  
done;
