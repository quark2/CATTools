#!/bin/bash
eval `scramv1 runtime -sh`

rm res_[0-9]*.txt

#cut='d0_L3D>0.2 && d0_LXY>0.1&& dstar_L3D>0.2 && dstar_LXY>0.1 && abs(dstar_diffMass-0.145)<0.01'
#cut='abs(dstar_diffMass-0.145)<0.02 && dstar_LXY>0.09'
cut_d0='d0_L3D>0.2&&d0_LXY>0.1&&abs(d0.M()-1.8648)<0.040'
cut_dstar='d0_L3D>0.2&&d0_LXY>0.1&&dstar_L3D>0.2&&dstar_LXY>0.1&&abs(dstar_diffMass-0.145)<0.01'
cut_dstar_nomassConstain='d0_L3D>0.2&&d0_LXY>0.1&&dstar_L3D>0.2&&dstar_LXY>0.1'
cut_dstar_noCut='abs(dstar_diffMass-0.145)<0.01'

./massPlot.py -c "${cut_d0}"  -s 5 -b [30,0,120] -p 'd0_lepSV_lowM1' -x 'M_{l+D0} [GeV/c^2]' >> res_001.txt & 
./massPlot.py -c "${cut_d0}"  -s 5 -b [30,0,120] -p 'd0_lepSV_dRM1' -x 'M_{l+D0} [GeV/c^2]' >> res_002.txt &

./massPlot.py -c "${cut_dstar}"  -s 5 -b [30,0,120] -p 'dstar_lepSV_lowM1' -x 'M_{l+D^{*}} [GeV/c^2]' >> res_101.txt  & 
./massPlot.py -c "${cut_dstar}"  -s 5 -b [30,0,120] -p 'dstar_lepSV_dRM1' -x 'M_{l+D^{*}} [GeV/c^2]'  >> res_102.txt &
./massPlot.py -c "${cut_dstar}"  -s 5 -b [30,0,120] -p 'dstar_lepSV_correctM1' -x 'M_{l+D^{*}} [GeV/c^2]'  >> res_103.txt &
./massPlot.py -c "${cut_dstar}"  -s 5 -b [30,0,120] -p 'dstar_opCharge_M' -x 'M_{l+D^{*}} [GeV/c^2]'  >> res_104.txt &

./massPlot.py -c "${cut_dstar_nomassConstain}"  -s 5 -b [10,0,120] -p 'dstar_lepSV_lowM1' -x 'M_{l+D^{*}} [GeV/c^2]' -f 'noMasscut' >> res_111.txt & 
./massPlot.py -c "${cut_dstar_nomassConstain}"  -s 5 -b [10,0,120] -p 'dstar_lepSV_dRM1' -x 'M_{l+D^{*}} [GeV/c^2]' -f 'noMasscut' >> res_112.txt &
./massPlot.py -c "${cut_dstar_nomassConstain}"  -s 5 -b [10,0,120] -p 'dstar_lepSV_correctM1' -x 'M_{l+D^{*}} [GeV/c^2]' -f 'noMasscut' >> res_113.txt &
./massPlot.py -c "${cut_dstar_nomassConstain}"  -s 5 -b [10,0,120] -p 'dstar_opCharge_M' -x 'M_{l+D^{*}} [GeV/c^2]' -f 'noMasscut' >> res_114.txt &

./massPlot.py -c "${cut_dstar_noCut}"  -s 5 -b [10,0,120] -p 'dstar_lepSV_lowM1' -x 'M_{l+D^{*}} [GeV/c^2]' -f 'onlyMassCut' >> res_121.txt & 
./massPlot.py -c "${cut_dstar_noCut}"  -s 5 -b [10,0,120] -p 'dstar_lepSV_dRM1' -x 'M_{l+D^{*}} [GeV/c^2]' -f 'onlyMassCut' >> res_122.txt &
./massPlot.py -c "${cut_dstar_noCut}"  -s 5 -b [10,0,120] -p 'dstar_lepSV_correctM1' -x 'M_{l+D^{*}} [GeV/c^2]' -f 'onlyMassCut' >> res_123.txt &
./massPlot.py -c "${cut_dstar_noCut}"  -s 5 -b [10,0,120] -p 'dstar_opCharge_M' -x 'M_{l+D^{*}} [GeV/c^2]' -f 'onlyMassCut' >> res_124.txt &

