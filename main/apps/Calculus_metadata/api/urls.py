"""
Calculus_metadata API URLs
"""
from django.urls import path
from main.apps.Calculus_metadata.actors import (
    StudentActor,
    ScoreActor,
    TestActor,
    TestFiledataActor,
)

urlpatterns = [
    # Student_MetadataWriter APIs
    path('Student_MetadataWriter/create', StudentActor.create, name='student_create'),
    path('Student_MetadataWriter/read', StudentActor.read, name='student_read'),
    path('Student_MetadataWriter/update', StudentActor.update, name='student_update'),
    path('Student_MetadataWriter/delete', StudentActor.delete, name='student_delete'),
    path('Student_MetadataWriter/status', StudentActor.status, name='student_status'),
    
    # Score_MetadataWriter APIs
    path('Score_MetadataWriter/create', ScoreActor.create, name='score_create'),
    path('Score_MetadataWriter/read', ScoreActor.read, name='score_read'),
    path('Score_MetadataWriter/update', ScoreActor.update, name='score_update'),
    path('Score_MetadataWriter/delete', ScoreActor.delete, name='score_delete'),
    path('Score_MetadataWriter/calculation_final', ScoreActor.calculation_final, name='score_calculation_final'),
    path('Score_MetadataWriter/test_score', ScoreActor.test_score, name='score_test_score'),
    
    # Test_MetadataWriter APIs
    path('Test_MetadataWriter/create', TestActor.create, name='test_create'),
    path('Test_MetadataWriter/read', TestActor.read, name='test_read'),
    path('Test_MetadataWriter/update', TestActor.update, name='test_update'),
    path('Test_MetadataWriter/delete', TestActor.delete, name='test_delete'),
    path('Test_MetadataWriter/status', TestActor.status, name='test_status'),
    path('Test_MetadataWriter/setweight', TestActor.setweight, name='test_setweight'),
    
    # test-filedata APIs (NonSQL)
    path('test-filedata/create', TestFiledataActor.create, name='testfiledata_create'),
    path('test-filedata/read', TestFiledataActor.read, name='testfiledata_read'),
    path('test-filedata/update', TestFiledataActor.update, name='testfiledata_update'),
    path('test-filedata/delete', TestFiledataActor.delete, name='testfiledata_delete'),
]
