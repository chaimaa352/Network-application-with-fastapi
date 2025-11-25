import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test_connection():
    """Test de connexion à MongoDB local SANS authentification"""
    
    # URL SANS authentification
    mongodb_url = "mongodb://localhost:27017"
    
    print("🔄 Tentative de connexion à MongoDB (sans authentification)...")
    print(f"URL: {mongodb_url}")
    
    try:
        # Créer le client
        client = AsyncIOMotorClient(mongodb_url)
        
        # Test ping
        await client.admin.command('ping')
        print("✅ Connexion MongoDB réussie!")
        
        # Lister les bases de données
        dbs = await client.list_database_names()
        print(f"📚 Bases de données disponibles: {dbs}")
        
        # Accéder à la base social_network
        db = client["social_network"]
        print(f"✅ Base de données 'social_network' accessible")
        
        # Insérer un document de test
        test_collection = db["test_connection"]
        result = await test_collection.insert_one({"message": "Test OK", "status": "success"})
        print(f"✅ Document inséré avec ID: {result.inserted_id}")
        
        # Lire le document
        doc = await test_collection.find_one({"_id": result.inserted_id})
        print(f"📄 Document lu: {doc}")
        
        # Supprimer le document
        await test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Document supprimé")
        
        # Fermer la connexion
        client.close()
        print("\n🎉 Test de connexion réussi!")
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")

if __name__ == "__main__":
    print("="*50)
    print("TEST MONGODB LOCAL")
    print("="*50)
    asyncio.run(test_connection())