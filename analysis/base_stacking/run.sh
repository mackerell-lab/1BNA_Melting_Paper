

#!/bin/bash

# Input file to modify
input_file="plane_dis_multi.inp"

# Define your groups as: ID,range1,range2,Label
groups=(
    "1,10:32, 65:94,CG"
    "2,65:94, 127:149,GC"
    "3,127:149, 182:211,CG"
    "4,182:211, 244:270,GA"
    "5,244:270, 303:329,AA"
    "6,303:329, 362:388,AT"
    "7,362:388, 421:447,TT"
    "8,421:447, 480:502,TC"
    "9,480:502, 535:564,CG"
    "10,535:564, 597:619,GC"
    "11,597:619,652:681,CG"

    "13,714:736, 769:798,CG"
    "14,769:798, 831:853,GC"
    "15,831:853, 886:915,CG"
    "16,886:915, 948:974,GA"
    "17,948:974, 1007:1033,AA"
    "18,1007:1033, 1066:1092,AT"
    "19,1066:1092, 1125:1151,TT"
    "20,1125:1151, 1184:1206,TC"
    "21,1184:1206, 1239:1268,CG"
    "22,1239:1268, 1301:1323,GC"
    "23,1301:1323, 1356:1385,CG"
)


# Backup original file
cp "$input_file" "${input_file}.bak"

# Loop through each group
for group in "${groups[@]}"; do
    IFS=',' read -r id range1 range2 label <<< "$group"

    echo "Processing group $id ($range1,$range2,$label)..."

    tmpfile="tmp_${id}.inp"
    cp "$input_file" "$tmpfile"

    # Perform substitutions:
    # replace XXX:XX1 → first range
    # replace XXX:XX2 → second range
    sed -i \
        -e "s/XXX:XX1/${range1}/g" \
        -e "s/XXX:XX2/${range2}/g" \
        -e "s/angle_dis_shift_XXX/angle_dis_shift_${id}_${label}/g" \
        "$tmpfile"

    # Rename to final file
    newfile="plane_${id}_${label}.inp"
    mv "$tmpfile" "$newfile"

    echo "→ Created $newfile"

    # Run CHARMM if needed
    $charmm -i "$newfile" -o "$newfile.out"
done

