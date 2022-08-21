#!/usr/bin/awk
#------------------------------------------------------------------------------
# line 1: 1 15:58:43 15:58:37 2919342 120 51 43 8 25 0 0
# parse log file of a mixing job with the Mixer module ran with mu2e.debugLevel = 1
# also assume that the "Begin processing" is printed for each event using
#
# services.message.destinations.log.categories.ArtReport.limit       : 10000  # number of events 
#
# event processing time: time=tend-tstart
#------------------------------------------------------------------------------
BEGIN { 
    xx = 0 
    event = -1;
    intensity = -1;
    time  = -1
    print "evt/I:time/I:lum/I:nflsh/I:nootm/I:nneut/I:ndio0/I:nepho/I:nprot/I:ndeut/I"
}

/Begin processing the/ {
    old_event = event
    event    = $11
    old_time = time
				# parse printed time, it is printed down to 1 sec accuracy
    split($14,t,":"); 
    time = 3600*t[1]+60*t[2]+t[3];  

    if (xx != 0) {
	# print previous data 
	printf "%5i %6i %10i ", old_event , time-old_time, intensity;
	printf "%5i %5i %5i %5i %5i %5i %5i\n", nflsh, nootm, nneut, ndio0, nepho, nprot, ndeut
    }

    xx    = 1
}

/flashMixerTrkCal::startEvent:/ {
    intensity= $7
}

/flashMixerTrkCal::nSecondaries:/ {
    nflsh= $3
}

/ootMixerTrkCal::nSecondaries:/ {
    nootm = $3
}

/neutronMixerTrkCal::nSecondaries:/ {
    nneut = $3
}

/dioMixerTrkCal::nSecondaries:/ {
    ndio0 = $3
}

/photonMixerTrkCal::nSecondaries:/ {
    nepho = $3
}

/protonMixerTrkCal::nSecondaries:/ {
    nprot = $3
}

/deuteronMixerTrkCal::nSecondaries:/ {
    ndeut = $3
}


/Closed output file/ {
    old_time = time
    split($2,t,":"); 

    time = 3600*t[1]+60*t[2]+t[3];  

    if (xx != 0) {
	# print previous data 
	printf "%5i %6i %10i ", old_event , time-old_time, intensity;
	printf "%5i %5i %5i %5i %5i %5i %5i\n", nflsh, nootm, nneut, ndio0, nepho, nprot, ndeut
    }
   
}
