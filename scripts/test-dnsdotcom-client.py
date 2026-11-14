#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PKG = os.path.join(ROOT, ".veikor-build", "cdnfly-master-v5.1.13", "master", "tasks", "dnsapi")
sys.path.insert(0, PKG)

import dnsdotcom
import tencent_dns


def test_sign_doc_example():
    param = {"domain": "51dns.com", "timestamp": "1602734019", "apiKey": "your api_key"}
    pairs = []
    for key in sorted(param):
        pairs.append("{0}={1}".format(key, param[key]))
    digest = hashlib.md5(("&".join(pairs) + "your api_secret").encode("utf-8")).hexdigest()
    client = dnsdotcom.Dns(json.dumps({"id": "your api_key", "token": "your api_secret"}))
    assert client._sign(param) == digest


def test_lines_shape():
    client = dnsdotcom.Dns(json.dumps({"id": "k", "token": "s"}))
    lines, err = client.get_lines("example.com", None)
    assert err is None
    tree = json.loads(lines)
    assert tree[0]["id"] == "0" and tree[0]["name"] == u"默认"
    assert "pid" in tree[0]


class Resp(object):
    def __init__(self, payload):
        self.content = json.dumps(payload).encode("utf-8")


class FakeAPI(object):
    def __init__(self):
        self.urls = []

    def get(self, url, params=None, timeout=None):
        self.urls.append((url, dict(params or {})))
        if url.endswith("domain/getsingle/"):
            return Resp({"code": 0, "data": {"domainID": 99, "domain": "example.com"}})
        if url.endswith("record/list/"):
            page = int(params.get("page", "1"))
            if page == 1:
                rows = [{
                    "recordID": 7,
                    "record": "www",
                    "type": "A",
                    "viewID": "285344962",
                    "value": "1.2.3.4",
                    "TTL": 600,
                }]
                return Resp({"code": 0, "data": {"data": rows, "pageCount": 1}})
            return Resp({"code": 0, "data": {"data": [], "pageCount": 1}})
        if url.endswith("record/create/"):
            return Resp({"code": 0, "data": {"recordID": 55}})
        if url.endswith("record/modify/"):
            return Resp({"code": 0, "data": {"recordID": params.get("recordID")}})
        if url.endswith("record/remove/"):
            return Resp({"code": 0, "data": {"recordID": params.get("recordID")}})
        if url.endswith("record/getsingle/"):
            return Resp({"code": 0, "data": {
                "recordID": params.get("recordID"),
                "record": "www",
                "type": "CNAME",
                "viewID": "0",
                "value": "a.example.com.",
                "TTL": 300,
            }})
        raise AssertionError(url)


def test_crud_flow():
    fake = FakeAPI()
    dnsdotcom.requests = fake
    tencent_dns.requests = fake
    client = dnsdotcom.Dns(json.dumps({"id": "key", "token": "sec"}))
    client.domain_name = "example.com"
    got, err = client.get_all_record("example.com")
    assert err is None and got["7"]["sub_domain"] == "www"
    assert all(url.startswith("https://www.51dns.com/api/") for url, _ in fake.urls)
    joined = " ".join(url for url, _ in fake.urls)
    assert "www.dns.com" not in joined
    rec, err = client.get_record("example.com", "7")
    assert err is None and rec["value"] == "a.example.com"
    rid, err = client.add_record("example.com", "@", "A", "0", "9.9.9.9", 600)
    assert rid == "55"
    ok, err = client.update_record("example.com", "7", "www", "A", "0", "8.8.8.8", 600, weight=5)
    assert ok is True and err is None
    ok, err = client.del_record("example.com", "7")
    assert ok is True and err is None


def test_auth_aliases():
    client = dnsdotcom.Dns(json.dumps({"authid": "kid", "authtoken": "sec"}))
    assert client.api_key == "kid" and client.api_secret == "sec"


def test_success_without_code_field():
    class Fake(object):
        def get(self, url, params=None, timeout=None):
            return Resp({"message": "", "data": {"domainID": 42, "domain": "example.com"}})

    dnsdotcom.requests = Fake()
    client = dnsdotcom.Dns(json.dumps({"id": "k", "token": "s"}))
    data, err = client.send_request("domain/getsingle", {"domainID": "example.com"})
    assert err is None and data.get("domainID") == 42


def test_api_error_message_without_code():
    class Fake(object):
        def get(self, url, params=None, timeout=None):
            return Resp({"message": u"鉴权失败"})

    dnsdotcom.requests = Fake()
    client = dnsdotcom.Dns(json.dumps({"id": "k", "token": "s"}))
    _, err = client.send_request("domain/getsingle", {"domainID": "example.com"})
    assert err == u"鉴权失败"


