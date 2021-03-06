import json
import boto3
from botocore.client import Config
import io
#from io import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    # TODO implement
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:458420087596:deployPortfolioTopic')

    location = {
        "bucketName": "portfoliobuild.rakeshpatel.info",
        "objectKey": "mybuild/portfoliobuild.zip"
    }

    try:

        job = event.get("CodePipeline.job")
        if job:
            for artifact in job["data"]["inputArtifacts"]:
                print("CodePipeline Job Artifact: " + str(artifact))
                if (artifact["name"] == "MyAppBuild") :
                    location = artifact["location"]["s3Location"]

        print("building portfolio from Location: " + str(location))

        s3 = boto3.resource('s3')

        portfolio_bucket = s3.Bucket('portfolio.rakeshpatel.info')

        build_bucket = s3.Bucket(location["bucketName"])
        portfolio_zip = io.BytesIO()

        build_bucket.download_fileobj(location["objectKey"], portfolio_zip)


        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj,nm, ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

        if job:
            codepipeline = boto3.client("codepipeline")
            codepipeline.put_job_success_result(jobId = job["id"])
    except:
        topic.publish(Subject="Portfolio Deployment Failed", Message="Deployment Failed")
        raise

    topic.publish(Subject="Portfolio Deployment", Message="Deployment done Successfully")

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

#
# import boto3
# from botocore.client import Config
# import io
# #from io import StringIO
# import zipfile
# import mimetypes
#
# #s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
# s3 = boto3.resource('s3')
#
# portfolio_bucket = s3.Bucket('portfolio.rakeshpatel.info')
#
# build_bucket = s3.Bucket('portfoliobuild.rakeshpatel.info')
#
# #for obj in portfolio_bucket.objects.all():
# #    print (obj.key)
#
# #portfolio_zip = StringIO.StrinIO()
# portfolio_zip = io.BytesIO()
#
# #build_bucket.download_file('portfoliobuild.zip', '/tmp/portfolio.zip')
#
# #zipObj = build_bucket('mybuild/portfoliobuild.zip')
#
# build_bucket.download_fileobj('mybuild/portfoliobuild.zip', portfolio_zip)
#
# with zipfile.ZipFile(portfolio_zip) as myzip:
#     for nm in myzip.namelist():
#         obj = myzip.open(nm)
#         portfolio_bucket.upload_fileobj(obj,nm, ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
#         portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
