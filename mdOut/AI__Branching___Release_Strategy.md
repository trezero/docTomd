---
title: "AI+ Branching & Release Strategy"
source_file: "AI__Branching___Release_Strategy.doc"
converted_date: "2025-09-17T11:24:59.204645"
format: "markdown"
---

# AI+ Branching & Release Strategy

- Overview
- Repos=itory Structure
- Versio=ning Strategy
- Branching =Model
- Devel=opment Workflow
- Release Pr=ocess
- Bug Managem=ent
- Hotfixes
- Automation=

# Overview

The AI+ project employs a fork-based development model that has proven s=uccessful across numerous large-scale open source projects. This approach p=rioritizes code quality, maintainability, and scalability while providing c=lear audit trails and predictable release cycles.

Our branching strategy centers around keeping the upstream repository cl�n and purpose-built. Rather than cluttering the main repository with deve=lopment branches, feature branches, and experimental work, we maintain only= the essential branches needed for production releases. All development wor=k occurs on personal forks, which developers maintain independently. This s=eparation ensures that the upstream repository serves as a reliable source =of truth for production-ready code.

The model emphasizes peer review as a fundamental quality gate. Every li=ne of code that enters the upstream repository must pass through the pull r=equest process, where it receives scrutiny from other team members. This re=quirement applies universally, including emergency situations where the nat=ural inclination might be to bypass review processes. Experience has shown =that even in crisis situations, the few extra minutes required for code rev=iew prevent far more problems than they cause.

During active release processes, we implement a complete freeze on mergi=ng to the main branch. This freeze serves multiple purposes: it provides st�ility during the critical release preparation period, ensures that releas=e branches contain exactly the intended code, and eliminates the confusion =that can arise from parallel development activities. While this might seem =restrictive, the practice has proven essential for maintaining release qual=ity and predictability.

The strategy acknowledges that bugs often affect multiple releases simul=taneously. Rather than attempting to manage a single fix across multiple br=anches, we create separate JIRA tickets for each affected release. This app=roach provides clear tracking, enables different fix approaches for differe=nt releases when necessary, and ensures that testing and deployment activit=ies are properly coordinated across all affected versions.

# Repository =Structure

The upstream repository maintains a minimal branch structure that reflec=ts only the essential long-term branches needed for production support. The= main branch serves as the primary development trunk, always containing the= latest stable development code. This branch represents the next release ca=ndidate and should remain in a deployable state at all times.

Release branches are created when the team decides to prepare a specific= version for production deployment. These branches follow the naming conven=tion `release/<version>` and include examples such as release/1.0, `release/2.0`, and `release/2.1. Each release branch represents a supported production version and remain=s active for the entire lifecycle of that release, receiving security updat=es, critical bug fixes, and other maintenance activities as needed.`

Personal forks contain the full spectrum of development work. Each devel=oper maintains their own fork of every repository they work with, and these= forks serve as the staging area for all development activities. Topic bran=ches within these forks follow descriptive naming patterns that include the= JIRA ticket identifier and a brief description of the work. Feature branch=es might be named `feature/AI-1234-user-authentication`, while b=ug fixes use the pattern `bugfix/AI-5678-memory-leak-fix`. For c=ritical issues requiring immediate attention, hotfix branches follow the pa=ttern `hotfix/AI-9999-security-patch`.

The fork structure provides developers with complete freedom to experime=nt, create intermediate commits, and maintain whatever branch organization =works best for their individual workflow. Since this work occurs entirely w=ithin personal forks, it does not impact other team members or pollute the =upstream repository with development artifacts.

# Versioning S=trategy

AI+ employs a comprehensive versioning system that tracks both developme=nt activities and release milestones through a unified format. The primary =version format follows `MAJOR.MINOR.PATCH-BUILD` where each comp=onent serves a specific purpose in tracking the evolution of the codebase a=nd coordinating release activities.

The MAJOR version increments for significant changes or breaking updates= that fundamentally alter the system's behavior or require substantial cust=omer migration efforts. These increments typically coincide with major arch=itectural changes, API breaking modifications, or significant feature overh=auls that impact backward compatibility. Major version changes signal to us=ers that they should expect substantial differences and may need to update =their integration approaches.

The MINOR version increments for new features that maintain backward com=patibility with existing functionality. These changes expand the system's c=apabilities without disrupting existing integrations or requiring customer =code modifications. Minor version increments represent the planned feature =releases that deliver new value while preserving the stability that existin=g users depend on.

