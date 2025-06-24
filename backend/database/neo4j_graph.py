# backend/database/neo4j_graph.py

from neo4j import GraphDatabase
import os

# Neo4j Connection
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "your_password_here"  # tb changed

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Create a user node


def create_user(tx, username):
    tx.run("MERGE (u:User {name: $username})", username=username)

# Create a post node


def create_post(tx, post_id, content, score, topic):
    tx.run("""
    MERGE (p:Post {id: $post_id})
    SET p.content = $content, p.score = $score, p.topic = $topic
    """, post_id=post_id, content=content, score=score, topic=topic)

# Create a forum node


def create_forum(tx, forum_name):
    tx.run("MERGE (f:Forum {name: $forum_name})", forum_name=forum_name)

# Create relationships


def create_relationships(tx, username, post_id, forum_name):
    tx.run("""
    MATCH (u:User {name: $username}), (p:Post {id: $post_id}), (f:Forum {name: $forum_name})
    MERGE (u)-[:POSTED]->(p)
    MERGE (p)-[:BELONGS_TO]->(f)
    """, username=username, post_id=post_id, forum_name=forum_name)

# Main function to save full data


def save_user_post_forum(username, post_id, content, score, topic, forum_name):
    with driver.session() as session:
        session.write_transaction(create_user, username)
        session.write_transaction(create_post, post_id, content, score, topic)
        session.write_transaction(create_forum, forum_name)
        session.write_transaction(
            create_relationships, username, post_id, forum_name)
