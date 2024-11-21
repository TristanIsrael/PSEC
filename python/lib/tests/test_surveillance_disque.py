from panoptiscan_lib import SurveillanceDisque

def testcase_surveille_tmp():
    sd = SurveillanceDisque("/var/tmp")
    sd.demarre()