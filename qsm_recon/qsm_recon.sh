#!/usr/bin/env bash

#source /etc/fsl/4.1/fsl.sh
gamma=773 ## (2*PI*f[MHz]=2*pi*123)
TE=0.0173  ## sec

BILD_MAG=FLASH_MAGNITUDE.nii
BILD_PHASE=FLASH_PHASE.nii
ORGMASK=brain_mask.nii.gz
TEMP_FOLDER=$1
OUTPUT=QSM.nii
WINKEL=$2
QSM_RECON_DIR=/scr/malta1/Github/GluIRON/qsm_recon
maskeverschieben=yes ### yes/no

bet $BILD_MAG brain -m -f 0.1
${QSM_RECON_DIR}/siemens_phase $BILD_PHASE $TEMP_FOLDER/rad_$BILD_PHASE

### place everything in cubic matrix
### original matrix: (x y z) 208 256 160
${QSM_RECON_DIR}/place_in_new_matrix $ORGMASK 350 350 350 $TEMP_FOLDER/newmat_$ORGMASK
${QSM_RECON_DIR}/place_in_new_matrix $BILD_MAG 350 350 350 $TEMP_FOLDER/newmat_$BILD_MAG
${QSM_RECON_DIR}/place_in_new_matrix $TEMP_FOLDER/rad_$BILD_PHASE 350 350 350 $TEMP_FOLDER/newmat_$BILD_PHASE

############ BEGIN modify mask#################
mask=$TEMP_FOLDER/newmat_$ORGMASK
outfile=mask.nii.gz
if [ $maskeverschieben = "yes" ] 
then
echo verschieben
miconv -noscale -shift '4,4,0' $mask $TEMP_FOLDER/kreis_verschoben1.nii
miconv -noscale -shift '4,-4,0' $mask $TEMP_FOLDER/kreis_verschoben2.nii
miconv -noscale -shift '-4,4,0' $mask $TEMP_FOLDER/kreis_verschoben3.nii
miconv -noscale -shift '-4,-4,0' $mask $TEMP_FOLDER/kreis_verschoben4.nii

miconv -noscale -shift '4,4,9' $mask $TEMP_FOLDER/kreis_verschoben5.nii
miconv -noscale -shift '4,-4,9' $mask $TEMP_FOLDER/kreis_verschoben6.nii
miconv -noscale -shift '-4,4,9' $mask $TEMP_FOLDER/kreis_verschoben7.nii
miconv -noscale -shift '-4,-4,9' $mask $TEMP_FOLDER/kreis_verschoben8.nii

miconv -noscale -shift '4,4,-3' $mask $TEMP_FOLDER/kreis_verschoben9.nii
miconv -noscale -shift '4,-4,-3' $mask $TEMP_FOLDER/kreis_verschoben10.nii
miconv -noscale -shift '-4,4,-3' $mask $TEMP_FOLDER/kreis_verschoben11.nii
miconv -noscale -shift '-4,-4,-3' $mask $TEMP_FOLDER/kreis_verschoben12.nii

micalc -noscale -if1 $mask -op '-' -if2 $TEMP_FOLDER/kreis_verschoben1.nii -of $TEMP_FOLDER/differenz1.nii
micalc -noscale -if1 $mask -op '-' -if2 $TEMP_FOLDER/kreis_verschoben2.nii -of $TEMP_FOLDER/differenz2.nii
micalc -noscale -if1 $mask -op '-' -if2 $TEMP_FOLDER/kreis_verschoben3.nii -of $TEMP_FOLDER/differenz3.nii
micalc -noscale -if1 $mask -op '-' -if2 $TEMP_FOLDER/kreis_verschoben4.nii -of $TEMP_FOLDER/differenz4.nii

