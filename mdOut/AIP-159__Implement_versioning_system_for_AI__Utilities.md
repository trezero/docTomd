---
title: "AIP-159: Implement versioning system for AI+ Utilities"
source_file: "AIP-159__Implement_versioning_system_for_AI__Utilities.doc"
converted_date: "2025-09-17T11:24:59.126193"
format: "markdown"
---

# AIP-159: Implement versioning system for AI+ Utilities

It’s high-time we implement a versioning system to keep =ourselves straight.

To implement a versioning system for Python projects on GitHub with auto=-incremented versioning, TeamCity builds, and AWS ECR deployment, here�=80�s a detailed step-by-step guide:

# Versioning Strategy

For AI+ projects, we will use the basic semantic versioning practices \(MAJOR.MINOR.PATCH\) with an additional **build number <=/strong>. We will track :**

- **MAJOR** for new releases a scoped release

- **MINOR** for new features within

- **PATCH** for bug fixes within a release.

- **BUILD** for each TeamCity build

MAJOR, MINOR, and PATCH releases will be manually committed with a PR. I=t will be the job of the committer and pull request viewer to ensure the ve=rsioning info is updated as part of the review process. BUILD numbers will � managed by the TeamCity CI/CD pipeline.

# AI=+ Utilities

Each project will have a setup.py: We will include a \_\_version\_\_ variabl=e that reads from a version file.

from setu=ptools import setup# Read version from a version filewith open("VERSION") as version_file: version = version_file.read().strip()setup( name="your_project", version=version, # other parameters)

The version file itself is very basic.

# Vers=ioning follows the format: MAJOR.MINOR.PATCH-BUILD# Only one line should be present in this file, e.g., 1.0.0-01.0.0-0

# TeamCi=ty

As part of the build process, we will use a Python script to update the =version and build number in a `VERSION` file. Here’s an =example script:

import re# File name where the current version is storedVERSION_FILE = "VERSION"def increment_version(version_file=VERSION_FILE): """ Reads the current version from the VERSION file, increments the build n=umber, and writes the new version back to the VERSION file. Version format: MAJOR.MINOR.PATCH-BUILD - MAJOR, MINOR, and PATCH should be updated manually for significant re=leases. - BUILD is auto-incremented on every build. """ # Open and read the current version with open(version_file, "r") as file: version = file.read().strip() # Use regular expressions to parse version components # Assumes format: MAJOR.MINOR.PATCH-BUILD major, minor, patch, build = map(int, re.match(r"(\d+)\.(\d+)\.(\d+)-=(\d+)", version).groups()) # Increment the build number for the next version build += 1 new_version = f"{major}.{minor}.{patch}-{build}" # Write the new version back to the VERSION file with open(version_file, "w") as file: file.write(new_version) # Display the updated version print(f"Updated version to {new_version}")# Entry point for the script, which increments the versionif __name__ == "__main__": increment_version()

We will run this script in TeamCity’s build steps to update the =version before every build.

In the TeamCity build configuration:

1. Run the version update script as a step.

2. Commit and tag the updated version.

### # TeamCity Build Steps:

1. **Increment Version Step** : Run the versioning script above=.

2. **Git Commit Step** :

git con=fig user.email "teamcity@datacore.com"git config user.name "TeamCity"git commit -am "Auto-incremented version to $(cat VERSION)"

3. **Git Tag Step** :

VERSION=3D$(cat VERSION)git tag -a "v$VERSION" -m "Build $VERSION"git push origin --tags

## # Integrate Docker Build and Push to AWS ECR

In TeamCity, add steps to:

1. **Build Docker Image** : Use the version as a tag.

VERSION=3D$(cat VERSION)docker build -t aiplus/notification-api:$VERSION .

2. **Push to ECR** :

# Log i=n to ECRaws ecr get-login-password --region us-east-1 | docker login --username AWS= --password-stdin <accountId>.dkr.ecr.us-east-1.amazonaws.comdocker tag aiplus/notification-api:$VERSION <accountId>.dkr.ecr.your-=region.amazonaws.com/aiplus/notification-api:$VERSIONdocker push <accountId>.dkr.ecr.your-region.amazonaws.com/aiplus/noti=fication-api:$VERSION

## # AWS ECR<=/h3>

To keep storage manageable, we should implement a lifecycle policy in AW=S ECR to delete old images.