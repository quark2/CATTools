#!/bin/bash

./run6.sh "noTopPtW"
./run6.sh "TTnominal=TT_powheg_herwig"
./run6.sh "TTnominal=TT_powheg_mpiOFF"
./run6.sh "TTnominal=TT_powheg_noCR"
./run6.sh "TTnominal=TT_powheg_scaledown"
./run6.sh "TTnominal=TT_powheg_scaleup"

./run6.sh "JES_Up"
./run6.sh "JES_Down"
./run6.sh "JER_Up"
./run6.sh "JER_Down"
./run6.sh "El_Up"
./run6.sh "El_Down"
./run6.sh "Mu_Up"
./run6.sh "Mu_Down"


