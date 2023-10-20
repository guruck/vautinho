from requests.models import Response


def print_response(res: Response):
    print("-" * 80)
    print("Content: ", res._content)
    print("Status Code: ", res.status_code)
    print("Headers: ", res.headers)
    print("Url: ", res.url)
    print("History: ", res.history)
    print("Encoding: ", res.encoding)
    print("Reason: ", res.reason)
    print("Cookies: ", res.cookies)
    print("Elapsed: ", res.elapsed)
    print("Request: ", res.request)
    print("-" * 80)


def is_success(status_code: int) -> bool:
    return (status_code == 200) | (status_code == 204)
