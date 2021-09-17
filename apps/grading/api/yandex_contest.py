import logging
import re
from enum import Enum, IntEnum
from typing import Optional

import requests

from core.typings import assert_never

logger = logging.getLogger(__name__)


YANDEX_SUBMISSION_REPORT_URL = 'https://contest.yandex.ru/contest/{contest_id}/run-report/{run_id}/'
YANDEX_CONTEST_PROBLEM_URL = 'https://contest.yandex.ru/contest/{contest_id}/problems/{problem_id}/'
YANDEX_CONTEST_PROBLEM_REGEX = re.compile(r"/contest\/(?P<contest_id>[\d]+)\/problems\/(?P<problem_alias>[a-zA-Z0-9]*)(?P<trailing_slash>[\/]?)")
YANDEX_CONTEST_DOMAIN = "contest.yandex.ru"


class RegisterStatus(IntEnum):
    CREATED = 201  # Successfully registered for contest
    OK = 200  # FIXME: Looks like it returns instead of DUPLICATED
    BAD_TOKEN = 401  # OAuth header is not declared or is wrong
    NO_ACCESS = 403  # You have no access to this contest
    NOT_FOUND = 404  # Contest not found
    DUPLICATED = 409  # You have already registered for this contest


class ResponseStatus(IntEnum):
    SUCCESS = 200
    BAD_REQUEST = 400  # Bad Request
    BAD_TOKEN = 401  # OAuth header is not declared or is wrong
    NO_ACCESS = 403  # You don't have enough permissions
    NOT_FOUND = 404  # User or contest not found
    NOT_ALLOWED = 405  # Method Not Allowed


STANDINGS_PARAMS = {
    'page': 'page',
    'page_size': 'pageSize',
    'for_judge': 'forJudge',  # something about freezing submissions
    # Participants can start contest after ending if allowed in settings
    'show_virtual': 'showVirtual',
    # Admins can attach results from external log without having
    # participants submissions.
    'show_external': 'showExternal',
    'locale': 'locale',
    'participant': 'participantSearch',
    'participant_group_id': 'userGroupId',
}

SUBMISSIONS_PARAMS = {
    'locale': 'locale',
    'page': 'page',
    'page_size': 'pageSize',
}


class SubmissionStatus(IntEnum):
    SUCCESS = 200
    BAD_REQUEST = 400  # Bad Request
    BAD_TOKEN = 401  # OAuth header is not declared or is wrong
    NOT_FOUND = 404  # Contest or your participation is not found


class SubmissionVerdict(Enum):
    OK = 'OK'
    WA = 'WrongAnswer'
    PE = 'PresentationError'
    CE = "CompilationError"
    RE = "RuntimeError"


class ProblemStatus(Enum):
    NOT_SUBMITTED = 'NOT_SUBMITTED'
    NOT_ACCEPTED = 'NOT_ACCEPTED'
    ACCEPTED = 'ACCEPTED'


class Error(Exception):
    pass


class Unavailable(Error):
    pass


class ContestAPIError(Error):
    def __init__(self, code, message):
        self.code = code
        self.message = message


# FIXME: Replace with ContestAPIError
class YandexContestAPIException(Exception):
    pass


def cast_contest_error(exc) -> Exception:
    from rest_framework import status
    from rest_framework.exceptions import APIException

    # Any errors returned from the Yandex.Contest in a
    # (lms client) - (lms server) - (yandex.contest) chain are considered
    # as an internal error from the client side.
    status_code = str(status.HTTP_500_INTERNAL_SERVER_ERROR)
    if isinstance(exc, Unavailable):
        msg = "Yandex.Contest is unavailable at this moment. Try again later."
        return APIException(detail=msg, code=status_code)
    elif isinstance(exc, ContestAPIError):
        code = ResponseStatus(exc.code)
        if code == ResponseStatus.NO_ACCESS:
            msg = ("Make sure contest@compscicenter.ru was added to the "
                   "contest participants with an admin role")
            return APIException(detail=msg, code=status_code)
        elif code == ResponseStatus.BAD_TOKEN:
            msg = ("Credentials for contest@compscicenter.ru are expired. "
                   "Please, contact curators to fix this problem.")
            return APIException(detail=msg, code=status_code)
        else:
            return APIException(detail=exc.message, code=str(code))
    else:
        assert_never(exc)


