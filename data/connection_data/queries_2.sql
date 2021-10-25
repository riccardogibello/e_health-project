SELECT '# serious games' , count(*) FROM app_features WHERE is_serious_game = 1
UNION
SELECT '# training apps', count(*) FROM app_features
UNION
SELECT '# teacher approved apps in training', count(*) FROM app_features WHERE teacher_approved = 1
UNION
SELECT '# apps', count(*) FROM app;