def test_api_error_unparseable_code():
    class Fake(object):
        def get(self, url, params=None, timeout=None):
            return Resp({"code": "bad", "message": ""})

    dnsdotcom.requests = Fake()
    client = dnsdotcom.Dns(json.dumps({"id": "k", "token": "s"}))
    _, err = client.send_request("domain/getsingle", {"domainID": "example.com"})
    assert err == u"请求失败"


def test_api_error_empty_body():
    class Fake(object):
        def get(self, url, params=None, timeout=None):
            return Resp({})

    dnsdotcom.requests = Fake()
    client = dnsdotcom.Dns(json.dumps({"id": "k", "token": "s"}))
    _, err = client.send_request("domain/getsingle", {"domainID": "example.com"})
    assert err == u"请求失败"


def test_api_error_empty_message():
    class Fake(object):
        def get(self, url, params=None, timeout=None):
            return Resp({"code": 5, "message": ""})

    dnsdotcom.requests = Fake()
    client = dnsdotcom.Dns(json.dumps({"id": "k", "token": "s"}))
    _, err = client.send_request("domain/getsingle", {"domainID": "example.com"})
    assert err == u"请求失败"


def test_empty_zone():
    class Fake(object):
        def get(self, url, params=None, timeout=None):
            if url.endswith("domain/getsingle/"):
                return Resp({"code": 0, "data": {"domainID": 1, "domain": "example.com"}})
            if url.endswith("record/list/"):
                return Resp({"code": 0, "data": {"data": [], "recordCount": 0, "total_page": 0, "pageCount": 0}})
            raise AssertionError(url)

    dnsdotcom.requests = Fake()
    client = dnsdotcom.Dns(json.dumps({"id": "k", "token": "s"}))
    got, err = client.get_all_record("example.com")
    assert err is None and got == {}


def test_record_count_past_page_count():
    class Fake(object):
        def get(self, url, params=None, timeout=None):
            if url.endswith("domain/getsingle/"):
                return Resp({"code": 0, "data": {"domainID": 1}})
            if url.endswith("record/list/"):
                page = int(params.get("page", "1"))
                if page == 1:
                    rows = [
                        {
                            "recordID": i,
                            "record": "h%d" % i,
                            "type": "A",
                            "viewID": 0,
                            "value": "1.1.1.1",
                        }
                        for i in range(1000)
                    ]
                    return Resp({
                        "code": 0,
                        "data": {
                            "data": rows,
                            "recordCount": 1500,
                            "pageCount": 1,
                            "total_page": 1,
                        },
                    })
                if page == 2:
                    rows = [
                        {
                            "recordID": i,
                            "record": "h%d" % i,
                            "type": "A",
                            "viewID": 0,
                            "value": "2.2.2.2",
                        }
                        for i in range(1000, 1500)
                    ]
                    return Resp({"code": 0, "data": {"data": rows, "recordCount": 1500}})
                return Resp({"code": 0, "data": {"data": [], "recordCount": 1500}})
            raise AssertionError(url)

    dnsdotcom.requests = Fake()
    client = dnsdotcom.Dns(json.dumps({"id": "k", "token": "s"}))
    got, err = client.get_all_record("example.com")
    assert err is None and len(got) == 1500


def test_short_first_page():
    class Fake(object):
        def get(self, url, params=None, timeout=None):
            if url.endswith("domain/getsingle/"):
                return Resp({"code": 0, "data": {"domainID": 1}})
            if url.endswith("record/list/"):
                page = int(params.get("page", "1"))
                if page == 1:
                    rows = [
                        {"recordID": i, "record": "a", "type": "A", "viewID": 0, "value": "1.1.1.1"}
                        for i in range(1, 501)
                    ]
                    return Resp({"code": 0, "data": {"data": rows, "recordCount": 1000, "pageCount": 2, "total_page": 2}})
                if page == 2:
                    rows = [
                        {"recordID": i, "record": "b", "type": "A", "viewID": 0, "value": "2.2.2.2"}
                        for i in range(501, 1001)
                    ]
                    return Resp({"code": 0, "data": {"data": rows, "recordCount": 1000}})
                return Resp({"code": 0, "data": {"data": [], "recordCount": 1000}})
            raise AssertionError(url)

    dnsdotcom.requests = Fake()
    client = dnsdotcom.Dns(json.dumps({"id": "k", "token": "s"}))
    got, err = client.get_all_record("example.com")
    assert err is None and len(got) == 1000


