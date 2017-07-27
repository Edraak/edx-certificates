from sqlalchemy import create_engine
from settings import EDXAPP_DATABASE_URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Float,
)


engine = create_engine(EDXAPP_DATABASE_URL)


def get_course(course_id):
    return engine.execute(
        text('SELECT * FROM course_overviews_courseoverview WHERE id=:course_id LIMIT 1'),
        course_id=course_id,
    ).fetchone()


def get_instructor_name(course_id):
    return engine.execute(
        text("""SELECT name FROM student_profile AS p
                INNER JOIN student_courseaccessrole AS r ON p.user_id = r.user_id
                WHERE r.role == 'instructor' AND r.course_id = :course_id"""),
        course_id=course_id,
    ).fetchone()[0]


class CourseOverview(Base):
    __tablename__ = 'course_overviews_courseoverview'

    # Course identification
    id = Column(String, primary_key=True)
    version = Column(Integer)
    org = Column(String)
    display_name = Column(String)
    display_number_with_default = Column(String)
    display_org_with_default = Column(String)

    # Start/end dates
    start = Column(DateTime)
    end = Column(DateTime)
    advertised_start = Column(String)
    announcement = Column(DateTime)

    # URLs
    course_image_url = Column(String)
    social_sharing_url = Column(String)
    end_of_course_survey_url = Column(String)

    # Certification data
    certificates_display_behavior = Column(String)
    certificates_show_before_end = Column(Boolean)
    cert_html_view_enabled = Column(Boolean)
    has_any_active_web_certificate = Column(Boolean)
    cert_name_short = Column(String)
    cert_name_long = Column(String)

    # Grading
    lowest_passing_grade = Column(Float)

    # Access parameters
    days_early_for_beta = Column(Float)
    mobile_available = Column(Boolean)
    visible_to_staff_only = Column(Boolean)

    # Enrollment details
    enrollment_start = Column(DateTime)
    enrollment_end = Column(DateTime)
    enrollment_domain = Column(String)
    invitation_only = Column(Boolean)
    max_student_enrollments_allowed = Column(Integer)

    # Catalog information
    catalog_visibility = Column(String)
    short_description = Column(String)
    course_video_url = Column(String)
    effort = Column(String)
    self_paced = Column(Boolean)

    def __repr__(self):
        return u'<CourseOverview(%s)>'.format(self.id)
