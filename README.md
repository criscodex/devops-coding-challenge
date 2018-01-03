
## s3du - an Amazon S3 storage analysis tool

### Pre-requisites

`python3` and `virtualenv`

Install guides [here](http://docs.python-guide.org/en/latest/starting/install3/osx/) and [here](https://virtualenv.pypa.io/en/stable/installation/)

### Setup

First, set up credentials (in e.g. ``~/.aws/credentials``):

    [default]
    aws_access_key_id = YOUR_KEY
    aws_secret_access_key = YOUR_SECRET


Then, set up a default region (in e.g. ``~/.aws/config``):

    [default]
    region=us-east-1

Alternatively, you may copy these files from this repo's `config` folder


### Installation

    $ virtualenv env
    $ source env/bin/activate
    $ pip install -r requirements.txt


### Usage

```
$ python3 s3du.py -h
usage: s3du.py [-h] [-u UNIT] [-b BUCKET] [-s SORT]

This is a command-line utility that returns information about S3 buckets in an
Amazon AWS account.

optional arguments:
  -h, --help                  show this help message and exit
  -u UNIT, --unit UNIT        Specify your desired bucket size units (B, KB, MB, GB, TB)
  -b BUCKET, --bucket BUCKET  Filter buckets by partial name or regex (e.g. buck or ^buck; no quotes)
  -s SORT, --sort SORT        Column to sort by (bucket, size, objects, created, modified, storage, region)
```

### Examples

  - Default, no arguments *(list all buckets, sorted by region, sizes in bytes)*
  ```
  $ python3 s3du.py
  ```
  - List specific buckets *(filter by partial bucket name, sizes in gigs)*
  ```
  $ python3 s3du.py -b mybuck -u GB
  ```
  - List a subset of buckets *(regex filter, sizes in megs)*
  ```
  $ python3 s3du.py -b ^mybuck -u MB
  ```
  - List all buckets sorted by size
  ```
  $ python3 s3du.py -s size
  ```
  - List all buckets sorted by storage class
  ```
  $ python3 s3du.py -s storage
  ```