# TODO: better handle exceptions. Use `register_in_contest` method as example
class YandexContestAPI:
    """
    https://api.contest.yandex.net/api/public/swagger-ui.html#/
    """
    BASE_URL = 'https://api.contest.yandex.net/api/public/v2'
    PARTICIPANTS_URL = BASE_URL + '/contests/{contest_id}/participants'
    PARTICIPANT_URL = PARTICIPANTS_URL + '/{pid}'
    SUBMISSIONS_URL = BASE_URL + '/contests/{contest_id}/submissions'
    SUBMISSION_URL = SUBMISSIONS_URL + '/{sid}'
    CONTEST_URL = BASE_URL + '/contests/{contest_id}'
    PROBLEMS_URL = CONTEST_URL + '/problems'
    STANDINGS_URL = CONTEST_URL + '/standings'

    def __init__(self, access_token, refresh_token=None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.base_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"OAuth {self.access_token}"
        }

    def register_in_contest(self, yandex_login, contest_id, timeout: int = 3):
        headers = self.base_headers
        payload = {'login': yandex_login}
        api_contest_url = self.PARTICIPANTS_URL.format(contest_id=contest_id)
        try:
            response = requests.post(api_contest_url,
                                     headers=headers,
                                     params=payload,
                                     timeout=timeout)
            response.raise_for_status()
        # Network problems
        except (requests.ConnectionError, requests.Timeout) as e:
            raise Unavailable() from e
        # Client 4xx or server 5xx HTTP errors
        except requests.exceptions.HTTPError as e:
            response = e.response
            try:
                RegisterStatus(response.status_code)  # look up in enum
                raise ContestAPIError(response.status_code, response.text)
            except ValueError:
                # Unpredictable client or server error
                logger.exception("Contest API service had internal error.")
                raise Unavailable() from e
        participant_id = None
        # FIXME: this logic should be encapsulated in the response object
        if response.status_code in (RegisterStatus.CREATED, RegisterStatus.OK):
            participant_id = response.json()
            logger.debug("Meta data: {}".format(participant_id))
        return response.status_code, participant_id

    # FIXME: api.contest(42).info()
    def contest_info(self, contest_id, timeout: Optional[int] = 1):
        headers = self.base_headers
        url = self.CONTEST_URL.format(contest_id=contest_id)
        response = self.request_and_check(url, "get", headers=headers,
                                          timeout=timeout)
        info = response.json()
        logger.debug("Meta data: {}".format(info))
        return response.status_code, info

    # FIXME: api.contest(42).problems()
    def contest_problems(self, contest_id, timeout: Optional[int] = 1):
        headers = self.base_headers
        url = self.PROBLEMS_URL.format(contest_id=contest_id)
        response = self.request_and_check(url, "get", headers=headers,
                                          timeout=timeout)
        info = response.json()
        logger.debug("Meta data: {}".format(info))
        return response.status_code, info["problems"]

    # FIXME: api.contest(42).submissions()
    # TODO: add pagination
    def contest_submissions(self, contest_id, timeout: Optional[int] = 2, **params):
        headers = self.base_headers
        url = self.SUBMISSIONS_URL.format(contest_id=contest_id)
        if "page" not in params:
            params["page"] = 1
        if "page_size" not in params:
            params["page_size"] = 100
        if "locale" not in params:
            params["locale"] = "ru"
        payload = {}
        for param_key, param_value in params.items():
            key = SUBMISSIONS_PARAMS.get(param_key, param_key)
            payload[key] = param_value
        response = self.request_and_check(url, "get", headers=headers,
                                          params=payload, timeout=timeout)
        info = response.json()
        logger.debug("Meta data: {}".format(info))
        return response.status_code, info["submissions"]

    # FIXME: api.contest(42).submission(1)
    def submission_details(self, contest_id, submission_id,
                           full=False, timeout: Optional[int] = 1):
        """Provide `full=True` to get all details like checker log"""
        headers = self.base_headers
        url = self.SUBMISSION_URL.format(contest_id=contest_id,
                                         sid=submission_id)
        if full:
            url = f"{url}/full"
        response = self.request_and_check(url, "get", headers=headers,
                                          timeout=timeout)
        data = response.json()
        logger.debug("Meta data: {}".format(data))
        return response.status_code, data

    def add_submission(self, contest_id, timeout=3, files=None, **params):
        headers = {
            **self.base_headers,
            'Accept': '*/*',
        }
        # requests doesn't set boundary if the header were provided explicitly
        del headers['Content-Type']
        url = self.SUBMISSIONS_URL.format(contest_id=contest_id)
        payload = {**params}
        response = self.request_and_check(url, "post", headers=headers,
                                          data=payload, files=files,
                                          timeout=timeout)
        data = response.json()
        logger.debug("Meta data: {}".format(data))
        return response.status_code, data

    @staticmethod
    def request_and_check(url, method, **kwargs):
        assert method in ('post', 'get')
        try:
            response = getattr(requests, method)(url, **kwargs)
            response.raise_for_status()
            return response
        # Some of the network problems
        except (requests.ConnectionError, requests.Timeout) as e:
            raise Unavailable() from e
        # Client 4xx or server 5xx HTTP errors
        except requests.exceptions.HTTPError as e:
            response = e.response
            try:
                s = response.status_code
                ResponseStatus(s)  # known statuses
                raise ContestAPIError(code=s, message=response.text) from e
            except ValueError:
                # Unpredictable client or server error
                logger.exception("Contest API service had internal error.")
                raise Unavailable() from e

    # FIXME: api.contest(42).participant(1).info()
    def participant_info(self, contest_id, participant_id):
        headers = self.base_headers
        url = self.PARTICIPANT_URL.format(contest_id=contest_id,
                                          pid=participant_id)
        response = requests.get(url, headers=headers, timeout=1)
        if response.status_code != ResponseStatus.SUCCESS:
            raise YandexContestAPIException(response.status_code, response.text)
        info = response.json()
        logger.debug("Meta data: {}".format(info))
        return response.status_code, info

    def standings(self, contest_id, timeout=3, **params):
        """
        Scoreboard contains results of those who started the contest and
        sent any submission for check.
        """
        headers = self.base_headers
        url = self.STANDINGS_URL.format(contest_id=contest_id)
        if "page_size" not in params:
            params["page_size"] = 100
        if "locale" not in params:
            params["locale"] = "ru"
        # Due to the features of the `shad` monitor, set for_judge to True
        if "for_judge" not in params:
            params["for_judge"] = True
        if "show_external" not in params:
            params["show_external"] = False
        if "show_virtual" not in params:
            params["show_virtual"] = False
        for bool_attr in ("for_judge", "show_external", "show_virtual"):
            params[bool_attr] = str(params[bool_attr]).lower()
        payload = {}
        for param_key, param_value in params.items():
            key = STANDINGS_PARAMS.get(param_key, param_key)
            payload[key] = param_value
        logger.debug(f"Payload: {payload}")
        response = self.request_and_check(url, "get", headers=headers,
                                          params=payload, timeout=timeout)
        json_data = response.json()
        logger.debug(f"Meta data: {json_data}")
        return response.status_code, json_data
