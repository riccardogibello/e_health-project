SELECT '# serious games' , count(*) FROM labeled_app WHERE human_classified = 1
UNION
SELECT '# training apps', count(*) FROM app_features
UNION
SELECT '# teacher approved apps in training', count(*) FROM app_features WHERE teacher_approved = 1
UNION
SELECT '# apps', count(*) FROM app;