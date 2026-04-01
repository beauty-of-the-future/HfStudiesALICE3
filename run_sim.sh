#!/bin/bash

bash $ACTS_ROOT/python/setup.sh

source $ACTS_ROOT/bin/this_acts.sh
export ACTS_SEQUENCER_DISABLE_FPEMON=true

python3 simulate_hf_events.py -c $1