def test_overstated_record_count_short_tail():
    class Fake(object):
        def get(self, url, params=None, timeout=None):
            if url.endswith("domain/getsingle/"):
                return Resp({"code": 0, "data": {"domainID": 1}})
            if url.endswith("record/list/"):
                page = int(params.get("page", "1"))
                if page == 1:
                    rows = [{"recordID": i, "record": "h", "type": "A", "viewID": 0, "value": "1.1.1.1"} for i in range(1000)]
                    return Resp({"code": 0, "data": {"data": rows, "recordCount": 5000, "pageCount": 1}})
                if page == 2:
                    rows = [{"recordID": i, "record": "h", "type": "A", "viewID": 0, "value": "1.1.1.1"} for i in range(1000, 1500)]
                    return Resp({"code": 0, "data": {"data": rows, "recordCount": 5000}})
                return Resp({"code": 0, "data": {"data": [], "recordCount": 5000}})
            raise AssertionError(url)

    dnsdotcom.requests = Fake()
    client = dnsdotcom.Dns(json.dumps({"id": "k", "token": "s"}))
    got, err = client.get_all_record("example.com")
    assert err is None and len(got) == 1500


def test_add_record_list_payload():
    class Fake(object):
        def get(self, url, params=None, timeout=None):
            if url.endswith("domain/getsingle/"):
                return Resp({"code": 0, "data": {"domainID": 9}})
            if url.endswith("record/create/"):
                return Resp({"code": 0, "data": [{"recordID": 88}]})
            raise AssertionError(url)

    dnsdotcom.requests = Fake()
    client = dnsdotcom.Dns(json.dumps({"id": "k", "token": "s"}))
    rid, err = client.add_record("example.com", "www", "A", "0", "1.1.1.1", 600)
    assert err is None and rid == "88"


def test_add_record_host_normalization():
    captured = []

    class Fake(object):
        def get(self, url, params=None, timeout=None):
            if url.endswith("domain/getsingle/"):
                return Resp({"code": 0, "data": {"domainID": 9}})
            if url.endswith("record/create/"):
                captured.append(dict(params or {}))
                return Resp({"code": 0, "data": {"recordID": 1}})
            raise AssertionError(url)

    dnsdotcom.requests = Fake()
    client = dnsdotcom.Dns(json.dumps({"id": "k", "token": "s"}))
    rid, err = client.add_record("example.com", "www.example.com", "A", "0", "1.1.1.1", 600)
    assert err is None and rid == "1"
    assert captured[0].get("host") == "www"


def test_trailing_empty_page():
    class Fake(object):
        def get(self, url, params=None, timeout=None):
            if url.endswith("domain/getsingle/"):
                return Resp({"code": 0, "data": {"domainID": 1}})
            if url.endswith("record/list/"):
                page = int(params.get("page", "1"))
                if page == 1:
                    rows = [{"recordID": 1, "record": "www", "type": "A", "viewID": 0, "value": "1.1.1.1"}]
                    return Resp({"code": 0, "data": {"data": rows, "total_page": 3, "pageCount": 3}})
                return Resp({"code": 0, "data": {"data": [], "total_page": 3, "pageCount": 3}})
            raise AssertionError(url)

    dnsdotcom.requests = Fake()
    client = dnsdotcom.Dns(json.dumps({"id": "k", "token": "s"}))
    got, err = client.get_all_record("example.com")
    assert err is None and "1" in got


def test_append_rs():
    client = dnsdotcom.Dns(json.dumps({"id": "k", "token": "s"}))
    client.domain_name = "example.com"
    bucket = {}
    client.append_rs([
        {"recordID": 1, "record": "@", "type": "A", "viewID": 0, "value": "1.1.1.1"},
        {"recordID": 2, "record": "cdn", "type": "CNAME", "viewID": "0", "value": "a.example.com."},
        {"recordID": 3, "record": "www.example.com", "type": "A", "viewID": 0, "value": "2.2.2.2"},
        "bad",
    ], bucket)
    assert bucket["1"]["sub_domain"] == "@"
    assert bucket["2"]["ip"] == "a.example.com"
    assert bucket["3"]["sub_domain"] == "www"


def main():
    test_sign_doc_example()
    test_lines_shape()
    test_crud_flow()
    test_auth_aliases()
    test_success_without_code_field()
    test_api_error_message_without_code()
    test_api_error_unparseable_code()
    test_api_error_empty_body()
    test_api_error_empty_message()
    test_empty_zone()
    test_record_count_past_page_count()
    test_short_first_page()
    test_overstated_record_count_short_tail()
    test_add_record_list_payload()
    test_add_record_host_normalization()
    test_trailing_empty_page()
    test_append_rs()
    print("ALL PASSED")


if __name__ == "__main__":
    main()