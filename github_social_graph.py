from github import Github
from py2neo import Graph, Node, Relationship

# AutoTrader UK github enterprise 
g = Github(user_name, password, "https://github.atcloud.io/api/v3")
org = g.get_organization("AutoTrader") 
repos = org.get_repos()
repo_set = set()
dev_set = set()
graph = Graph()
graph.delete_all()

for repo in repos[0:100]:
    repo_node = Node()
    if repo.id not in repo_set:
        repo_set.add(repo.id)
        repo_node.labels.add("REPO")
        repo_node.properties["repo_name"] = repo.name
        graph.create(repo_node)
        print(repo.name)
    else:
        repo_node = graph.find_one("REPO", "repo_name", repo.name)

    # create parent Relationship
    if(repo.parent is not None):
        parent_node = Node()
        if repo.parent.id not in repo_set:
            repo_set.add(repo.parent.id)
            parent_node.labels.add("REPO", "PARENT_REPO")
            parent_node.properties["repo_name"] = repo.parent.name
            graph.create(parent_node)
        else:
            parent_node = graph.find_one("PARENT_REPO", "repo_name", repo.name)
            
        repo_parent_rel = Relationship(parent_node, "PARENT", repo_node)
        graph.create(repo_parent_rel)

    # create dev nodes
    for dev in repo.get_collaborators():
        dev_node = Node()
        if dev.id not in dev_set:
            dev_set.add(dev.id)
            dev_node.labels.add("DEV")
            dev_node.properties["dev_name"] = dev.name
            graph.create(dev_node)
        else:
            dev_node = graph.find_one("DEV", "dev_name", dev.name)

        repo_dev_rel = Relationship(dev_node, "CONTRIBUTES", repo_node)
        graph.create(repo_dev_rel)
        print("---> " + dev.name)

cypher = graph.cypher
cypher.execute("MATCH (d:DEV)-[:CONTRIBUTES]->(m)<-[:CONTRIBUTES]-(coDevs:DEV) " +
                   "CREATE (coDevs)-[:KNOWS]->(d)")
