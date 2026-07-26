.docs/research-collections-specification.md

 AIPubs.cloud

Research Collections Feature

Repository Architecture Specification



Version: 1.0

Feature: Research Collections

Purpose: Transform AIPubs.cloud into a collaborative research organization platform.



==================================================

OVERVIEW

========



Research Collections are the organizational foundation of AIPubs.cloud.



The concept:



"GitHub Organizations for research."



A Research Collection provides laboratories, universities, companies, and research groups with a branded environment to organize:



* Publications

* Projects

* Researchers

* Datasets

* Code repositories

* Research resources

* Announcements

* Discussions



Each collection becomes a living research hub.



Example:



Open Quantum Initiative



aipubs.cloud/org/open-quantum-initiative



==================================================

REPOSITORY STRUCTURE

====================



aipubs.cloud/



apps/



```

web/



    pages/



        index/



        publications/



        collections/



            [slug]/



                index.html



                papers.html



                projects.html



                members.html



                datasets.html



                repositories.html





        researchers/





    components/



        CollectionCard.js



        ResearchHeader.js



        PaperCard.js



        DatasetCard.js



        MemberCard.js



        RepositoryCard.js





    styles/





dashboard/



    collection-manager/



    publication-editor/



    member-management/



    analytics/

```



packages/



```

collections/



    collection-schema.json



    collection-engine.js



    permissions.js



    roles.js





publications/



    markdown-parser.js



    pdf-generator.js



    citation-engine.js



    metadata.js





search/



    indexer.js



    query.js



    ranking.js





identity/



    researcher-profile.js



    organization-profile.js

```



data/



```

collections/



    example-open-quantum-initiative/



        collection.json



        members.json



        papers.json



        projects.json



        datasets.json



        repositories.json





publications/





researchers/

```



api/



```

collections/



    create.js



    get.js



    update.js



    members.js





publications/





datasets/





repositories/

```



workers/



```

search-worker.js



publishing-worker.js



github-sync-worker.js



citation-worker.js

```



database/



```

schema.sql



migrations/



seed/

```



docs/



```

architecture.md



collections.md



publishing-guide.md



contributor-guide.md



api-reference.md

```



templates/



```

research-collection/



    collection.json



    README.md



    landing-page.md





publication/



    paper.md



    metadata.json

```



.github/



```

workflows/



    deploy.yml



    publish.yml



    validate.yml





ISSUE_TEMPLATE/

```



package.json



wrangler.toml



README.md



LICENSE



==================================================

COLLECTION DATA MODEL

=====================



File:



data/collections/{collection-slug}/collection.json



Example:



{

"id": "open-quantum-initiative",



"name": "Open Quantum Initiative",



"type": "research-lab",



"description":

"Advancing open quantum computing research",



"created":

"2026-07-26",



"visibility":

"public",



"links": {



```

"website": "",



"github": "",



"orcid": ""

```



},



"stats": {



```

"papers": 48,



"projects": 12,



"datasets": 8,



"repositories": 15,



"members": 21

```



}



}



==================================================

COLLECTION COMPONENTS

=====================



COLLECTION PROFILE



Displays:



* Organization name

* Logo

* Banner

* Description

* Research areas

* Website links

* Statistics



Example:



Open Quantum Initiative



Advancing open quantum computing research



Members: 21



Publications: 48



Projects: 12



Datasets: 8



Repositories: 15



==================================================

PAPERS MODULE

=============



Purpose:



Connect publications to research groups.



Features:



* Markdown publishing

* PDF export

* Citation metadata

* DOI support

* Version history

* Author attribution

* Discussion



Example:



Quantum Error Correction



Version:



2.1



Available:



PDF



Markdown



Citation



Dataset



Repository



==================================================

PROJECTS MODULE

===============



Purpose:



Organize active research efforts.



Project contains:



Name



Description



Status



Researchers



Publications



Repositories



Datasets



Milestones



Roadmap



Example:



Quantum Compiler Project



Status:



Active



Associated:



12 Papers



3 Repositories



4 Datasets



==================================================

MEMBERS MODULE

==============



Purpose:



Represent researchers and contributors.



Member profile:



Name



Biography



Research Areas



Publications



Repositories



ORCID



GitHub



Website



Roles:



Owner



Administrator



Editor



Researcher



Reviewer



Member



Visitor



==================================================

DATASETS MODULE

===============



Purpose:



Publish research data alongside publications.



Supported:



CSV



JSON



Parquet



Images



Archives



Scientific formats



Dataset metadata:



Title



Description



License



Version



Size



Authors



Associated papers



==================================================

REPOSITORY MODULE

=================



Purpose:



Connect research software.



Supported:



GitHub repositories



GitLab repositories



Other source repositories



Metadata:



Repository name



Description



Stars



License



Documentation



Releases



Commit activity



==================================================

API DESIGN

==========



Base:



/api/collections



GET



/api/collections



Returns public collections.



POST



/api/collections



Creates collection.



GET



/api/collections/{slug}



Returns collection information.



PUT



/api/collections/{slug}



Updates collection.



GET



/api/collections/{slug}/papers



Returns publications.



GET



/api/collections/{slug}/members



Returns members.



GET



/api/collections/{slug}/datasets



Returns datasets.



GET



/api/collections/{slug}/repositories



Returns repositories.



==================================================

DATABASE SCHEMA

===============



collections



id



slug



name



description



owner_id



logo_url



created_at



collection_members



collection_id



user_id



role



collection_publications



collection_id



publication_id



collection_projects



collection_id



project_id



collection_datasets



collection_id



dataset_id



collection_repositories



collection_id



repository_url



==================================================

SUBSCRIPTION ALIGNMENT

======================



FREE



Includes:



* Individual researcher profile

* Public publications

* One research collection

* Basic discovery



PRO ($9/month)



Includes:



* Multiple collections

* Enhanced researcher profile

* Analytics

* Custom branding



RESEARCH LAB ($39/month)



Includes:



* Unlimited members

* Organization branding

* Private drafts

* Team management

* Collection analytics



ENTERPRISE ($199+/month)



Includes:



* Custom domains

* Institutional accounts

* Advanced analytics

* SSO

* Dedicated support



==================================================

MVP IMPLEMENTATION ORDER

========================



Phase 1:



Collection creation



↓



Collection landing page



↓



Add members



↓



Attach publications



↓



Attach repositories



↓



Public research hub



Phase 2:



Datasets



Analytics



Permissions



Custom branding



Phase 3:



Peer review



Citation analytics



AI research discovery



Knowledge graphs



Collaboration tools



==================================================

VISION

======



Research Collections transform AIPubs.cloud from a publication repository into a complete research infrastructure platform.



The goal:



A unified home where researchers, organizations, papers, datasets, and software projects exist as connected knowledge objects.



AIPubs.cloud becomes the operating layer for open research.
