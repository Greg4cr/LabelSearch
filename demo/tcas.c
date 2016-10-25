#include <stdio.h>


#define OLEV       600		/* in feets/minute */
#define MAXALTDIFF 600		/* max altitude difference in feet */
#define MINSEP     300          /* min separation in feet */
#define NOZCROSS   100		/* in feet */

typedef int bool;

int Cur_Vertical_Sep;
bool High_Confidence;		/* 1/0 */
bool Two_of_Three_Reports_Valid;		/* 1/0 */
int Own_Tracked_Alt;
int Own_Tracked_Alt_Rate;
int Other_Tracked_Alt;
int Alt_Layer_Value;		/* 0, 1, 2, 3 */
int Positive_RA_Alt_Thresh[4];
int Up_Separation;
int Down_Separation;
int Other_RAC;			/* NO_INTENT, DO_NOT_CLIMB, DO_NOT_DESCEND */
#define NO_INTENT 0
#define DO_NOT_CLIMB 1
#define DO_NOT_DESCEND 2
int Other_Capability;		/* TCAS_TA, OTHER */
#define TCAS_TA 1
#define OTHER 2
int Climb_Inhibit;
#define UNRESOLVED 0
#define UPWARD_RA 1
#define DOWNWARD_RA 2




bool Own_Below_Threat();
bool Own_Above_Threat();


void initialize(){

    Positive_RA_Alt_Thresh[0] = 400;
    Positive_RA_Alt_Thresh[1] = 500;
    Positive_RA_Alt_Thresh[2] = 640;
    Positive_RA_Alt_Thresh[3] = 740;
}


int ALIM (){

  

 return Positive_RA_Alt_Thresh[Alt_Layer_Value];
}



int Inhibit_Biased_Climb (){


 


	    	if(Climb_Inhibit == 1){


		
 

	    		return (Up_Separation + NOZCROSS);
	    	}
	    	else{

		 

	    		return (Up_Separation);
	    	}
}



bool Non_Crossing_Biased_Climb(){
    int upward_preferred;
    bool result;

    bool aux_bool; 
    int aux_int;
 
    upward_preferred = Inhibit_Biased_Climb() > Down_Separation;
    if (upward_preferred)
    {

      aux_bool = Own_Below_Threat(); 
      aux_int = ALIM(); 

     
	result = !aux_bool || (aux_bool && !(Down_Separation >= aux_int));
    }
    else
    {	


	result = Own_Above_Threat() && (Cur_Vertical_Sep >= MINSEP) && (Up_Separation >= ALIM());
    }
    return result;
}

bool Non_Crossing_Biased_Descend(){
    int upward_preferred;
    bool result;


    upward_preferred = Inhibit_Biased_Climb() > Down_Separation;
    if (upward_preferred)
    {



	result = Own_Below_Threat() && (Cur_Vertical_Sep >= MINSEP) && (Down_Separation >= ALIM());
    }
    else
    {

	result = !(Own_Above_Threat()) || ((Own_Above_Threat()) && (Up_Separation >= ALIM()));
    }
    return result;
}

bool Own_Below_Threat(){
    //return (Own_Tracked_Alt < Other_Tracked_Alt);
    if(Own_Tracked_Alt < Other_Tracked_Alt){
    	return 1;
    }
    else{
    	return 0;
    }
}

bool Own_Above_Threat(){
    //return (Other_Tracked_Alt < Own_Tracked_Alt);
	if(Other_Tracked_Alt < Own_Tracked_Alt){
		return 1;
	}
	else{
		return 0;
	}
}

int alt_sep_test()     // function under test
{
    bool enabled, tcas_equipped, intent_not_known;
    bool need_upward_RA, need_downward_RA;
    int alt_sep;

    initialize(); 

    enabled = High_Confidence && (Own_Tracked_Alt_Rate <= OLEV) && (Cur_Vertical_Sep > MAXALTDIFF);
    tcas_equipped = Other_Capability == TCAS_TA;
    intent_not_known = Two_of_Three_Reports_Valid && Other_RAC == NO_INTENT;
    


    alt_sep = UNRESOLVED;
    


    if (enabled && ((tcas_equipped && intent_not_known) || !tcas_equipped))
    {


	need_upward_RA = Non_Crossing_Biased_Climb() && Own_Below_Threat();
	need_downward_RA = Non_Crossing_Biased_Descend() && Own_Above_Threat();


	if (need_upward_RA && need_downward_RA){



        /* unreachable: requires Own_Below_Threat and Own_Above_Threat
           to both be 1 - that requires Own_Tracked_Alt < Other_Tracked_Alt
           and Other_Tracked_Alt < Own_Tracked_Alt, which isn't possible */
	    alt_sep = UNRESOLVED;
	}
	else if (need_upward_RA){

	

	    alt_sep = UPWARD_RA;
	}
	else if (need_downward_RA){

	

	    alt_sep = DOWNWARD_RA;
	}
	else{



	    alt_sep = UNRESOLVED;
    }
    }


  

    
    return alt_sep;
}
