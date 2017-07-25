# coding=utf-8
from edraak_certificates.utils import EdraakCertificateDataFetcher


def test_certificate_data_fetcher():
    """
    A basic test for the EdraakCertificateDataFetcher() class.
    """
    fetcher = EdraakCertificateDataFetcher()
    course_data = fetcher['course-v1:edX+DemoX_v3+Demo_Course_v3']
    assert course_data == {
        "LONG_ORG": "Sample Org v3",
        "LONG_COURSE": u"Computer Science 101 with utf-8 char like à",
        "VERSION": "3_dynamic",
        "interstitial": {
            "Pass": "This person passed.",
            "Distinction": "This person is a complete overachiever!"
        }
    }