micalc -noscale -if1 $mask -op '-' -if2 $TEMP_FOLDER/kreis_verschoben5.nii -of $TEMP_FOLDER/differenz5.nii
micalc -noscale -if1 $mask -op '-' -if2 $TEMP_FOLDER/kreis_verschoben6.nii -of $TEMP_FOLDER/differenz6.nii
micalc -noscale -if1 $mask -op '-' -if2 $TEMP_FOLDER/kreis_verschoben7.nii -of $TEMP_FOLDER/differenz7.nii
micalc -noscale -if1 $mask -op '-' -if2 $TEMP_FOLDER/kreis_verschoben8.nii -of $TEMP_FOLDER/differenz8.nii

micalc -noscale -if1 $mask -op '-' -if2 $TEMP_FOLDER/kreis_verschoben9.nii -of $TEMP_FOLDER/differenz9.nii
micalc -noscale -if1 $mask -op '-' -if2 $TEMP_FOLDER/kreis_verschoben10.nii -of $TEMP_FOLDER/differenz10.nii
micalc -noscale -if1 $mask -op '-' -if2 $TEMP_FOLDER/kreis_verschoben11.nii -of $TEMP_FOLDER/differenz11.nii
micalc -noscale -if1 $mask -op '-' -if2 $TEMP_FOLDER/kreis_verschoben12.nii -of $TEMP_FOLDER/differenz12.nii

micalc -noscale -if $TEMP_FOLDER/differenz1.nii -op 'abs' -of $TEMP_FOLDER/differenz1.nii
micalc -noscale -if $TEMP_FOLDER/differenz2.nii -op 'abs' -of $TEMP_FOLDER/differenz2.nii
micalc -noscale -if $TEMP_FOLDER/differenz3.nii -op 'abs' -of $TEMP_FOLDER/differenz3.nii
micalc -noscale -if $TEMP_FOLDER/differenz4.nii -op 'abs' -of $TEMP_FOLDER/differenz4.nii

micalc -noscale -if $TEMP_FOLDER/differenz5.nii -op 'abs' -of $TEMP_FOLDER/differenz5.nii
micalc -noscale -if $TEMP_FOLDER/differenz6.nii -op 'abs' -of $TEMP_FOLDER/differenz6.nii
micalc -noscale -if $TEMP_FOLDER/differenz7.nii -op 'abs' -of $TEMP_FOLDER/differenz7.nii
micalc -noscale -if $TEMP_FOLDER/differenz8.nii -op 'abs' -of $TEMP_FOLDER/differenz8.nii

micalc -noscale -if $TEMP_FOLDER/differenz9.nii -op 'abs' -of $TEMP_FOLDER/differenz9.nii
micalc -noscale -if $TEMP_FOLDER/differenz10.nii -op 'abs' -of $TEMP_FOLDER/differenz10.nii
micalc -noscale -if $TEMP_FOLDER/differenz11.nii -op 'abs' -of $TEMP_FOLDER/differenz11.nii
micalc -noscale -if $TEMP_FOLDER/differenz12.nii -op 'abs' -of $TEMP_FOLDER/differenz12.nii

micalc -noscale -if1 $TEMP_FOLDER/differenz1.nii -op '+' -if2 $TEMP_FOLDER/differenz2.nii -of $TEMP_FOLDER/result.nii
micalc -noscale -if1 $TEMP_FOLDER/result.nii -op '+' -if2 $TEMP_FOLDER/differenz3.nii -of $TEMP_FOLDER/result.nii
micalc -noscale -if1 $TEMP_FOLDER/result.nii -op '+' -if2 $TEMP_FOLDER/differenz4.nii -of $TEMP_FOLDER/result.nii
micalc -noscale -if1 $TEMP_FOLDER/result.nii -op '+' -if2 $TEMP_FOLDER/differenz5.nii -of $TEMP_FOLDER/result.nii
micalc -noscale -if1 $TEMP_FOLDER/result.nii -op '+' -if2 $TEMP_FOLDER/differenz6.nii -of $TEMP_FOLDER/result.nii
micalc -noscale -if1 $TEMP_FOLDER/result.nii -op '+' -if2 $TEMP_FOLDER/differenz7.nii -of $TEMP_FOLDER/result.nii
micalc -noscale -if1 $TEMP_FOLDER/result.nii -op '+' -if2 $TEMP_FOLDER/differenz8.nii -of $TEMP_FOLDER/result.nii
micalc -noscale -if1 $TEMP_FOLDER/result.nii -op '+' -if2 $TEMP_FOLDER/differenz9.nii -of $TEMP_FOLDER/result.nii
micalc -noscale -if1 $TEMP_FOLDER/result.nii -op '+' -if2 $TEMP_FOLDER/differenz10.nii -of $TEMP_FOLDER/result.nii
micalc -noscale -if1 $TEMP_FOLDER/result.nii -op '+' -if2 $TEMP_FOLDER/differenz11.nii -of $TEMP_FOLDER/result.nii
micalc -noscale -if1 $TEMP_FOLDER/result.nii -op '+' -if2 $TEMP_FOLDER/differenz12.nii -of $TEMP_FOLDER/result.nii