The PATCH version increments for bug fixes, security updates, and small =improvements that do not introduce new functionality. These changes focus o=n maintaining and improving the reliability, performance, and security of e=xisting features. Patch releases provide critical updates that users can ad=opt with confidence that their existing integrations will continue to funct=ion unchanged.

The BUILD component is automatically incremented by TeamCity on each bui=ld and provides fine-grained tracking of development activities between for=mal releases. This automatic incrementation ensures that every build receiv=es a unique identifier, enabling precise tracking of which specific build c=ontains particular changes or fixes. The build number serves the developmen=t team's need to identify specific versions during testing, debugging, and �ployment activities.

Only the BUILD segment receives automatic modification by the build syst=em. The MAJOR, MINOR, and PATCH components require manual updates by the de=velopment team based on the nature and scope of the changes being released.= This manual control ensures that version increments reflect intentional de=cisions about the significance and impact of each release rather than arbit=rary automated changes.

During development phases, versions include a `-SNAPSHOT` suf=fix to indicate work in progress that has not yet been formally released. T=he snapshot designation helps differentiate between stable releases and dev=elopment builds, preventing confusion about which versions are appropriate =for production use. When a version is formally released, the snapshot suffi=x is removed to indicate that the version represents a stable, tested relea=se.

The versioning system integrates with the branching strategy to provide =clear identification of which code belongs to which release. Release branch=es use the target release version in their names, such as `release/2.1=.0`, creating a direct correlation between the branch structure and t=he versioning scheme. This correlation simplifies navigation between differ=ent versions and helps team members understand the relationship between bra=nches and releases.

# Branching Model<=/h1>

The main branch serves as the authoritative source for the next release =under development. All feature development ultimately targets this branch, =and it maintains a state where it could theoretically be released at any ti=me. This requirement drives discipline in the development process, as teams= must ensure that incomplete features either remain disabled through featur=e flags or are developed in a way that does not compromise the overall syst=em stability.

Protection of the main branch occurs through repository settings that re=quire pull request reviews before any code can be merged. This protection c=annot be bypassed, even by repository administrators, ensuring that all cod=e changes receive appropriate scrutiny regardless of urgency. The branch al=so requires that all status checks pass before merging, providing an additi=onal quality gate through automated testing and validation processes.

Release branches are created at the point when the team decides that the= main branch contains all the features intended for a specific release. The= timing of this decision typically occurs one to two weeks before the inten�d release date, providing time for final testing and stabilization activi=ties. Once created, the release branch becomes the authoritative source for= that specific version, and all subsequent work related to that release tar=gets the release branch rather than main.

The creation of a release branch triggers the freeze of the main branch =for merging activities. This freeze ensures that the release branch contain=s exactly the intended code and prevents the confusion that could arise fro=m parallel development activities. During the freeze period, developers con=tinue their work on feature branches, but these branches cannot be merged u=ntil the release process completes and the freeze lifts.

Fork management requires developers to maintain personal forks that stay= synchronized with the upstream repository. This synchronization should occ=ur daily and involves pulling the latest changes from upstream branches and= pushing those updates to the corresponding branches in the personal fork. =Regular synchronization prevents the accumulation of large divergences that= can make merge conflicts more difficult to resolve.

Topic branch creation follows specific patterns based on the type of wor=k being performed. Feature branches are created from the main branch and re=present new functionality intended for the next release. Bug fix branches m=ay be created from either the main branch or a specific release branch, dep=ending on where the bug was discovered and which versions require the fix. =Hotfix branches are always created from the release branch that requires th=e emergency fix.

The lifecycle of a topic branch begins with creation from the appropriat=e base branch, continues through development and testing activities, progre=sses through the pull request and review process, and concludes with the de=letion of the branch after successful merge. This lifecycle ensures that to=pic branches serve their intended purpose without accumulating as long-term= maintenance burdens.

# Development= Workflow

