# sceptre-s3-packager

Hook and resolver for [Sceptre](https://sceptre.cloudreach.com/latest/) `v2` to
package code dependencies and uploading it to an S3 bucket for usage in a
template.

Inspired by https://github.com/cloudreach/sceptre-zip-code-s3

## Getting started

Install using pip:

```bash
pip install sceptre-s3-packager
```

Use the hook and resolver in your template config:

```yaml
template_path: ...
hooks:
  before_create:
    - !sceptre_s3_upload ./directory-to-zip-to-s3
  before_update:
    - !sceptre_s3_upload ./directory-to-zip-to-s3
sceptre_user_data:
  Code:
    S3Bucket: my-s3-bucket
    S3Key: !sceptre_s3_key ./directory-to-zip-to-s3
```

Use the data in the template, e.g. by using Jinja2 template with something
like:

```yaml
  MyLambda:
    Type: AWS::Lambda::Function
    Properties:
      Code:
        S3Bucket: {{ sceptre_user_data.Code.S3Bucket }}
        S3Key: {{ sceptre_user_data.Code.S3Key }}
```

## Usage

Hook:

- `!sceptre_s3_upload <directory>` (reads `S3Bucket` from
  `sceptre_user_data.Code.S3Bucket`)
- `!sceptre_s3_upload <directory>^^<s3-bucket>`

Resolver:

- `!sceptre_s3_key <directory>` (returns a path where the packaged
  directory is uploaded, e.g. `sceptre/68063a99bb6d95401d688d28f19ee412`)

## Details

The hook will zip the contents of the directory and upload it as
`sceptre/MD5HASH` to the S3-bucket, with `MD5HASH` being md5 hash of the zip
file content.

When zipping all files will be given a fixed modification time, so that only
the contents of the files are used to determine the upload file and cause
invalidation on changes.
