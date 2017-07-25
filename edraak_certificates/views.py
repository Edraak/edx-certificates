import logging
import os

from wand.image import Image

from django.http import HttpResponse
from django.shortcuts import redirect
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.servers.basehttp import FileWrapper
from django.core.files.temp import NamedTemporaryFile
from django.contrib.auth.decorators import login_required
from django.db import transaction

from dateutil.relativedelta import relativedelta
from edxmako.shortcuts import render_to_response
from xmodule.modulestore.django import modulestore

from opaque_keys.edx import locator
from datetime import date
from .utils import generate_certificate
from edraak_misc.utils import is_student_pass, is_certificate_allowed


logger = logging.getLogger(__name__)

@login_required
def issue(request, course_id):
    return render_to_response('edraak_certificates/issue.html', {
        'course_id': course_id,
    })


@transaction.non_atomic_requests
@login_required
def view(request, course_id):
    user = request.user

    course_key = locator.CourseLocator.from_string(course_id)
    course = modulestore().get_course(course_key)

    if is_certificate_allowed(user, course) and is_student_pass(user, request, course_id):
        template = 'edraak_certificates/view.html'
    else:
        template = 'edraak_certificates/fail.html'

    course_end_date = course.end or date.today()
    course_expiration_date = course_end_date + relativedelta(years=settings.BAYT_VALID_YEARS)

    return render_to_response(template, {
        'user': user,
        'cert_course': course,  # Course name is set to `cert_course` to avoid header design bug
        'cert_end': course_expiration_date.strftime('%m-%Y')
    })


@transaction.non_atomic_requests
@login_required
def download(request, course_id):
    user = request.user

    if is_student_pass(user, request, course_id):
        pdf_file = generate_certificate(request, course_id)
        wrapper = FileWrapper(pdf_file)

        # `application/octet-stream` is to force download
        response = HttpResponse(wrapper, content_type='application/octet-stream')

        response['Content-Length'] = os.path.getsize(pdf_file.name)
        response['Content-Disposition'] = "attachment; filename=Edraak-Certificate.pdf"

        return response
    else:
        return redirect(reverse('dashboard'))


@transaction.non_atomic_requests
@login_required
def preview(request, course_id):
    user = request.user

    if is_student_pass(user, request, course_id):
        pdf_file = generate_certificate(request, course_id)
        image_file = NamedTemporaryFile(suffix='-cert.png')

        with Image(filename=pdf_file.name) as img:
            with img.clone() as i:
                # i.resize(445, 315)
                i.save(filename=image_file.name)

        wrapper = FileWrapper(image_file)
        response = HttpResponse(wrapper, content_type='image/png')
        response['Content-Length'] = os.path.getsize(image_file.name)

        return response
    else:
        return redirect(reverse('dashboard'))
