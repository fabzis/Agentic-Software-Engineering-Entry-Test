import json
from datetime import datetime, timezone
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen


def packagecheck(filepath):
    checked = 0
    packages_not_found = 0
    versions_not_found = 0
    oldest_pinned_release = None

    with open(filepath, 'r', encoding='utf-8') as f:
        for line_number, line in enumerate(f, start=1):
            line = line.split('#', 1)[0].strip()
            package, version = (part.strip() for part in line.split('==', 1))
            checked += 1
            package_url = "https://pypi.org/pypi/{}/json".format(
                quote(package, safe='')
            )
            request = Request(
                package_url, headers={"User-Agent": "requirements-pypi-checker/1.0"}
            )
            try:
                with urlopen(request, timeout=15) as response:
                    package_data = json.load(response)
            except HTTPError as error:
                if error.code == 404:
                    packages_not_found += 1
                    continue
                raise

            if version not in package_data.get('releases', {}):
                versions_not_found += 1
                continue

            version_url = "https://pypi.org/pypi/{}/{}/json".format(
                quote(package, safe=''), quote(version, safe='')
            )
            version_request = Request(
                version_url, headers={"User-Agent": "requirements-pypi-checker/1.0"}
            )
            try:
                with urlopen(version_request, timeout=15) as response:
                    version_data = json.load(response)
            except HTTPError as error:
                if error.code == 404:
                    versions_not_found += 1
                    continue
                raise

            urls = version_data.get('urls', [])
            if urls:
                upload_time = (
                    urls[0].get('upload_time_iso_8601') or urls[0].get('upload_time')
                )
                if upload_time:
                    parsed_time = datetime.fromisoformat(
                        upload_time.replace('Z', '+00:00')
                    )
                    if parsed_time.tzinfo is None:
                        parsed_time = parsed_time.replace(tzinfo=timezone.utc)
                    if (
                        oldest_pinned_release is None
                        or parsed_time < oldest_pinned_release[0]
                    ):
                        oldest_pinned_release = (
                            parsed_time, package, version, upload_time
                        )
            print("{}=={} exists on PyPI".format(package, version))

    print("Dependencies checked:", checked)
    print("Packages not on PyPI:", packages_not_found)
    print("Versions not on PyPI:", versions_not_found)
    if oldest_pinned_release is None:
        print("Oldest pinned release: no dated releases found")
    else:
        upload_time, package, version, _ = oldest_pinned_release
        print(
            "Oldest pinned release: {}=={} ({})".format(
                package, version, upload_time.year
            )
        )


packagecheck(r"C:\Users\fabia\Agentic-Software-Engineering-Entry-Test\requirements.txt")

packagecheck(r"C:\Users\fabia\Agentic-Software-Engineering-Entry-Test\requirements2.txt")