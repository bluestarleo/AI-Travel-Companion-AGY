# 1
Create me a monorepo scaffolding:

client/ that is a Next.js app for this travel company app that uses the src/ directory, React, Typescript, Tailwind
worker/ that is an empty directory for now

🧠 What the person is asking for
They want you to set up the initial folder structure (scaffolding) of a monorepo with two parts:
1. client/
This is a frontend application
Specifically:

Built with Next.js (React framework)
Uses:

✅ React
✅ TypeScript
✅ Tailwind CSS


Uses a src/ folder structure (common best practice)

👉 So this is the main web app for a travel company.

2. worker/
This is:

Just an empty directory for now

👉 Likely intended for:

background jobs
APIs
data processing
queue workers

But nothing is implemented yet.

🏗️ What “monorepo scaffolding” means here
They are NOT asking for full code yet.
They are asking for the initial structure of the repo — like a skeleton.


# 2
Put together an artifact documenting the Wikipedia geolocation search API that can take a list
of coordinates and a number of results and turn it into an array of articles that are near those
coordinates with some radius filtering the results. I want to use this to find points of interest
around my coordinates. Put together an artifact describing what this API does and include a
sample curl request on how it works and how I can test it. Run it for me so that I can see some
of the examples of it working. |

请制作一份关于 Wikipedia 地理定位搜索 API 的说明文档。该 API 能够接收一组坐标和结果数量参数，并返回位于这些坐标附近（在指定半径范围内）的条目列表。我希望利用它来查找自身坐标附近的兴趣点。请在文档中描述该 API 的功能，并提供一个示例 `curl` 请求，以展示其工作原理及测试方法。同时，请实际运行该 API，让我看看具体的运行结果示例。
wikipedia_geosearch_api_zh.md
wikipedia_geosearch_api.md

# 3 Create wikipedia_util.py in worker directory
now make a util in Python in the worker directory that takes in
coordinates, a radius, and a max search results arg. Just make the util.
现在，在 `worker` 目录下用 Python 编写一个工具函数，该函数接收坐标、半径以及最大搜索结果数量作为参数。只需编写这个工具函数即可。
File Location
wikipedia_utils.py


# 4 Create DB 
Now make a database directory that has a SQLite database with two tables. I want to store a
list of Wikipedia articles with their coordinates and some details that we get in the API and
associate each point of interest with a group. The group should be something like a city. So if I
put in Rome as a city, I should have many entries of articles associated with that city. Tell me
how I can make and provision this database.|
现在，请创建一个包含 SQLite 数据库的目录，其中需包含两张数据表。我希望存储一份维基百科（Wikipedia）条目列表，其中包括通过 API 获取的坐标及相关详情，并将每个“兴趣点”与一个“组”关联起来。这个“组”应当代表某种类别，例如城市；也就是说，如果我指定“罗马”作为城市，数据库中就应包含许多与该城市相关联的条目记录。请告诉我该如何创建并构建这个数据库。
I have created a new database/ directory in your monorepo containing:

Schema definitions: 
schema.sql
Initialization & seeding script: 
init_db.py
 (which I ran to provision travel_app.db with sample data for Rome and Paris).

 # 5 Create worker agent.py with antigravity sdk, wikipedia geosearch api and sql db utils
 create an antigravity sdk agent python script in the worker directory that takes in a city name as a script argument and runs the antigravity sdk to populate the sql db with article entries for that city. it should have a custom tool that uses the Wikipedia quey tool and have a system prompt that tells it that its goal is to find interesting articles for that city and add it to the sql db (specfy the path and how to add items to the db)

 在 `worker` 目录下创建一个使用 Antigravity SDK 的 Python 脚本（Agent）。该脚本应接收城市名称作为参数，并运行 Antigravity SDK，将关于该城市的文章条目写入 SQL 数据库。脚本需包含一个利用维基百科（Wikipedia）查询工具的自定义工具，并配置系统提示词（System Prompt），明确其目标是查找关于该城市的有趣文章并将其存入 SQL 数据库（需指定数据库路径及数据写入方式）。

 # 6 Run python agent.py with arg San Diego to populate the DB with points of interest for San Diego.

run the agent.py to populate the DB with the city: San Diego, let's populate 10-15 points of interest

# 7 UI design
Let's build our travel companion UI. It should have three main
pages:
- Homepage: Browser the available groups that are in the sql DB
- City page: show a sidebar of articles / points of interest on the left. Show a
map with pins for all the locations. Clicking on a pin should show a popup of
the city to read a bit more. Clicking this would bring up the article page
- Article page: Show all information about that particular point of interest
using the Wikipedia API


