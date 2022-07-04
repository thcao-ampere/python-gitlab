# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2017 Gauvain Pocentek <gauvain@pocentek.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from typing import Any, Callable, Dict, Optional, Union
from urllib.parse import quote, urlparse

import requests


class _StdoutStream(object):
    def __call__(self, chunk: Any) -> None:
        print(chunk)


def response_content(
    response: requests.Response,
    streamed: bool,
    action: Optional[Callable],
    chunk_size: int,
) -> Optional[bytes]:
    if streamed is False:
        return response.content

    if action is None:
        action = _StdoutStream()

    for chunk in response.iter_content(chunk_size=chunk_size):
        if chunk:
            action(chunk)
    return None


def copy_dict(dest: Dict[str, Any], src: Dict[str, Any]) -> None:
    for k, v in src.items():
        if isinstance(v, dict):
            # Transform dict values to new attributes. For example:
            # custom_attributes: {'foo', 'bar'} =>
            #   "custom_attributes['foo']": "bar"
            for dict_k, dict_v in v.items():
                dest["%s[%s]" % (k, dict_k)] = dict_v
        else:
            dest[k] = v

class EncodedId(str):
    """A custom `str` class that will return the URL-encoded value of the string.
      * Using it recursively will only url-encode the value once.
      * Can accept either `str` or `int` as input value.
      * Can be used in an f-string and output the URL-encoded string.
    Reference to documentation on why this is necessary.
    See::
        https://docs.gitlab.com/ee/api/index.html#namespaced-path-encoding
        https://docs.gitlab.com/ee/api/index.html#path-parameters
    """

    def __new__(cls, value: Union[str, int, "EncodedId"]) -> "EncodedId":
        if isinstance(value, EncodedId):
            return value

        if not isinstance(value, (int, str)):
            raise TypeError(f"Unsupported type received: {type(value)}")
        if isinstance(value, str):
            value = quote(value, safe="")
        return super().__new__(cls, value)


def clean_str_id(id: str) -> str:
    return quote(id, safe="")


def sanitized_url(url: str) -> str:
    parsed = urlparse(url)
    new_path = parsed.path.replace(".", "%2E")
    return parsed._replace(path=new_path).geturl()


def remove_none_from_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in data.items() if v is not None}
