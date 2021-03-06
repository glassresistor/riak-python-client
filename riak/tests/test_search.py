# -*- coding: utf-8 -*-
import os
import platform
if platform.python_version() < '2.7':
    unittest = __import__('unittest2')
else:
    import unittest

SKIP_SEARCH = int(os.environ.get('SKIP_SEARCH', '0'))


class EnableSearchTests(object):
    @unittest.skipIf(SKIP_SEARCH, 'SKIP_SEARCH is defined')
    def test_bucket_search_enabled(self):
        bucket = self.client.bucket("unsearch_bucket")
        self.assertFalse(bucket.search_enabled())

    @unittest.skipIf(SKIP_SEARCH, 'SKIP_SEARCH is defined')
    def test_enable_search_commit_hook(self):
        bucket = self.client.bucket("search_bucket")
        bucket.enable_search()
        self.assertTrue(self.client.bucket("search_bucket").search_enabled())

    @unittest.skipIf(SKIP_SEARCH, 'SKIP_SEARCH is defined')
    def test_disable_search_commit_hook(self):
        bucket = self.client.bucket("no_search_bucket")
        bucket.enable_search()
        self.assertTrue(self.client.bucket("no_search_bucket")\
                            .search_enabled())
        bucket.disable_search()
        self.assertFalse(self.client.bucket("no_search_bucket")\
                             .search_enabled())


class SolrSearchTests(object):
    @unittest.skipIf(SKIP_SEARCH, 'SKIP_SEARCH is defined')
    def test_add_document_to_index(self):
        self.client.solr().add("searchbucket",
                               {"id": "doc", "username": "tony"})
        results = self.client.solr().search("searchbucket", "username:tony")
        self.assertEquals("tony", results['docs'][0]['username'])

    @unittest.skipIf(SKIP_SEARCH, 'SKIP_SEARCH is defined')
    def test_add_multiple_documents_to_index(self):
        self.client.solr().add("searchbucket",
                               {"id": "dizzy", "username": "dizzy"},
                               {"id": "russell", "username": "russell"})
        results = self.client.solr()\
            .search("searchbucket", "username:russell OR username:dizzy")
        self.assertEquals(2, len(results['docs']))

    @unittest.skipIf(SKIP_SEARCH, 'SKIP_SEARCH is defined')
    def test_delete_documents_from_search_by_id(self):
        self.client.solr().add("searchbucket",
                               {"id": "dizzy", "username": "dizzy"},
                               {"id": "russell", "username": "russell"})
        self.client.solr().delete("searchbucket", docs=["dizzy"])
        results = self.client.solr()\
            .search("searchbucket", "username:russell OR username:dizzy")
        self.assertEquals(1, len(results['docs']))

    @unittest.skipIf(SKIP_SEARCH, 'SKIP_SEARCH is defined')
    def test_delete_documents_from_search_by_query(self):
        self.client.solr().add("searchbucket",
                               {"id": "dizzy", "username": "dizzy"},
                               {"id": "russell", "username": "russell"})
        self.client.solr()\
            .delete("searchbucket",
                    queries=["username:dizzy", "username:russell"])
        results = self.client.solr()\
            .search("searchbucket", "username:russell OR username:dizzy")
        self.assertEquals(0, len(results['docs']))

    @unittest.skipIf(SKIP_SEARCH, 'SKIP_SEARCH is defined')
    def test_delete_documents_from_search_by_query_and_id(self):
        self.client.solr().add("searchbucket",
                               {"id": "dizzy", "username": "dizzy"},
                               {"id": "russell", "username": "russell"})
        self.client.solr().delete("searchbucket",
                                  docs=["dizzy"],
                                  queries=["username:russell"])
        results = self.client.solr()\
            .search("searchbucket",
                    "username:russell OR username:dizzy")
        self.assertEquals(0, len(results['docs']))

    def test_build_rest_path_excludes_empty_query_params(self):
        self.assertEquals(
            self.client.get_transport().build_rest_path(
                bucket=self.client.bucket("foo"),
                key="bar", params={'r': None}), "/riak/foo/bar?")


class SearchTests(object):
    @unittest.skipIf(SKIP_SEARCH, 'SKIP_SEARCH is defined')
    def test_solr_search_from_bucket(self):
        bucket = self.client.bucket('searchbucket')
        bucket.new("user", {"username": "roidrage"}).store()
        results = bucket.search("username:roidrage")
        self.assertEquals(1, len(results['docs']))

    @unittest.skipIf(SKIP_SEARCH, 'SKIP_SEARCH is defined')
    def test_solr_search_with_params_from_bucket(self):
        bucket = self.client.bucket('searchbucket')
        bucket.new("user", {"username": "roidrage"}).store()
        results = bucket.search("username:roidrage", wt="xml")
        self.assertEquals(1, len(results['docs']))

    @unittest.skipIf(SKIP_SEARCH, 'SKIP_SEARCH is defined')
    def test_solr_search_with_params(self):
        bucket = self.client.bucket('searchbucket')
        bucket.new("user", {"username": "roidrage"}).store()
        results = self.client.solr().search("searchbucket",
                                            "username:roidrage", wt="xml")
        self.assertEquals(1, len(results['docs']))

    @unittest.skipIf(SKIP_SEARCH, 'SKIP_SEARCH is defined')
    def test_solr_search(self):
        bucket = self.client.bucket('searchbucket')
        bucket.new("user", {"username": "roidrage"}).store()
        results = self.client.solr().search("searchbucket",
                                            "username:roidrage")
        self.assertEquals(1, len(results["docs"]))

    @unittest.skipIf(SKIP_SEARCH, 'SKIP_SEARCH is defined')
    def test_search_integration(self):
        # Create some objects to search across...
        bucket = self.client.bucket("searchbucket")
        bucket.new("one", {"foo": "one", "bar": "red"}).store()
        bucket.new("two", {"foo": "two", "bar": "green"}).store()
        bucket.new("three", {"foo": "three", "bar": "blue"}).store()
        bucket.new("four", {"foo": "four", "bar": "orange"}).store()
        bucket.new("five", {"foo": "five", "bar": "yellow"}).store()

        # Run some operations...
        results = self.client.solr().search("searchbucket",
                                            "foo:one OR foo:two")
        if (len(results) == 0):
            print "\n\nNot running test \"testSearchIntegration()\".\n"
            print """Please ensure that you have installed the Riak
            Search hook on bucket \"searchbucket\" by running
            \"bin/search-cmd install searchbucket\".\n\n"""
            return
        self.assertEqual(len(results['docs']), 2)
        query = "(foo:one OR foo:two OR foo:three OR foo:four) AND\
                 (NOT bar:green)"
        results = self.client.solr().search("searchbucket", query)
        self.assertEqual(len(results['docs']), 3)
