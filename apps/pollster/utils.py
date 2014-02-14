from . import models
from django.conf import settings

import logging
logger = logging.getLogger('logview.userlogins')

from datetime import date

def get_user_profile(user_id):
    function ='def get_user_profile'
    logger.info(function)
    logger.info('%s - user_id:%s' % (function, user_id ))

    try:
        shortname = getattr(settings, 'POLLSTER_USER_PROFILE_SURVEY', 'intake')
        logger.info('%s - shortname:%s' % (function, shortname))
        survey = models.Survey.get_by_shortname(shortname)
        profile = survey.get_last_participation_data(user_id)
        return profile

    except models.Survey.DoesNotExist:
        logger.info('%s - Survey.DoesNotExit' % function)
        return None

    except StandardError, e:
        return None

# Calculate request for energy consumption at home, according
# to home characteristics inserted by the user
# Pre: survey_intake (not null) contains intake survey
# Post: energy_requests dictionary with attributes for
#       heating and cooling requests
def get_energy_requests(survey_intake):
    # Debug
    function = 'def get_energy_requests'
    logger.info(function)

    # Initialize the dict
    energy_requests = {}

    # Transform the year (QUESTION_7) from the output of the survey
    year = survey_intake.QUESTION_7
    if year == 0:
        # year < 1981
        year = 1981
    elif year == 1:
        # 1981 < year < 2008
        year = 1995
    else:
        # 2008 < year
        year = 2008

    # Get the surface of the home (QUESTION_8)
    space = survey_intake.QUESTION_8

    # Initial calculus
    heating = ((-0.000220643)*(year**3)+1.323999443*(year**2)+(-2648.626838)*year + 1766465.479)*space/72
    cooling = (0.0003233*(year**3)+(-1.923202341)*(year**2)+3813.256282*year - 2520082.149)*space/72
    dhw = 294*(survey_intake.QUESTION_2_multi_row1_col1 + survey_intake.QUESTION_2_multi_row1_col2 + survey_intake.QUESTION_2_multi_row1_col3)

    # Update according to the floor
    floor = survey_intake.QUESTION_5
    num_plantas = 1
    if floor == 0:
        # floor = ground floor
        heating = heating + (((-0.000393813)*(year**3)+2.353809365*(year**2)+(-4690.491288)*year + 3116349.539)*space/72)/num_plantas
        cooling = cooling + ((0.000734323*(year**3)+(-4.364033863)*(year**2)+8645.005594*year - 5708438.801)*space/72)/num_plantas
    elif floor == 2:
        # floor = attic
        heating = heating + ((0.00000705128*(year**3)+(-0.044398077)*(year**2)+91.89927564*year + (-62514.76038))*space/72)/num_plantas
        cooling = cooling + (((-0.002522436)*(year**3)+15.10422115*(year**2)+(-30146.98997)*year + 20056604.85)*space/72)/num_plantas

    # Update according to the windows

    # Update in order to rectify the model used
    heating = heating + 13.1
    cooling = cooling - 17.6

    energy_requests['heating'] = heating
    energy_requests['cooling'] = cooling

    # Go through the whole rooms modifying the
    # requests according to the windows' orientation
    # Third parameter indicates if the room is the living room
    energy_requests = orientation_rect(energy_requests, survey_intake.QUESTION_10_multi_row1_col1, False)
    energy_requests = orientation_rect(energy_requests, survey_intake.QUESTION_10_multi_row1_col2, False)
    energy_requests = orientation_rect(energy_requests, survey_intake.QUESTION_10_multi_row1_col3, True)
    energy_requests = orientation_rect(energy_requests, survey_intake.QUESTION_10_multi_row1_col4, False)
    energy_requests = orientation_rect(energy_requests, survey_intake.QUESTION_10_multi_row1_col5, False)

    # Check windows' quality for rectifications
    # Add the punctuation of the whole windows inserted
    windows_quality = survey_intake.QUESTION_11_multi_row1_col1+survey_intake.QUESTION_11_multi_row1_col2+survey_intake.QUESTION_11_multi_row1_col3+survey_intake.QUESTION_11_multi_row1_col4+survey_intake.QUESTION_11_multi_row1_col5
    if windows_quality > 12:
        # Most of the windows are high quality (max punct = 15)
        energy_requests['heating'] = energy_requests['heating']*0.9
        energy_requests['cooling'] = energy_requests['cooling']*0.9
    elif windows_quality > 7:
        # Most of the windows are medium quality
        energy_requests['heating'] = energy_requests['heating']*0.95
        energy_requests['cooling'] = energy_requests['cooling']*0.95

    # Rectifications because of ventilation
    if survey_intake.QUESTION_20 - 20 > 0:
	# Ventilation > 20 minutes
	energy_requests['heating'] = energy_requests['heating'] + (survey_intake.QUESTION_20 - 20)*0.001*energy_requests['heating']

    # Rectification because of the type of heating system
    heating_system = survey_intake.QUESTION_16
    if (heating_system == 0) or (heating_system == 1):
	# Central system with general or individual counter 
	energy_requests['heating'] = energy_requests['heating']*1.1
    elif  heating_system == 3:
	# Individual system with old heater
	energy_requests['heating'] = energy_requests['heating']*1.15

    # Rectification because of the type of acs system
    acs_system = survey_intake.QUESTION_21
    if acs_system == 0:
    	# Individual heater 
        dhw = dhw*1.1

    # Modify cooling request according to the type of system
    cooling_system = survey_intake.QUESTION_23
    if (cooling_system == 1) or (cooling_system == 2)  or (cooling_system == 3):
        # There is a cooling system for some of the rooms, but not the whole home 
        energy_requests['cooling'] = energy_requests['cooling']/2
    elif  heating_system == 5:
        # There is no cooling system, so cooling request is zero
        energy_requests['cooling'] = 0

    # Calculate data for the estimated consumption and cost table
    heating_source = survey_intake.QUESTION_18
    acs_source = survey_intake.QUESTION_22 
    
    # Calculate heating units, consumption and cost
    if heating_source == 0:
	# Energy source = electricity
	heating_units = energy_requests['heating']
	energy_requests['heating_consumption'] = round(heating_units*0.4, 4)
	energy_requests['heating_cost'] = round(energy_requests['heating']*0.18, 2)
    elif heating_source == 1:
        # Energy source = natural gas
        heating_units = energy_requests['heating']/10.7
        energy_requests['heating_consumption'] = round(heating_units*2.2, 4)
        energy_requests['heating_cost'] = round(energy_requests['heating']*0.081, 2)
    elif heating_source == 2:
        # Energy source = butane
        heating_units = energy_requests['heating']/(12.5*11.78)
        energy_requests['heating_consumption'] = round(heating_units*12.5*2.9, 4)
        energy_requests['heating_cost'] = round(energy_requests['heating']*0.1103, 2)
    elif heating_source == 3:
        # Energy source = diesel oil
        heating_units = energy_requests['heating']/9.98
        energy_requests['heating_consumption'] = round(heating_units*2.8, 4)
        energy_requests['heating_cost'] = round(energy_requests['heating']*0.085, 2)
    elif heating_source == 5:
        # Energy source = biomass
        heating_units = energy_requests['heating']/5
        energy_requests['heating_consumption'] = 0
        energy_requests['heating_cost'] = round(energy_requests['heating']*0.04, 2)

    # Calculate cooling units, consumption and cost
    cooling_units = energy_requests['cooling']/2.5
    energy_requests['cooling_consumption'] = round(cooling_units*0.4/2.5, 4)
    energy_requests['cooling_cost'] = round(energy_requests['cooling']*0.18/2.5, 2)

    # Calculate acs units, consumption and cost
    if acs_source == 0:
        # Energy source = electricity
        acs_units = dhw
        energy_requests['acs_consumption'] = round(acs_units*0.4, 4)
        energy_requests['acs_cost'] = round(dhw*0.18, 2)
    elif acs_source == 1:
        # Energy source = natural gas
        acs_units = dhw/10.7
        energy_requests['acs_consumption'] = round(acs_units*2.2, 4)
        energy_requests['acs_cost'] = round(dhw*0.081, 2)
    elif acs_source == 2:
        # Energy source = butane
        acs_units = dhw/(12.5*11.78)
        energy_requests['acs_consumption'] = round(acs_units*12.5*2.9, 4)
        energy_requests['acs_cost'] = round(dhw*0.1103, 2)
    elif acs_source == 3:
        # Energy source = diesel oil
        acs_units = dhw/9.98
        energy_requests['acs_consumption'] = round(acs_units*2.8, 4)
        energy_requests['acs_cost'] = round(dhw*0.085, 2)
    elif acs_source == 5:
        # Energy source = biomass
        acs_units = dhw/5
        energy_requests['acs_consumption'] = 0
        energy_requests['acs_cost'] = round(dhw*0.04, 2)

    datenow = date.today()
    
    month = (int(datenow.month) - 1) % 12
    if month == 1:
	electric_consumption = survey_intake.QUESTION_30_multi_row1_col1
	thermal_consumption = survey_intake.QUESTION_30_multi_row1_col2
    elif month == 2:
        electric_consumption = survey_intake.QUESTION_30_multi_row2_col1
        thermal_consumption = survey_intake.QUESTION_30_multi_row2_col2
    elif month == 3:
        electric_consumption = survey_intake.QUESTION_30_multi_row3_col1
        thermal_consumption = survey_intake.QUESTION_30_multi_row3_col2
    elif month == 4:
        electric_consumption = survey_intake.QUESTION_30_multi_row4_col1
        thermal_consumption = survey_intake.QUESTION_30_multi_row4_col2
    elif month == 5:
        electric_consumption = survey_intake.QUESTION_30_multi_row5_col1
        thermal_consumption = survey_intake.QUESTION_30_multi_row5_col2
    elif month == 6:
        electric_consumption = survey_intake.QUESTION_30_multi_row6_col1
        thermal_consumption = survey_intake.QUESTION_30_multi_row6_col2
    elif month == 7:
        electric_consumption = survey_intake.QUESTION_30_multi_row7_col1
        thermal_consumption = survey_intake.QUESTION_30_multi_row7_col2
    elif month == 8:
        electric_consumption = survey_intake.QUESTION_30_multi_row8_col1
        thermal_consumption = survey_intake.QUESTION_30_multi_row8_col2
    elif month == 9:
        electric_consumption = survey_intake.QUESTION_30_multi_row9_col1
        thermal_consumption = survey_intake.QUESTION_30_multi_row9_col2
    elif month == 10:
        electric_consumption = survey_intake.QUESTION_30_multi_row10_col1
        thermal_consumption = survey_intake.QUESTION_30_multi_row10_col2
    elif month == 11:
        electric_consumption = survey_intake.QUESTION_30_multi_row11_col1
        thermal_consumption = survey_intake.QUESTION_30_multi_row11_col2
    else:
        if datenow.year == 2014:
		electric_consumption = survey_intake.QUESTION_29_multi_row12_col1
        	thermal_consumption = survey_intake.QUESTION_29_multi_row12_col2
	else:
		electric_consumption = survey_intake.QUESTION_30_multi_row12_col1
                thermal_consumption = survey_intake.QUESTION_30_multi_row12_col2

    # Calculate consumption and cost of the real
    # data inserted by the user
    thermal_source = survey_intake.QUESTION_28
    if thermal_source == 0:
        # Energy source = electricity
        energy_requests['real_consumption'] = round((electric_consumption+thermal_consumption)*0.4, 4)
        energy_requests['real_cost'] = round((electric_consumption+thermal_consumption)*0.18, 2)
    elif thermal_source == 1:
        # Energy source = natural gas
	energy_requests['real_consumption'] = round(electric_consumption*0.4+thermal_consumption*2.2/10.7, 4)
        energy_requests['real_cost'] = round(electric_consumption*0.18+thermal_consumption*0.081, 2)
    elif thermal_source == 2:
        # Energy source = butane
        energy_requests['real_consumption'] = round(electric_consumption*0.4+thermal_consumption*12.5*2.9/(12.5*11.78), 4)
        energy_requests['real_cost'] = round(electric_consumption*0.18+thermal_consumption*0.1103, 2)
    elif thermal_source == 3:
        # Energy source = diesel oil
	energy_requests['real_consumption'] = round(electric_consumption*0.4+thermal_consumption*2.8/9.98, 4)
        energy_requests['real_cost'] = round(electric_consumption*0.18+thermal_consumption*0.085, 2)
    elif thermal_source == 5:
        # Energy source = biomass
	energy_requests['real_consumption'] = round(electric_consumption*0.4, 4)
        energy_requests['real_cost'] = round(electric_consumption*0.18+thermal_consumption*0.04, 2)

    energy_requests['total_consumption'] = round(energy_requests['heating_consumption']+energy_requests['cooling_consumption']+energy_requests['acs_consumption'], 4)
    energy_requests['total_cost'] = round(energy_requests['heating_cost']+energy_requests['cooling_cost']+energy_requests['acs_cost'], 2)
    
    # Saves in this attribute if the user can improve the consumption
    if energy_requests['total_consumption'] > energy_requests['real_consumption']:
	energy_requests['improvable'] = False
    else:
   	energy_requests['improvable'] = True

    return energy_requests

