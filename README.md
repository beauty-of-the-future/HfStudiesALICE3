# HfStudiesALICE3
Repository for HF performance studies with ACTS for ALICE3

# install ACTS with aliBuild
1. Prepare for the installation
```bash
mkdir -p alice
cd alice
aliBuild init O2@dev
aliBuild init ACTSO2,HepMC3
```
* At this point, if you have the error: `ERROR: Error during git clone for reference repo for ACTSO2`, make sure to have an updated gitLab SSH key, or replace line 16 of `~/alice/alidist/actso2.sh` with: `source: https://gitlab.cern.ch/alice3-trackers/wp1-simulationsandperformances/actso2.git`. This will prompt you a request to insert your GitLab username and password.
* If instead you have problems with the init of HepMC3, just run `git clone https://gitlab.cern.ch/hepmc/HepMC3.git` and do not run the init for HepMC3.

2. Compile O2 with ACTS dependencies
```bash
aliBuild build O2 --defaults o2-acts
```
3. Compile ACTSO2
```bash
aliBuild build ACTSO2
```

# enter the environment
```bash
alienv enter O2/latest ACTSO2/latest
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

