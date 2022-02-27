
from AWS import Lambda, Configuration
from Interfaces import LogMethod

import sys
import argparse


def load_from_cli():
    args = sys.argv[1:]

    parser = argparse.ArgumentParser(description="Publish the specified lambda function.")
    parser.add_argument("--name", type=str, required=True, dest="NAME",
                        help="The name of the lambda function")
    parser.add_argument("--handler", type=str, default="main.handler", dest="HANDLER",
                        help="The name of the handler function.")
    parser.add_argument("--build-dir", type=str, default="_build", dest="BUILD_DIR")
    parser.add_argument("--src-dir", type=str, default="src", dest="SOURCE_DIR")
    parser.add_argument("--requirements", type=str, default="requirements.txt", dest="REQUIREMENTS_FILE")
    parser.add_argument("--environment", type=str, default="live.env", dest="ENVIRONMENT_FILE")
    parser.add_argument("--tags", type=str, default="tags.toml", dest="TAGS_FILE")
    parser.add_argument("--package-file", type=str, default="package.zip", dest="PACKAGE_FILE")
    parser.add_argument("--code-bucket", type=str, default="sprelf-lambda-zips", dest="CODE_BUCKET")
    parser.add_argument("--code-bucket-path", type=str, default="", dest="CODE_BUCKET_PATH")
    parser.add_argument("--no-publish", action="store_true", dest="NO_PUBLISH")
    parser.add_argument("--dry-run", action="store_true", dest="DRY_RUN")
    parser.add_argument("--delete-lock", action="store_true", dest="DELETE_LOCK")
    parser.add_argument("--aws-profile", type=str, default=None, dest="AWS_PROFILE")
    parser.add_argument("--skip-package-upload", action="store_true", dest="SKIP_UPLOAD")
    parser.add_argument("--cwd", type=str, default="./", dest="CWD")
    parser.add_argument("--skip-dependencies", "-s", action="store_true", dest="SKIP_DEPENDENCIES")

    options = parser.parse_args(args)

    publish(options)


def publish(options: argparse.Namespace):

    Lambda.publish(lambda_name=options.NAME,
                   handler=options.HANDLER,
                   build_dir=options.BUILD_DIR,
                   src_dir=options.SOURCE_DIR,
                   requirements_file=options.REQUIREMENTS_FILE,
                   environment_file=options.ENVIRONMENT_FILE,
                   tags_file=options.TAGS_FILE,
                   package_file=options.PACKAGE_FILE,
                   code_bucket=options.CODE_BUCKET,
                   code_bucket_path=options.CODE_BUCKET_PATH,
                   publish_after=not options.NO_PUBLISH and not options.DRY_RUN,
                   dry_run=options.DRY_RUN,
                   delete_lock=options.DELETE_LOCK,
                   skip_dependencies=options.SKIP_DEPENDENCIES,
                   skip_package_upload=options.SKIP_UPLOAD,
                   local_libs=options.LOCAL_LIBS if hasattr(options, "LOCAL_LIBS") else dict(),
                   aws_client_kwargs=Configuration.get_client_args(profile_name=options.AWS_PROFILE),
                   cwd=options.CWD,
                   logger=LogMethod.printer())


if __name__ == "__main__":
    load_from_cli()
