# Magnet

## GOAL
Create a solution named "Magnet" as a RSS news reader enhanced by generative AI

## FEATURES

### For web user

- Manage account and settings (language, ...)
- Discover and subscribe to available RSS sources
    - Research by filter : category
    - Recommendation by popularity
    - Manage favorite catagories
    - Manage subscription to RSS
- RSS news viewer
    - Filter management : date, not read, by catagory
    - Different list display : tabular, short tile
    - RSS news content preview for a selected item
- RSS news digest
    - Summary per period (today, last x days)
    - Create a summary of the most important news per catagory in the period
- Chatbot
    - user can ask question regarding the news, getting a response and a list of corresponding news
- Graph view
    - Represent a topic with a graph of entities and relation between them
    - Each entity has a summary


### For solution admin

- Manage the list a available RSS sources
    - Research on internet for RSS sources list per category, then select RSS sources to import (no duplicate)
    - Automatic catagory organization with Generative AI (in a tree of cateory / sub category)
- Monitoring Usage 
    - Dashboard for solution usage : number of user, top subscribed RSS sources, ...

### For external solution

- Create a MCP service for external intégration


## TECHNICAL STACK

- Front end : shadcn
- Backend : python  FastAPI
- Agentic : pydantic
- database : pgvector and/or neo4j
- GraphRag framework : Zep Graphiti