# Change specification
Update all the documentation : prd, architecture and backlog (epic, story, task)

## Functional changes :
- simplify project configuration : they are all project in development with claude code and the bmad method
  so the template is confusing maybe find another naming: it's represent different part of the documentation which can be visualized or give access to specific features
  so project should have a normalize structure of directory for documentation : /.bmad-core, /.claude, /docs (bmad generated specification)
- So it's important that the tool is focus ton support in process to review by the user the specification in the documents before running to the next step
    - see the history of version based on github commit change
    - when exploring the documentation from the lastest version : can have a review process to validate or not to go to the next step (managed externally in claude code)
      in the review the user can validate to go to the next step (ex: start epic development) or rerun the last step with required changes
- In development cycle : the validation process with DocGraph is used to validate to merge or not a specific devlopment branch to the main branch
- Additional import feature of the documentation : use markdown organization
    - table of content : with markdown Headings tree
    - Links between document files, with often an index file (ex: prod/index.md) 

## Technical changes :
- no need any interaction with AWS (cognito, ...), the MVP will be a docker application first running locally
- no s3 storage in the MVP, mapped volume in docker for persistency in local inside the project structure
- just a basic user management, register and login with an email (later maybe admin for user access to the project)
- no need github authentification, access to public repo accessible with git clone

## process in claude code
THIS IS NOT MANAGED IN THE APPLICATION, BUT BY SOMEONE DIRECTLY IN CLAUDE CODE
- Apply the expected changes, store them in /review and update the status after changes are made
  Information will be added in the next commit after changes, for the next review with the DocGraph application
- Insure consistency over all the documentation : prd, architecture, front-end-spec, backlog
    The product onwer can delegate to any subagent if necessary : architect, ux-expert, ...
    Then Run Master Checklist by the product owner
- when develop a new cycle of development create a branch 