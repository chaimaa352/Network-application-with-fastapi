"""
Script to initialize the database with sample data
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import random

# Sample data
SAMPLE_USERS = [
    {
        "title": "mr",
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "dateOfBirth": datetime(1990, 5, 15),
        "phone": "+1234567890",
        "picture": "https://randomuser.me/api/portraits/men/1.jpg",
        "location": {
            "street": "123 Main Street",
            "city": "New York",
            "state": "NY",
            "country": "USA",
            "timezone": "-5:00",
        },
    },
    {
        "title": "miss",
        "firstName": "Jane",
        "lastName": "Smith",
        "email": "jane.smith@example.com",
        "dateOfBirth": datetime(1992, 8, 20),
        "phone": "+1987654321",
        "picture": "https://randomuser.me/api/portraits/women/2.jpg",
        "location": {
            "street": "456 Oak Avenue",
            "city": "Los Angeles",
            "state": "CA",
            "country": "USA",
            "timezone": "-8:00",
        },
    },
    {
        "title": "dr",
        "firstName": "Marie",
        "lastName": "Dubois",
        "email": "marie.dubois@example.com",
        "dateOfBirth": datetime(1985, 3, 10),
        "phone": "+33612345678",
        "picture": "https://randomuser.me/api/portraits/women/3.jpg",
        "location": {
            "street": "10 Rue de la Paix",
            "city": "Paris",
            "state": "Île-de-France",
            "country": "France",
            "timezone": "+1:00",
        },
    },
    {
        "title": "mr",
        "firstName": "Ahmed",
        "lastName": "Hassan",
        "email": "ahmed.hassan@example.com",
        "dateOfBirth": datetime(1988, 11, 25),
        "phone": "+212612345678",
        "picture": "https://randomuser.me/api/portraits/men/4.jpg",
        "location": {
            "street": "25 Boulevard Mohammed V",
            "city": "Rabat",
            "state": "Rabat-Salé-Kénitra",
            "country": "Morocco",
            "timezone": "+0:00",
        },
    },
    {
        "title": "miss",
        "firstName": "Sofia",
        "lastName": "Garcia",
        "email": "sofia.garcia@example.com",
        "dateOfBirth": datetime(1995, 7, 5),
        "phone": "+34612345678",
        "picture": "https://randomuser.me/api/portraits/women/5.jpg",
        "location": {
            "street": "Calle Mayor 15",
            "city": "Madrid",
            "state": "Madrid",
            "country": "Spain",
            "timezone": "+1:00",
        },
    },
]

SAMPLE_POSTS_TEMPLATES = [
    {
        "text": "Just discovered an amazing new tech stack! FastAPI is incredibly fast and easy to use. Highly recommend it for building modern APIs. The async support is phenomenal!",
        "tags": ["technology", "fastapi", "python", "programming"],
    },
    {
        "text": "Beautiful sunset today at the beach. Nature never ceases to amaze me. Perfect way to end a productive day!",
        "tags": ["nature", "photography", "sunset", "beach"],
    },
    {
        "text": "Finished reading 'Clean Code' by Robert Martin. Essential read for any software developer. The principles are timeless!",
        "tags": ["books", "programming", "learning", "development"],
    },
    {
        "text": "Excited to announce that our team won the hackathon! Building innovative solutions with MongoDB and FastAPI was an incredible experience.",
        "tags": ["hackathon", "technology", "innovation", "teamwork"],
    },
    {
        "text": "Morning coffee and coding session. There's something magical about solving complex problems early in the day.",
        "tags": ["lifestyle", "coding", "productivity", "coffee"],
    },
    {
        "text": "Just deployed my first microservices architecture using Docker and Kubernetes. The learning curve was steep but worth it!",
        "tags": ["devops", "docker", "kubernetes", "microservices"],
    },
    {
        "text": "Travel tip: Always backup your code before leaving for a trip. Learned this the hard way!",
        "tags": ["travel", "programming", "tips", "lifestyle"],
    },
    {
        "text": "The AI revolution is here! Working on an exciting machine learning project using TensorFlow. The possibilities are endless.",
        "tags": ["ai", "machinelearning", "tensorflow", "innovation"],
    },
]

SAMPLE_COMMENTS = [
    "Great post! Thanks for sharing.",
    "This is exactly what I was looking for!",
    "Interesting perspective. I agree with your points.",
    "Could you elaborate more on this topic?",
    "Amazing content! Keep it up!",
    "I had a similar experience. Very relatable.",
    "This helped me solve my problem. Thank you!",
    "Love the enthusiasm in this post!",
    "Bookmarking this for future reference.",
    "Excellent explanation! Very clear and concise.",
]


async def init_database():
    """Initialize database with sample data"""

    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["social_network"]

    print(" Clearing existing data...")
    await db.users.delete_many({})
    await db.posts.delete_many({})
    await db.comments.delete_many({})

    # Insert users
    print(" Creating users...")
    user_ids = []
    for user_data in SAMPLE_USERS:
        user_data["registerDate"] = datetime.utcnow() - timedelta(
            days=random.randint(30, 365)
        )
        result = await db.users.insert_one(user_data)
        user_ids.append(str(result.inserted_id))
        print(f"   ✓ Created user: {user_data['firstName']} {user_data['lastName']}")

    # Insert posts
    print("\n Creating posts...")
    post_ids = []
    for i, post_template in enumerate(SAMPLE_POSTS_TEMPLATES):
        for j in range(2):  # Create 2 posts per template with different users
            post_data = {
                "text": post_template["text"],
                "image": f"https://picsum.photos/800/600?random={i}{j}",
                "likes": random.randint(0, 100),
                "tags": post_template["tags"],
                "owner": user_ids[random.randint(0, len(user_ids) - 1)],
                "link": f"https://example.com/article/{i}{j}",
                "publishDate": datetime.utcnow()
                - timedelta(days=random.randint(1, 30)),
            }
            result = await db.posts.insert_one(post_data)
            post_ids.append(str(result.inserted_id))
            print(f"   ✓ Created post {len(post_ids)}: {post_data['text'][:50]}...")

    # Insert comments
    print("\n Creating comments...")
    comment_count = 0
    for post_id in post_ids:
        # Random number of comments per post (1-5)
        num_comments = random.randint(1, 5)
        for _ in range(num_comments):
            comment_data = {
                "message": random.choice(SAMPLE_COMMENTS),
                "owner": user_ids[random.randint(0, len(user_ids) - 1)],
                "post": post_id,
                "publishDate": datetime.utcnow() - timedelta(days=random.randint(0, 7)),
            }
            await db.comments.insert_one(comment_data)
            comment_count += 1

    print(f"   ✓ Created {comment_count} comments")

    # Summary
    print("\n" + "=" * 50)
    print(" Database initialized successfully!")
    print("=" * 50)
    print(f" Users: {len(user_ids)}")
    print(f" Posts: {len(post_ids)}")
    print(f" Comments: {comment_count}")
    print(
        f"  Tags: {len(set([tag for post in SAMPLE_POSTS_TEMPLATES for tag in post['tags']]))}"
    )
    print("\n You can now access the API at http://localhost:8000/api/v1")
    print(" Documentation: http://localhost:8000/api/v1/docs")

    client.close()


if __name__ == "__main__":
    asyncio.run(init_database())
