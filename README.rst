==========
Hootsweet
==========

.. image:: https://img.shields.io/pypi/v/hootsweet
    :alt: PyPI

.. image:: https://img.shields.io/pypi/pyversions/hootsweet
    :alt: PyPI Versions

.. image:: https://img.shields.io/pypi/format/hootsweet
    :alt: PyPi Format

.. image:: https://requires.io/github/ciaranmccormick/hootsweet/requirements.svg?branch=develop
    :target: https://requires.io/github/ciaranmccormick/hootsweet/requirements/?branch=develop
    :alt: Requirements Status

.. image:: https://readthedocs.org/projects/hootsweet/badge/?version=latest
    :target: https://hootsweet.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

A python API for the HootSuite REST API.


Quick Start
-----------

.. code-block::python
    from hootsweet import Hootsweet

    redirect_uri = "https://mydomain.com/hootsuite/callback"
    client = HootSweet("client-id", "client-secret", redirect_uri=redirect_uri)
