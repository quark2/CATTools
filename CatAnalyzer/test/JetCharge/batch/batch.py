#!/usr/bin/env python

import os,sys


if ( not os.path.isfile(sys.argv[1]) or not sys.argv[1].endswith('.py' )) :
  print "Wrong cfg"
  sys.exit(-1)
if ( not os.path.isfile(sys.argv[2]) or not sys.argv[2].startswith('dataset')   ) :
  print "Wrong dataset filename"
  sys.exit(-1)
if ( len(sys.argv) != 3) : 
  print "Wrong argument"
  sys.exit(-1)
  
datasetList =  open(sys.argv[2]).readlines()


for filename in datasetList :
  filename = filename.strip()
  if ( filename == "") : continue
  print filename
  dataset = filename.replace("dataset_","").replace(".txt","")
  print dataset
  cmd = "create-batch --jobName %s --fileList ../../../data/dataset/%s --maxFiles 20 --cfg %s"%(dataset,filename,sys.argv[1]) 
  if ( dataset.find("TT") != -1 ) :
    cmd += " --args \"isTT=True\""
  print cmd
  os.system(cmd)