# Calculate variations in the requests according to
# window orientation
# Pre: energy_requests (not null) contains current requests
#      orientation not null, 0<=orientation<8
#      is_lounge boolean indicating if the room is the living room
# Post: energy_requests with update requests
def orientation_rect(energy_requests, orientation, is_lounge):

    # Debug
    function = 'def orientation_rect'
    logger.info(function)

    if orientation == 3:
        # orientation = south
        energy_requests['heating'] = energy_requests['heating']-2.5*2*1.44 if is_lounge else energy_requests['heating']-2.55*1.44
        energy_requests['cooling'] = energy_requests['cooling']+2.5*2*1.44 if is_lounge else energy_requests['heating']+2.55*1.44
    elif orientation == 4:
        # orientation = south east
        energy_requests['heating'] = energy_requests['heating']-2.32*2*1.44 if is_lounge else energy_requests['heating']-2.32*1.44
        energy_requests['cooling'] = energy_requests['cooling']+2.56*2*1.44 if is_lounge else energy_requests['heating']+2.56*1.44
    elif orientation == 5:
        # orientation = south west
        energy_requests['heating'] = energy_requests['heating']-1.63*2*1.44 if is_lounge else energy_requests['heating']-1.63*1.44
        energy_requests['cooling'] = energy_requests['cooling']+2.74*2*1.44 if is_lounge else energy_requests['heating']+2.74*1.44
    elif orientation == 6:
        # orientation = east
        energy_requests['heating'] = energy_requests['heating']-1.25*2*1.44 if is_lounge else energy_requests['heating']-1.25*1.44
        energy_requests['cooling'] = energy_requests['cooling']+1.94*2*1.44 if is_lounge else energy_requests['heating']+1.94*1.44
    elif orientation == 7:
        # orientation = west
        energy_requests['heating'] = energy_requests['heating']-0.55*2*1.44 if is_lounge else energy_requests['heating']-0.55*1.44
        energy_requests['cooling'] = energy_requests['cooling']+2.04*2*1.44 if is_lounge else energy_requests['heating']+2.04*1.44
    elif orientation == 0:
        # orientation = north
        energy_requests['heating'] = energy_requests['heating']+0.1*2*1.44 if is_lounge else energy_requests['heating']+0.1*1.44
        energy_requests['cooling'] = energy_requests['cooling']+3.47*2*1.44 if is_lounge else energy_requests['heating']+3.47*1.44

    return energy_requests
