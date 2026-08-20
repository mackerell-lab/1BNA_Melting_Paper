#!/bin/bash

# Input file to modify
input_file="dip_multi.inp"

# Define your groups as: ID,start:end,Label
groups=(
    "1,10:32,C"
    "2,65:94,G"
    "3,127:149,C"
    "4,182:211,G"
    "5,244:270,A"
    "6,303:329,A"
    "7,362:388,T"
    "8,421:447,T"
    "9,480:502,C"
    "10,535:564,G"
    "11,597:619,C"
    "12,652:681,G"

    "13,714:736,C"
    "14,769:798,G"
    "15,831:853,C"
    "16,886:915,G"
    "17,948:974,A"
    "18,1007:1033,A"
    "19,1066:1092,T"
    "20,1125:1151,T"
    "21,1184:1206,C"
    "22,1239:1268,G"
    "23,1301:1323,C"
    "24,1356:1385,G"
    # ... up to 22
)

# Backup original file before modification
cp "$input_file" "${input_file}.bak"

# Loop through each group
for group in "${groups[@]}"; do
    IFS=',' read -r id range label <<< "$group"

    echo "Processing group $id ($range, $label)..."

    # Create a temporary copy for each iteration
    tmpfile="tmp_${id}.inp"
    cp "$input_file" "$tmpfile"

    # Perform the substitutions
    sed -i \
        -e "s/XXX:XXX/${range}/g" \
        -e "s/base_XX/base_${id}_${label}/g" \
        "$tmpfile"

    # Optional: rename output file
    newfile="dip_${id}_${label}.inp"
    mv "$tmpfile" "$newfile"

    echo "→ Created $newfile"

    $charmm -i $newfile -o $newfile.out
done