${QSM_RECON_DIR}/create_mask $TEMP_FOLDER/result.nii 1 1000 $TEMP_FOLDER/result.nii
micalc -noscale -if1 $TEMP_FOLDER/result.nii -op '*' -if2 $mask -of $TEMP_FOLDER/result.nii
micalc -noscale -if1 $mask -op '-' -if2 $TEMP_FOLDER/result.nii -of $TEMP_FOLDER/result.nii
${QSM_RECON_DIR}/place_in_new_matrix $TEMP_FOLDER/result.nii  208 256 160 $outfile
fi
fslcpgeom $BILD_MAG $outfile
rm -rf $TEMP_FOLDER/*verschoben* $TEMP_FOLDER/*differenz* $TEMP_FOLDER/result.nii

############ END modify mask#################

${QSM_RECON_DIR}/place_in_new_matrix $outfile 350 350 350 $TEMP_FOLDER/newmat_$outfile

${QSM_RECON_DIR}/SDI $TEMP_FOLDER/newmat_$BILD_PHASE 2 0.00005 $TEMP_FOLDER/newmat_$outfile $TEMP_FOLDER/newmat

micalc -noscale -if1 $TEMP_FOLDER/newmat_sharp.nii -op '/' -in2 $gamma -of /tmp/mask1.nii
micalc -noscale -if1 /tmp/mask1.nii -op '/' -in2 $TE -of /tmp/mask2.nii
miconv -noscale /tmp/mask2.nii $TEMP_FOLDER/newmat_sharp.nii

${QSM_RECON_DIR}/fit_sph_harm 2 $TEMP_FOLDER/newmat_sharp.nii $TEMP_FOLDER/newmat_$outfile $TEMP_FOLDER/newmat_sharp_plus_pol

${QSM_RECON_DIR}/from_phase_to_susc_1angle2 $WINKEL $TEMP_FOLDER/newmat_sharp_plus_pol_filtered.nii 1.99 $OUTPUT

### back to right geometry 
${QSM_RECON_DIR}/place_in_new_matrix $OUTPUT 208 256 160 $OUTPUT
micalc -noscale -if1 $OUTPUT -op '*' -if2 $outfile -of $OUTPUT
fslcpgeom $BILD_MAG $OUTPUT

${QSM_RECON_DIR}/place_in_new_matrix $TEMP_FOLDER/newmat_sharp_plus_pol_filtered.nii 208 256 160 sharp_plus_pol_filtered.nii
micalc -noscale -if1 sharp_plus_pol_filtered.nii -op '*' -if2 $outfile -of sharp_plus_pol_filtered.nii
fslcpgeom $BILD_MAG sharp_plus_pol_filtered.nii

#cleaning
rm -rf Mzk.nii k_filter.nii qmphase* sharp_Bdelta.nii sharp_DeltaMinusRho.nii mask_newmat.nii sharp_filtered.nii sharp_plus_pol_fit.nii unwrapped_newmat.nii unwrapped.nii uwphase* bet* mask_newmat.nii test.nii delme* newmat_* rad_*

### view
#fslview $BILD_MAG sharp_plus_pol_filtered.nii $OUTPUT


