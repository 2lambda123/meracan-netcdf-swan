import os
import shutil
import uuid

import boto3
from boto3.s3.transfer import TransferConfig
from botocore.errorfactory import ClientError
from tqdm import tqdm

cacheLocation = "../data"
s3Prefix = "partitionSWANv6"
bucketName = "uvic-bcwave"

years = ["{}".format(x) for x in range(2004, 2018)]
months = ["{0:02d}".format(x) for x in range(1, 13)]


def getKeys(variable):
    """

    :param variable:

    """
    keys = []
    for year in years:
        for month in months:
            keys.append("{}/{}/{}/results/{}.mat".format(
                s3Prefix, year, month, variable))
    return keys


def getKey(self, filepath):
    """

    :param filepath:

    """
    path = os.path.relpath(filepath, cacheLocation)
    return os.path.join(s3Prefix, path)


def getCachePath(key):
    """

    :param key:

    """
    path = os.path.relpath(key, s3Prefix)
    return os.path.join(cacheLocation, path)


def hook(t):
    """

    :param t:

    """

    def inner(bytes_amount):
        """

        :param bytes_amount:

        """
        t.update(bytes_amount)

    return inner


def downloadWithProgress(key):
    """

    :param key:

    """
    session = boto3.Session(profile_name="jcousineau")
    s3 = session.client("s3")
    filepath = getCachePath(key)
    file_object = s3.get_object(Bucket=bucketName, Key=key)
    name = file_object.get("name")
    filesize = file_object.get("ContentLength")
    with tqdm(total=filesize, unit="B", unit_scale=True, desc=key) as t:
        with open(filepath, "wb") as data:
            s3.download_fileobj(bucketName, key, data, Callback=hook(t))
    return True


def run():
    """ """
    # variable="PTHSIGN"
    # variable="PTRTP"
    variable = "PTDIR"
    # variable="PTDSPR"
    # variable="PTSTEEP"
    # variable="PTWLEN"
    keys = getKeys(variable)
    for key in keys:
        path = getCachePath(key)
        if not os.path.exists(path):
            folder = os.path.dirname(path)
            os.makedirs(folder, exist_ok=True)
            response = downloadWithProgress(key)


run()
