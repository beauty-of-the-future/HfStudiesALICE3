# HfStudiesALICE3
Repository for HF performance studies with ACTS for ALICE3

# install ACTS with aliBuild
1. Prepare for the installation
```bash
mkdir -p alice
cd alice
git clone https://github.com/AliceO2Group/acts.git
mv acts ACTS
cd ACTS
git checkout v46.2.0-alice
cd ..
aliBuild init O2@dev
aliBuild init ACTSO2  ### -> this provides you a collection of scripts and geometries which can be useful in several analyses
aliBuild init HepMC3
```
* At this point if you have problems with the init of HepMC3, just run `git clone https://gitlab.cern.ch/hepmc/HepMC3.git` instead of running the init for HepMC3.

2. Compile O2 with ACTS dependencies --> this allows you to have all the tools to run also ACTS algorithms on O2 outputs
```bash
aliBuild build O2 --defaults o2-acts --debug
```
3. Compile ACTSO2
```bash
aliBuild build ACTSO2
```

# enter the environment
```bash
alienv enter O2/latest ACTS/latest
```

# setup python bindings
This step is automatically done if running ```run_sim.sh```
```bash
source ~/alice/ACTSO2/setup.sh
```

# run the simulation
```bash
./run_sim.sh config.yml
```
examples of config files can be found in the `config` directory

