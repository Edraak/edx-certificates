# -*- coding: utf-8 -*-

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import utils
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import landscape, A4
import arabicreshaper
from bidi.algorithm import get_display
import re
from os import path
from tempfile import NamedTemporaryFile
import gettext

from settings import ARABIC_DIR

gettext.bindtextdomain('messages', ARABIC_DIR)
gettext.textdomain('messages')

from edraak_certificates.db import CourseOverview, session


class Gettext():
    def __init__(self, language):

        self.language = language

    def __enter__(self):
        if self.language == 'ar':
            return gettext.gettext

        return lambda s: s

    def __exit__(self, type, value, traceback):
        pass


def text_to_bidi(text):
    text = normalize_spaces(text)

    reshaped_text = arabicreshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text


def normalize_spaces(text):
    return re.sub(' +', ' ', text)


def contains_rtl_text(string):
        try:
            string.decode('ascii')
        except (UnicodeDecodeError, UnicodeEncodeError) as e:
            return True
        else:
            return False


class EdraakCertificateDataFetcher(object):
    """
    A replacement for edX's static `cert-data.yaml` for Edraak.

    This helps to detect whether the course is Arabic or not and fetch some course data
    from the edxapp databases.
    """
    @staticmethod
    def get_organization_logo(organization, course_id):
        org_lower = organization.lower()
        if org_lower == 'mitx' or org_lower == 'harvardx' or org_lower == 'qrf':
            return 'edx.png'
        elif org_lower == u'bayt.com':
            return 'bayt-logo2-en.png'
        elif org_lower == u'qrta':
            return 'qrta_logo.jpg'
        elif org_lower == 'aub':
            return 'Full-AUB-Seal.jpg'
        elif org_lower == "csbe":
            return 'csbe.png'
        elif org_lower == "hcac":
            return 'HCAC_Logo.png'
        elif org_lower == "delftx":
            return 'delftx.jpg'
        elif org_lower == "britishcouncil":
            return 'british-council.jpg'
        elif org_lower == "crescent_petroleum":
            return 'crescent-petroleum.jpg'
        elif org_lower == 'auc':
            return 'auc.jpg'
        elif org_lower == 'pmijo':
            return 'pmijo.jpg'
        elif org_lower == 'qou':
            return 'qou.png'
        elif org_lower == 'moe':
            return 'moe.png'
        elif org_lower == 'mbrcgi':
            return 'mbrcgi.png'
        elif org_lower == 'hsoub':
            return 'hsoub.png'
        elif org_lower == 'psut':
            return 'psut.png'
        elif course_id == 'course-v1:Edraak+STEAM101+R1_Q1_2017':
            return 'auc.jpg'
        else:
            return None

    @staticmethod
    def get_course_sponsor(course_id):
        if course_id in (
                "BritishCouncil/Eng100/T4_2015",
                "course-v1:BritishCouncil+Eng100+T4_2015",
                "course-v1:BritishCouncil+Eng2+2016Q3",
                "course-v1:BritishCouncil+Eng3+Q4-2016"
        ):
            return "crescent_petroleum"
        else:
            return None

    def is_english_course(self, course_name):
        return not contains_rtl_text(course_name)

    def course_org_disclaimer(self, course_org, language):
        with Gettext(language) as _:
            if course_org == 'MITX':
                return _("A course of study offered by Edraak with cooperation from MITx. "
                              "The learning experience has been supervised and managed by the course team.")
            else:
                return _("A course of study offered by Edraak. The learning experience has been supervised and "
                          "managed by the course team.")

    def get_course(self, course_key):
        return session.query(CourseOverview).get(course_key)

    def get(self, item, default=None):
        return self[item]

    def __getitem__(self, item):
        # raise Exception('Not implemented yet!')
        course = self.get_course(item)

        language = 'en' if self.is_english_course(course.display_name) else 'ar'

        return {
            'course': course,
            'organization_logo': self.get_organization_logo(course.org, course.id),
            'sponsor': self.get_course_sponsor(course.id),
            'language': language,
            'instructor': '',
            'is_english_course': self.is_english_course(course.display_name),
            'organization_disclaimer': self.course_org_disclaimer(course.display_org_with_default, language),
            'LONG_ORG': course.display_org_with_default,
            'LONG_COURSE': course.display_name,
            'VERSION': 'edraak',
        }
