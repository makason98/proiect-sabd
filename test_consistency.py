"""
Script de testare automată pentru consistența datelor SQL Server <-> CouchDB

Testează:
1. Creare student (SQL + CouchDB sync)
2. Verificare consistență
3. Actualizare student
4. Verificare sync UPDATE
5. Ștergere student
6. Verificare sync DELETE

Rulare:
    python test_consistency.py
"""

import requests
import time
from datetime import date

BASE_URL = "http://127.0.0.1:8000"
COUCHDB_URL = "http://admin:password@localhost:5984/students_sync"

def test_create_student():
    """Test CREATE + sync"""
    print("\n🧪 TEST 1: CREATE Student")
    
    student_data = {
        "nume": "Test",
        "prenume": "Consistency",
        "email": f"test.consistency.{int(time.time())}@example.com",
        "data_nasterii": "1995-05-15"
    }
    
    # 1. Creare via API
    response = requests.post(f"{BASE_URL}/students/", json=student_data)
    
    if response.status_code != 200:
        print(f"❌ Eroare creare student: {response.status_code}")
        return None
    
    student = response.json()
    student_id = student['id']
    print(f"✅ Student creat cu ID={student_id}")
    
    # 2. Verificare în CouchDB
    time.sleep(0.5)  # Așteptare sincronizare
    couch_response = requests.get(f"{COUCHDB_URL}/student_{student_id}")
    
    if couch_response.status_code == 200:
        couch_doc = couch_response.json()
        if couch_doc.get('nume') == student_data['nume']:
            print(f"✅ Date sincronizate corect în CouchDB")
            return student_id
        else:
            print(f"❌ Date inconsistente în CouchDB")
            return None
    else:
        print(f"❌ Document nu există în CouchDB")
        return None

def test_update_student(student_id):
    """Test UPDATE + sync"""
    print(f"\n🧪 TEST 2: UPDATE Student (ID={student_id})")
    
    updated_data = {
        "nume": "Updated",
        "prenume": "Name",
        "email": f"updated.{int(time.time())}@example.com",
        "data_nasterii": "1995-05-15"
    }
    
    # 1. Actualizare via API
    response = requests.put(f"{BASE_URL}/students/{student_id}", json=updated_data)
    
    if response.status_code != 200:
        print(f"❌ Eroare actualizare: {response.status_code}")
        return False
    
    print(f"✅ Student actualizat în SQL")
    
    # 2. Verificare în CouchDB
    time.sleep(0.5)
    couch_response = requests.get(f"{COUCHDB_URL}/student_{student_id}")
    
    if couch_response.status_code == 200:
        couch_doc = couch_response.json()
        if couch_doc.get('nume') == "Updated":
            print(f"✅ UPDATE sincronizat corect în CouchDB")
            return True
        else:
            print(f"❌ UPDATE nu s-a sincronizat")
            return False
    else:
        print(f"❌ Document nu există în CouchDB după UPDATE")
        return False

def test_delete_student(student_id):
    """Test DELETE + sync"""
    print(f"\n🧪 TEST 3: DELETE Student (ID={student_id})")
    
    # 1. Ștergere via API
    response = requests.delete(f"{BASE_URL}/students/{student_id}")
    
    if response.status_code != 200:
        print(f"❌ Eroare ștergere: {response.status_code}")
        return False
    
    print(f"✅ Student șters din SQL")
    
    # 2. Verificare în CouchDB
    time.sleep(0.5)
    couch_response = requests.get(f"{COUCHDB_URL}/student_{student_id}")
    
    if couch_response.status_code == 404:
        print(f"✅ DELETE sincronizat corect (document șters din CouchDB)")
        return True
    else:
        print(f"❌ Document încă există în CouchDB după DELETE")
        return False

def main():
    print("=" * 60)
    print("🚀 TESTARE CONSISTENȚĂ SQL SERVER <-> COUCHDB")
    print("=" * 60)
    
    results = {
        "create": False,
        "update": False,
        "delete": False
    }
    
    # Test CREATE
    student_id = test_create_student()
    if student_id:
        results["create"] = True
        
        # Test UPDATE
        if test_update_student(student_id):
            results["update"] = True
        
        # Test DELETE
        if test_delete_student(student_id):
            results["delete"] = True
    
    # Rezultate finale
    print("\n" + "=" * 60)
    print("📊 REZULTATE FINALE")
    print("=" * 60)
    print(f"CREATE + Sync: {'✅ PASS' if results['create'] else '❌ FAIL'}")
    print(f"UPDATE + Sync: {'✅ PASS' if results['update'] else '❌ FAIL'}")
    print(f"DELETE + Sync: {'✅ PASS' if results['delete'] else '❌ FAIL'}")
    
    all_passed = all(results.values())
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 TOATE TESTELE AU TRECUT!")
    else:
        print("⚠️  UNELE TESTE AU EȘUAT")
    print("=" * 60)

if __name__ == "__main__":
    main()
