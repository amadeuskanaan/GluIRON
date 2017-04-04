if [ ! "$#" -eq "2" ]
then
  echo "usage: sh reconstruct_phase_FLASH.sh /scr/mrincoming7t/2015/measurement_folder/ /a/projects/neu009_sequencing_plasticity/probands/subject_code/d#/P##_d#_"
  exit 1
fi

source /etc/fsl/4.1/fsl.sh
TE1=4.08 ##9.18 4.08; low res scan
TE2=9.18 ##9.18 4.08; low res scan
TEhighres1=8.16 ##8.16 18.35
TEhighres2=18.35 ##8.16 18.35
DeltaTE=5.1	# offset=(TE2*Phi1-TE1*Phi2)/(TE2-TE1)
Phi1=unwrapped_channels_Te4.08.nii.gz # output don't change
Phi2=unwrapped_channels_Te9.18.nii.gz # output don't change

## input folders on mrincoming7t or archives
Archivfolder=$1

#Dicomfolder=/scr/mrincoming7t/2015/OL1T150618_102025.SEPT/
Dicomfolder=$Archivfolder

Niftifolder=NIFTI

## output folder + file prefix
FINAL_DEST=$2

## input images
Prefixhighresmagchannels=all_partitions_magnitude
Prefixhighresmagcombined=all_partitions_magnitude_mean
Prefixhighresphasechannels=all_partitions_phase

Prefixlowresmagchannels=S12_gre_phase_ref
Prefixlowresmagcombined=S13_gre_phase_ref
Prefixlowresphasechannels=S14_gre_phase_ref

### check below "to check leave out certain channels"

phase_offset=phase_channels_offset_smoothed.nii.gz
prefix_output1=lowres2highres1 # output don't change
prefix_output2=lowres2highres2 # output don't change
lowres_magnitude=${Niftifolder}/${Prefixlowresmagcombined}_Te${TE2}.nii
highres_magnitude1=${Niftifolder}/${Prefixhighresmagcombined}_Te${TEhighres1}.nii
highres_magnitude2=${Niftifolder}/${Prefixhighresmagcombined}_Te${TEhighres2}.nii
phase_offset=phase_channels_offset_smoothed.nii.gz # output don't change
prefix_output=lowres2highres # output don't change


# processing steps
step_previous_cleaning=0	#delete outputs from a previous run
step_copy=0 			#don't use it!!! copy the data from mrincoming7t
step_conversion=0		#conversion to nifti
step_unwrapping=0		#unwrapping the lowres reference scan
step_offset=1			#calculate the phase offset map
step_correction=1		#corrects the highres phase images using the offset map
step_copy_to_final_dest=1	#copy the corrected phase/magn data to the final destination
step_cleaning=0			#delete outputs, which are not needed anymore

# first go to a /tmp directory
mkdir -p /tmp/flash_phase_both
cd /tmp/flash_phase_both/

if [ $step_previous_cleaning == 1 ]
  then echo "===================== deleting files from previous runs ====================="
  rm -rf *.nii.gz *.nii
  rm -rf $Niftifolder
fi

if [ $step_copy == 1 ]
  then echo "===================== copying ====================="