See: [Using Git](https://perifery.atlassian.net/wiki/wiki/spaces/AI/pages=/3642195983/Using+Git)

Daily development begins with synchronization activities that ensure the= developer's fork reflects the current state of the upstream repository. Th=is synchronization involves checking out the main branch, pulling the lates=t changes from the upstream main branch, and pushing those changes to the o=rigin main branch in the personal fork. If the developer is working with re=lease branches, the same synchronization process applies to those branches =as well.

Topic branch creation requires careful consideration of the appropriate �se branch. Features intended for the next release should branch from main=, while fixes for current releases should branch from the appropriate relea=se branch. The choice of base branch determines where the eventual pull req=uest will target and affects how the changes integrate with ongoing develop=ment activities.

The development process emphasizes atomic commits that represent complet=e, logical changes to the codebase. Each commit should be self-contained an=d should not leave the system in a broken state. Commit messages follow a s=tandard format that includes the JIRA ticket identifier and a clear descrip=tion of the change. This discipline in commit creation pays dividends durin=g debugging activities, code reviews, and historical analysis of the codeba=se.

Before submitting a pull request, developers must ensure their topic bra=nch remains current with its base branch. This requirement involves rebasin=g the topic branch against the latest version of the base branch and resolv=ing any conflicts that arise. The rebase process also provides an opportuni=ty to clean up the commit history by squashing related commits or reorderin=g commits to improve logical flow.

Pull request submission involves creating a detailed description that ex=plains the purpose of the changes, the approach taken to implement them, an=d any testing that has been performed. The description should reference the= relevant JIRA tickets and provide sufficient context for reviewers to unde=rstand the changes without requiring extensive investigation. Screenshots, =test results, and other supporting documentation enhance the quality of the= pull request and facilitate more effective reviews.

The code review process serves as a critical quality gate that ensures a=ll changes meet the project's standards for functionality, maintainability,= and security. Reviewers examine not only the correctness of the implementa=tion but also its alignment with architectural principles, its impact on pe=rformance, and its potential for introducing technical debt. The review pro�ss is collaborative, with reviewers providing constructive feedback and d=evelopers responding thoughtfully to suggestions.

Integration of approved changes occurs through the "squash and merge" st=rategy, which combines all commits from the topic branch into a single comm=it on the target branch. This approach provides a clean history on the main= and release branches while preserving the detailed commit history within t=he pull request for future reference. After successful integration, the top=ic branch is deleted to prevent accumulation of stale branches.

Multi-repository coordination becomes necessary when features span multi=ple repositories or when changes in one repository depend on changes in ano=ther. This coordination requires careful planning of the development sequen�, creation of matching topic branches across repositories, and synchroniz� timing of pull request submission and merging. Feature flags can help ma=nage dependencies by allowing partial functionality to be merged while rela=ted changes are still in development.

# Release Process<=/h1>

Release preparation begins several weeks before the intended release dat=e with planning activities that define the scope of the release and establi=sh the timeline for various milestones. The planning process identifies whi=ch features will be included, which bugs must be fixed, and what testing ac=tivities will be required. This planning culminates in the creation of a re=lease milestone in JIRA that tracks all the work items intended for the rel�se.

Feature freeze occurs when the team determines that all intended feature=s have been developed and merged to the main branch. The timing of the feat=ure freeze depends on the complexity of the release and the amount of testi=ng required, but typically occurs one to two weeks before the intended rele=ase date. After the feature freeze, only bug fixes and stabilization work c=an be merged to the main branch.

The main branch freeze represents the transition from general developmen=t activities to focused release preparation. When the freeze begins, all pe=nding pull requests targeting the main branch are either merged quickly or �ferred to the next release. The freeze announcement goes out to all team =members through multiple channels to ensure awareness and compliance.

Release branch creation occurs immediately after the main branch freeze =and involves creating the `release/<version>` branch from =the current head of the main branch. This creation happens simultaneously a=cross all repositories to ensure consistency. The new release branch become=s the focus of all release-related activities, including bug fixes, testing=, and final preparations.

Version number updates occur within the release branch to reflect the tr=ansition from development versions to release versions. This process involv=es removing the `-SNAPSHOT` suffix from build versions and updat=ing release version numbers to their final values. These changes are commit=ted to the release branch and represent the first commits that differentiat=e the release branch from main.

Staging deployment uses the release branch to deploy to staging environm=ents where final testing occurs. This testing includes not only functional =validation but also performance testing, security scanning, and integration= testing with external systems. Any issues discovered during this testing r=esult in bug fixes that target the release branch.

Release candidate tagging provides waypoints during the stabilization pr=ocess and enables specific builds to be deployed for testing. Release candi�tes follow the naming pattern `v2.1.0-rc1`, `v2.1.0-rc2, and so forth. Each release candidate represents a potential final re=lease and receives thorough testing before the decision to either release i=t or create another candidate.`

Production release occurs when the team determines that a release candid=ate has passed all required testing and approval processes. The final relea=se tag removes the release candidate suffix and represents the official ver=sion that will be deployed to production environments. The tag creation tri=ggers deployment processes and marks the formal completion of the release.<=/p>

Post-release activities include unfreezing the main branch, updating ver=sion numbers for the next development cycle, and cherry-picking any critica=l fixes from the release branch back to main. The release branch remains ac=tive to support ongoing maintenance of that release version, but the main b=ranch returns to normal development activities.

Release branch maintenance continues throughout the supported lifecycle =of each release. This maintenance includes applying security patches, fixin=g critical bugs, and making other necessary updates. Each maintenance updat=e results in a new patch version tag and follows the same testing and appro=val processes as major releases.

# Bug Management

The management of bugs that affect multiple releases requires a systemat=ic approach that ensures proper tracking, coordinated development, and sync=hronized deployment across all affected versions. When a bug is discovered =that impacts multiple release branches and the main development branch, the= team creates separate JIRA tickets for each affected version rather than a=ttempting to manage the fix through a single ticket.

This multi-ticket approach provides several advantages over single-ticke=t management. Each ticket can track the specific testing requirements for i=ts target version, the deployment timeline for that version, and any versio=n-specific considerations that might affect the fix implementation. The app=roach also provides clear accountability for each version and ensures that =the fix receives appropriate attention across all affected releases.

JIRA ticket creation follows a consistent naming pattern that identifies= the affected version and links related tickets together. For a security vu=lnerability affecting releases 1.0, 1.1, 2.0, and the main branch, the team= would create tickets such as "AI-5001: Fix XSS vulnerability \(release/1.0\)=", "AI-5002: Fix XSS vulnerability \(release/1.1\)", "AI-5003: Fix XSS vulner�ility \(release/2.0\)", and "AI-5004: Fix XSS vulnerability \(main\)". These =tickets are linked in JIRA to show their relationship and ensure coordinate=d management.

The development approach for multi-release fixes depends on the nature o=f the bug and the differences between the affected versions. For bugs that �n be fixed identically across all versions, the team typically develops t=he fix on the oldest affected release branch and then cherry-picks the chan=ges to newer versions. This approach ensures that the fix works correctly o=n the most constrained version and typically adapts well to newer versions =with minimal modification.

For bugs that require different approaches across versions due to archit�tural changes or other differences, the team may develop separate fixes f=or each version. This approach requires more development effort but ensures= that each fix is optimized for its target version and does not introduce u=nnecessary complexity or risk.

Testing requirements for multi-release fixes are more extensive than sin=gle-version fixes because the team must verify the fix across all affected =versions and their respective deployment environments. Each version receive=s independent testing to ensure that the fix resolves the issue without int=roducing regressions. The testing may reveal that the fix requires modifica=tion for specific versions, leading to version-specific commits within the =overall fix effort.

Deployment coordination becomes critical for security fixes and other ur=gent updates that affect multiple production versions. The team typically d=eploys fixes to older versions first, as these represent the highest risk d=ue to their longer exposure to the vulnerability. Staggered deployments all=ow monitoring of the fix impact and provide opportunities to halt the deplo=yment process if unexpected issues arise.

The classification of bugs affects how they are prioritized and managed �ross multiple releases. Critical bugs, including security vulnerabilities=, data corruption risks, and system stability issues, receive immediate att=ention across all affected versions. High priority bugs may be included in =the next scheduled maintenance release for each affected version. Standard =bugs might only be fixed in currently active release branches, with older v=ersions receiving the fix only if specifically requested by customers.

Communication about multi-release fixes requires careful coordination to= ensure that all stakeholders understand which versions are affected, when =fixes will be available, and what actions they may need to take. Release no=tes for each affected version document the fix and its impact, while securi=ty advisories provide additional detail for security-related fixes.

- * *

# # Hotfixes

Emergency situations require expedited processes while maintaining the q=uality and review standards that protect the codebase and production system=s. The definition of an emergency includes security vulnerabilities that po=se immediate risk, data corruption or loss scenarios, system outages that a�ect customer operations, and compliance violations that could result in r=egulatory action.

When an emergency is declared, the response begins with rapid assessment= to understand the scope of the problem, identify affected systems and vers=ions, and determine the appropriate response strategy. This assessment driv=es decisions about which release branches require fixes, what testing can b=e performed within the available timeframe, and how to coordinate communica=tions with stakeholders.

Hotfix branch creation follows the same patterns as normal bug fixes but= with compressed timelines and elevated priority. The hotfix branch is crea=ted from the appropriate release branch, and development begins immediately= with focus on the minimal change necessary to resolve the emergency. The p=rinciple of minimal change is crucial during emergencies because it reduces= the risk of introducing additional problems while addressing the immediate= crisis.

Code review remains mandatory even during emergency situations. While th=e review process may be expedited through immediate reviewer availability a=nd focused review scope, the requirement for peer review cannot be bypassed=. Experience has consistently shown that emergency situations are precisely= when human error is most likely, making the extra set of eyes provided by =code review invaluable for preventing additional problems.

The expedited review process may involve verbal pre-review where the dev=eloper explains the changes to a reviewer before submitting the pull reques=t, immediate reviewer assignment to ensure prompt attention, and focused re=view scope that concentrates on the correctness of the emergency fix rather= than broader code quality considerations. Despite these accommodations, th=e review must still verify that the fix addresses the emergency without int=roducing new risks.

Testing during emergencies balances speed with safety by focusing on the= most critical validation activities. This testing includes verification th=at the fix resolves the emergency situation, confirmation that the fix does= not break core system functionality, and validation that the fix can be sa�ly deployed to production environments. Automated testing provides rapid �edback, while manual testing focuses on the specific emergency scenario a=nd related functionality.

Emergency deployment follows expedited processes that may bypass normal =change management procedures while maintaining essential safety checks. The= deployment process includes verification of the deployment target environm=ent, confirmation that rollback procedures are available and tested, and mo=nitoring setup to detect any issues introduced by the emergency fix.

Communication during emergencies requires regular updates to stakeholder=s about the response progress, estimated resolution timeline, and any actio=ns they may need to take. The communication plan includes immediate notific=ation of key stakeholders, regular status updates throughout the response p=rocess, and post-resolution communication about the final outcome and any f=ollow-up actions required.

Post-emergency activities include conducting a thorough post-mortem to u=nderstand how the emergency occurred, what response processes worked well, =and what improvements could prevent similar situations or improve response �fectiveness. The post-mortem results in specific action items that addres=s both the underlying cause of the emergency and any process improvements i�ntified during the response.

The application of emergency fixes to multiple release branches follows =the same multi-release bug management processes but with compressed timelin=es and coordinated deployment schedules. All affected versions receive the =emergency fix, but deployment may be staggered to allow monitoring of the f=ix impact across different environments and customer configurations.

# Automation

The AI+ project is currently developing its automation and tooling infra=structure to support the branching and release processes described in this =guide. Multiple automation platforms and tools are being evaluated and inte=grated to create a comprehensive development and deployment pipeline.

**Development Status: Work in Progress**

The following areas are currently under active development:

- **Build System Integration** : Evaluating TeamCity for prima=ry build orchestration and artifact management • **Source Con=trol Automation** : Implementing GitHub Actions for pull request vali�tion and branch management

- **Release Coordination** : Developing scripts and tooling fo=r multi-repository release branch creation and version management •= **Deployment Pipeline** : Designing automated deployment proce=sses for staging and production environments • **Quality Gate=s** : Establishing automated testing, security scanning, and code qua=lity checks • **Notification Systems** : Integrating Sl�k, email, and JIRA notifications for development lifecycle events �=A2 **Monitoring and Alerting** : Implementing branch health mo=nitoring and build failure detection • **Repository Managemen=t** : Automating branch protection rules, cleanup processes, and main=tenance activities

The automation strategy will focus on reducing manual effort, improving =consistency, and minimizing human error while maintaining the quality and r=eview standards outlined in this guide. As these tools and processes mature=, this section will be updated with comprehensive guidance on their usage a=nd integration with the overall development workflow.

Teams should continue following the manual processes described throughou=t this guide while the automation infrastructure is being developed and tes=ted. The fundamental branching and release strategies remain unchanged rega=rdless of automation status, and the manual processes provide the foundatio=n upon which automation will be built.