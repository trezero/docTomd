---
title: "Release Process"
source_file: "Release_Process.doc"
converted_date: "2025-09-17T11:24:59.442242"
format: "markdown"
---

# Release Process

AI+ RELEASE PROCESS — RCs, PROMOTION, AND PATCHES

\(Updated for single “release/X.Y.Z” branch per version += optional base\_ref\)

=========================3D=========================3D======================

1. OVERVIEW & CONVENTIONS

- * *

- One branch per version line: release/X.Y.Z

\(Example: release/1.2.0, release/1.2.1, etc.\)

- RCs and final builds are tags: vX.Y.Z-rc1, vX.Y.Z-rc2, �=80�, vX.Y.Z

\(Example: v1.2.0-rc1, v1.2.0-rc2, v1.2.0\)

- Normalization: RCs DO NOT create separate branches.

All RCs for 1.2.0 live on the same branch: release/1.2.0

- base\_ref \(optional\):

- A tag/branch/commit to start from \(e.g., v1.1.1 or release/1.2.0\).

- If omitted, new lines default to main/master.

- For patch lines, ALWAYS start from the last final tag \(e.g., v1.2.0\).

- Final tags are immutable. If a problem is found after promotion, bump th=e

PATCH version and start a new RC \(e.g., 1.2.1-rc1 from v1.2.0\).

# # **==============3D=========================3D==========**

# # **2\) PREREQUISITES** =

- GitHub CLI installed and authenticated \(gh auth login\).

- Org-level workflows live in the .github repo; build\_releases.sh calls:

gh workflow run create\_release.yml –repo workflow-intelligence-n=exus/.github

–ref cicd-integration

\(Change –ref if the workflow is on another branch.\)

- Required token/permissions are already wired as RELEASE\_WORKFLOW\_GITHUB\_=TOKEN.

# # **==============3D=========================3D==========**

# # =**3\) BUILD A NEW MINOR RELEASE CANDIDATE \(e.g., 1.2.0-rc1\)**

Default \(cut from main/master\):

./scripts/build\_releases.sh 1.2.0-rc1

Freeze at a specific point \(tag/branch/commit\):

./scripts/build\_releases.sh 1.2.0-rc1 <base\_ref>

Result:

- Creates/updates release/1.2.0

- Creates tag v1.2.0-rc1

During stabilization:

- Land fixes on release/1.2.0 \(via PRs or cherry-picks\).

- Re-spin RC as needed:

./scripts/build\_releases.sh 1.2.0-rc2

\(Do not pass base\_ref for re-spins; the workflow will reuse release/1.2.=0.\)

# # **==============3D=========================3D==========**

# # **4\) PROM=OTE A RELEASE CANDIDATE TO FINAL**

When the chosen RC \(e.g., rc2\) is approved:

./scripts/promote\_release.sh 1.2.0-rc2

Result:

- Creates final tag v1.2.0 \(immutable\)

# # **==============3D=========================3D==========**

# # **5\) PATCH A PROMOTED RELEASE \(e.g., produce 1.2.1-rc1 from v=1.2.0\)**

Start from the last final tag \(NOT from main\):

./scripts/build\_releases.sh 1.2.1-rc1 v1.2.0

Result:

- Creates/updates release/1.2.1

- Creates tag v1.2.1-rc1

Bring in only the required fixes \(example cherry-pick flow\):

git fetch –all –tags

git checkout release/1.2.1

git cherry-pick -x \[…\]

git push

If you added commits after v1.2.1-rc1 already exists, either:

- Move the RC tag \(allowed for RCs you control\):

git tag -d v1.2.1-rc1 && git push origin :refs/tags/v1.2.1-rc1

git tag -a v1.2.1-rc1 -m “Update RC after hotfixes”

git push origin v1.2.1-rc1

OR

- Create the next RC:

git tag -a v1.2.1-rc2 -m “Second RC”

git push origin v1.2.1-rc2

Promote when ready:

./scripts/promote\_release.sh 1.2.1-rcX

# # **==============3D=========================3D==========**

# # **6\) QUICK DECISION M=ATRIX**

- Start new minor line \(e.g., 1.3.0-rc1\):

./scripts/build\_releases.sh 1.3.0-rc1

\(No base\_ref → cut from main/master, or pass a freeze ref.\)

- Re-spin RC on same minor \(e.g., 1.3.0-rc2\):

./scripts/build\_releases.sh 1.3.0-rc2

\(Reuses release/1.3.0.\)

- Promote RC to final:

./scripts/promote\_release.sh 1.3.0-rcN

- Patch a promoted minor \(e.g., 1.3.1-rc1\):

./scripts/build\_releases.sh 1.3.1-rc1 v1.3.0

\(ALWAYS base from the last final tag.\)

# # **==============3D=========================3D==========**

# # **7\) BEST PRACTIC=ES & NOTES**

- Don’t merge main wholesale into a patch line; cherry-pick only w=hat you need.

- Projects that embed a version \(package.json, pyproject.toml, etc.\) must �

bumped on the release/X.Y.Z branch before publishing artifacts.

- Old RC-suffixed branches from before this policy \(e.g., release/1.1.1-rc=1\)

can be cleaned up once unused:

git push origin :release/1.1.1-rc1

# # **==============3D=========================3D==========**

# # **8\) FAQ**

Q: What exactly is base\_ref?

A: Any tag/branch/commit in the TARGET repo used as the starting point f=or the

release branch. Examples: v1.1.1, release/1.2.0, a specific SHA. If omit=ted,

new minor lines are cut from main/master.

Q: For RC re-spins, do I need base\_ref?

A: No. The workflow will switch to the existing release/X.Y.Z branch if =it

exists and use that head. \(It briefly checks out main/master first, then=

checks out and fast-forwards release/X.Y.Z.\)

Q: Can I promote more than once?

A: No. Final tags \(e.g., v1.2.0\) are immutable. If an issue is found aft=er

promotion, bump PATCH and start a new RC \(e.g., 1.2.1-rc1 from v1.2.0\).<=/p>

Q: Is it okay to move RC tags?

A: Yes, if your team controls the consumers. Delete and recreate the RC =tag at

the desired commit. Do NOT move final tags.

Q: Which branch of the .github repo runs the workflow?

A: build\_releases.sh uses –ref cicd-integration by default. Chan=ge it if your

workflow is on another branch.

Q: How do I verify what I’m building from?

A:

git tag -l v1.2.0

git show –no-patch –decorate v1.2.0

git branch -r –contains v1.2.0

git log –oneline v1.2.0..origin/main \# what changed on ma=in since final

Q: What if I need to freeze 1.2.0 earlier than current main?

A: Pass a base\_ref \(tag/branch/commit\) when creating 1.2.0-rc1:

./scripts/build\_releases.sh 1.2.0-rc1 <base\_ref>

# # **==============3D=========================3D==========**

# # **9\) NOTE**

A final \(e.g., 1.2.0\) can only be promoted once. If issues are found aft=er

promotion, bump the patch and start a new RC from the last final tag:

./scripts/build\_releases.sh 1.2.1-rc1 v1.2.0