mkdir -p $Niftifolder
# this subfolder is just for keeping track of which data set is being processed
mkdir -p $Niftifolder/$Dicomfolder
cp $Archivfolder/*_$Prefixlowresmagchannels.tar.xz $Niftifolder
tar -xvf $Niftifolder/*_$Prefixlowresmagchannels.tar.xz
cp $Archivfolder/*_$Prefixlowresmagcombined.tar.xz $Niftifolder
tar -xvf $Niftifolder/*_$Prefixlowresmagcombined.tar.xz
cp $Archivfolder/*_$Prefixlowresphasechannels.tar.xz $Niftifolder
tar -xvf $Niftifolder/*_$Prefixlowresphasechannels.tar.xz
cp $Archivfolder/*_$Prefixhighresmagchannels.tar.xz $Niftifolder
tar -xvf $Niftifolder/*_$Prefixhighresmagchannels.tar.xz
cp $Archivfolder/*_$Prefixhighresmagcombined.tar.xz $Niftifolder
tar -xvf $Niftifolder/*_$Prefixhighresmagcombined.tar.xz
cp $Archivfolder/*_$Prefixhighresphasechannels.tar.xz $Niftifolder
tar -xvf $Niftifolder/*_$Prefixhighresphasechannels.tar.xz

fi

if [ $step_conversion == 1 ]
  then echo "===================== conversion ====================="
mkdir -p $Niftifolder
# this subfolder is just for keeping track of which data set is being processed
mkdir -p $Niftifolder/$Dicomfolder
isisconv -in $Dicomfolder/$Prefixlowresmagchannels/ -rf dcm -out $Niftifolder/S{sequenceNumber}_{sequenceDescription}_Te{echotime}_chan{coilChannelMask}.nii -wdialect fsl

isisconv -in $Dicomfolder/$Prefixlowresmagcombined/ -rf dcm -out $Niftifolder/S{sequenceNumber}_{sequenceDescription}_Te{echotime}.nii -wdialect fsl

isisconv -in $Dicomfolder/$Prefixlowresphasechannels/ -rf dcm -out $Niftifolder/S{sequenceNumber}_{sequenceDescription}_Te{echotime}_chan{coilChannelMask}.nii -wdialect fsl

isisconv -in $Dicomfolder/$Prefixhighresmagchannels/ -rf dcm -out $Niftifolder/S{sequenceNumber}_{sequenceDescription}_Te{echotime}_chan{coilChannelMask}.nii -wdialect fsl

isisconv -in $Dicomfolder/$Prefixhighresmagcombined/ -rf dcm -out $Niftifolder/S{sequenceNumber}_{sequenceDescription}_Te{echotime}.nii -wdialect fsl

isisconv -in $Dicomfolder/$Prefixhighresphasechannels/ -rf dcm -out $Niftifolder/S{sequenceNumber}_{sequenceDescription}_Te{echotime}_chan{coilChannelMask}.nii -wdialect fsl

fi

if [ $step_unwrapping == 1 ]
  then echo "===================== unwrapping ====================="
fslmerge -t phase_channels_Te$TE1.nii.gz ${Niftifolder}/${Prefixlowresphasechannels}_Te${TE1}*
fslmerge -t phase_channels_Te$TE2.nii.gz ${Niftifolder}/${Prefixlowresphasechannels}_Te${TE2}*
fslmerge -t magnitude_channels_Te$TE1.nii.gz ${Niftifolder}/${Prefixlowresmagchannels}_Te${TE1}*
fslmerge -t magnitude_channels_Te$TE2.nii.gz ${Niftifolder}/${Prefixlowresmagchannels}_Te${TE2}*

/afs/cbs.mpg.de/projects/neu009_sequencing-plasticity/scripts/QSM/siemens_phase phase_channels_Te$TE1.nii.gz phase_channels_rad_Te$TE1.nii.gz
/afs/cbs.mpg.de/projects/neu009_sequencing-plasticity/scripts/QSM/siemens_phase phase_channels_Te$TE2.nii.gz phase_channels_rad_Te$TE2.nii.gz

fslsplit phase_channels_rad_Te$TE1.nii.gz phase_rad_Te$TE1 -t
fslsplit phase_channels_rad_Te$TE2.nii.gz phase_rad_Te$TE2 -t
fslsplit magnitude_channels_Te$TE1.nii.gz magnitude -t
bet ${lowres_magnitude}.nii brain -m -f 0.1

for chan in 0000 0001 0002 0003 0004 0005 0006 0007 0008 0009 0010 0011 0012 0013 0014 0015 0016 0017 0018 0019 0020 0021 0022 0023 0024 0025 0026 0027 0028 0029 0030 0031
do
echo "channel:" $chan
# prelude is slow for large "-n" option
prelude -p phase_rad_Te${TE1}${chan}.nii.gz -a magnitude$chan.nii.gz -o unwrapped$chan.nii.gz -v -m brain_mask.nii.gz -n 30
done
fslmerge -t unwrapped_channels_Te$TE1.nii.gz unwrapped00*

for chan in 0000 0001 0002 0003 0004 0005 0006 0007 0008 0009 0010 0011 0012 0013 0014 0015 0016 0017 0018 0019 0020 0021 0022 0023 0024 0025 0026 0027 0028 0029 0030 0031
do
echo "channel:" $chan
prelude -p phase_rad_Te${TE2}${chan}.nii.gz -a magnitude$chan.nii.gz -ols unwrapped$chan.nii.gz -v -m brain_mask.nii.gz -n 30
done
fslmerge -t unwrapped_channels_Te$TE2.nii.gz unwrapped00*

fi

if [ $step_offset == 1 ]
# calculates the phase offset map, see also Robinson et al. MRM 2011
  then echo "===================== calc offset ====================="
micalc -if1 $Phi1 -op '*' -in2 $TE2 -of tmp1.nii.gz
micalc -if1 $Phi2 -op '*' -in2 $TE1 -of tmp2.nii.gz

micalc -if1 tmp1.nii.gz -op '-' -if2 tmp2.nii.gz -of tmp3.nii.gz

micalc -if1 tmp3.nii.gz -op '/' -in2 $DeltaTE -of phase_channels_offset.nii.gz

fslmaths phase_channels_offset.nii.gz -kernel box 5 -fmedian phase_channels_offset_smoothed.nii.gz

fi

if [ $step_correction == 1 ]
  then echo "===================== phase correction ====================="
fslmerge -t phase_channels_highres1.nii.gz ${Niftifolder}/${Prefixhighresphasechannels}_Te${TEhighres1}*
fslmerge -t magnitude_channels_highres1.nii.gz ${Niftifolder}/${Prefixhighresmagchannels}_Te${TEhighres1}*
fslmerge -t phase_channels_highres2.nii.gz ${Niftifolder}/${Prefixhighresphasechannels}_Te${TEhighres2}*
fslmerge -t magnitude_channels_highres2.nii.gz ${Niftifolder}/${Prefixhighresmagchannels}_Te${TEhighres2}*
fslmerge -t magnitude_channels_lowres.nii.gz ${Niftifolder}/${Prefixlowresmagchannels}_Te${TE1}*

flirt -in $lowres_magnitude -ref $highres_magnitude1 -out $prefix_output1.nii.gz -omat $prefix_output1.mat -bins 256 -cost mutualinfo -searchrx -20 20 -searchry -20 20 -searchrz -20 20 -dof 12  -interp trilinear

flirt -in $phase_offset -ref $highres_magnitude1 -out phase_channels_offset_smoothed_$prefix_output1.nii.gz -applyxfm -init $prefix_output1.mat -interp trilinear

/afs/cbs.mpg.de/projects/neu009_sequencing-plasticity/scripts/QSM/siemens_phase phase_channels_highres1.nii.gz phase_channels_highres1_rad.nii.gz

flirt -in $lowres_magnitude -ref $highres_magnitude2 -out $prefix_output2.nii.gz -omat $prefix_output2.mat -bins 256 -cost mutualinfo -searchrx -20 20 -searchry -20 20 -searchrz -20 20 -dof 12  -interp trilinear

flirt -in $phase_offset -ref $highres_magnitude2 -out phase_channels_offset_smoothed_$prefix_output2.nii.gz -applyxfm -init $prefix_output2.mat -interp trilinear

/afs/cbs.mpg.de/projects/neu009_sequencing-plasticity/scripts/QSM/siemens_phase phase_channels_highres2.nii.gz phase_channels_highres2_rad.nii.gz

rm -rf corrected_phase_sum.nii.gz
rm -rf corrected_magnitude_sum.nii.gz
rm -rf test*

### to check leave out certain channels; check on phase_channels_offset_smoothed_$prefix_output.nii.gz
miconv -noscale -trange 0-1 magnitude_channels_highres1.nii.gz test1.nii.gz
miconv -noscale -trange 3-31 magnitude_channels_highres1.nii.gz test2.nii.gz
fslmerge -t magnitude_lesschan1.nii.gz test*
rm -rf test*

miconv -noscale -trange 0-1 phase_channels_highres1_rad.nii.gz test1.nii.gz
miconv -noscale -trange 3-31 phase_channels_highres1_rad.nii.gz test2.nii.gz
fslmerge -t phase_lesschan1.nii.gz test*
rm -rf test*

miconv -noscale -trange 0-1 phase_channels_offset_smoothed_$prefix_output1.nii.gz test1.nii.gz
miconv -noscale -trange 3-31 phase_channels_offset_smoothed_$prefix_output1.nii.gz test2.nii.gz
fslmerge -t offset_lesschan1.nii.gz test*
rm -rf test*

miconv -noscale -trange 0-1 magnitude_channels_highres2.nii.gz test1.nii.gz
miconv -noscale -trange 3-31 magnitude_channels_highres2.nii.gz test2.nii.gz
fslmerge -t magnitude_lesschan2.nii.gz test*
rm -rf test*

miconv -noscale -trange 0-1 phase_channels_highres2_rad.nii.gz test1.nii.gz
miconv -noscale -trange 3-31 phase_channels_highres2_rad.nii.gz test2.nii.gz
fslmerge -t phase_lesschan2.nii.gz test*
rm -rf test*

miconv -noscale -trange 0-1 phase_channels_offset_smoothed_$prefix_output2.nii.gz test1.nii.gz
miconv -noscale -trange 3-31 phase_channels_offset_smoothed_$prefix_output2.nii.gz test2.nii.gz
fslmerge -t offset_lesschan2.nii.gz test*
rm -rf test*

#/afs/cbs.mpg.de/projects/neu009_sequencing-plasticity/scripts/QSM/siemens_phase_arraycoil magnitude_channels_highres.nii.gz phase_channels_highres_rad.nii.gz phase_channels_offset_smoothed_$prefix_output.nii.gz 0 corrected
/afs/cbs.mpg.de/projects/neu009_sequencing-plasticity/scripts/QSM/siemens_phase_arraycoil magnitude_lesschan1.nii.gz phase_lesschan1.nii.gz offset_lesschan1.nii.gz 0 corrected1

gzip corrected1_phase_sum.nii
fslcpgeom $highres_magnitude1 corrected1_phase_sum.nii.gz

gzip corrected1_magnitude_sum.nii
fslcpgeom $highres_magnitude1 corrected1_magnitude_sum.nii.gz

mv corrected1_phase_sum.nii.gz corrected_phase_sum_Te${TEhighres1}.nii.gz
mv corrected1_magnitude_sum.nii.gz corrected_magnitude_sum_Te${TEhighres1}.nii.gz

/afs/cbs.mpg.de/projects/neu009_sequencing-plasticity/scripts/QSM/siemens_phase_arraycoil magnitude_lesschan2.nii.gz phase_lesschan2.nii.gz offset_lesschan2.nii.gz 0 corrected2

gzip corrected2_phase_sum.nii
fslcpgeom $highres_magnitude2 corrected2_phase_sum.nii.gz

gzip corrected2_magnitude_sum.nii
fslcpgeom $highres_magnitude2 corrected2_magnitude_sum.nii.gz

mv corrected2_phase_sum.nii.gz corrected_phase_sum_Te${TEhighres2}.nii.gz
mv corrected2_magnitude_sum.nii.gz corrected_magnitude_sum_Te${TEhighres2}.nii.gz

fi

if [ $step_copy_to_final_dest == 1 ]
  then echo "===================== copying the corrected phase/magn data to final destination ====================="
   #mkdir -p $FINAL_DEST #we assume the correct directories are already created
   cp corrected_phase_sum_Te${TEhighres1}.nii.gz ${FINAL_DEST}${Prefixhighresphasechannels}_corrected_phase_sum_Te${TEhighres1}.nii.gz
   cp corrected_magnitude_sum_Te${TEhighres1}.nii.gz ${FINAL_DEST}${Prefixhighresmagchannels}_corrected_magnitude_sum_Te${TEhighres1}.nii.gz
   cp corrected_phase_sum_Te${TEhighres2}.nii.gz ${FINAL_DEST}${Prefixhighresphasechannels}_corrected_phase_sum_Te${TEhighres2}.nii.gz
   cp corrected_magnitude_sum_Te${TEhighres2}.nii.gz ${FINAL_DEST}${Prefixhighresmagchannels}_corrected_magnitude_sum_Te${TEhighres2}.nii.gz
fi

if [ $step_cleaning == 1 ]
  then echo "===================== deleting files, which are not needed ====================="
  rm -rf unwrapped00* unwrapped_channels* tmp* phase_rad* phase_channels* magnitude_channels* magnitude00* lowres2highres* 
fi
