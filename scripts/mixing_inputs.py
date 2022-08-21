#
from local_classes import *
#------------------------------------------------------------------------------
# define common inputs for SU2020 mixing
#------------------------------------------------------------------------------
def define_mixing_inputs(job):
    job.fAuxInputs               = {}

    # name, dataset, number_of_files per segment

    job.fAuxInputs['deuteronMixerTrkCal'] = ('physics.filters.deuteronMixerTrkCal.fileNames', 
                                             Dataset('sim.mu2e.deut0s41b0.su2020.art','deut0s41b0','local'),
                                             1);

    job.fAuxInputs['dioMixerTrkCal'     ] = ('physics.filters.dioMixerTrkCal.fileNames', 
                                             Dataset('sim.mu2e.dio00s41b0.su2020.art','dio00s41b0','local'),
                                             1);
    
    job.fAuxInputs['flashMixerTrkCal'   ] = ('physics.filters.flashMixerTrkCal.fileNames', 
                                             Dataset('sim.mu2e.flsh1s51b0.su2020.art','flsh1s51b0','local'),
                                             1);
    
    job.fAuxInputs['ootMixerTrkCal'     ] = ('physics.filters.ootMixerTrkCal.fileNames', 
                                             Dataset('sim.mu2e.ootm0s41b0.su2020.art','ootm0s41b0','local'),
                                             1);

    job.fAuxInputs['neutronMixerTrkCal' ] = ('physics.filters.neutronMixerTrkCal.fileNames', 
                                             Dataset('sim.mu2e.neut0s41b0.su2020.art','neut0s41b0','local'),
                                             1);

    job.fAuxInputs['photonMixerTrkCal'  ] = ('physics.filters.photonMixerTrkCal.fileNames', 
                                             Dataset('sim.mu2e.epho0s41b0.su2020.art','epho0s41b0','local'),
                                             1);

    job.fAuxInputs['protonMixerTrkCal'  ] = ('physics.filters.protonMixerTrkCal.fileNames', 
                                             Dataset('sim.mu2e.prot0s41b0.su2020.art','prot0s41b0','local'),
                                             1);

#------------------------------------------------------------------------------
# inputs for mixing in CRV
#------------------------------------------------------------------------------
def define_mixing_inputs_crv(job):
    job.fAuxInputs               = {}

    # name, dataset, number_of_files per segment

    job.fAuxInputs['dioMixerCRV'        ] = ('physics.filters.dioMixerCRV.fileNames', 
                                             Dataset('sim.mu2e.dio00s42b0.su2020.art','dio00s42b0','local'),
                                             1);
    
    job.fAuxInputs['neutronMixerCRV'    ] = ('physics.filters.neutronMixerCRV.fileNames', 
                                             Dataset('sim.mu2e.neut0s42b0.su2020.art','neut0s42b0','local'),
                                             1);

    job.fAuxInputs['DSMixerCRV'         ] = ('physics.filters.DSMixerCRV.fileNames', 
                                             Dataset('sim.mu2e.crv02s32b0.su2020.art','crv02s32b0','local'),
                                             1);
    
    job.fAuxInputs['PSMixerCRV'         ] = ('physics.filters.PSMixerCRV.fileNames', 
                                             Dataset('sim.mu2e.crv02s33b0.su2020.art','crv02s33b0','local'),
                                             1);

#------------------------------------------------------------------------------
# inputs for CE mixing with noise in the tracker, calo and CRV
#------------------------------------------------------------------------------
def define_mixing_inputs_ce_trkcalocrv(job):
    job.fAuxInputs               = {}

    # name, dataset, number_of_files per segment

    job.fAuxInputs['dioMixerCRV'        ] = ('physics.filters.dioMixerCRV.fileNames', 
                                             Dataset('sim.mu2e.dio00s42b0.su2020.art','dio00s42b0','local'),
                                             1);
    
    job.fAuxInputs['neutronMixerCRV'    ] = ('physics.filters.neutronMixerCRV.fileNames', 
                                             Dataset('sim.mu2e.neut0s42b0.su2020.art','neut0s42b0','local'),
                                             1);

    job.fAuxInputs['DSMixerCRV'         ] = ('physics.filters.DSMixerCRV.fileNames', 
                                             Dataset('sim.mu2e.crv02s32b0.su2020.art','crv02s32b0','local'),
                                             1);
    
    job.fAuxInputs['PSMixerCRV'         ] = ('physics.filters.PSMixerCRV.fileNames', 
                                             Dataset('sim.mu2e.crv02s33b0.su2020.art','crv02s33b0','local'),
                                             1);

    # name, dataset, number_of_files per segment

    job.fAuxInputs['deuteronMixerTrkCal'] = ('physics.filters.deuteronMixerTrkCal.fileNames', 
                                             Dataset('sim.mu2e.deut0s41b0.su2020.art','deut0s41b0','local'),
                                             1);

    job.fAuxInputs['dioMixerTrkCal'     ] = ('physics.filters.dioMixerTrkCal.fileNames', 
                                             Dataset('sim.mu2e.dio00s41b0.su2020.art','dio00s41b0','local'),
                                             1);
    
    job.fAuxInputs['flashMixerTrkCal'   ] = ('physics.filters.flashMixerTrkCal.fileNames', 
                                             Dataset('sim.mu2e.flsh1s51b0.su2020.art','flsh1s51b0','local'),
                                             1);
    
    job.fAuxInputs['ootMixerTrkCal'     ] = ('physics.filters.ootMixerTrkCal.fileNames', 
                                             Dataset('sim.mu2e.ootm0s41b0.su2020.art','ootm0s41b0','local'),
                                             1);

    job.fAuxInputs['neutronMixerTrkCal' ] = ('physics.filters.neutronMixerTrkCal.fileNames', 
                                             Dataset('sim.mu2e.neut0s41b0.su2020.art','neut0s41b0','local'),
                                             1);

    job.fAuxInputs['photonMixerTrkCal'  ] = ('physics.filters.photonMixerTrkCal.fileNames', 
                                             Dataset('sim.mu2e.epho0s41b0.su2020.art','epho0s41b0','local'),
                                             1);

    job.fAuxInputs['protonMixerTrkCal'  ] = ('physics.filters.protonMixerTrkCal.fileNames', 
                                             Dataset('sim.mu2e.prot0s41b0.su2020.art','prot0s41b0','local'),
                                             1);

